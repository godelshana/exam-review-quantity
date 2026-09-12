# -*- coding: utf-8 -*-
"""下载 66 卷数量关系全部图片（题图+公式渲染图），断点续传。"""
import json, glob, re, os, time, sys

BASE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = r"E:\codeBase\examReview\真题库\图片\省考"
STATE = os.path.join(BASE, "img_dl_state.json")

def collect():
    urls = {}
    for f in glob.glob(os.path.join(BASE, "fb", "paper_[GTSH]*.json")) + \
             glob.glob(os.path.join(BASE, "fb", "paper_AH*.json")) + \
             glob.glob(os.path.join(BASE, "fb", "paper_SC*.json")) + \
             glob.glob(os.path.join(BASE, "fb", "paper_GD*.json")) + \
             glob.glob(os.path.join(BASE, "fb", "paper_HB*.json")) + \
             glob.glob(os.path.join(BASE, "fb", "paper_HEN*.json")):
        try: d = json.load(open(f, encoding="utf-8"))
        except: continue
        chs = d.get("chapters") or []
        start = 1; rng = None
        for c in chs:
            n = c.get("count") or 0
            if "数量关系" in c["name"] and n: rng = (start, start+n-1); break
            start += n
        if not rng: continue
        for q in d.get("questions") or []:
            if "num" not in q or not (rng[0] <= q["num"] <= rng[1]): continue
            urls_in_q = list(q.get("imgs") or [])
            sh = q.get("stemHtml") or ""
            urls_in_q += re.findall(r'src="([^"]+)"', sh)
            for oh in q.get("optionsHtml") or []:
                urls_in_q += re.findall(r'src="([^"]+)"', oh)
            for u in urls_in_q:
                u = u.replace("&amp;", "&")
                if u.startswith("//"): u = "https:" + u
                name = hashlib.md5(u.encode()).hexdigest()[:12] + ".png"
                urls[name] = u
    return urls

def main():
    import urllib.request, ssl, hashlib
    os.makedirs(IMGDIR, exist_ok=True)
    done = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    urls = collect()
    todo = [x for x in urls.items() if x[0] not in done]
    print(f"总图 {len(urls)}，已下 {len(done)}，待下 {len(todo)}", flush=True)
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    ok = fail = 0
    for i, (name, u) in enumerate(todo, 1):
        path = os.path.join(IMGDIR, name)
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0", "Referer": "https://spa.fenbi.com/"})
            with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
                data = r.read()
            with open(path, "wb") as fh:
                fh.write(data)
            done[name] = 1; ok += 1
        except Exception as e:
            done[name] = "FAIL: " + str(e)[:40]; fail += 1
        if i % 50 == 0 or i == len(todo):
            json.dump(done, open(STATE, "w", encoding="utf-8"))
            print(f"[{i}/{len(todo)}] ok={ok} fail={fail}", flush=True)
        time.sleep(0.25)
    fails = [k for k, v in done.items() if v and str(v).startswith("FAIL")]
    print(f"完成。成功 {ok}，失败 {fail}（可重跑本脚本续传）", flush=True)
    if fails: print("失败清单前10:", fails[:10], flush=True)

if __name__ == "__main__":
    main()
