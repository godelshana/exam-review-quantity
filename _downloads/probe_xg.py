# -*- coding: utf-8 -*-
"""探测星光公考PDF直链：尝试年份x卷种x科目组合"""
import urllib.request, ssl, time, os

BASE = "https://upload.xingguanggongkao.com/pdf/"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
os.makedirs("xg", exist_ok=True)

def probe(name):
    url = BASE + urllib.request.quote(name) + ".pdf"
    req = urllib.request.Request(url, headers=HDRS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            return r.status, r.headers.get("Content-Length")
    except Exception:
        return None, None

years = [2023, 2024, 2025, 2026]
juan = ["副省卷", "地市卷", "行政执法卷", "市地卷", "地市级", "副省级"]
kehu = ["行测", "申论"]
suffix = ["考生回忆版", "网友回忆版", "回忆版"]
found = []
for y in years:
    for k in kehu:
        for j in juan:
            for s in suffix:
                name = f"{y}年国家公务员考试《{k}》真题（{j}-{s}）"
                st, cl = probe(name)
                if st == 200:
                    print("FOUND:", name, cl)
                    found.append(name)
        # 无卷种后缀
        for s in suffix:
            name = f"{y}年国家公务员考试《{k}》真题（{s}）"
            st, cl = probe(name)
            if st == 200:
                print("FOUND:", name, cl)
                found.append(name)
time.sleep(1)
print("total found:", len(found))
