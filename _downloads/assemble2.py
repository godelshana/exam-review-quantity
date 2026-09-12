# -*- coding: utf-8 -*-
"""总装第二部分：申论 + 按模块汇编 + 原始PDF整理"""
import re, os, json, sys, glob, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(BASE, *a)
ROOT = os.path.normpath(os.path.join(BASE, "..", "真题库"))
sys.path.insert(0, BASE)
from parse_lib import MODULES
from assemble import load, write, norm_stem, answer_table, fmt_question, SRC_NAME, MOD_DIR, MOD_ORDER, MOD_TITLE, build_xingce_registry

YEARS = range(2011, 2027)


# ============================================================ 申论
def sl_questions_for(y, lv):
    for name in [f"sl_sl_{y}_{lv}_q.json", f"ht_sl_{y}_{lv}_q.json", f"aipta_sl_{y}_{lv}_q.json"]:
        d = load(name)
        if d and d.get("lines"):
            return d
    return None


def sl_answers_for(y, lv):
    for name in [f"sl_sl_{y}_{lv}_a.json", f"gwy_sl_{y}_{lv}_a.json", f"hqwx_sl_{y}_{lv}_a.json"]:
        d = load(name)
        if d and d.get("lines"):
            return d
    return None


def build_shenlun():
    YDIR = os.path.join(ROOT, "按年份")
    made = []
    for y in YEARS:
        levels = ["副省级", "地市级"] if y <= 2021 else ["副省级", "地市级", "行政执法类"]
        for lv in levels:
            q = sl_questions_for(y, lv)
            a = sl_answers_for(y, lv)
            if not q and not a:
                continue
            ydir = os.path.join(YDIR, f"{y}年国考")
            if q:
                L = [f"# {y}年国考《申论》真题（{lv}）", "",
                     f"> 题目来源：{q['source']}（考生回忆版）", ""]
                L.extend(q["lines"])
                write(os.path.join(ydir, f"申论_{lv}_题目.md"), "\n".join(L) + "\n")
            if a:
                A = [f"# {y}年国考《申论》参考答案（{lv}）", "",
                     f"> 答案来源：{a['source']}｜申论为开放性主观题，参考答案仅供对照学习", ""]
                A.extend(a["lines"])
                write(os.path.join(ydir, f"申论_{lv}_参考答案.md"), "\n".join(A) + "\n")
            made.append((y, lv, bool(q), bool(a)))
    for m in made:
        print("申论", m)


# ============================================================ 按模块
def build_modules():
    papers = build_xingce_registry()
    MDIR = os.path.join(ROOT, "按模块")
    tagmap = {"副省级": "副省", "地市级": "地市", "行政执法类": "执法", "合卷": "合卷"}
    # questions[i] = (year, level, module, block, ans)
    for mod in MODULES:
        if mod == "政治理论":
            continue
        d = MOD_DIR[mod]
        items = []
        for (y, lv), pap in sorted(papers.items()):
            if not pap["sections"] or mod not in pap["sections"]:
                continue
            for b in pap["sections"][mod]:
                ent = pap["answers"].get(b["num"])
                items.append((y, lv, b, ent[0] if ent else None, ent[1] if ent else None))
        if not items:
            continue
        tdir = os.path.join(MDIR, d)

        # ---- 题目汇编 ----
        L = [f"# {MOD_TITLE[d]}·历年国考真题汇编（2011–2026）", "",
             f"> 共 {len(items)} 题。每题标注 `[年份·卷种·原卷题号]`，方便对照原卷与解析。", "",
             "> 答案见同目录《答案速查.md》；文字解析见《答案与解析.md》。", ""]
        cur = None
        for y, lv, b, ans, ana in items:
            if (y, lv) != cur:
                cur = (y, lv)
                lvname = "（2015年前合卷）" if lv == "合卷" else lv
                L.append(f"## {y}年 · {lvname}")
                L.append("")
            tag = f"{y}·{tagmap[lv]}·{b['num']:02d}"
            body = fmt_question(b, tag=tag, year=y, level=lv, mod=mod)
            L.append(body)
        write(os.path.join(tdir, "题目汇编.md"), "\n".join(L))

        # ---- 答案速查 ----
        A = [f"# {MOD_TITLE[d]}·答案速查表", "",
             "> 按年份排列；「—」表示该题答案暂缺。", ""]
        cur = None
        rows = []
        for y, lv, b, ans, ana in items:
            rows.append((y, lv, b["num"], ans))
        # 每张卷一个小表
        from itertools import groupby
        for (y, lv), grp in groupby(rows, key=lambda r: (r[0], r[1])):
            grp = list(grp)
            lvname = "（2015年前合卷）" if lv == "合卷" else lv
            A.append(f"## {y}年 {lvname}（{len(grp)}题）")
            A.append("")
            A.append("| 原卷题号 | 答案 |")
            A.append("|---|---|")
            for _, _, num, ans in grp:
                A.append(f"| {num} | {ans if ans else '—'} |")
            A.append("")
        write(os.path.join(tdir, "答案速查.md"), "\n".join(A))

        # ---- 答案与解析 ----
        B = [f"# {MOD_TITLE[d]}·答案与解析（2011–2026）", "", "> 「—」表示暂无解析。", ""]
        n_ana = 0
        cur = None
        for y, lv, b, ans, ana in items:
            if (y, lv) != cur:
                cur = (y, lv)
                lvname = "（2015年前合卷）" if lv == "合卷" else lv
                B.append(f"## {y}年 · {lvname}")
                B.append("")
            tag = f"{y}·{tagmap[lv]}·{b['num']:02d}"
            if ans:
                B.append(f"**{tag}（答案：{ans}）**")
                B.append("")
                stem = (b.get("stem") or "")[:80]
                B.append(f"题干：{stem}{'…' if len(b.get('stem') or '')>80 else ''}")
                B.append("")
                if ana:
                    B.append(f"解析：{ana}")
                    n_ana += 1
                else:
                    B.append("（暂无文字解析）")
                B.append("")
        write(os.path.join(tdir, "答案与解析.md"), "\n".join(B))
        print(f"模块 {MOD_TITLE[d]}: {len(items)}题, 有解析 {n_ana}")


