# -*- coding: utf-8 -*-
"""给 assemble.py 打AI答案集成补丁"""
import io

src = open('assemble.py', encoding='utf-8').read()

# 1) merge AI 答案
old = '''            if d["answers"]:
                papers[(2026, lv)]["asrc"] = (papers[(2026, lv)].get("asrc") or "") + "+hqwx"
    return papers'''
new = '''            if d["answers"]:
                papers[(2026, lv)]["asrc"] = (papers[(2026, lv)].get("asrc") or "") + "+hqwx"

    # AI 独立解答合并（仅填空缺）+ 争议检测
    ai = load("ai_answers.json") or {}
    for key, answers in ai.items():
        if "|" not in key or not isinstance(answers, dict):
            continue
        y, lv, mod = key.split("|")
        pap = papers.get((int(y), lv))
        if not pap or not pap["sections"]:
            continue
        for num, val in answers.items():
            num = int(num)
            block = next((b for b in pap["sections"].get(mod, []) if b["num"] == num), None)
            if block is None:
                continue
            if val.startswith("?"):
                if num not in pap["answers"]:
                    reason = {"?图": "图形题，AI无法仅凭文字作答，请看原卷图", "?矛盾": "回忆版题面数据自相矛盾，答案待核",
                              "?表": "题目依赖原卷表格，答案待核"}.get(val, "答案待核")
                    pap["answers"][num] = ("待核", reason, block.get("stem", ""))
                    pap["airaw"] = pap.get("airaw", {})
                    pap["airaw"][num] = val
                continue
            letter = val[-1] if val.endswith("图") else val
            if num in pap["answers"]:
                inst = pap["answers"][num][0]
                if inst and inst != letter:
                    pap.setdefault("disputes", {})[num] = {"ai": letter, "inst": inst}
            else:
                note = "AI独立解答，建议用粉笔/华图APP复核"
                if val.endswith("图"):
                    note = "AI基于对原图的视觉判读作答，建议复核"
                pap["answers"][num] = (letter, note, block.get("stem", ""))
                pap.setdefault("aisrc", set()).add(num)
    for pap in papers.values():
        pap["airaw"] = pap.get("airaw", {})
        pap["aisrc"] = pap.get("aisrc", set())
        pap["disputes"] = pap.get("disputes", {})
    return papers'''
assert old in src, "merge anchor"
src = src.replace(old, new)

# 2) answer_table 签名
old2 = 'def answer_table(answers, total_max):'
new2 = 'def answer_table(answers, total_max, ai_nums=None, disputes=None, pending=None):'
assert old2 in src, "sig"
src = src.replace(old2, new2)

# 3) answer_table 主体标注
old3 = '''    nums = sorted(answers)
    rows = []
    line = []
    for n in range(1, total_max + 1):
        a = answers.get(n)
        line.append(str(answers.get(n, "—")) if a else "—")'''
new3 = '''    ai_nums = ai_nums or set()
    disputes = disputes or {}
    nums = sorted(answers)
    rows = []
    line = []
    for n in range(1, total_max + 1):
        a = answers.get(n)
        if a == "待核":
            s = "？"
        else:
            s = str(a) if a else "—"
        if n in disputes:
            s = "⚠{}/{}†".format(s, disputes[n]["ai"])
        elif n in ai_nums and a:
            s = s + "†"
        line.append(s)'''
assert old3 in src, "body"
src = src.replace(old3, new3)

# 4) 调用传参
old4 = '''        ansmap = {n: v[0] for n, v in pap["answers"].items()}
        A.append(answer_table(ansmap, total))'''
new4 = '''        ansmap = {n: v[0] for n, v in pap["answers"].items()}
        A.append(answer_table(ansmap, total, pap.get("aisrc"), pap.get("disputes"), pap.get("airaw")))'''
assert old4 in src, "call"
src = src.replace(old4, new4)

# 5) 逐题解析标注
old5 = '''                if ent:
                    a, ana, _ = ent
                    A.append(f"**{b['num']}.（{a}）** {esc(b.get('stem',''))[:60]}{'…' if len(b.get('stem',''))>60 else ''}")
                    A.append("")
                    if ana:'''
new5 = '''                if ent:
                    a, ana, _ = ent
                    disp = pap.get("disputes", {}).get(b["num"])
                    mark = "（† AI独立解答）" if b["num"] in pap.get("aisrc", set()) else ""
                    if a == "待核":
                        A.append(f"**{b['num']}.** {str(ana)[:50]}")
                        A.append("")
                        continue
                    A.append(f"**{b['num']}.（{a}）**{mark} {esc(b.get('stem',''))[:60]}{'…' if len(b.get('stem',''))>60 else ''}")
                    A.append("")
                    if disp:
                        A.append(f"> ⚠️ 争议题：来源答案 {disp['inst']}，AI独立解答 {disp['ai']}。请以粉笔/华图等APP在线解析为准。")
                        A.append("")
                    if ana:'''
assert old5 in src, "jiexi"
src = src.replace(old5, new5)

open('assemble.py', 'w', encoding='utf-8').write(src)
print("all patched OK")
