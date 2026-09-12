# -*- coding: utf-8 -*-
"""总装：从 parsed/*.json 构建真题库交付目录"""
import re, os, json, sys, glob, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(BASE, *a)
ROOT = os.path.normpath(os.path.join(BASE, "..", "真题库"))
sys.path.insert(0, BASE)
from parse_lib import MODULES

YEARS = range(2011, 2027)
LEVELS = ["副省级", "地市级", "行政执法类", "合卷"]
MOD_DIR = {"政治理论": "05_常识判断与政治理论", "常识判断": "05_常识判断与政治理论",
           "言语理解与表达": "04_言语理解与表达", "数量关系": "01_数量关系",
           "判断推理": "03_判断推理", "资料分析": "02_资料分析"}
MOD_ORDER = ["01_数量关系", "02_资料分析", "03_判断推理", "04_言语理解与表达", "05_常识判断与政治理论"]
MOD_TITLE = {"01_数量关系": "数量关系", "02_资料分析": "资料分析", "03_判断推理": "判断推理",
             "04_言语理解与表达": "言语理解与表达", "05_常识判断与政治理论": "常识判断与政治理论"}


def load(name):
    f = os.path.join(P("parsed"), name)
    if os.path.exists(f):
        return json.load(open(f, encoding="utf-8"))
    return None


def norm_stem(s, n=42):
    s = re.sub(r"[^\u4e00-\u9fa50-9A-Za-z]", "", s or "")
    return s[:n]