# ============================================================ 原始PDF
def build_rawpdf():
    man = json.load(open(P("manifest.json"), encoding="utf-8"))
    d1 = os.path.join(ROOT, "原始PDF", "01_行测真题及解析_2011-2022_高教版")
    os.makedirs(d1, exist_ok=True)
    for x in man:
        t = x["title"]
        if "行测" not in t:
            continue
        m = re.search(r"(\d{4})年（", t)
        if not m or not x["pdfs"]:
            continue
        year = m.group(1)
        if "市地级" in t and "综合" not in t or "地市级" in t and "综合" not in t:
            lv = "地市级"
        elif "省级" in t:
            lv = "副省级"
        elif "市地级" in t:
            lv = "地市级"
        else:
            lv = "合卷" if int(year) <= 2014 else "副省级"
        if int(year) == 2022 and lv == "地市级":
            continue  # 该PDF实为副省级（网站错链）
        # 选含答案的PDF（体积较大的那个）
        best = max(x["pdfs"], key=lambda p: os.path.getsize(os.path.join(P("raw"), p)))
        src = os.path.join(P("raw"), best)
        dst = os.path.join(d1, f"{year}年国考行测真题及答案解析（{lv}）_高教版.pdf")
        if not os.path.exists(dst):
            shutil.copy(src, dst)

    d2 = os.path.join(ROOT, "原始PDF", "02_行测题目_2019-2026_星光版")
    os.makedirs(d2, exist_ok=True)
    for f in glob.glob(P("xg", "*.pdf")):
        shutil.copy(f, os.path.join(d2, os.path.basename(f)))

    d3 = os.path.join(ROOT, "原始PDF", "03_2023-2026真题答案及补充_环球版")
    os.makedirs(d3, exist_ok=True)
    for f in glob.glob(P("hqwx_pdf", "*.pdf")):
        b = os.path.basename(f)
        if any(k in b for k in ["面试", "公安", "金融监管", "经济金融"]):
            continue
        shutil.copy(f, os.path.join(d3, b))
    d4 = os.path.join(ROOT, "原始PDF", "04_专业科目与面试补充_环球版")
    os.makedirs(d4, exist_ok=True)
    for f in glob.glob(P("hqwx_pdf", "*.pdf")):
        b = os.path.basename(f)
        if any(k in b for k in ["面试", "公安", "金融监管", "经济金融"]):
            shutil.copy(f, os.path.join(d4, b))
    print("原始PDF整理完成")


if __name__ == "__main__":
    build_shenlun()
    build_modules()
    build_rawpdf()
    print("ALL DONE")
