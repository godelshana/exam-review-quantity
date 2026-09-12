# -*- coding: utf-8 -*-
"""生成 数量关系使用说明+考点索引、按模块总览"""
import re, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import build_xingce_registry, load, write, ROOT, MOD_DIR

# 数量关系粗分类关键词（检索用，非严格界定）
CATS = [
    ("行程问题", r"速度|千米|公里|每小时|相遇|追上|往返|行程|时速|步行|骑车|跑道"),
    ("工程问题", r"工程|效率|合作完成|单独完成|工期|施工队|生产批次|生产线"),
    ("经济利润", r"成本|利润|打折|售价|定价|进价|销量|营业|万元|亏损|折扣|售价|单价"),
    ("排列组合与概率", r"概率|排列|组合|多少种|方法数|抽取|选中|不同的顺序|签|比赛场次|分队"),
    ("几何问题", r"面积|体积|周长|边长|圆形|矩形|三角形|正方|立方|半径|对角线|花坛|草坪"),
    ("容斥与最值", r"都参加|都报名|至少|至多|最多|最少|都不|保证.*个|百分比.*同时"),
    ("年龄问题", r"年龄|岁那年|年纪"),
    ("日期与周期", r"星期|周几|日期|闰年|循环|周期|每隔.*天|重复出现"),
    ("浓度与溶液", r"浓度|溶液|盐水|酒精|稀释|含水"),
    ("数列与数性", r"数列|质数|奇数|偶数|余数|整除|各位数字|自然数|连续.*整数"),
    ("比例与倍数", r"之比|比例|倍数|是.*的.*倍|占.*比重"),
    ("统筹与趣味", r"统筹|安排|如何分配|运输方案|空瓶|换水|过河|烙饼|货物装卸"),
]

def classify(stem):
    hits = []
    for name, pat in CATS:
        if re.search(pat, stem or ""):
            hits.append(name)
    return hits or ["其他/综合"]

def main():
    papers = build_xingce_registry()
    mod = "数量关系"
    rows = []
    for (y, lv), pap in sorted(papers.items()):
        blocks = (pap.get("sections") or {}).get(mod) or []
        for b in blocks:
            ent = pap["answers"].get(b["num"])
            rows.append((y, lv, b["num"], b.get("stem", ""), ent[0] if ent else None))
    # 分类
    index = {}
    for y, lv, num, stem, ans in rows:
        for c in classify(stem):
            index.setdefault(c, []).append((y, lv, num))
    d = os.path.join(ROOT, "按模块", MOD_DIR[mod])
    L = ["# 数量关系 · 使用说明与考点索引", ""]
    L.append("## 一、这里有什么")
    L.append("")
    L.append(f"- **题目汇编.md**：2011–2026年国考数量关系全部 {len(rows)} 题，按年份排列，每题标注 `[年份·卷种·原卷题号]`。")
    L.append("- **答案速查.md**：每套卷一张答案表，做完即对。")
    L.append("- **答案与解析.md**：带文字解析的题目（2011–2022年为主，2026年部分），按年份排列。")
    L.append("- 原始试卷PDF在 `真题库/原始PDF/` 目录，图形/复杂排版请配合PDF查看。")
    L.append("")
    L.append("## 二、建议复习流程（真题四刷法）")
    L.append("")
    L.append("1. **摸底**：掐时间做最近一年（2026地市级卷10题），对照答案速查，记录正确率。")
    L.append("2. **分类突破**：按下表考点索引，一个题型一个题型地刷。每个题型先看《答案与解析》里的解法套路，再把对应题目限时重做。")
    L.append("3. **套卷模考**：把每年的数量关系当10–15题小套卷（副省卷15题/13分钟，地市卷10题/10分钟），稳定正确率。")
    L.append("4. **错题本**：把错题按下面的考点归类记录，考前只看错题本。")
    L.append("")
    L.append("> 副省级卷数量关系15题（题号61–75），地市级/行政执法卷10题（题号61–70）。")
    L.append("> 2023–2025年答案暂无公开文字版，可用粉笔APP「历年试卷」或华图在线估分入口核对；其余年份答案齐全。")
    L.append("")
    L.append("## 三、考点 × 真题索引（关键词粗分，供检索定位）")
    L.append("")
    order = [c for c, _ in CATS] + ["其他/综合"]
    L.append("| 考点 | 题量 | 真题定位（年份·卷种·题号） |")
    L.append("|---|---|---|")
    for c in order:
        lst = index.get(c)
        if not lst:
            continue
        locs = "、".join(f"{y}·{'副省' if lv=='副省级' else ('地市' if lv=='地市级' else ('执法' if lv=='行政执法类' else '合卷'))}·{num:02d}"
                          for y, lv, num in lst[:24])
        more = f"（等共{len(lst)}题）" if len(lst) > 24 else ""
        L.append(f"| {c} | {len(lst)} | {locs}{more} |")
    L.append("")
    L.append("> 注：一道题可能同时命中多个考点关键词，归类有交叉属正常现象；标注为粗分，用于快速检索，不代表严格题型划分。")
    L.append("")
    write(os.path.join(d, "00_使用说明与考点索引.md"), "\n".join(L))

    # ---- 按模块总览 ----
    stats = {}
    papers2 = papers
    for m2 in ["常识判断", "政治理论", "言语理解与表达", "数量关系", "判断推理", "资料分析"]:
        n = 0
        nans = 0
        for (y, lv), pap in papers2.items():
            for b in (pap.get("sections") or {}).get(m2, []):
                n += 1
                if b["num"] in pap["answers"]:
                    nans += 1
        if n:
            stats[m2] = (n, nans)
    O = ["# 按模块复习 · 总览", ""]
    O.append("行测五大模块历年真题已按模块汇编，**建议从《01_数量关系》开始**（数量关系题量少、套路强、提分快，且全部为纯文字题，适合纯文本复习）。")
    O.append("")
    O.append("| 模块 | 题目总数(2011-2026) | 有答案题目 | 模块文件夹 |")
    O.append("|---|---|---|---|")
    show = [("数量关系", "01_数量关系"), ("资料分析", "02_资料分析"), ("判断推理", "03_判断推理"),
            ("言语理解与表达", "04_言语理解与表达"), ("常识判断", "05_常识判断与政治理论")]
    for name, d2 in show:
        n, nans = stats.get(name, (0, 0))
        if name == "常识判断":
            n2, nans2 = stats.get("政治理论", (0, 0))
            n, nans = n + n2, nans + nans2
        O.append(f"| {name} | {n} | {nans} | {d2}/ |")
    O.append("")
    O.append("每个模块文件夹包含：")
    O.append("")
    O.append("1. `00_使用说明与考点索引.md`（数量关系已配考点索引，其他模块为通用说明）")
    O.append("2. `题目汇编.md` —— 全部题目，按年份排列")
    O.append("3. `答案速查.md` —— 做完对答案")
    O.append("4. `答案与解析.md` —— 逐题解析（2011–2022最全）")
    O.append("")
    O.append("> 资料分析/判断推理中的图表题、图形推理题在文本中仅保留题干文字，图形请回到 `原始PDF/` 查看对应年份试卷。")
    O.append("")
    write(os.path.join(ROOT, "按模块", "00_总览.md"), "\n".join(O))
    print("DONE")
    print(json.dumps({k: v for k, v in stats.items()}, ensure_ascii=False))

if __name__ == "__main__":
    main()