# ---------------------------------------------------------------- 行测论文注册
def build_xingce_registry():
    """(year, level) -> {questions:[blocks with module], answers:{num:(ans,ana)}, source_info}"""
    papers = {}
    for y in YEARS:
        for lv in ["合卷"] if y <= 2014 else ["副省级", "地市级"]:
            papers[(y, lv)] = {"year": y, "level": lv, "sections": None, "answers": {}, "qsrc": None, "asrc": None}
        if y >= 2023:
            papers[(y, "行政执法类")] = {"year": y, "level": "行政执法类", "sections": None, "answers": {}, "qsrc": None, "asrc": None}
        # 注：2022年行测无官方行政执法卷，不收录

    # --- 题目来源优先级: sl解析PDF > xg > aipta > sl_html(仅2022地市) ---
    prio = ["sl", "xg", "aipta", "slh"]
    for (y, lv), pap in papers.items():
        for tag in prio:
            data = load(f"{tag}_xc_{y}_{lv}.json")
            if data and data.get("total", 0) >= 100:
                pap["sections"] = data["sections"]
                pap["qsrc"] = f"{tag}"
                is_sl_pdf = data.get("meta", {}).get("source") == "sanlianbook解析PDF"
                if tag == "sl" and is_sl_pdf:  # 仅解析PDF自带答案
                    for mod, blocks in data["sections"].items():
                        for b in blocks:
                            if b.get("ans"):
                                pap["answers"][b["num"]] = (b["ans"], b.get("ana", ""), b.get("stem", ""))
                    pap["asrc"] = "sl"
                break

    # 2016副省：sl版缺损(130题)，改用aipta完整135题 + sl答案按题干匹配
    a16 = load("aipta_xc_2016_副省级.json")
    s16 = load("sl_xc_2016_副省级.json")
    if a16 and s16:
        papers[(2016, "副省级")]["sections"] = a16["sections"]
        papers[(2016, "副省级")]["qsrc"] = "aipta"
        papers[(2016, "副省级")]["answers"] = {}
        by_stem = {}
        for mod in s16["sections"]:
            for b in s16["sections"][mod]:
                if b.get("ans"):
                    by_stem[norm_stem(b["stem"])] = (b["ans"], b.get("ana", ""), b.get("stem", ""))
        for mod in a16["sections"]:
            for b in a16["sections"][mod]:
                k = norm_stem(b.get("stem", ""))
                if k in by_stem:
                    papers[(2016, "副省级")]["answers"][b["num"]] = by_stem[k]
        papers[(2016, "副省级")]["asrc"] = "sl"

    # 2026执法：改用aipta完整130题
    a26 = load("aipta_xc_2026_行政执法类.json")
    if a26 and a26.get("total", 0) >= 100:
        papers[(2026, "行政执法类")]["sections"] = a26["sections"]
        papers[(2026, "行政执法类")]["qsrc"] = "aipta"

    # 2015-2017: sl只有一版；另一版用aipta题目
    for y in (2015, 2016, 2017):
        sl_lv = "地市级" if os.path.exists(os.path.join(P("parsed"), f"sl_xc_{y}_地市级.json")) else "副省级"
        other = "副省级" if sl_lv == "地市级" else "地市级"
        if papers[(y, other)]["sections"] is None:
            data = load(f"aipta_xc_{y}_{other}.json")
            if data and data.get("total", 0) >= 100:
                papers[(y, other)]["sections"] = data["sections"]
                papers[(y, other)]["qsrc"] = "aipta"

    # --- 视觉核对补丁（缺公式等） ---
    pf = os.path.join(BASE, "visual_patches.json")
    if os.path.exists(pf):
        for k, v in json.load(open(pf, encoding="utf-8")).items():
            y, lv, mod, num = k.split("|")
            pap = papers.get((int(y), lv))
            if not pap or not pap["sections"]:
                continue
            for b in pap["sections"].get(mod, []):
                if b["num"] == int(num):
                    if v.get("stem"):
                        b["stem"] = v["stem"]
                    if v.get("opts"):
                        b["opts"] = v["opts"]

    # --- 答案: 同年另一卷 stem 继承 (2015-2017另一版 & 2022地市) ---
    for (y, lv), pap in papers.items():
        if pap["sections"] and not pap["answers"]:
            for (y2, lv2), src in papers.items():
                if y2 == y and lv2 != lv and src["answers"]:
                    # 题号对齐: 官方两卷题号在共同模块一致（常识/言语），但数量/判断不同 → 用stem匹配
                    ans_by_stem = {}
                    for num, (a, ana, stem) in src["answers"].items():
                        ans_by_stem[norm_stem(stem)] = (a, ana)
                    for mod, blocks in pap["sections"].items():
                        for b in blocks:
                            k = norm_stem(b.get("stem", ""))
                            if k and k in ans_by_stem:
                                a, ana = ans_by_stem[k]
                                pap["answers"][b["num"]] = (a, ana, b.get("stem", ""))
                    pap["asrc"] = f"inherit:{lv2}"
                    break

    # 2026: hqwx 答案补充
    for lv in ["副省级", "地市级", "行政执法类"]:
        d = load(f"hqwx_xc_2026_{lv}_a.json")
        if d and papers.get((2026, lv)):
            for num, v in d["answers"].items():
                num = int(num)
                if v.get("ans") and num not in papers[(2026, lv)]["answers"]:
                    papers[(2026, lv)]["answers"][num] = (v["ans"], v.get("ana", ""), v.get("stem", ""))
            if d["answers"]:
                papers[(2026, lv)]["asrc"] = (papers[(2026, lv)].get("asrc") or "") + "+hqwx"

    # 粉笔答案合并（2023-2026 权威源，先于 AI）
    fa_f = os.path.join(BASE, "fenbi_answers.json")
    if os.path.exists(fa_f):
        fa = json.load(open(fa_f, encoding="utf-8"))
        for key, amap in fa.items():
            y, lv = key.split("|")
            pap = papers.get((int(y), lv))
            if not pap or not pap["sections"]:
                continue
            for num, v in amap.items():
                num = int(num)
                if num in pap["answers"]:
                    continue
                note = "粉笔答案" if v.get("mapped") else "粉笔答案（粉笔卷选项顺序，字母未映射）"
                pap["answers"][num] = (v["ans"], note, "")
                pap.setdefault("fbsrc", set()).add(num)
                if not v.get("mapped"):
                    pap.setdefault("fbunmapped", set()).add(num)
    for pap in papers.values():
        pap["fbsrc"] = pap.get("fbsrc", set())
        pap["fbunmapped"] = pap.get("fbunmapped", set())

    # AI 独立解答合并（仅填空缺）+ 争议检测
    ai_f = os.path.join(BASE, "ai_answers.json")
    ai = json.load(open(ai_f, encoding="utf-8")) if os.path.exists(ai_f) else {}
    for key, answers in ai.items():
        if "|" not in key or not isinstance(answers, dict):
            continue
        y, lv, mod = key.split("|")
        pap = papers.get((int(y), lv))
        if not pap or not pap["sections"]:
            continue
        for num, val in answers.items():
            num = int(num)
            block = next((b for b in pap["sections"].get(mod, []) if b["num"] == num), None)
            if block is None:
                continue
            if val.startswith("?"):
                if num not in pap["answers"]:
                    reason = {"?图": "图形题，AI无法仅凭文字作答，请看原卷图", "?矛盾": "回忆版题面数据自相矛盾，答案待核",
                              "?表": "题目依赖原卷表格，答案待核"}.get(val, "答案待核")
                    pap["answers"][num] = ("待核", reason, block.get("stem", ""))
                    pap["airaw"] = pap.get("airaw", {})
                    pap["airaw"][num] = val
                continue
            letter = val[-1] if val.endswith("图") else val
            if num in pap["answers"]:
                inst = pap["answers"][num][0]
                if inst and inst != letter and num not in pap.get("fbunmapped", set()):
                    pap.setdefault("disputes", {})[num] = {"ai": letter, "inst": inst}
            else:
                note = "AI独立解答，建议用粉笔/华图APP复核"
                if val.endswith("图"):
                    note = "AI基于对原图的视觉判读作答，建议复核"
                pap["answers"][num] = (letter, note, block.get("stem", ""))
                pap.setdefault("aisrc", set()).add(num)
    for pap in papers.values():
        pap["airaw"] = pap.get("airaw", {})
        pap["aisrc"] = pap.get("aisrc", set())
        pap["disputes"] = pap.get("disputes", {})
    return papers


