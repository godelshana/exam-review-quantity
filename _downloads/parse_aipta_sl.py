# -*- coding: utf-8 -*-
"""aipta 申论文章 -> parsed/aipta_sl_{y}_{lv}_q.json"""
import re, os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_parse2 import html_lines

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "parsed")
am = json.load(open(os.path.join(BASE, "aipta_manifest.json"), encoding="utf-8"))
for aid, info in am.items():
    t = info["title"]
    m = re.search(r"(\d{4})国考申论", t)
    if not m:
        continue
    year = int(m.group(1))
    if "副省" in t:
        lv = "副省级"
    elif "地市" in t:
        lv = "地市级"
    elif "行政执法" in t:
        lv = "行政执法类"
    else:
        continue
    lines = html_lines(info["file"])
    # 截尾部
    for i, ln in enumerate(lines):
        if "猜你喜欢" in ln or "注：篇幅有限" in ln or "下载真题" in ln:
            lines = lines[:i]
            break
    # 去掉头部导航行（到 注意事项 / 材料1 / 给定资料1 等）
    start = 0
    for i, ln in enumerate(lines):
        if (ln.startswith("注意事项")
                or re.match(r"^(材料|给定资料)\s*[一二三1]", ln)):
            start = i
            break
    lines = lines[start:]
    json.dump({"year": year, "level": lv, "kind": "shilun_questions", "lines": lines,
               "source": "aipta", "title": t},
              open(os.path.join(OUT, f"aipta_sl_{year}_{lv}_q.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    print(year, lv, len(lines), "行")
