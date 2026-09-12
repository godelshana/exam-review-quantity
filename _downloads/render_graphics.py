# -*- coding: utf-8 -*-
"""渲染 v2：图形题裁剪（跨页、止于【答案】）+ aipta内嵌图 + 数量关系缺公式题"""
import re, os, json, sys, glob, urllib.request, ssl
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import build_xingce_registry

BASE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.normpath(os.path.join(BASE, "..", "真题库", "图片"))
os.makedirs(IMGDIR, exist_ok=True)
for f in glob.glob(os.path.join(IMGDIR, "*.png")):
    os.remove(f)

man = json.load(open(os.path.join(BASE, "manifest.json"), encoding="utf-8"))
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def sl_pdf_for(year, level):
    singles = {}
    for x in man:
        t = x["title"]
        if "行测" not in t:
            continue
        m = re.search(r"(\d{4})年（", t)
        if not m or not x["pdfs"]:
            continue
        year2 = int(m.group(1))
        if "市地级" in t or "地市级" in t:
            lv = "地市级"
        elif "省级" in t:
            lv = "副省级"
        else:
            lv = "合卷" if year2 <= 2014 else ("副省级" if year2 != 2017 else "地市级")
        if year2 == 2022 and lv == "地市级":
            continue
        best = max((os.path.join(BASE, "raw", p) for p in x["pdfs"]), key=lambda p: os.path.getsize(p))
        singles[(year2, lv)] = best
    if year in (2015, 2016, 2017):
        for (y2, _lv), f in singles.items():
            if y2 == year:
                return f
    return singles.get((year, level))

def xg_pdf_for(year, level):
    tag = {"副省级": "副省", "地市级": ["市地", "地市"], "行政执法类": "行政执法"}[level]
    for f in glob.glob(os.path.join(BASE, "xg", f"{year}年*.pdf")):
        b = os.path.basename(f)
        if "行测" in b:
            tags = tag if isinstance(tag, list) else [tag]
            if any((f"（{t}卷" in b) or (f"（{t}-" in b) for t in tags):
                return f
    return None

GRAPH_PAT = re.compile(r"从所给的四个选项中|把下面的六个图形分为两类|左边给定的是纸盒|给定的是.*立体图形|多面体组合|折叠而成|剖面图|截面")

def crop_pieces(doc, start, end):
    sp, sy = start
    ep, ey = end
    pieces = []
    for p in range(sp, ep + 1):
        ph = doc[p].rect.height
        top = sy if p == sp else 38
        bottom = ey if p == ep else ph - 42
        if bottom - top > 18:
            pieces.append((p, max(28, top), min(ph - 28, bottom)))
    return pieces

mapping = {}
missing_formula = []
registry = build_xingce_registry()

