# -*- coding: utf-8 -*-
"""行测真题解析库：把各来源的 PDF/HTML 文本解析成结构化题目"""
import re

MODULES = ["政治理论", "常识判断", "言语理解与表达", "数量关系", "判断推理", "资料分析"]
SUB_SEC = re.compile(
    r"^[一二三四五六七八九十]+、\s*"
    r"(政治理论|常识判断|言语理解与表达|片段阅读|语句表达|逻辑填空|数量关系|数学运算|数字推理|"
    r"图形推理|定义判断|类比推理|逻辑判断|资料分析)")
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}

FOOTER_PATTERNS = [
    r"^本试卷由星光公考提供\s*$",
    r"^第\d+页/共\d+页\s*$",
    r"^扫一扫，?对答案\s*$",
    r"^\d{1,3}\s*$",
    r"^咨询热线[：:].*$",
    r"^微信扫码刷题\s*$",
    r"^免费约直播领资料\s*$",
    r"^免费订阅考试提醒\s*$",
    r"^扫二维码下载环球网校移动课堂APP\s*$",
    r"^移动学习职达未来\s*$",
    r"^环球网校移动课堂APP\s*$",
    r"^环球网校侵权必究\s*$",
    r"^扫码关注\w*公众号\s*$",
    r"^扫码用手机访问\s*$",
]
FOOTER_RE = re.compile("|".join(FOOTER_PATTERNS))


def pdf_clean(raw_text, drop_note=True):
    """逐行清洗 PDF 文本：去页眉页脚、去多余空白。"""
    lines = []
    for ln in raw_text.split("\n"):
        ln = ln.replace("\u00a0", " ").rstrip()
        s = ln.strip()
        if not s:
            continue
        if FOOTER_RE.match(s):
            continue
        if drop_note and re.match(r"^注[：:].{0,30}(图|解析|答案)", s):
            continue
        lines.append(s)
    return lines


Q_START = re.compile(r"^(\d{1,3})[．.、]\s*(.*)$")
OPT_START = re.compile(r"^([A-D])\s*[．.、、]\s*(.*)$")
ANS_MARK = re.compile(r"【答案】\s*([A-D]{1,4})")
SEC_RE = re.compile(r"^第([一二三四五六])部分\s*[-—–]?\s*[-—–]?\s*(.*)$")


def find_sections(lines):
    """定位各部分标题，返回 [(module, start_idx)]。标题样式多样：
    '第一部分 常识判断' / '第一部分 - 常识判断' / '第一部分  常识判断 ' / '三、数量关系。...'"""
    secs = []
    for i, ln in enumerate(lines):
        m = SEC_RE.match(ln)
        if m:
            name = m.group(2).strip(" -—–。.，,")
            secs.append((i, name))
            continue
        m2 = re.match(r"^([一二三四五六七八九十])、\s*(常识判断|言语理解(?:与表达)?|数量关系|判断推理|资料分析|政治理论)", ln)
        if m2:
            name = m2.group(2)
            if name == "言语理解":
                name = "言语理解与表达"
            secs.append((i, name))
            continue
        # 标题单独成行：仅包含模块名
        s = ln.strip(" -—–。.，,0-9共题参考时限分钟 ()（）")
        if s in MODULES and len(ln) <= 16:
            secs.append((i, s))
    return secs


def normalize_module(name):
    for m in MODULES:
        if m in name:
            return m
    return None


def join_cjk(parts):
    """把多行合并：中日韩字符间不加空格，其他加一个空格。"""
    out = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if not out:
            out = p
            continue
        a, b = out[-1], p[0]
        if _is_cjk(a) or _is_cjk(b) or a in "（(" or b in "）),，。；：" or a in "、。；：，":
            out += p
        else:
            out += " " + p
    return out


def _is_cjk(ch):
    return "\u4e00" <= ch <= "\u9fff" or ch in "（）：；。，、“”‘’①②③④⑤⑥⑦⑧⑨⑩％"


def split_questions(lines):
    """把一段文本按题号切分为题目列表。返回
    [{num, stem, options:{A:..}, raw_end}]，选项之后的剩余文本并入 stem 尾部字段 extra。"""
    questions = []
    cur = None
    pending = []       # 当前题干行
    opt_key = None
    opt_buf = []

    def flush_q():
        nonlocal cur, pending, opt_key, opt_buf
        if cur is None:
            return
        if opt_key:
            cur["options"][opt_key] = join_cjk(opt_buf)
        cur["stem"] = join_cjk(pending).strip()
        questions.append(cur)
        cur, pending, opt_key, opt_buf = None, [], None, []

    def flush_opt():
        nonlocal opt_key, opt_buf
        if opt_key and opt_buf:
            cur["options"][opt_key] = join_cjk(opt_buf)
        opt_key, opt_buf = None, []

    for ln in lines:
        qm = Q_START.match(ln)
        om = OPT_START.match(ln)
        if qm and (cur is None or int(qm.group(1)) == cur["num"] + 1 or int(qm.group(1)) > cur["num"]):
            flush_q()
            cur = {"num": int(qm.group(1)), "stem": "", "options": {}}
            first = qm.group(2).strip()
            pending = [first] if first else []
        elif om and cur is not None and cur["num"] >= 0:
            # 判断推理图形题选项可能带汉字以外内容，照收
            flush_opt()
            opt_key = om.group(1)
            first = om.group(2).strip()
            opt_buf = [first] if first else []
        elif cur is not None:
            if opt_key:
                opt_buf.append(ln)
            else:
                pending.append(ln)
    flush_q()
    return questions


def parse_answers_from_text(text):
    """从含【答案】X。解析：...的全文中抽出 {题号: (答案, 解析)}"""
    out = {}
    # 题号在【答案】之前不远处出现；按顺序扫描
    pattern = re.compile(r"(\d{1,3})[．.、]\s*(.{0,4000}?)【答案】\s*([A-D]{1,4})(?:。|,|，)?\s*(?:解析[：:])?\s*(.*?)(?=(?:\d{1,3}[．.、]\s*\S{4,4000}?【答案】)|$)", re.S)
    for m in pattern.finditer(text):
        num = int(m.group(1))
        out[num] = (m.group(3), m.group(4).strip())
    return out


def answer_key_by_order(text, total):
    """从答案区按出现顺序提取 {序号: 答案字母}，用于纯答案表。"""
    keys = {}
    for i, m in enumerate(re.finditer(r"(\d{1,3})\s*[．.、]?\s*([A-D])(?![A-Za-z])", text)):
        pass
    return keys
