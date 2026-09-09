# -*- coding: utf-8 -*-
"""审查 GLM 数量关系生成题库。

用途：发现结构重复、格式/答案索引问题、解释残留占位符和跳过卡标注风险。
注意：本脚本不能替代逐题数学复核；生成器自身的 assert/独立 checker 仍是答案校验第一道防线。
用法：python 教学/速刷/gen/audit_glm_bank.py
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = sorted(ROOT.glob("gen_*_output.json"))
errors, warnings = [], []
all_q = []

def stem_signature(s):
    s = re.sub(r"\d+(?:\.\d+)?", "{数}", s)
    s = re.sub(r"[甲乙丙丁ABCD]", "X", s)
    s = re.sub(r"\s+", "", s)
    return s

def check(q, src, i):
    for k in ("h", "t", "s", "o", "a", "e", "tr"):
        if k not in q: errors.append(f"{src}[{i}] 缺字段 {k}")
    if not isinstance(q.get("o"), list) or len(q.get("o", [])) != 4:
        errors.append(f"{src}[{i}] 选项不是4个")
    elif len(set(map(str, q["o"]))) != 4:
        errors.append(f"{src}[{i}] 选项重复")
    if not isinstance(q.get("a"), int) or not -1 <= q.get("a", 9) <= 3:
        errors.append(f"{src}[{i}] 答案下标非法: {q.get('a')}")
    if q.get("t") == "跳过" and q.get("a") != -1:
        errors.append(f"{src}[{i}] 跳过卡必须 a=-1")
    if q.get("t") != "跳过" and q.get("a") == -1:
        errors.append(f"{src}[{i}] 非跳过题不能 a=-1")
    text = " ".join(str(q.get(k, "")) for k in ("s", "e", "tr"))
    # {an} 是有意的等差数列记号；其它常见单字占位符多半说明格式化漏掉。
    for token in re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", text):
        if token not in {"an"}:
            warnings.append(f"{src}[{i}] 疑似残留占位符 {{{token}}}")
    if q.get("t") == "跳过":
        rationale = text
        if not re.search(r"跳过|枚举|递推|分类|最不利|容斥|整除|自指|最优化|两分钟|45秒", rationale):
            warnings.append(f"{src}[{i}] 跳过理由缺少成本/结构说明")
    if len(str(q.get("e", ""))) < 8:
        warnings.append(f"{src}[{i}] 解析过短")

for f in FILES:
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{f.name}: JSON解析失败 {e}"); continue
    print(f"{f.name}: {len(data)}题")
    for i, q in enumerate(data):
        check(q, f.name, i); all_q.append((f.name, i, q))

exact = defaultdict(list); templates = defaultdict(list)
for src, i, q in all_q:
    exact[re.sub(r"\s+", "", q.get("s", ""))].append((src, i))
    templates[(q.get("h"), q.get("t"), stem_signature(q.get("s", "")))].append((src, i))
for key, locs in exact.items():
    if len(locs) > 1: errors.append(f"重复题干×{len(locs)}: {locs}")
for key, locs in templates.items():
    if len(locs) >= 3:
        warnings.append(f"同模板×{len(locs)} [{key[0]}/{key[1]}]: {locs[:4]}")

print("总题数:", len(all_q))
print("卡型:", dict(Counter(q.get("t") for _, _, q in all_q)))
print("钩子:", dict(Counter(q.get("h") for _, _, q in all_q)))
print("精确重复:", sum(len(v)-1 for v in exact.values() if len(v)>1))
print("高重复模板组(≥3):", sum(len(v)>=3 for v in templates.values()))
print("错误:", len(errors), "警告:", len(warnings))
for x in errors: print("ERROR", x)
for x in warnings[:80]: print("WARN ", x)
if len(warnings) > 80: print(f"... 另有 {len(warnings)-80} 条警告")
sys.exit(1 if errors else 0)
