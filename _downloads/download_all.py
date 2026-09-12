# -*- coding: utf-8 -*-
"""批量下载 sanlianbook 高教公考真题库的国考行测/申论真题页面及答案PDF"""
import re, os, time, urllib.request, ssl

BASE = "http://sanlianbook.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(OUT, exist_ok=True)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
                return r.read()
        except Exception as e:
            print(f"  retry {i+1} for {url}: {e}")
            time.sleep(2)
    return None

def parse_list(fname, cat_tag):
    html = open(fname, encoding="utf-8", errors="ignore").read()
    items = []
    # pattern: <a href="/index.php/shows/X/N.html" target="_blank">[国考行测]</a> ... title in following <a>
    for m in re.finditer(
        r'<a href="(/index\.php/shows/(\d+)/(\d+)\.html)" target="_blank">\[' + cat_tag +
        r'\]</a>\s*</td>.*?<a href="\1"[^>]*>([^<]+)</a>', html, flags=re.S):
        items.append((m.group(1), m.group(4).strip()))
    return items

xc = parse_list("list_xc_guokao.html", "国考行测")
sl = parse_list("list_sl_guokao.html", "国考申论")
print(f"行测条目: {len(xc)}, 申论条目: {len(sl)}")

# 过滤近15年: 考试年度2011-2026
def year_ok(title):
    m = re.search(r"(20\d{2})年（", title)
    if not m:
        return False
    return 2011 <= int(m.group(1)) <= 2026

todo = []
for url, title in xc + sl:
    if year_ok(title):
        todo.append((url, title))
print(f"近15年(2011-2026考试年度)条目: {len(todo)}")

manifest = []
for i, (url, title) in enumerate(todo):
    safe = re.sub(r'[\\/:*?"<>|\s（）()]+', "_", title)[:80]
    page_path = os.path.join(OUT, f"{safe}.html")
    if not os.path.exists(page_path):
        data = fetch(BASE + url)
        if data is None:
            print(f"[FAIL] {title}")
            continue
        open(page_path, "wb").write(data)
        time.sleep(0.8)
    html = open(page_path, encoding="utf-8", errors="ignore").read()
    # 找PDF附件
    pdfs = re.findall(r'href="(/public/uploads/files/[^"]+\.pdf)"', html)
    pdf_files = []
    for p in pdfs:
        pdf_name = p.split("/")[-1]
        pdf_path = os.path.join(OUT, pdf_name)
        if not os.path.exists(pdf_path):
            data = fetch(BASE + p)
            if data:
                open(pdf_path, "wb").write(data)
                time.sleep(0.8)
        if os.path.exists(pdf_path):
            pdf_files.append(pdf_name)
    manifest.append({"title": title, "url": BASE + url, "page": page_path, "pdfs": pdf_files})
    print(f"[{i+1}/{len(todo)}] {title} | pdfs={len(pdf_files)}")

import json
json.dump(manifest, open("manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE, manifest.json saved")
