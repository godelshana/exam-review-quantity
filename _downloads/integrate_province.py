# -*- coding: utf-8 -*-
"""省考/联考卷整理 v3：数量关系抽取、去重、公式图/题图本地化内联。"""
import json, glob, os, re, hashlib, time

BASE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.join(BASE, "fb")
OUTDIR = os.path.normpath(os.path.join(BASE, "..", "真题库", "按模块", "06_省考联考"))
IMGDIR = os.path.normpath(os.path.join(BASE, "..", "真题库", "图片", "省考"))
PROV = {"GD": "广东", "HB": "湖北", "HEN": "河南", "AH": "安徽", "SC": "四川"}
LETTER = "ABCD"


def load_papers():
    papers, seen_f = [], set()
    for pat in ["paper_[GTSH]*.json", "paper_AH*.json", "paper_SC*.json",
                "paper_GD*.json", "paper_HB*.json", "paper_HEN*.json"]:
        for f in sorted(glob.glob(os.path.join(FB, pat))):
            if f in seen_f:
                continue
            seen_f.add(f)
            base = os.path.basename(f)[:-5]
            m = re.match(r"paper_([A-Z]{2,3})_(.+)", base)
            if not m:
                continue
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception as e:
                print("skip", base, e)
                continue
            papers.append({"code": m.group(1), "variant": m.group(2),
                           "name": d.get("name", ""), "data": d})
    return papers


def shuliang_range(chapters):
    start = 1
    for c in chapters:
        n = c.get("count") or 0
        if "数量关系" in c["name"] and n:
            return start, start + n - 1
        start += n
    return None


def norm_url(u):
    u = u.replace("&amp;", "&")
    if u.startswith("//"):
        u = "https:" + u
    return u


def img_name(u):
    return hashlib.md5(u.encode()).hexdigest()[:12] + ".png"


def localize_html(html):
    """html 内 img src 替换为本地相对路径；清理 angular 属性。"""
    if not html:
        return ""

    def rep(m):
        src = norm_url(m.group(1))
        name = img_name(src)
        return (f'<img src="../../图片/省考/{name}" '
                f'style="vertical-align:middle;max-width:280px">')

    h = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', rep, html)
    h = re.sub(r'\s_ngcontent[^=>]*(="[^"]*")?', "", h)
    h = re.sub(r"^<div[^>]*><p[^>]*>", "", h)
    h = re.sub(r"</p></div>$", "", h)
    return h.strip()


def is_shulitui(q):
    s = re.sub(r"（\s*）", "", q.get("stem", ""))
    s = re.sub(r"[\d.,，、\s]", "", s)
    return len(s) == 0 and bool(q.get("stem"))


def by_paper_set(items):
    return {q["_paper"] for q in items}


def main():
    os.makedirs(IMGDIR, exist_ok=True)
    papers = load_papers()
    seen_ids, items, stats = {}, [], []
    all_urls = {}
    for p in sorted(papers, key=lambda x: (x["code"], x["variant"])):
        d = p["data"]
        chs = d.get("chapters") or []
        rng = shuliang_range(chs)
        if not rng:
            print(f"[warn] {p['code']}_{p['variant']} 无法定位数量关系（章节数据缺失）")
            continue
        lo, hi = rng
        qs = [q for q in d["questions"] if q.get("num") and lo <= q["num"] <= hi]
        keep, dup = [], 0
        for q in qs:
            qid = q.get("id")
            if qid and qid in seen_ids:
                dup += 1
                continue
            if qid:
                seen_ids[qid] = 1
            keep.append(q)
        stats.append({"paper": f"{p['code']}_{p['variant']}", "name": p["name"],
                      "shuliang": len(qs), "kept": len(keep), "dup": dup})
        for q in keep:
            q["_paper"] = f"{p['code']}_{p['variant']}"
            items.append(q)
            urls = list(q.get("imgs") or [])
            for h in [q.get("stemHtml") or ""] + list(q.get("optionsHtml") or []):
                urls += re.findall(r'src="([^"]+)"', h)
            for u in urls:
                u = norm_url(u)
                all_urls[img_name(u)] = u

    print(f"数量关系: {len(items)} 题（去重后），{len(by_paper_set(items))} 套卷；需图 {len(all_urls)} 张")

    # 下载缺失图
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    miss = [(n, u) for n, u in all_urls.items()
            if not (os.path.exists(os.path.join(IMGDIR, n))
                    and os.path.getsize(os.path.join(IMGDIR, n)) > 100)]
    print(f"需新下载: {len(miss)} 张", flush=True)
    fail = []
    for i, (name, u) in enumerate(miss, 1):
        try:
            req = urllib.request.Request(u, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0",
                "Referer": "https://spa.fenbi.com/"})
            with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
                data = r.read()
            with open(os.path.join(IMGDIR, name), "wb") as fh:
                fh.write(data)
        except Exception as e:
            fail.append((name, u[:80], str(e)[:40]))
        if i % 100 == 0:
            print(f"  下载 {i}/{len(miss)}", flush=True)
        time.sleep(0.2)
    if fail:
        print("下载失败:", len(fail))
        for x in fail[:8]:
            print("  ", x[0], x[2])

    # 生成汇编
    by_paper = {}
    for q in items:
        by_paper.setdefault(q["_paper"], []).append(q)
    md = ["# 省考/联考 · 数量关系真题汇编（粉笔·网友回忆版）", "",
          f"> 收录 {len(by_paper)} 套卷、去重后 {len(items)} 题；跨省联考同题只保留首次出现。",
          "> 数学公式为粉笔渲染图，已本地化内联；图片在 `真题库/图片/省考/`。", ""]
    ans = ["# 省考/联考 · 数量关系答案速查", ""]
    for paper in sorted(by_paper.keys()):
        qs = by_paper[paper]
        code, variant = paper.split("_", 1)
        title = next((s["name"] for s in stats if s["paper"] == paper), paper)
        md.append(f"## {PROV.get(code, code)} · {variant}（{len(qs)}题）")
        md.append("")
        md.append(f"> {title}")
        md.append("")
        ans.append(f"## {PROV.get(code, code)} · {variant}")
        ans.append("")
        ans.append("| 题号 | 答案 |")
        ans.append("|---|---|")
        for q in qs:
            numline = f"{q['num']}" + ("（数字推理）" if is_shulitui(q) else "")
            stem = localize_html(q.get("stemHtml") or "")
            if not stem:
                stem = q.get("stem") or ""
            md.append(f"**{numline}.** {stem}")
            md.append("")
            opts = q.get("optionsHtml") or []
            for i in range(min(4, len(opts))):
                oh = localize_html(opts[i])
                oh = re.sub(r"^[A-D][.、．\s]*(\s)?", "", oh) if oh else oh
                if not oh and i < len(q.get("options") or []):
                    alt = re.sub(r"^[A-D][.、．\s]*", "", q["options"][i])
                    oh = alt
                md.append(f"- **{LETTER[i]}.** {oh}")
            md.append("")
            ans.append(f"| {numline} | {LETTER[int(q['choice'])] if q.get('choice') not in (None, '') else '?'} |")
        ans.append("")
        md.append("---")
        md.append("")

    with open(os.path.join(OUTDIR, "数量关系题目汇编.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(OUTDIR, "数量关系答案速查.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(ans))
    json.dump(stats, open(os.path.join(BASE, "province_stats.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("汇编与答案速查已重建:", OUTDIR)


if __name__ == "__main__":
    main()