# ---------------------------------------------------------------- 渲染
def esc(t):
    return (t or "").replace("|", "｜").strip()


IMG_MAP = None

def get_images(year, level, mod, num):
    global IMG_MAP
    if IMG_MAP is None:
        import json as _json
        f = os.path.join(BASE, "img_map.json")
        raw = _json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
        IMG_MAP = {}
        for k, name in raw.items():
            y, lv, m, n, seq = k.split("|")
            IMG_MAP.setdefault((y, lv, m, int(n)), []).append((int(seq), name))
        for v in IMG_MAP.values():
            v.sort()
    return [name for _, name in IMG_MAP.get((str(year), level, mod, num), [])]


def fmt_question(q, with_ans=None, tag="", year=None, level=None, mod=None):
    """渲染一道题。with_ans: None|答案字母"""
    out = [f"**{q['num']}.** {q.get('stem','').strip()}"]
    if tag:
        out[0] = f"**{q['num']}.** {q.get('stem','').strip()}" + f"  `[{tag}]`"
    opts = q.get("opts") or {}
    for k in "ABCD":
        if k in opts and opts[k]:
            out.append(f"- {k}. {opts[k]}")
    imgs = get_images(year, level, mod, q["num"]) if year else []
    if imgs:
        for name in imgs:
            out.append(f"")
            out.append(f"![题目原图](../../图片/{name})")
    elif len(opts) == 0:
        out.append("> （本题选项为图片，请配合原始PDF查看）")
    if with_ans:
        if with_ans == "?":
            out.append(f"> **答案**：待补（见下方说明）")
        else:
            out.append(f"> **答案**：{with_ans}")
    out.append("")
    return "\n".join(out)


