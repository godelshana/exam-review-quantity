# -*- coding: utf-8 -*-
"""合并所有 gen_*_output.json 为题库数据.js，供刷题页面外载。
用法：python merge.py
校验：schema 完整性、选项唯一、答案下标合法、题干去重。
"""
import json, glob, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "题库数据.js")

def template_key(q):
    # 只用于防止一轮内连续同构题；保留数字和题目本身，不用于删除题目
    s = re.sub(r"\s+", "", q.get("s", ""))
    return re.sub(r"\d+(?:\.\d+)?", "#", s)[:80]

def quality_meta(q):
    h, t = q["h"], q["t"]
    if t == "跳过":
        return {"cost":"高", "optionValue":"低", "canEstimate":False, "canPlugOptions":False, "skipReason":q.get("tr", "高成本结构")}
    if t == "估算":
        return {"cost":"低", "optionValue":"高", "canEstimate":True, "canPlugOptions":True, "skipReason":""}
    if t == "双钩":
        return {"cost":"中", "optionValue":"中", "canEstimate":True, "canPlugOptions":True, "skipReason":""}
    if t == "深钩":
        return {"cost":"中", "optionValue":"中", "canEstimate":True, "canPlugOptions":True, "skipReason":""}
    return {"cost":"低", "optionValue":"高", "canEstimate":True, "canPlugOptions":True, "skipReason":""}

def normalize(q):
    # 选项统一为字符串（数字 118 -> "118"，小数去尾零）
    def s(v):
        if isinstance(v, str):
            return v
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    q["o"] = [s(v) for v in q["o"]]
    q["e"] = str(q["e"])
    q["tr"] = str(q.get("tr", ""))
    q["template"] = template_key(q)
    q.update(quality_meta(q))
    return q

def validate(q, src):
    for k in ("h", "t", "s", "o", "a", "e"):
        if k not in q:
            raise ValueError(f"{src}: 缺字段 {k}: {q}")
    if not isinstance(q["o"], list) or len(q["o"]) != 4:
        raise ValueError(f"{src}: 选项数≠4: {q['s'][:20]}")
    if len(set(q["o"])) != 4:
        raise ValueError(f"{src}: 选项重复: {q['s'][:20]}")
    if not (isinstance(q["a"], int) and -1 <= q["a"] <= 3):
        raise ValueError(f"{src}: a 越界: {q['s'][:20]} a={q['a']}")
    if len(q["s"]) > 150:
        raise ValueError(f"{src}: 题干过长: {q['s'][:30]}")

def main():
    bank, seen = [], set()
    files = sorted(glob.glob(os.path.join(HERE, "gen_*_output.json")))
    if not files:
        print("未找到任何 gen_*_output.json"); sys.exit(1)
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        n0 = len(bank)
        for q in data:
            q = normalize(q)
            validate(q, os.path.basename(f))
            key = re.sub(r"\s+", "", q["s"])[:40]
            if key in seen:
                print(f"  [去重] 跳过重复题干: {q['s'][:24]}")
                continue
            seen.add(key)
            bank.append({"h": q["h"], "t": q["t"], "s": q["s"], "o": q["o"],
                         "a": q["a"], "e": q["e"], "tr": q.get("tr", ""),
                         "template": q["template"], "cost": q["cost"],
                         "optionValue": q["optionValue"], "canEstimate": q["canEstimate"],
                         "canPlugOptions": q["canPlugOptions"], "skipReason": q["skipReason"],
                         "sourceType": "mock", "sourceLabel": "GLM模拟"})
        print(f"{os.path.basename(f)}: {len(data)} 题，入库 {len(bank)-n0}")
    # 分类统计
    from collections import Counter
    ch, ct = Counter(q["h"] for q in bank), Counter(q["t"] for q in bank)
    print("按钩子:", dict(ch))
    print("按卡型:", dict(ct))
    print("合计:", len(bank))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("// 自动生成：由 gen/gen_*_output.json 合并，请勿手改；重跑 merge.py 再生\n")
        fh.write("window.BANK = ")
        fh.write(json.dumps(bank, ensure_ascii=False, separators=(",", ":")))
        fh.write(";\n")
    print(f"已写出 {OUT}")

if __name__ == "__main__":
    main()
