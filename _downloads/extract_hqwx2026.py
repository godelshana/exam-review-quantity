# -*- coding: utf-8 -*-
"""hqwx 2026行测答案专用宽松提取器：题号允许跳号，仅当题号单调不减时接受"""
import re, os, json, sys
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lib import pdf_clean

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed")
Q_STEM = re.compile(r"^(\d{1,3})[．.、]\s*(\S.*)$")
BARE_ANS = re.compile(r"^(\d{1,3})[．.、]\s*([A-D])\s*$")
GZH = re.compile(r"[故即]?正确答案为\s*([A-D])")

def extract(path):
    doc = fitz.open(path)
    lines = pdf_clean("".join(p.get_text() for p in doc))
    lines = [l for l in lines if not re.match(r"^(26国考行测|~\d+~|2026 ?年国考|注：来源于考生回忆)", l)]
    answers = {}
    prev = 0
    cur = None
    for ln in lines:
        bm = BARE_ANS.match(ln)
        if bm:
            n = int(bm.group(1))
            if cur == n and n in answers or (cur == n):
                answers.setdefault(n, {})["ans"] = bm.group(2)
            continue
        gm = GZH.search(ln)
        if gm and cur is not None:
            answers.setdefault(cur, {})["ans"] = gm.group(1)
            continue
        qm = Q_STEM.match(ln)
        if qm:
            n = int(qm.group(1))
            rest = qm.group(2)
            # 疑似资料分析数据行
            if re.match(r"^[\d.%↵\\s]+$", rest):
                continue
            if prev <= n <= prev + 45:
                cur = n
                prev = n
                answers.setdefault(n, {}).setdefault("stem", rest[:70])
                answers[n]["ana"] = ""
                continue
        if cur is not None and answers.get(cur, {}).get("ans"):
            a = answers[cur]
            if len(a.get("ana", "")) < 900:
                a["ana"] = (a.get("ana", "") + ln)[:900]
    return answers

pairs = [
    ("hqwx_pdf/2026年国考真题《行测》（市地级）答案及解析（网友回忆）_2ae7359ca27b234771d2753342525b8ed1d8e675.pdf", "地市级"),
    ("hqwx_pdf/2026-国考真题-《行测》-（副省）真题及答案（网友回忆）(1)_a3ce53508e279d5ba2bac7aaf8f61f67eefd3b0e.pdf", "副省级"),
]
for f, level in pairs:
    ans = extract(f)
    for n, v in ans.items():
        v.pop("ana", None) if not v.get("ana") else None
    json.dump({"year": 2026, "level": level, "kind": "xinge_answers", "answers": ans},
              open(os.path.join(OUT, f"hqwx_xc_2026_{level}_a.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    got = {n: v.get("ans") for n, v in sorted(ans.items())}
    print(level, len(ans), "题", got)
