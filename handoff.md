# 数量关系训练 / 验证隔离交接

## 当前实现与不可回退的边界

本轮把旧“原创 / GLM / 待核真题”入口改成了训练混编天梯、迁移混编、最近三年验证首测、验证复盘四种模式。默认仍然五题。

**保留年份固定为2024、2025、2026，国考与广东省考都只作验证，不得进入普通训练池。** 已知同构的原创 / GLM也保守隔离；不能因为一题是V3、不评分，就拿它的改数字版本去训练。

| 范围 | 实际清单 | 本轮放行 | 其他处置 |
|---|---:|---:|---|
| 原创100v2＋复合24 | 124 | 112训练 | 10高风险＋2中风险同构暂不训练；原题未删除 |
| 2011—2023国考 | 295 | 26训练 | 269逐条隔离 |
| GLM | 545 | 9训练 | 536逐条隔离；不再把初筛104题当合格题库 |
| 2024—2026国考 | 105题位 | V1 30题位 | V3 75题位；跨卷去重后V1仅21个独立题目 |
| 2024—2026广东 | 每年均有缺口记录 | 0 | 本地没有可靠卷别、题面、答案；预期数量为null，不虚构题位 |

**当前普通训练池147题＝原创112＋旧国考26＋GLM9。** 不能把105题位说成105道合格题，不能把945条审查记录说成945道数学审计通过。

945条国考 / GLM资料都有处置记录：80条精确模型计算通过、1条反例否定、864条未独立复算。计算通过还须过来源、图片、争议、泄漏和重复门禁。新放行题另有第二审查者复审，见下列脚本及报告。已有原创124题保留原有独立数学审计和冻结SHA，不手改原题资产。

## 数据和维护入口

- `教学/速刷/datasets/sources.json`：完成本任务必需的结构化快照；默认构建无需未跟踪的原始真题库，也不联网。
- `datasets/certificates.json`、`datasets/make_certificates.py`：逐题计算模型、专属快法 / 常规法、回代、唯一选项核验。
- `datasets/audit.json`、`quarantine.json`、`manifest.json`、`summary.json`：逐条审查、隔离及105题位 / 广东缺口。
- `datasets/template_screening.json`、`authored_policy.json/js`：原创124＋GLM545的模板筛查；前端必须完整加载124个原创UID策略，缺失即停用，不可默认低风险。
- `build_datasets.py`：默认从快照重建；`--check`只读；仅需补原始资料时才`--import-local`。修改题面后不能未经复审直接重绑证书。
- `authored_methods.json`、`build_authored_methods.py`、`authored_methods.js`、`原创逐题方法审计.md`：124道原创的两路解法、适用边界、快法收益、跳题理由及梯度。53题明确低额外收益，不伪装秒杀。
- `audit_datasets_independent.py`、`datasets_independent_review.md`：新放行训练 / V1的独立模型复审、错误注入及内容指纹锁。
- 不修改`真题库/按年份/`、`按模块/`生成文件；维护仍须遵守根目录AGENTS.md。

独立复审已发现并处理：`glm:D:30`只有“125等份”，不能推出125个全等小正方体，保留原题并隔离；2025副省76 / 执法72的常规法毛利反比表述已修正。来源争议不静默改成AI答案，缺少来源推理时也不编造另一方理由。

## 引擎 / 页面关键点

`core.js`强制判断年份与来源标记，拒绝把验证改成train绕过边界。`sample`默认只抽可训练题；混编倾向3训练＋2未曝光验证，控制family与题源分散；不足不复制。跨卷共题按稳定identity去重。

验证题一显示就保存曝光：刷新 / 中途退出不恢复首测；未作答曝光不造分。V1首测、重复复盘、V2暂定分别统计。V3不抽题。首测仅指本浏览器记录，不能证明学习者过去从未见过题。清除浏览器存储或换设备也不能被当成真正新题。

验证记录不参与训练错题权重、训练正确率或晋级。迁移轮中的训练题属于训练统计，但整轮不晋级。正式验证 / 迁移整轮硬限时、禁提示和暂停、结束后才显示解析。训练正确率−V1首测正确率是描述性迁移差，不是同难度实验或官方分数预测。

页面显示专属快法 / 常规法 / 适用边界 / 中文跳题建议 / 易错点；无可靠快法标low。默认五题，四档梯度，147题中只有合格且未被隔离者可用。schema3历史兼容；坏记录备份隔离。

## 检查与发布

完整CI门禁在`.github/workflows/pages.yml`：原题生成复现、GLM初筛复现、结构校验、124原题数学复算、发布hash故障注入、core与隔离测试、1000轮实际数据抽样、20项数据测试、14项原创方法测试、新放行题独审，然后构建。

重点命令：

```powershell
python -X utf8 教学/速刷/build_datasets.py --check
python -X utf8 教学/速刷/test_datasets.py
python -X utf8 教学/速刷/build_authored_methods.py --check
python -X utf8 教学/速刷/test_authored_methods.py
python -X utf8 教学/速刷/audit_datasets_independent.py
node 教学/速刷/test_core.cjs
node 教学/速刷/test_isolation.cjs
node 教学/速刷/test_dataset_integration.cjs
python -X utf8 教学/速刷/build_site.py
```

真实Chrome验收脚本`browser_acceptance.py`通过WebBridge驱动用户浏览器；仅允许独立localhost测试origin，绝不清空学习者历史。1920和390px下五题闭环、错选映射、曝光及复盘隔离、硬截止、刷新保持、策略文件缺失停用均已测。移动端无横向溢出，按钮 / select / summary触控区至少44px。

发布只拷白名单到`_site`，不发布原始目录和旧真题入口。`version.json`记录发布commit与静态资产SHA256；本地未提交构建中的revision不是已上线证明。

仓库：`https://github.com/godelshana/exam-review-quantity`

Pages：`https://godelshana.github.io/exam-review-quantity/`

```powershell
$env:HTTPS_PROXY='http://127.0.0.1:7890'
$env:HTTP_PROXY='http://127.0.0.1:7890'
git push origin main
python -X utf8 教学/速刷/verify_release.py --revision <本次commit完整SHA>
```

`verify_release.py`通过7890代理等待**该commit**的Actions成功，再校验Pages的version和全部资产与git对象的hash一致；还应实际打开线上页面，核验147训练、验证入口、默认五题、资源无错误。发布成功以实际执行结果为准，不以push成功或旧`7be77e8`工作流为准。

## 尚存的素材缺口

广东近三年资料仍缺；国考75个验证题位仍V3（缺图 / 题面疑点 / 答案争议 / 尚无独立复算等）。未独立复算的旧真题及GLM仍隔离。后续先补可靠原卷和解析再逐题审计，不以增加题量取代质量，不把结构筛查冒称数学审计，也不承诺对缺失广东题已完成语义零泄漏证明。