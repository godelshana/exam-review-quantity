# -*- coding: utf-8 -*-
"""全量解析所有来源 -> parsed/*.json，并输出质量报告"""
import re, os, json, sys, glob
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_parse import read_pdf_lines, strip_paper_header, parse_paper, parse_blocks
from parse_lib import pdf_clean

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed")
os.makedirs(OUT, exist_ok=True)
import html as H


def html_lines(path, container="warp-content"):
    """从 HTML 提取正文行（sanlianbook 整页 / aipta warp-content）"""
    html = open(path, encoding="utf-8", errors="ignore").read()
    if container:
        i = html.find(container)
        if i >= 0:
            html = html[i:]
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = H.unescape(text)
    lines = []
    for ln in text.split("\n"):
        ln = ln.strip()
        if ln:
            lines.append(ln)
    return lines


def strip_sl_header(lines):
    """sanlianbook HTML 页头去除：到'第一部分'或'注意事项'"""
    for i, ln in enumerate(lines):
        if re.match(r"^第[一二三四五]部分", ln) or ln.startswith("注意事项"):
            return lines[i:]
    return lines


report = []


def save(name, data):
    json.dump(data, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False)
    n = data.get("total") or sum(len(v) for v in data.get("sections", {}).values())
    iss = "; ".join(data.get("issues", [])[:4])
    report.append(f"{name}: {n}题 {iss}")


# ============ 1) sanlianbook 行测解析PDF (2011-2022省级) ============
man = json.load(open("manifest.json", encoding="utf-8"))
import fitz
for x in man:
    t = x["title"]
    if "行测" not in t:
        continue
    m = re.search(r"(\d{4})年（", t)
    if not m:
        continue
    year = int(m.group(1))
    level = None
    if "省级" in t or ("（市地级" not in t and "地市级" not in t and "行政执法" not in t and year >= 2015):
        level = "副省级" if year >= 2015 else "合卷"
    elif "市地级" in t or "地市级" in t:
        level = "地市级"
    if level is None:
        level = "合卷"
    if not x["pdfs"]:
        continue
    # 选含答案的PDF
    best = None
    for p in x["pdfs"]:
        fp = os.path.join("raw", p)
        lines = read_pdf_lines(fp)
        if any("【答案】" in ln for ln in lines):
            best = lines
            break
        best = best or lines
    pp = parse_paper(strip_paper_header(best))
    # 2015-2017按内容判定卷种：数量关系15题/总135=副省；10题/130=地市
    if year in (2015, 2016, 2017):
        ns = len(pp["sections"].get("数量关系", []))
        tt = pp["total"]
        level = "副省级" if (tt >= 135 or ns >= 15) else "地市级"
    pp["meta"] = {"year": year, "level": level, "source": "sanlianbook解析PDF", "src_file": p}
    # 2022市地错误指向省级PDF：丢弃
    if year == 2022 and level == "地市级":
        continue
    save(f"sl_xc_{year}_{level}.json", pp)

# ============ 2) sanlianbook 2022市地 HTML 题目 ============
f2022 = [x for x in man if "2022年" in x["title"] and "行测" in x["title"] and "市地" in x["title"]]
if f2022:
    lines = strip_sl_header(html_lines(f2022[0]["page"]))
    # 去尾部网站导航
    for i, ln in enumerate(lines):
        if "相关推荐" in ln or "相关文章" in ln:
            lines = lines[:i]
            break
    pp = parse_paper(lines)
    pp["meta"] = {"year": 2022, "level": "地市级", "source": "sanlianbook页面", "src_file": f2022[0]["page"]}
    save("sl_xc_2022_地市级.json", pp)

# ============ 3) xingguang PDF (2019-2026) ============
for f in sorted(glob.glob("xg/*.pdf")):
    base = os.path.basename(f).replace(".pdf", "")
    m = re.search(r"(\d{4})年国家公务员(?:录用)?考试《行测》真题（(副省|市地|地市|行政执法)卷?", base)
    if not m:
        print("skip xg:", base[:40]); continue
    year = int(m.group(1))
    j = m.group(2)
    level = {"副省": "副省级", "市地": "地市级", "地市": "地市级", "行政执法": "行政执法类"}[j]
    lines = strip_paper_header(pdf_clean("".join(p.get_text() for p in fitz.open(f))))
    pp = parse_paper(lines)
    pp["meta"] = {"year": year, "level": level, "source": "xingguangPDF", "src_file": f}
    save(f"xg_xc_{year}_{level}.json", pp)

# ============ 4) aipta 文章 (备用/补漏) ============
am = json.load(open("aipta_manifest.json", encoding="utf-8"))
for aid, info in am.items():
    t = info["title"]
    my = re.search(r"(\d{4})国考(行测|申论)", t)
    if not my or my.group(2) != "行测":
        continue
    year = int(my.group(1))
    level = "合卷"
    if "副省" in t:
        level = "副省级"
    elif "地市" in t:
        level = "地市级"
    elif "行政执法" in t:
        level = "行政执法类"
    lines = html_lines(info["file"])
    # 只截尾部（导航/推荐区），头部由 find_sections 跳过
    for i, ln in enumerate(lines):
        if "猜你喜欢" in ln or "注：篇幅有限" in ln or "下载真题" in ln or "相关推荐" in ln:
            lines = lines[:i]
            break
    pp = parse_paper(lines)
    pp["meta"] = {"year": year, "level": level, "source": "aipta", "src_file": info["file"]}
    save(f"aipta_xc_{year}_{level}.json", pp)

print("\n".join(report))
