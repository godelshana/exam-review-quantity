# -*- coding: utf-8 -*-
"""生成 真题库/README.md（含覆盖矩阵）"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import load, write, ROOT

P = lambda *a: os.path.join(os.path.dirname(os.path.abspath(__file__)), *a)

def shenlun_status():
    st = {}
    for y in range(2011, 2027):
        levels = ["副省级", "地市级"] if y <= 2021 else ["副省级", "地市级", "行政执法类"]
        for lv in levels:
            q = a = False
            for n in [f"sl_sl_{y}_{lv}_q.json", f"ht_sl_{y}_{lv}_q.json", f"aipta_sl_{y}_{lv}_q.json"]:
                d = load(n)
                if d and d.get("lines"):
                    q = True; break
            for n in [f"sl_sl_{y}_{lv}_a.json", f"gwy_sl_{y}_{lv}_a.json", f"hqwx_sl_{y}_{lv}_a.json"]:
                d = load(n)
                if d and d.get("lines"):
                    a = True; break
            st[(y, lv)] = (q, a)
    return st

def main():
    stats = json.load(open(P("stats.json"), encoding="utf-8"))
    sl = shenlun_status()
    xmap = {(s["year"], s["level"]): s for s in stats}

    L = ["# 国考历年真题库（2011–2026）", ""]
    L.append("本真题库收录 **2011–2026 年近15年国家公务员考试** 行测+申论真题（考生回忆版），题目已解析为结构化 Markdown，并按「年份」和「模块」两种方式组织，可直接用于复习。")
    L.append("")
    L.append("> 说明：国考真题官方从不公布，以下所有内容均为各机构整理的**考生回忆版**；答案为机构解析，个别争议题请以多机构互核为准。")
    L.append("")
    L.append("## 目录结构")
    L.append("")
    L.append("```")
    L.append("真题库/")
    L.append("├── README.md            ← 本文件（覆盖情况总表）")
    L.append("├── 按年份/               ← 按年成套刷卷（模考用）")
    L.append("│   └── 2021年国考/")
    L.append("│       ├── 行测_副省级_题目.md / 行测_副省级_答案与解析.md")
    L.append("│       ├── 行测_地市级_题目.md / 行测_地市级_答案与解析.md")
    L.append("│       └── 申论_xx_题目.md / 申论_xx_参考答案.md")
    L.append("├── 按模块/               ← 按模块专项刷题（复习用，建议从 01_数量关系 开始）")
    L.append("│   ├── 00_总览.md")
    L.append("│   ├── 01_数量关系/     ← 400题汇编 + 考点索引 + 答案解析 ★从这里开始")
    L.append("│   ├── 02_资料分析/")
    L.append("│   ├── 03_判断推理/")
    L.append("│   ├── 04_言语理解与表达/")
    L.append("│   └── 05_常识判断与政治理论/")
    L.append("└── 原始PDF/             ← 各来源原始试卷PDF（图形题必看）")
    L.append("```")
    L.append("")
    L.append("## 复习怎么用")
    L.append("")
    L.append("1. **专项复习（主路径）**：打开 `按模块/01_数量关系/00_使用说明与考点索引.md`，按「摸底 → 考点分类突破 → 套卷模考 → 错题本」四步走。其他模块同理（总览见 `按模块/00_总览.md`）。")
    L.append("2. **套卷模考**：`按年份/` 下每年一套完整卷，严格掐时间（行测120分钟/130–135题），用《答案与解析》里的速查表估分。")
    L.append("3. **图形题**：图形推理、资料分析图表在 Markdown 中只有文字，做题时请打开 `原始PDF/` 对应年份试卷。")
    L.append("")
    L.append("## 覆盖情况总表")
    L.append("")
    L.append("格式：`题目数/答案数`。行测 2011–2014 年不分卷（一套卷）；2015 年起分副省级（135题）、地市级（130题）；2023 年起增设行政执法类（130题）。")
    L.append("")
    L.append("| 年份 | 行测·副省级 | 行测·地市级 | 行测·行政执法类 | 申论·副省级 | 申论·地市级 | 申论·行政执法类 |")
    L.append("|---|---|---|---|---|---|---|")
    for y in range(2011, 2027):
        cells = [str(y)]
        lvls = (["合卷"] if y <= 2014 else ["副省级", "地市级"]) + (["行政执法类"] if y >= 2023 else [])
        row = []
        for lv in ["副省级", "地市级", "行政执法类", "合卷"]:
            pass
        def xc_cell(y, lv):
            s = xmap.get((y, lv))
            if not s or not s["total"]:
                return "—"
            return f"{s['total']}/{s['answers']}"
        # 列顺序：副省、地市、执法（合卷并入副省列显示）
        c1 = xc_cell(y, "副省级")
        if y <= 2014:
            c1 = xc_cell(y, "合卷") + "（合卷）"
        row = [c1, xc_cell(y, "地市级"), xc_cell(y, "行政执法类")]
        for lv in ["副省级", "地市级", "行政执法类"]:
            q, a = sl.get((y, lv), (False, False))
            if y <= 2021 and lv == "行政执法类":
                row.append("—")
            else:
                row.append(("✓" if q else "✗") + "/" + ("✓" if a else "✗"))
        L.append("| " + " | ".join([str(y)] + row) + " |")
    L.append("")
    L.append("注：")
    L.append("")
    L.append("- 行测答案列 < 题目列 的年份：少量题目答案按「同年另一卷种同题匹配」继承后仍无对应（两卷差异题），标注「待补」。")
    L.append("- **2023–2025 年行测答案**暂无免费完整文字版，本库未编造任何答案；可用 [粉笔APP-历年试卷](https://www.fenbi.com)、[华图在线估分](https://ah.huatu.com/tiku/gjgwy/) 核对。2026 年已有部分答案（副省 48 题、地市 87 题，来自环球网校回忆解析）。")
    L.append("- 申论为开放性主观题，「✗」表示暂未收集到参考答案（2022 年三卷、2023 执法、2024 地市）。")
    L.append("")
    L.append("## 资料来源（致谢）")
    L.append("")
    L.append("| 来源 | 内容 | 说明 |")
    L.append("|---|---|---|")
    L.append("| [高教公考真题库](http://sanlianbook.com/index.php/lists/19.html) | 2011–2022 行测真题+逐题解析PDF；2011–2022 申论真题+参考答案 | 本库 2011–2022 年主力来源，答案解析质量最高 |")
    L.append("| [星光公考](https://www.xingguanggongkao.com/XingQuestion/paperList.html) | 2019–2026 行测各卷种题目PDF | 近年题目版式最干净 |")
    L.append("| [环球网校](https://m.hqwx.com/gjgwy-kaoshi/zhenti/) | 2023–2026 真题/答案PDF、2024–2026 申论参考答案 | 补齐近年答案缺口 |")
    L.append("| [爱题库](https://www.aipta.com/zt/gk/xc/) | 2011–2026 行测/申论题目页 | 补齐 2015–2017 地市级卷、2026 行政执法卷 |")
    L.append("| [上岸鸭公考](https://m.gwy.com/gjgwy/224662.html) | 2023 申论参考答案（副省/地市） | |")
    L.append("| [安徽华图](https://ah.huatu.com/guojia/shiti/slzt/) | 2022/2023 申论真题页 | |")
    L.append("")
    L.append("## 粉笔版试卷（2023–2026 全卷种）")
    L.append("")
    L.append("通过粉笔网页版登录态抓取了 2023–2026 年全部 12 套行测卷的**题目+官方正确答案**（1580题，覆盖率100%），存放在两个位置：")
    L.append("")
    L.append("1. `按年份/20XX年国考/行测_XX_粉笔版.md` —— 粉笔重建的完整试卷，正确答案以 ✅ 标注在选项后，图形/公式均为本地图片引用（`图片/fenbi/` 目录，600+张）。")
    L.append("2. 主库《行测_XX_答案与解析.md》的答案速查表 —— 粉笔答案已按选项内容映射合并为主答案（2023–2026年各卷覆盖率 86%–100%）。")
    L.append("")
    L.append("> 注意：不同机构回忆版的**题目顺序与选项顺序可能不同**。粉笔版与主库（星光版）题目顺序存在差异属正常现象；主库中的粉笔答案均已按选项内容对齐到主库选项字母。")
    L.append("")
    L.append("## 答案核对与争议题机制")
    L.append("")
    L.append("国考答案官方不公布，各机构版本可能不一致。本库做了三层核对：")
    L.append("")
    L.append("1. **多来源交叉核对（考卷真实性）**：同一套卷用 2–4 个独立来源（高教/星光/爱题库/粉笔/环球）做题目集合级比对，2011–2026 全部试卷一致性 89–100%，确认各来源为同一套真题；个别差异为回忆版文字出入与题序排列不同。核对明细见 `_downloads/verify_report.json`。")
    L.append("2. **粉笔答案（2023–2026 主答案）**：登录粉笔后通过官方接口抓取的 1580 题正确答案（含政治理论/常识/言语/数量/判断/资料全部模块），已按选项内容映射进主库速查表，为当前最权威来源。")
    L.append("3. **AI 独立解答交叉验证（答案† 标记）**：此前 AI 对 2023–2026 年数量关系 140 题做了独立解答，与粉笔答案逐题内容比对：**97 题一致、6 题存在真实分歧**（复核确认其中粉笔正确的有「2023执法67 会议报告场次」「2025地市69 认证容斥」「2024执法70 培训安排」等，AI 已认错；「2025地市66 张某往返」「2023副省63 零件采购」等 AI 复核后仍坚持己见，速查表以 ⚠双答案呈现供自行判断）。")
    L.append("4. **争议题（⚠ 标记）**：答案速查表以 `⚠来源/AI†` 双答案标注，逐题解析中给出提示，请以粉笔/华图APP在线解析为准。")
    L.append("5. **待核题（？标记）**：回忆版题面数据自相矛盾（如 2024 地市 63/66 题）、依赖原卷缺失表格的题目，如实标注原因。")
    L.append("")
    L.append("## 视觉补全说明")
    L.append("")
    L.append("`真题库/图片/` 内含 **357 张**从原卷裁剪的题目图片：全部图形推理题、资料分析图表题、以及数量关系中被回忆版丢失的分数/公式题（如 2023 年副省 67/71 题的根式选项、2015 年地市 70 题的分数条件），均已视觉核对并补回文字。Markdown 中相应题目下方已嵌入图片。")
    L.append("")
    L.append("## 粉笔APP核对入口（答案最全，需登录）")
    L.append("")
    L.append("粉笔网页版题库需登录（本库未收录账号），复核答案的最深入口路径：**粉笔APP → 练习 → 历年试卷 → 公务员 → 国考 → 选择年份+卷种 → 开始练习 → 答题后查看解析**；网页版为 fenbi.com/spa/tiku（登录后同样路径）。华图在线估分入口：ah.huatu.com/tiku/gjgwy/。")
    L.append("")
    L.append("## 已知缺口（如实说明）")
    L.append("")
    L.append("1. 行测 2023–2025 年机构答案缺失，已用 AI 独立解答补齐数量关系（† 标记）；其他模块答案仍缺，可用粉笔APP核对。")
    L.append("2. 2015–2017 年两卷中的「非主力来源卷」部分题目答案为同题继承或 AI 解答（数量关系已全补）。")
    L.append("3. 2022 年行测地市级卷答案 74/130（同题继承），其余待补。")
    L.append("4. 图形推理、资料分析图表题的题干文字已保留，图形以裁剪图片形式嵌入；2026 年行政执法卷资料分析的 3 道饼图题的图待补（原卷PDF见 `原始PDF/03_` 目录）。")
    L.append("5. 2011–2014 年为合卷（当年不分级）；2022 年行测无官方行政执法卷，未收录网络上的非官方版本。")
    L.append("6. 个别回忆版题面数据自相矛盾（2024 年地市 63/66 题、2026 年行政执法 66 题选项D疑似缺字等），已在答案文件中标注「待核」。")
    L.append("")
    write(os.path.join(ROOT, "README.md"), "\n".join(L))
    print("README done")

if __name__ == "__main__":
    main()
