# -*- coding: utf-8 -*-
"""爬取环球网校真题新闻页 -> 资料页 -> OSS PDF 直链并下载"""
import re, os, time, html as H, urllib.request, urllib.parse, ssl

BASE = "https://www.hqwx.com"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
os.makedirs("hqwx_pdf", exist_ok=True)

def fetch(url, retries=2, binary=False):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", errors="ignore")
        except Exception as e:
            time.sleep(1.5)
    return None

def decode(raw):
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")

# 1) 真题汇总页所有新闻链接
zt = decode(open("hqwx_zt.html", "rb").read())
news = sorted(set(re.findall(r'href="(/gjgwy-kaoshi/news/\d+\.html)"', zt)))
print("news pages:", len(news))

ziliao_links = set()
for i, n in enumerate(news):
    html = fetch(BASE + n)
    if not html:
        continue
    for z in re.findall(r'href="(/gjgwy-kaoshi/ziliaolm/\d+\.html)"', html):
        ziliao_links.add(z)
    time.sleep(0.4)
print("ziliao pages:", len(ziliao_links))

# 2) 每个资料页 -> 标题匹配的主PDF
SIDEBAR_KW = ["高频考点速记", "申论时政热点", "申论规范表达", "怎么备考之学习计划"]
results = []
for i, z in enumerate(sorted(ziliao_links)):
    html = fetch(BASE + z)
    if not html:
        continue
    t = re.search(r"<title>([^<]*)</title>", html)
    title = H.unescape(t.group(1)) if t else ""
    if not any(k in title for k in ["真题", "答案", "试题", "解析"]):
        continue
    pdfs = [H.unescape(m.group(1)) for m in re.finditer(r'["\']?(https?://[^"\' >]+\.pdf[^"\' >]*)', html, flags=re.I)]
    main = None
    # 用标题关键词匹配文件名
    tkey = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", title.split("_")[0])[:12]
    for p in pdfs:
        pname = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", urllib.parse.unquote(p.split("/")[-1]))
        if tkey and tkey[:8] in pname:
            main = p; break
    if not main:
        cands = [p for p in pdfs if not any(k in p for k in SIDEBAR_KW)]
        if len(cands) == 1:
            main = cands[0]
    results.append((title, main))
    print(f"[{i+1}/{len(ziliao_links)}]", title[:50], "->", "OK" if main else "-")
    time.sleep(0.4)

# 3) 下载
import json
for title, pdf in results:
    if not pdf:
        continue
    name = urllib.parse.unquote(pdf.split("/")[-1]).split("?")[0]
    name = re.sub(r'[\\/:*?"<>|]', "_", name)[:100]
    if not name.endswith(".pdf"):
        name += ".pdf"
    out = os.path.join("hqwx_pdf", name)
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        print("skip", name); continue
    data = fetch(pdf, binary=True)
    if data and len(data) > 10000:
        open(out, "wb").write(data)
        print("DL", name, len(data))
        time.sleep(0.6)
    else:
        print("FAIL", name)
json.dump([(t, p) for t, p in results], open("hqwx_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
