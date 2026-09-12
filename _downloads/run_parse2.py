# -*- coding: utf-8 -*-
"""申论真题/答案 + hqwx 2026行测答案 解析 -> parsed/*.json"""
import re, os, json, sys, glob
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lib import pdf_clean
from build_parse import parse_blocks, strip_paper_header

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed")
os.makedirs(OUT, exist_ok=True)
import html as H


def html_lines(path):
    html = open(path, encoding="utf-8", errors="ignore").read()
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"</p>|<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    lines = []
    for ln in H.unescape(text).split("\n"):
        ln = ln.strip()
        if ln and ln not in ("/>", "-->", ">"):
            lines.append(ln)
    return lines


def cut_between(lines, start_pats, end_pats):
    s = 0
    for i, ln in enumerate(lines):
        if any(re.search(p, ln) for p in start_pats):
            s = i
            break
    e = len(lines)
    for i in range(s, len(lines)):
        if any(re.search(p, ln) for p in end_pats):
            e = i
            break
    return lines[s:e]


report = []
man = json.load(open("manifest.json", encoding="utf-8"))

# ============ sanlian 申论真题页 2011-2022 ============
for x in man:
    t = x["title"]
    if "申论真题" not in t or "参考答案" in t:
        continue
    m = re.search(r"(\d{4})年（", t)
    if not m:
        continue
    year = int(m.group(1))
    level = "副省级" if ("省级" in t and "市地" not in t) else ("行政执法类" if "行政执法" in t else "地市级")
    lines = html_lines(x["page"])
    body = cut_between(lines, [r"^注意事项"], [r"欢迎使用高教公考真题库", "相关推荐", "上一篇"])
    json.dump({"year": year, "level": level, "kind": "shilun_questions", "lines": body,
               "source": "sanlianbook", "title": t},
              open(os.path.join(OUT, f"sl_sl_{year}_{level}_q.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    report.append(f"sl_sl_{year}_{level}_q: {len(body)}行")

# ============ sanlian 申论参考答案页 2011-2021 ============
for x in man:
    t = x["title"]
    if "申论" not in t or "参考答案" not in t:
        continue
    m = re.search(r"(\d{4})年（", t)
    if not m:
        continue
    year = int(m.group(1))
    level = "副省级" if ("省级" in t and "市地" not in t) else "地市级"
    lines = html_lines(x["page"])
    body = cut_between(lines, [r"第一题", r"（一）", r"一、", r"【"], [r"欢迎使用高教公考真题库", "相关推荐", "上一篇"])
    json.dump({"year": year, "level": level, "kind": "shilun_answers", "lines": body,
               "source": "sanlianbook", "title": t},
              open(os.path.join(OUT, f"sl_sl_{year}_{level}_a.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    report.append(f"sl_sl_{year}_{level}_a: {len(body)}行")

# ============ gwy.com 2023 申论参考答案 ============
lines = html_lines("syd_2023sl.html")
i_ds = next(i for i, l in enumerate(lines) if "地市级" in l and "参考解析" in l)
i_end = next(i for i, l in enumerate(lines) if "时间分配" in l)
fs = lines[11:i_ds]
ds = lines[i_ds + 1:i_end]
json.dump({"year": 2023, "level": "副省级", "kind": "shilun_answers", "lines": fs, "source": "gwy.com"},
          open(os.path.join(OUT, "gwy_sl_2023_副省级_a.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"year": 2023, "level": "地市级", "kind": "shilun_answers", "lines": ds, "source": "gwy.com"},
          open(os.path.join(OUT, "gwy_sl_2023_地市级_a.json"), "w", encoding="utf-8"), ensure_ascii=False)
report.append(f"gwy_sl_2023_副省级_a: {len(fs)}行 | gwy_sl_2023_地市级_a: {len(ds)}行")

# ============ 华图 2023 申论真题页（备用） ============
for f, level in [("huatu/2023shenlun_fs.html", "副省级"), ("huatu/2023shenlun_ds.html", "地市级"),
                 ("huatu/2023shenlun_zf.html", "行政执法类")]:
    lines = html_lines(f)
    body = cut_between(lines, [r"^注意事项", r"给定资料", r"一、", r"（一）"], ["相关阅读", "以上是", "相关推荐"])
    json.dump({"year": 2023, "level": level, "kind": "shilun_questions", "lines": body,
               "source": "huatu", "title": f},
              open(os.path.join(OUT, f"ht_sl_2023_{level}_q.json"), "w", encoding="utf-8"), ensure_ascii=False)
    report.append(f"ht_sl_2023_{level}_q: {len(body)}行")

# ============ hqwx 申论参考答案 PDF 2024-2026 ============
for f in glob.glob("hqwx_pdf/*申论*.pdf") + glob.glob("hqwx_pdf/*《申论》*.pdf"):
    b = os.path.basename(f)
    m = re.search(r"(20\d{2})", b)
    if not m:
        continue
    year = int(m.group(1))
    if b.startswith("2019") or b.startswith("2020") or b.startswith("2021") or b.startswith("2022"):
        continue  # 这几年用sanlianbook
    level = "副省级" if ("副省" in b) else ("地市级" if ("地市" in b or "市地" in b) else "行政执法类")
    doc = fitz.open(f)
    lines = pdf_clean("".join(p.get_text() for p in doc))
    lines = [re.sub(r"^咨询热线.*$|^微信扫码.*$|^扫码.*$", "", l) for l in lines]
    lines = [l for l in lines if l.strip()]
    kind = "shilun_questions" if "参考答案" not in "".join(lines)[:2000] and year < 2024 else "shilun_answers"
    # 2025/2026 hqwx 申论文件名是"真题"，但内容含参考答案；2024两个文件明确含参考答案
    joined = "".join(lines)
    if "参考答案" in joined or "答案解析" in joined or "【解析】" in joined:
        kind = "shilun_answers"
    json.dump({"year": year, "level": level, "kind": kind, "lines": lines, "source": "hqwxPDF", "title": b},
              open(os.path.join(OUT, f"hqwx_sl_{year}_{level}_{ 'a' if kind=='shilun_answers' else 'q'}.json"),
                   "w", encoding="utf-8"), ensure_ascii=False)
    report.append(f"hqwx_sl_{year}_{level}: {len(lines)}行 {kind}")

# ============ hqwx 2026 行测答案（尽力解析，含部分题） ============
for f, level in [
    ("hqwx_pdf/2026年国考真题《行测》（市地级）答案及解析（网友回忆）_2ae7359ca27b234771d2753342525b8ed1d8e675.pdf", "地市级"),
    ("hqwx_pdf/2026-国考真题-《行测》-（副省）真题及答案（网友回忆）(1)_a3ce53508e279d5ba2bac7aaf8f61f67eefd3b0e.pdf", "副省级"),
    ("hqwx_pdf/2026-国考真题《行测》（行政执法）-真题及答案（网友回忆）_809ff87895cb06a602d28db5b67255f19ff25f6f.pdf", "行政执法类"),
]:
    doc = fitz.open(f)
    lines = pdf_clean("".join(p.get_text() for p in doc))
    # 去掉 hqwx 页眉页脚
    lines = [l for l in lines if not re.match(r"^(26国考行测|~\d+~|2026 ?年国考|注：来源于考生回忆)", l)]
    pp = parse_blocks(strip_paper_header(lines), start_num=1)
    answers = {}
    for blk in pp:
        if blk["ans"] and blk["stem"] and len(blk["stem"]) > 12:
            answers[blk["num"]] = {"ans": blk["ans"], "stem": blk["stem"][:80], "ana": blk["ana"][:1200]}
    json.dump({"year": 2026, "level": level, "kind": "xinge_answers", "answers": answers},
              open(os.path.join(OUT, f"hqwx_xc_2026_{level}_a.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    report.append(f"hqwx_xc_2026_{level}_a: {len(answers)}题有答案")

print("\n".join(report))