def answer_table(answers, total_max, ai_nums=None, disputes=None, pending=None):
    """答案速查表，每行10题"""
    if not answers:
        return "（暂无答案数据）\n"
    ai_nums = ai_nums or set()
    disputes = disputes or {}
    nums = sorted(answers)
    rows = []
    line = []
    for n in range(1, total_max + 1):
        a = answers.get(n)
        if a == "待核":
            s = "？"
        else:
            s = str(a) if a else "—"
        if n in disputes:
            s = "⚠{}/{}†".format(s, disputes[n]["ai"])
        elif n in ai_nums and a:
            s = s + "†"
        line.append(s)
        if len(line) == 10:
            rows.append((n - 9, n, line[:]))
            line = []
    if line:
        rows.append((rows[-1][1] + 1 if rows else 1, nums[-1], line))
    out = ["| 题号 | " + " | ".join(str(i) for i in range(1, 11)) + " |", "|---" * 11 + "|"]
    for s, e, vals in rows:
        out.append(f"| {s}-{s+len(vals)-1} | " + " | ".join(vals) + " |")
    return "\n".join(out) + "\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    papers = build_xingce_registry()
    YDIR = os.path.join(ROOT, "按年份")

    # 统计
    stats = []
    for (y, lv), pap in sorted(papers.items()):
        if not pap["sections"]:
            stats.append((y, lv, 0, 0, pap.get("qsrc"), pap.get("asrc")))
            continue
        qs = {mod: pap["sections"].get(mod, []) for mod in MODULES}
        total = sum(len(v) for v in pap["sections"].values())
        nans = len(pap["answers"])
        stats.append((y, lv, total, nans, pap.get("qsrc"), pap.get("asrc")))

        ydir = os.path.join(YDIR, f"{y}年国考")
        lvname = lv if lv != "合卷" else "（2015年前合卷）"
        # ---------- 题目文件 ----------
        L = [f"# {y}年国考《行政职业能力测验》真题（{lvname}）", ""]
        L.append(f"> 题目来源：{SRC_NAME.get(pap['qsrc'], pap['qsrc'])}（考生回忆版）｜共 {total} 题")
        L.append(f"> 答案与解析见同目录《{y}年国考行测答案与解析（{lvname}）.md》")
        L.append("")
        for mod in MODULES:
            blocks = pap["sections"].get(mod)
            if not blocks:
                continue
            sub = SUBTITLE.get(mod, "")
            L.append(f"## {mod}")
            if sub:
                L.append(f"*{sub}*")
            L.append("")
            for b in blocks:
                L.append(fmt_question(b, year=y, level=lv, mod=mod))
        write(os.path.join(ydir, f"行测_{'题目' if lv!='合卷' else '题目'}_{lv}.md").replace("行测_题目_", "行测_") if False else os.path.join(ydir, f"行测_{lv}_题目.md"), "\n".join(L))

        # ---------- 答案与解析文件 ----------
        A = [f"# {y}年国考《行政职业能力测验》答案与解析（{lvname}）", ""]
        asrc_disp = SRC_NAME.get(pap.get("asrc") or "", pap.get("asrc") or "")
        if pap.get("fbsrc"):
            asrc_disp = "粉笔题库（权威答案）" + (" + " + asrc_disp if asrc_disp and "AI" not in asrc_disp else "")
        if pap.get("aisrc") and not pap.get("fbsrc") and (not pap.get("asrc") or pap["asrc"] in ("+hqwx",)):
            asrc_disp = (asrc_disp + " + " if asrc_disp and not asrc_disp.startswith("+") else "") + "AI独立解答（数量关系等，标†）"
        A.append(f"> 答案来源：{asrc_disp or '—'}")
        if (pap.get("asrc") or "").startswith("inherit"):
            A.append("> 注：答案由同年另一卷种同题匹配继承，未匹配上的题目标注「待补」。")
        if y >= 2023:
            A.append("> 注：近4年暂无完整公开文字版解析，缺失部分可用粉笔/华图APP在线解析核对。")
        A.append("")
        A.append("## 答案速查表")
        A.append("")
        ansmap = {n: v[0] for n, v in pap["answers"].items()}
        A.append(answer_table(ansmap, total, pap.get("aisrc"), pap.get("disputes"), pap.get("airaw")))
        A.append("## 逐题解析")
        A.append("")
        for mod in MODULES:
            blocks = pap["sections"].get(mod)
            if not blocks:
                continue
            mod_has = any(b["num"] in pap["answers"] for b in blocks)
            A.append(f"### {mod}")
            A.append("")
            for b in blocks:
                ent = pap["answers"].get(b["num"])
                if ent:
                    a, ana, _ = ent
                    disp = pap.get("disputes", {}).get(b["num"])
                    mark = "（† AI独立解答）" if b["num"] in pap.get("aisrc", set()) else ("（粉笔答案）" if b["num"] in pap.get("fbsrc", set()) else "")
                    if a == "待核":
                        A.append(f"**{b['num']}.** {str(ana)[:50]}")
                        A.append("")
                        continue
                    A.append(f"**{b['num']}.（{a}）**{mark} {esc(b.get('stem',''))[:60]}{'…' if len(b.get('stem',''))>60 else ''}")
                    A.append("")
                    if disp:
                        A.append(f"> ⚠️ 争议题：来源答案 {disp['inst']}，AI独立解答 {disp['ai']}。请以粉笔/华图等APP在线解析为准。")
                        A.append("")
                    if ana:
                        A.append(f"解析：{ana}")
                    else:
                        A.append("（无文字解析，仅有答案）")
                    A.append("")
                else:
                    A.append(f"**{b['num']}.** — 答案待补")
                    A.append("")
        write(os.path.join(ydir, f"行测_{lv}_答案与解析.md"), "\n".join(A))

    json.dump([{ "year": s[0], "level": s[1], "total": s[2], "answers": s[3], "qsrc": s[4], "asrc": s[5]} for s in stats],
              open(P("stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for s in stats:
        print(s)


SRC_NAME = {
    "sl": "高教公考真题库解析版（含答案+逐题解析）",
    "xg": "星光公考",
    "aipta": "爱题库",
    "slh": "高教公考真题库网页版",
    "inherit:副省级": "同年副省级卷同题继承",
    "inherit:地市级": "同年地市级卷同题继承",
    "+hqwx": "环球网校回忆版（2026年部分题目答案）",
    "sl+hqwx": "高教解析版 + 环球网校（2026补充）",
}

SUBTITLE = {
    "常识判断": "根据题目要求，在四个选项中选出一个最恰当的答案。",
}

if __name__ == "__main__":
    main()
