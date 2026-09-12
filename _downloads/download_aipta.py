# -*- coding: utf-8 -*-
"""下载 aipta 全部国考行测/申论文章页（免费题目部分）"""
import re, os, time, urllib.request, ssl

BASE = "https://www.aipta.com"
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
os.makedirs("aipta", exist_ok=True)

def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
                return r.read()
        except Exception:
            time.sleep(2)
    return None

def decode(raw):
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")

items = {}
for f, cat in [("aipta_xc.html", "行测"), ("aipta_sl.html", "申论")]:
    raw = open(f, "rb").read()
    html = decode(raw)
    for m in re.finditer(r'href="(https://www\.aipta\.com/article/(\d+)\.html)"[^>]*>\s*([^<]{4,80})', html):
        t = m.group(3).strip()
        if "国考" in t and ("行测" in t or "申论" in t):
            items[m.group(2)] = (m.group(1), t)
print("articles:", len(items))

import json
meta = {}
for i, (aid, (url, title)) in enumerate(sorted(items.items(), key=lambda kv: -int(kv[0]))):
    out = os.path.join("aipta", aid + ".html")
    if not os.path.exists(out) or os.path.getsize(out) < 5000:
        data = fetch(url)
        if not data:
            print("FAIL", aid, title); continue
        open(out, "wb").write(data)
        time.sleep(0.6)
    meta[aid] = {"title": title, "url": url, "file": out}
    print(f"[{i+1}/{len(items)}]", aid, title[:50])

json.dump(meta, open("aipta_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
