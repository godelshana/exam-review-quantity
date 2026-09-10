# 完整真题审查与接入说明

## 已纠正上一版的错误

项目本来就有省考数据。此前“广东近三年缺资料”“只放147题即可完成”的说法错误，旧版把没有完成的工作当成了隔离结果。本版已经逐条审核并实际接入现有真题，不能再回退到旧小池。

| 项目 | 本版实际结果 |
|---|---:|
| 国考输入（卷内题位） | 400 |
| 省考输入（按粉笔ID去重） | 705 |
| 省考原始卷 / 卷内出现记录 | 66 / 855 |
| 已逐条审核 | 1105 / 1105 |
| 可训练真题条目 / 规范化题干去重 | 917 / 841 |
| 近三年国考、广东测试题位 | 150 |
| V1正式 / V2暂定题位 | 148 / 2 |
| V1去重独立测试题 | 114 |
| 争议或缺损研读题 | 27（23争议＋4缺损/矛盾） |
| 误抓到其他模块的题 | 11，不当数量题练 |
| 原创 / GLM可选补充 | 112 / 9 |
| 含补充的可训练条目合计 | 1038 |

**只把2024、2025、2026年国考和广东省考留给测试。广东三年各15题，共45题已接入。其他省份近三年题正常训练。**

普通相同考点、同一方法家族不是拒收理由。跨省联考同题保留全部 `occurrences`，湖北筛选可练87条，不是“只抓到14题”；代表题源统计不能误当该省全部覆盖。

训练梯度：入门285、熟练465、深化156、综合11。梯度和45/65/90/120秒目标为教学判断，不是考生群体实测。

## 页面交付

- 默认直接练真题，五题一轮；可按地区、考点、难度筛选，也可选择原创 / GLM补充。
- 题库目录按当前筛选分页，可指定单题限时练；指定单题不计天梯晋级。
- 每题含独立推导、难度理由、省步路径、常规解法、快法边界、陷阱、跳题理由及来源/修复说明。
- 真题保留原选项顺序；图形选项在作答和复盘两处都显示为图片。
- 争议题不自动强行判分，提供原标记、独立论证与条件解释。缺损题具体说明现有材料为什么不足，不编答案。补充条件与原文分开。
- 二审指出的2道口径题，在题目前明确展示教学作答口径，未把新增口径冒充原卷事实。
- 验证题显示即保存曝光，旧版曝光按原UID继承到修复后的新标识，退出/刷新/换题解不重获首测资格。验证、V2、复盘与训练成绩分开，不影响训练晋级。

## 数据链与文件

1. `full_audit/intake.json`：400国考＋705省考原始快照、全部855个省考出现位置、来源与机构原答案；不改用户原题文件。
2. `full_audit/national_01..04.json`、`provincial_01..08.json`：12个逐题任务输入。
3. `full_audit/reviews/*.json`：六个subagents与主代理完成的逐题审核。不能用pending或“未审计”替代推导。
4. `full_audit/review_bindings.json`：每条源数据与审核overlay的精确指纹；改题面或答案后默认构建拒绝沿用旧审核。
5. `full_audit/oracles/`、`check_full_oracles.py`：离线标准库重算、枚举与性质回归；自动检查和人工推导分开统计，绝不把字段齐全冒称数学双审。
6. `full_audit/second_reviews/`：额外82道高风险verified复核＋3道invalid来源核查，保留初算、比对与边界意见。
7. `prepare_full_assets.py`、`asset_map.json`：保留原图，恢复39个Brotli封装文件，生成白底PNG副本及双哈希。页面实际用129张独立图片；不发布整页PDF和联系页。
8. `build_full_bank.py` → `full_audit/banks.js`、`catalog.json`、`summary.json`、`manifest.json` → `app.js`。

旧 `datasets/`、旧147题报告仍保留以复现上一版及GLM补充策略，**不再决定本版真题的准入或覆盖统计**。页面只使用新 `FULL_REAL_*` 真题数据。

## 本地与CI检查

```powershell
python -X utf8 教学/速刷/build_full_intake.py --check
python -X utf8 教学/速刷/prepare_full_assets.py --check
python -X utf8 教学/速刷/check_full_oracles.py --require-all-batches
python -X utf8 教学/速刷/check_full_oracles.py --self-test
python -X utf8 教学/速刷/build_full_bank.py --check
python -X utf8 教学/速刷/test_full_bank.py
node 教学/速刷/test_core.cjs
node 教学/速刷/test_isolation.cjs
node 教学/速刷/test_full_bank.cjs
python -X utf8 教学/速刷/build_site.py
```

有用户原始素材时，另可执行 `build_full_intake.py --check --verify-local`，核对全部400国考与855省考原始出现记录。CI不需要未跟踪的原始PDF库，也不联网爬题。

重新审核或修复后的维护顺序：先完成逐题review及重算，必要时运行 `prepare_full_assets.py --import-local`，再显式 `bind_full_reviews.py --seal-reviewed-inputs`，最后重建并测试。绑定指纹只是记录，不是数学证明，禁止在未复审时自动重绑。

浏览器验收：`browser_acceptance.py` 覆盖1920/390px五题闭环、正确选项映射、提示/暂停、硬截止、曝光/复盘、刷新及必需资产缺失。`browser_full_acceptance.py`另验四川/广东/湖北五题、四川2024单题、图选项、争议研读、全量129张图片解码和新题库缺失停用。只在独立localhost origin运行，不往学习者线上历史灌测试成绩。

发布：`.github/workflows/pages.yml` → 白名单 `_site` → GitHub Pages；`verify_release.py --revision <commit>` 经7890代理等待该commit的Actions成功，并逐个核对线上版本和全部资产哈希。push成功或旧工作流成功都不等于新版本上线。最终上线结果以实际发布验证日志为准。

自动回归的精确边界：956条执行算术/枚举/局部性质计算（其中290条为性质或补充检查）、25条重复结果复用、11条人工边界、113条尚无可执行算例；642条核对唯一选项。1105条均有逐题审核与自己的题解，但不能把这些统计称作1105条全自动数学证明。82道高风险另有独立第二次人工推导。
