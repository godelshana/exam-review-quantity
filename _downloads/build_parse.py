# -*- coding: utf-8 -*-
"""把所有来源解析成结构化 JSON：parsed/ 目录"""
import re, os, json, sys, glob
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lib import pdf_clean, find_sections, normalize_module, join_cjk, MODULES, SUB_SEC

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed")
os.makedirs(OUT, exist_ok=True)

Q_LINE = re.compile(r"^(\d{1,3})[．.、]\s*(.*)$")
OPT_LINE = re.compile(r"^([A-D])\s*[．.、、]\s*(.*)$")
MULTI_OPT = re.compile(r"^A\s*[．.、]\s*(.*?)\s*B\s*[．.、]\s*(.*?)\s*C\s*[．.、]\s*(.*?)\s*D\s*[．.、]\s*(.*)$")
ANS_LINE = re.compile(r"^【答案】\s*([A-D]{1,4})")
BARE_ANS = re.compile(r"^\d{1,3}[．.、]\s*[A-D]?\s*$")          # hqwx答案行 "20.A" / "21."
GZH_ANS = re.compile(r"故正确答案为\s*([A-D])")
JIE_START = re.compile(r"^【解析】|^解析[：:]")


def parse_blocks(lines, start_num=1):
    """状态机切题：仅接受 期望题号 的题行。返回 blocks: [{num, body_lines, ans, analysis_lines}]"""
    blocks = []
    expect = start_num
    cur = None
    mode = None  # stem/opt/ana + opt_key
    opt_key = None
    near_subheader = 0  # 子部分标题后的宽容窗口

    def new_block(num, first):
        nonlocal cur, mode, opt_key
        cur = {"num": num, "stem": [first] if first else [], "opts": {}, "ans": None, "ana": []}
        mode, opt_key = "stem", None

    for ln in lines:
        if BARE_ANS.match(ln):
            # "20.A"/"21." 裸答案行：取答案，不作为题号
            m = re.match(r"^(\d{1,3})[．.、]\s*([A-D])", ln)
            if m and cur is not None and int(m.group(1)) == cur["num"] and cur["ans"] is None:
                cur["ans"] = m.group(2)
                mode = "ana"
            elif cur is not None:
                mode = "ana"
            continue
        gm = GZH_ANS.search(ln)
        if gm and cur is not None:
            cur["ans"] = gm.group(1)
            rest = GZH_ANS.sub("", ln).strip("。 ，,")
            if rest:
                cur["ana"].append(rest)
            mode = "ana"
            continue
        if SUB_SEC.match(ln):
            near_subheader = 4
        qm = Q_LINE.match(ln)
        if qm:
            num = int(qm.group(1))
            rest = qm.group(2) or ""
            has_cjk = bool(re.search(r"[\u4e00-\u9fff]", rest))
            # 接受：正着来 / 跳一个号且题干像文字（防止表格数值"116.5"误判）/ 子部分标题后重新同步
            ok = num == expect or ((num == expect + 1 or (near_subheader > 0 and num >= expect - 2)) and has_cjk)
            if ok:
                if cur is not None:
                    blocks.append(cur)
                new_block(num, rest.strip())
                expect = num + 1
                if near_subheader:
                    near_subheader -= 1
                continue
        if near_subheader:
            near_subheader -= 1
        if cur is None:
            continue
        am = ANS_LINE.match(ln)
        if am:
            cur["ans"] = am.group(1)
            mode = "ana"
            rest = ANS_LINE.sub("", ln).strip()
            rest = re.sub(r"^[。.：:,，]\s*", "", rest)
            rest = re.sub(r"^解析[：:]\s*", "", rest)
            if rest:
                cur["ana"].append(rest)
            continue
        if mode == "ana":
            cur["ana"].append(ln)
            continue
        # 行内出现>=2个选项标记时按标记拆分
        marks = list(re.finditer(r"([A-D])\s*[．.、]\s*", ln))
        if len(marks) >= 2:
            segs = {}
            for i2, m2 in enumerate(marks):
                start_i = m2.end()
                end_i = marks[i2 + 1].start() if i2 + 1 < len(marks) else len(ln)
                segs[m2.group(1)] = ln[start_i:end_i].strip()
            if any(not cur["opts"].get(k2) for k2 in segs):
                for key, val in segs.items():
                    if not cur["opts"].get(key):
                        cur["opts"][key] = [val] if val else []
                opt_key = max(segs)
                mode = "opt"
                continue
        om = OPT_LINE.match(ln)
        if om and not cur["opts"].get(om.group(1)):
            opt_key = om.group(1)
            cur["opts"][opt_key] = [om.group(2).strip()] if om.group(2).strip() else []
            mode = "opt"
            continue
        if mode == "opt" and opt_key:
            cur["opts"][opt_key].append(ln)
        else:
            cur["stem"].append(ln)
    if cur is not None:
        blocks.append(cur)
    for b in blocks:
        b["stem"] = join_cjk(b["stem"])
        b["opts"] = {k: join_cjk(v) for k, v in b["opts"].items()}
        b["ana"] = join_cjk(b["ana"])
    return blocks


def extract_sections(full_lines):
    """在清洗后的行上定位五大模块标题，返回 {module: lines}。标题行本身去掉。"""
    secs = find_sections(full_lines)
    result = {}
    used = set()
    for idx, (i, name) in enumerate(secs):
        mod = normalize_module(name)
        if not mod or mod in used:
            continue
        end = secs[idx + 1][0] if idx + 1 < len(secs) else len(full_lines)
        result[mod] = full_lines[i + 1:end]
        used.add(mod)
    return result


def parse_paper(lines, expect_total=None):
    """输入整卷清洗后的行，输出 {sections:{mod:[blocks]}, order:[mods], total:int}"""
    secs = extract_sections(lines)
    out = {"sections": {}, "order": [], "issues": []}
    next_num = 1
    for mod in MODULES:
        if mod not in secs:
            out["issues"].append(f"缺少模块: {mod}")
            continue
        blocks = parse_blocks(secs[mod], start_num=next_num)
        out["sections"][mod] = blocks
        out["order"].append(mod)
        if blocks:
            next_num = blocks[-1]["num"] + 1
        n = sum(len(v) for v in out["sections"].values())
    out["total"] = n
    # 连续性检查
    nums = [b["num"] for mod in out["order"] for b in out["sections"][mod]]
    for a, b in zip(nums, nums[1:]):
        if b != a + 1:
            out["issues"].append(f"题号不连续: {a}->{b}")
    return out


def read_pdf_lines(path):
    doc = fitz.open(path)
    raw = "".join(p.get_text() for p in doc)
    return pdf_clean(raw)


def strip_paper_header(lines):
    """去掉试卷说明头（到'第一部分'之前，但保留注意事项精简版）"""
    for i, ln in enumerate(lines):
        if re.match(r"^第[一二三四五]部分", ln):
            return lines[i:]
    return lines
