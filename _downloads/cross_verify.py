# -*- coding: utf-8 -*-
"""多来源交叉核对：同一套卷在不同来源的题目一致性 → 真实性报告"""
import re, os, json, sys, glob, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lib import MODULES

P = lambda *a: os.path.join(os.path.dirname(os.path.abspath(__file__)), *a)

def norm(s):
    return re.sub(r"[^\u4e00-\u9fa50-9A-Za-z]", "", s or "")

def load(name):
    f = os.path.join(P("parsed"), name)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None

def as_paper(d):
    """{num: stem}"""
    out = {}
    if not d or not d.get("sections"):
        return out
    for mod, blocks in d["sections"].items():
        for b in blocks:
            out[b["num"]] = norm(b.get("stem", ""))[:60]
    return out

pairs_to_check = []
# 2019-2022: sl vs xg
for y in range(2019, 2023):
    for lv in ["副省级", "地市级"]:
        pairs_to_check.append((y, lv, f"sl_xc_{y}_{lv}.json", f"xg_xc_{y}_{lv}.json"))
for y in range(2022, 2023):
    pairs_to_check.append((y, "行政执法类", None, f"xg_xc_{y}_行政执法类.json"))
# 2015-2017: sl vs aipta
for y in (2015, 2016, 2017):
    for lv in ["副省级", "地市级"]:
        pairs_to_check.append((y, lv, f"sl_xc_{y}_{lv}.json", f"aipta_xc_{y}_{lv}.json"))
# 2023-2026: xg vs aipta
for y in range(2023, 2027):
    for lv in ["副省级", "地市级", "行政执法类"]:
        pairs_to_check.append((y, lv, f"xg_xc_{y}_{lv}.json", f"aipta_xc_{y}_{lv}.json"))

report = []
all_issues = []
for y, lv, fa, fb in pairs_to_check:
    da = load(fa) if fa else None
    db = load(fb) if fb else None
    if not da or not db:
        continue
    A, B = as_paper(da), as_paper(db)
    common = sorted(set(A) & set(B))
    same = sum(1 for n in common if A[n] and B[n] and (A[n] == B[n] or A[n][:30] == B[n][:30] or difflib.SequenceMatcher(None, A[n], B[n]).ratio() > 0.85))
    diff_list = [n for n in common if not (A[n] == B[n] or A[n][:30] == B[n][:30] or difflib.SequenceMatcher(None, A[n], B[n]).ratio() > 0.85)]
    rate = same / len(common) * 100 if common else 0
    report.append({
        "year": y, "level": lv,
        "srcA": os.path.basename(fa or "-").replace(".json", ""), "srcB": os.path.basename(fb).replace(".json", ""),
        "nA": len(A), "nB": len(B), "common": len(common),
        "same": same, "rate": round(rate, 1),
        "diff_nums": diff_list[:20],
    })
    for n in diff_list[:6]:
        all_issues.append((y, lv, n, A.get(n, "")[:40], B.get(n, "")[:40]))

json.dump(report, open(P("verify_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in report:
    flag = "OK " if r["rate"] >= 95 and r["common"] >= r["nA"] * 0.9 else "CHK"
    print(f"[{flag}] {r['year']} {r['level']}: A={r['nA']}题 B={r['nB']}题 共同{r['common']} 一致{r['same']} ({r['rate']}%) 不一致:{r['diff_nums'][:8]}")
print("\n--- 题干不一致样本 ---")
for y, lv, n, sa, sb in all_issues[:12]:
    print(f"{y}{lv} Q{n}:\n  A: {sa}\n  B: {sb}")