for (y, lv), pap in sorted(registry.items()):
    if not pap["sections"]:
        continue
    blocks = []
    for mod in ["判断推理", "数量关系"]:
        for b in pap["sections"].get(mod, []):
            if mod == "判断推理" and GRAPH_PAT.search(b.get("stem", "")):
                blocks.append((mod, b))
            elif mod == "数量关系" and re.search(
                    r"(上涨|下降|提高|降低|增长|减少|增加|回落|扩大|缩小)了[，。]", b.get("stem", "")):
                blocks.append((mod, b))
                missing_formula.append((y, lv, b["num"], b["stem"][:40]))
            elif len(b.get("opts") or {}) > 0 and any(not b["opts"].get(k) for k in "ABCD"):
                blocks.append((mod, b))  # 选项含图片/分数
    if not blocks:
        continue

    if pap["qsrc"] == "aipta":
        am = json.load(open(os.path.join(BASE, "aipta_manifest.json"), encoding="utf-8"))
        src = None
        for a_id, info in am.items():
            t = info["title"]
            if not t.startswith(f"{y}国考行测"):
                continue
            if lv == "副省级" and "副省" in t: src = info["file"]; break
            if lv == "地市级" and "地市" in t: src = info["file"]; break
            if lv == "行政执法类" and "行政执法" in t: src = info["file"]; break
        if not src:
            print("无aipta来源:", y, lv); continue
        html = open(src, encoding="utf-8", errors="ignore").read()
        tokens = re.findall(r'<img[^>]*?src="([^"]+)"|>([^<]*)', html)
        cur_num = 0
        per_q = {}
        for img, text in tokens:
            if text:
                m = re.match(r"^\s*(\d{1,3})[．.、]", text)
                if m and m.group(1).isdigit():
                    n = int(m.group(1))
                    if cur_num <= n <= cur_num + 3 or cur_num == 0:
                        cur_num = n
            elif img and cur_num and "qingyun" not in img:
                per_q.setdefault(cur_num, []).append(img)
        tag_lv = {"副省级": "副省", "地市级": "地市", "行政执法类": "执法", "合卷": "合卷"}[lv]
        for mod, b in blocks:
            num = b["num"]
            for k, u in enumerate(per_q.get(num, [])[:12]):
                try:
                    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                    data = urllib.request.urlopen(req, timeout=30, context=CTX).read()
                    name = f"{y}_{tag_lv}_{mod}_{num:03d}{'_' + str(k + 2) if k else ''}.png"
                    open(os.path.join(IMGDIR, name), "wb").write(data)
                    mapping[f"{y}|{lv}|{mod}|{num}|{k}"] = name
                except Exception as e:
                    print("  下载失败:", y, lv, num, str(e)[:50])
        continue

    pdf = sl_pdf_for(y, lv) if pap["qsrc"] in ("sl", "slh") else xg_pdf_for(y, lv)
    if (not pdf or not os.path.exists(pdf)) and pap["qsrc"] in ("sl", "slh"):
        pdf = xg_pdf_for(y, lv)  # 2022地市等无高教PDF时回退星光版
    if not pdf or not os.path.exists(pdf):
        print("无PDF:", y, lv, pap["qsrc"])
        continue
    doc = fitz.open(pdf)
    has_ans = "【答案】" in "".join(doc[p].get_text() for p in range(min(3, len(doc))))
    cursor = (0, 0.0)
    located = []
    for mod, b in blocks:
        num = b["num"]
        found = None
        for pno in range(cursor[0], len(doc)):
            page = doc[pno]
            rects = []
            for pat in (f"{num}.", f"{num}．", f"{num}、"):
                rects += [r for r in page.search_for(pat) if r.x0 < 100 and r.y0 > 40
                          and (pno > cursor[0] or r.y0 >= cursor[1] - 2)]
            if rects:
                found = (pno, min(rects, key=lambda r: r.y0).y0)
                break
        if found is None:
            for pno in range(len(doc)):
                rects = []
                for pat in (f"{num}.", f"{num}．", f"{num}、"):
                    rects += [r for r in doc[pno].search_for(pat) if r.x0 < 100 and r.y0 > 40]
                if rects:
                    found = (pno, min(rects, key=lambda r: r.y0).y0)
                    break
        if found:
            located.append((mod, num, found))
            cursor = found
        else:
            print(f"  未定位: {y}{lv} {mod} Q{num}")

    for i, (mod, num, start) in enumerate(located):
        sp, sy = start
        end = None
        if has_ans:
            for pno in range(sp, min(sp + 4, len(doc))):
                marks = [r for r in doc[pno].search_for("【答案】")
                         if (pno > sp or r.y0 > sy + 5)]
                if marks:
                    r = min(marks, key=lambda r: r.y0)
                    end = (pno, r.y0)
                    break
        if end is None or end[0] < sp or (end[0] == sp and end[1] <= sy + 10):
            end = located[i + 1][2] if i + 1 < len(located) else (sp, doc[sp].rect.height - 42)
        tag_lv = {"副省级": "副省", "地市级": "地市", "行政执法类": "执法", "合卷": "合卷"}[lv]
        for k, (pno, top, bottom) in enumerate(crop_pieces(doc, start, end)):
            clip = fitz.Rect(30, top, doc[pno].rect.width - 30, bottom)
            pix = doc[pno].get_pixmap(clip=clip, dpi=120)
            name = f"{y}_{tag_lv}_{mod}_{num:03d}{'_' + str(k + 2) if k else ''}.png"
            pix.save(os.path.join(IMGDIR, name))
            mapping[f"{y}|{lv}|{mod}|{num}|{k}"] = name

json.dump(mapping, open(os.path.join(BASE, "img_map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"生成图片文件 {len(glob.glob(os.path.join(IMGDIR, '*.png')))} 张，映射 {len(mapping)} 条")
print("数量关系疑似缺公式:", missing_formula)
