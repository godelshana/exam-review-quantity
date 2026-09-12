# -*- coding: utf-8 -*-
"""多来源交叉核对 v2：顺序无关的题目集合比对（验证真实性）"""
import re, os, json, sys, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

P = lambda *a: os.path.join(os.path.dirname(os.path.abspath(__file__)), *a)

def norm(s):
    return re.sub(r"[^\u4e00-\u9fa50-9A-Za-z]", "", s or "")

def load(name):
    f = os.path.join(P("parsed"), name)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None

def as_set(d):
    """{norm_stem_key: num}"""
    out = {}
    for mod, blocks in (d.get("sections") or {}).items():
        for b in blocks:
            k = norm(b.get("stem", ""))[:50]
            if len(k) >= 12:
                out[k] = b["num"]
    return out

def set_match(A, B):
    """A中每题在B中找最佳匹配（前后缀/相似度）"""
    keysB = list(B.keys())
    matched = 0
    unmatched_A = []
    for ka, na in A.items():
        hit = None
        if ka in B:
            hit = na
        else:
            for kb in keysB:
                # 前30字符相同 或 相似度>0.8
                if ka[:30] == kb[:30] or difflib.SequenceMatcher(None, ka, kb).ratio() > 0.8:
                    hit = na
                    break
        if hit:
            matched += 1
        else:
            unmatched_A.append((na, ka[:36]))
    return matched, unmatched_A

pairs = []
for y in range(2015, 2023):
    for lv in ["副省级", "地市级"]:
        pairs.append((y, lv, f"sl_xc_{y}_{lv}.json", f"xg_xc_{y}_{lv}.json", f"aipta_xc_{y}_{lv}.json"))
for y in range(2023, 2027):
    for lv in ["副省级", "地市级", "行政执法类"]:
        pairs.append((y, lv, f"xg_xc_{y}_{lv}.json", f"aipta_xc_{y}_{lv}.json", None))

results = []
for y, lv, f1, f2, f3 in pairs:
    sources = [(f1, load(f1)), (f2, load(f2)), (f3, load(f3))]
    sources = [(n, as_set(d)) for n, d in sources if d]
    if len(sources) < 2:
        continue
    line = {"year": y, "level": lv}
    ok_all = True
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            (n1, A), (n2, Bs) = sources[i], sources[j]
            m, unm = set_match(A, Bs)
            rate = m / max(len(A), 1) * 100
            line[f"{n1.split('_')[0]}vs{n2.split('_')[0]}"] = f"{m}/{len(A)}={rate:.0f}%"
            if rate < 90:
                ok_all = False
                line.setdefault("issues", []).append({"pair": f"{n1}vs{n2}", "unmatched_sample": [u[0] for u in unm[:8]], "stems": [u[1] for u in unm[:4]]})
    results.append(line)
    print(("OK " if ok_all else "CHK"), y, lv, {k: v for k, v in line.items() if k not in ("year", "level", "issues")})

json.dump(results, open(P("verify_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
