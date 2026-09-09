# -*- coding: utf-8 -*-
"""生成作者侧结构复核、100条变更表和给独立审计员的交接文件；不写JS。
结构归并是作者审读判断，不冒充独立审计放行。
"""
import json,re,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parent
G='''1,27|平均数增删的总量差|人数变化决定均值差额权重
2,26,52,77|比例转移与未变基准|守总量、追踪调动时基数或双边差量
3,28,35|统一假设后的差额替换|单一基准覆盖全量，差额只由变化部分承担
4|精确比例的整数分母约束|最简分母整除总人数，附带开区间
5,30,32,54,78|阶段工作量守恒|按加入退出、进排水或效率变化事件分段
6,31|成对效率重复计数消元|成对和相加或加减恢复个体和总体
7|等路程调和平均速度|总路程除以分段总时间，不平均速度
8,33,58|相对速度及起点平移|先同步时刻，再消耗间距
9,60|最坏抽取容量|不达目标时每类最多容纳多少
10,59,85|互异整数的最小占用构造|递增最小序列封边界并检验可达性
11,62|禁止同时入选的补集计数|固定或恰选限制后排除非法对子
12|相邻对象捆绑|外部块排列乘内部次序
13,65|不放回分类抽样|无序等可能子集内按颜色定额分类
14|独立伯努利补事件|微样本乘法或全部失败的反面
15,45|共角分点线性比到面积比|两邻边缩放乘积，不把长度比直接当面积比
16|固定和的乘积极值|平方非负证明上界并取等
17,46,70|整周余日及反推月初|月长除7后的余日必须连续
18,71|共同周期对齐|经过天数的共同倍数及日期编号偏移
19|连续涨折的变基数倍率|连续比例操作相乘，不直接加减
20|收入固定的反比例补偿|数量倍率与价格倍率乘积固定
21|年龄时间平移与差不变|统一年份后用总和、比例，年龄差不变
22,49|溶质守恒加水稀释|溶质不变而总质量改变
23|两集合交并与全集补集|先找真正并集，再扣重复计数
24,99|等差中项及块总和消元|等长块相减消首项，平均值锁中间位置
25,50,81|范围或相位的同余交集|同一未知量满足多个余类，再取最小候选
29,53|分批利润与收益下界|按数量加权，收入目标先覆盖总成本
34|顺逆流速度差与时间反比|等程的反时间比例与二倍水速共同定尺度
36|容量的向上取整|验证少一单位不够、多一单位足够
37,84|有界分数与极值名次|他人分数边界封住目标，互异时递增填充
38,40|有名位置的资格先安排|限制位置先选，已用对象不得再用
39|分类定额选取|独立类别组合数相乘
41,42,89|已知条件缩减样本空间|事件必须在过滤后的条件空间中计数
43|均匀边带的几何补形|外减内避免四角重复计算
44|恒流注满与体积比例|变化维度决定体积比，流量固定才转时间比
48|严格盈利整数临界点|固定成本除边际收益，区分等号与严格大于
51,76|均值转移反推人数尺度|均值差恢复人数，再带真实转移总分计算
55|交替作业与分数末日|完整周期后下一位接尾量，不强制整天
56|往返相遇的展开路程|相遇次数转累计路程倍数并追踪折返位置
57|环道转向的有向弧长|转向前相位决定随后消耗哪一段弧
61|有名同质物资整数分配|总量、每组下限和指定组上限限制整数解
63,64,88|前缀路径状态边界|严格性、终点及中途状态共同筛路径
66,90|来源后验混合概率|先验乘证据更新来源，再算条件内事件
67|分线交点的仿射面积|保持分点比例的坐标规范化、交点方程求高度
68,93|切割挖孔的表面收支|消失外面与新增内面分别计数
69|熔铸体积守恒|形状可变且无损，守恒体积而非表面
47,72,94|固定相位的工作日周期统计|单一周期或共同周期内计数，尾段另补
73,96|离散二次利润及可行域|价格销量共同变化，筛产能与整数约束
74,83,97|资源与容量的整数优化|有限整数域求最优，不接受实数松弛答案
75|重复置换的保留比例|每次移出按当时浓度更新溶质量
79|可抢占并行任务调度|容量下界还须有符合不并机限制的排程
80|整日多项目资源派工|每队整日分配与各项目需求共同限制工期
82|时间燃料双预算|同一目标被两个预算封顶，取较紧者并验可达
86|有名分组及固定成员禁同组|按受限人物归属分类，组间标签不可删
87|相对先后的对称性与位置排除|交换标签保留其余限制才可除2
91|锥柱液面时间的分段体积模型|锥内高度立方比，越过截面后才线性柱高
92|直角射影与平行截取|射影恢复必要边长，相似给剩余图形周长
95|周末顺延后的实际日期交集|原始计划不等于执行日期，固定星期筛候选
98|三集合按参与次数分层|人数与参与次数是两条不同线性约束
100|异长度连续块的日程概率|压缩必须一一对应，事件再用休息插空计数'''
C='''76|人数比例、调出者均分、接收后均分共用人数尺度|设三组人数和总分并写大方程组|只用甲均值变化锁x，再扣丙调出的真实总分
77|两次调动先后改变百分比基数，终态比例约束人数|从原三组人数顺向展开|由终态30/60/90逆序恢复每一步基数
78|延迟加入和跨阶段效率切换是两个不同事件|把总工作量除以一个平均效率|在每个事件边界守恒，首阶段8天、次阶段8天
79|总容量下界与同任务不并机共同约束排程|固定分配两机器两任务得到5小时|44/10封下界，再以3.2与1.2小时互换证明可达
80|各组整日占用和三个项目独立需求共同限制工期|按天枚举两组的项目顺序|先取总量下界，再按项目构造7个甲日、8个乙日
81|同一时间需满足两个相对位置同余|逐秒模拟所有绝对位置|甲乙先筛t=300k，再检查甲丙相位
82|往返速度和停留构成时间预算，双向耗油构成另一预算|只解时间上限84|分别求84与80，取较紧80并回代时间
83|材料、工时、整数件数共同限制利润|求实数交点再随意取整|分y区间使用不同资源上界，仅查中间两种并给850构造
84|固定90分、总分、互异整数与名次共用高分人数|枚举五个其他人的精确分数|假设第6名推出最低555矛盾，再构造第5名总550
85|互异正整数、总量和最大为最小两倍共同限制|枚举四组人数|以m、m+1、m+2、2m封5m+3下界并构造
86|有名组定员、甲固定和乙丙禁同组共用组归属|全员排列再多次除重|按乙丙是否一人在第一天分两类直接选组
87|相对顺序、不相邻、另一人非端点同时成立|固定甲乙位置再处理余人|补集剔相邻及端点，再利用甲乙交换的对称性
88|全程前缀非负、最终平衡、中途余额固定|直接套末点卡特兰数14|在第4天状态2拆开，两段各3种相乘
89|至少一偶的条件、最大值和总和奇偶共用抽样集合|把三个事件视为独立概率|条件空间先缩到19，固定5后另两张一奇一偶共4种
90|首红改变来源权重，不放回又改变盒内概率|仍按两盒各一半或仍按原红球比例|权重先更新2:3，再加权各盒1/3、2/3
91|恒流、锥内立方比例和跨截面体积守恒|把水位当作时间的线性函数|由1分钟装1/27锥锁27分钟，余量换圆柱高6
92|高的射影、原边长与半高平行截线相似共同影响周长|全面建坐标求所有交点|射影得15/20/25，按半高缩线段后加梯形四边
93|体积损失反推孔截面，表面又含孔壁|只从原表面减开口|先得孔边4，再数600−32+160
94|工作4日周期、星期7日周期及统计尾段共同计数|将两个出勤率相乘后取整|28日实际交集15，再补29、30两天
95|三个原始周期与周末顺延共同决定实际交集|只取原始周期最小公倍数|固定周一作候选，向前回看周末待顺延的原计划
96|整数价格档、需求变化、必须满足全部需求及产能上限|直接使用无产能约束的5040|产能先将k限制为0至3，再比较合法利润
97|整包、80至83窄需求区间和成本共同限制采购|只按单价优先买大包|窄区间筛7a+11b的整数解，再比较4个方案
98|恰一项人数与各项目边际人数共同限制Venn区域|设3个两两交集展开容斥|按参与次数只设x、y消元，再额外核对各边际可实现
99|前3月包含于前6月，等差规律延伸到后6月|把块总差直接视为公差|先用等长块差900=9d，再求目标块均值
100|不同长度连续课程、互斥日程、休息不邻及等可能基准|把8天无条件组合或给休息日编号|证明压缩一一对应得20种，再插3个相同休息日得2种'''

def load():
    data=(R/'手写模拟题_100.js').read_text(encoding='utf-8')
    return json.loads(re.search(r'window\.HAND_LADDER_100\s*=\s*(\[.*\]);',data,re.S)[1])

def main():
    new=load(); old=json.loads((R/'hand100_v1_拒收快照.json').read_text(encoding='utf-8'))
    audit=json.loads((R/'手写百题v2数学审计.json').read_text(encoding='utf-8'))
    bankhash=hashlib.sha256((R/'手写模拟题_100.js').read_bytes()).hexdigest()
    assert bankhash==audit['bankSha256']
    # 以Mill实际初审快照做完整字段差异，防止修层级时意外改数字/100题面。
    baseline=json.loads((R/'hand100_v2_Mill初审快照.json').read_text(encoding='utf-8'))
    previous=baseline['records']
    expected_changes={6,10,36,37,38,39,40,52,53,59,60,68,69,77,82,84,85,98,99}
    assert len(previous)==len(new)==100
    assert all(a['uid']==b['uid'] and a['o']==b['o'] and a['a']==b['a'] for a,b in zip(previous,new)), '禁止本次顺带改答案/选项/UID'
    assert previous[99]==new[99], '第100题必须原样保留，镜像重复由主线程处理24库010'
    assert all(previous[51][k]==new[51][k] for k in ('s','o','a','e','tr','signal')), '052本次数值和教学正文不变'
    diffs=[]; level_changes=[]
    for i,(a,b) in enumerate(zip(previous,new),1):
        fields={k:{'before':a.get(k),'after':b.get(k)} for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)}
        if fields: diffs.append({'uid':b['uid'],'id':i,'fields':fields})
        if a['level']!=b['level']:
            level_changes.append({'id':i,'uid':b['uid'],'before':{k:a[k] for k in ('level','t','cost','targetSeconds','difficultyBasis')},'after':{k:b[k] for k in ('level','t','cost','targetSeconds','difficultyBasis')}})
    assert {x['id'] for x in level_changes}==expected_changes
    assert {x['id'] for x in diffs}==expected_changes|{61,72}
    for d in diffs:
        allowed={'level','t','cost','targetSeconds','difficultyBasis'} if d['id'] in expected_changes else ({'s','e','tr','signal'} if d['id']==61 else {'e','tr','signal'})
        assert set(d['fields'])<=allowed, d
    counts=dict(collections.Counter(q['level'] for q in new))
    assert counts=={'入门':29,'熟练':27,'深化':25,'综合':19}
    diff_report={'status':'已执行Mill建议，待其绑定新hash复审，不自批放行',
                 'previousBankSha256':baseline['bankSha256'],'bankSha256':bankhash,
                 'independentReportSha256':hashlib.sha256((R/'手写百题v2独立审计.md').read_bytes()).hexdigest(),
                 'levelCounts':counts,'changedRecords':len(diffs),'levelAdjustments':level_changes,
                 'all100OptionsAndAnswersUnchanged':True,'question100Unchanged':True,'question052MathUnchanged':True,'changes':diffs}
    (R/'手写百题v2_Mill复审差异.json').write_text(json.dumps(diff_report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    patchlines=['# 手写百题v2：落实Mill初审后的差异交接','',
                '> 仅表示作者已执行修订，等待Mill复审；不将初审结果自动延伸为新hash放行。','',
                f'- Mill初审JS：`{baseline["bankSha256"]}`',f'- 本次JS：`{bankhash}`',
                '- 100条记录仍为100题；100道题的UID、4选项及答案下标全部未改。',
                '- 共21条记录变更：19项分层联动，另061和072教学修订。',
                '- 第100题全部字段不变，challenge:010镜像重复由主线程重写24库处理；052数值仍144，本次只降为熟练。','',
                '## 两项教学阻断执行情况','',
                '- **061**：明确各部门所得份数允许相同，只要至少一个有名部门所得改变即算新方案。同步题解、陷阱、识别信号。枚举允许同份数22；错误附加互异为14，已加回归。',
                '- **072**：明确周期4与3互质、12天覆盖完整共同周期，比例法12×3/4×2/3=6合法；保留容斥法对照。陷阱改为只反对无条件推广，增加同相位非互质周期的反例回归。','',
                '## 19项分层及配套元数据','',
                f'- 新层数：{counts}；不补题凑每层25。time字段采用主线程支持的`targetSeconds`。',
                '| UID | 旧层 → 新层 | 卡型 | 成本 | 秒数 | 当前实质依据 |','|---|---|---|---|---|---|']
    for c in level_changes:
        a,b=c['before'],c['after']
        patchlines.append(f'| {c["uid"]} | {a["level"]} → {b["level"]} | {a["t"]} → {b["t"]} | {a["cost"]} → {b["cost"]} | {a["targetSeconds"]} → {b["targetSeconds"]} | {b["difficultyBasis"]} |')
    patchlines+=['','## 文字原值与新值','']
    for d in diffs:
        if d['id'] not in (61,72): continue
        patchlines.append('### '+d['uid'])
        for k,v in d['fields'].items(): patchlines.extend([f'- **{k}旧**：{v["before"]}',f'- **{k}新**：{v["after"]}'])
        patchlines.append('')
    (R/'手写百题v2_Mill复审差异.md').write_text('\n'.join(patchlines)+'\n',encoding='utf-8',newline='\n')
    groups=[]
    for i,line in enumerate(G.splitlines(),1):
        ids,name,criterion=line.split('|')
        groups.append({'code':f'M{i:02d}','name':name,'ids':list(map(int,ids.split(','))),'structure':criterion})
    flat=[n for g in groups for n in g['ids']]
    assert sorted(flat)==list(range(1,101)),set(range(1,101))-set(flat)
    assert len(groups)>=40
    couplings=[]
    for line in C.splitlines():
        i,co,normal,fast=line.split('|')
        couplings.append({'id':int(i),'coupledConstraints':co,'conventionalRisk':normal,'compressedRoute':fast})
    assert [x['id'] for x in couplings]==list(range(76,101))
    for item in couplings: item['level']=new[item['id']-1]['level']
    composite_review=[x for x in couplings if x['level']=='综合']
    deeper_review=[x for x in couplings if x['level']=='深化']
    assert len(composite_review)==19 and len(deeper_review)==6
    structure={'scope':'作者按数学约束归并，待Mill独立复审；不是考生实测难度。','bankSha256':bankhash,
               'records':len(new),'exactUnique':len({q['s'] for q in new}),
               'normalizedDuplicateGroups':len(audit['normalizedDuplicateCandidates']),
               'conservativeModelFamilies':len(groups),'families':groups,'levelCounts':counts,'levelAdjustments':level_changes,'compositeReview':composite_review,'downgradedAdvancedReview':deeper_review,
               'targetSeconds':{'入门':35,'熟练':55,'深化':75,'综合':100}}
    (R/'手写百题v2结构复核.json').write_text(json.dumps(structure,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    lines=['# 手写百题v2：结构去重与梯度作者复核','',
           '> 作者侧教学复核，不冒充Mill独审通过。外部release_manifest.json绑定的独审hash决定放行，题目不自批发布状态。','',
           f'- 冻结JS SHA-256：`{bankhash}`',
           '- 100条记录、100个精确唯一题面；数字归一化后重复题面组0。',
           f'- 将100个细标签保守归并为**{len(groups)}个模型家族**；每题恰归入1组，不把template名称数量直接当数学结构数。',
           '- 例如63/64/88合为前缀路径，74/83/97合为资源整数优化，47/72/94合为工作周期统计。模型粒度是否合适仍交Mill判断。',
           '- 分层依据为识别及约束耦合，而不是数字大小；真实耦合若可压为单一界或短消元，也不必保留最高层。',
           f'- 已落实Mill全部19项建议，当前层数{counts}；详见Mill复审差异表，不维持每阶25题。',
           '- 目标用时35/55/75/100秒均为训练目标，未经考生试测或IRT校准。未执行手机端体验验证。','',
           '| 模型 | 家族 | 题号（v2） | 实质判据 |','|---|---|---|---|']
    for g in groups: lines.append(f'| {g["code"]} | {g["name"]} | '+', '.join(f'{i:03d}' for i in g['ids'])+f' | {g["structure"]} |')
    lines+=['','## 原076—100的逐题结构与当前层级','', '当前保留综合19题、另6题已降深化。下面逐条标注现层级，不把原编号当作现梯度。比较中间量与约束，不虚构实测秒数。','']
    for c in couplings:
        lines += [f'### hand100:v2:{c["id"]:03d}（现{c["level"]}）',f'- 耦合约束：{c["coupledConstraints"]}。',f'- 常规展开或易走弯路：{c["conventionalRisk"]}。',f'- 压缩路线：{c["compressedRoute"]}。','']
    (R/'手写百题v2结构复核.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')

    defects={4:'两个余数的最小正解21，37为负例',6:'相遇时间2',7:'利润10',8:'整除计数13',18:'可能值18',31:'精确平均数286/3',33:'最多7组',34:'4步平衡且非负为2',37:'相遇时间60',40:'有名分组72',42:'面积135/4不得截断',50:'2次至少一成=3/4',60:'3次至少一成=7/8',62:'面积135/4不得截断',70:'2次至少一成=3/4',80:'3次至少一成=7/8',82:'面积135/4不得截断',90:'2次至少一成=3/4',100:'3次至少一成=7/8'}
    changes=['# 手写百题：v1拒收稿到v2逐题变更清单','',
      '> 保留原失败报告，不修改其审计结论。新UID的replacesUid仅对应旧槽位，不表示同一道题换参数；旧成绩不得移到新题。','',
      '- 原报告`手写百题独立审计.md`原样保留。',
      '- `hand100_v1_拒收快照.json`保存重写前100条记录的语义快照；重新排版的JSON不能冒充原JS字节指纹。',
      f'- 冻结新JS SHA-256：`{bankhash}`',
      '- v1仅57个精确题面；v2为100个，旧43条超出首题的重复记录不再保留。',
      '','## v2复核中修复的阻断','',
      '1. **052**：原新稿误标72且正确值缺失；现以调8人使人数差减少16，得到9×16=144。选项改为72/128/144/160，最终D=144。从生成器修复并重新生成。',
      '2. **046**：星期数字1—7的定义移到题面，避免用户作答时无法确认编码；结果仍为2（周二）。题面锁经人工核读后更新。',
      '3. **056审计器**：不能用有限整数长度枚举证明任意实数长度唯一。改为实数域线性方程唯一根，再检两人的路程、位置及各折返一次的条件；题库原值不变。',
      '4. 删除生成器与题目的`published`、`auditStatus`；目标35/55/75/100秒。发布只接受外部release_manifest.json中独审hash，不自批。',
      '5. 审计器从格式检查升级为100个按题面转录的异实现模型；结果不从a/e反推。每题提供expected和全部满足条件的选项集合。',
      '6. **跨平台LF阻断**：生成器JS使用write_bytes，审计及说明输出显式newline=LF；三个Python源文件及条件锁自身均LF。新增make_hand100.py --check严格只读逐字节复现，CRLF/BOM/内容变化均判失败。',
      '7. **Mill初审后的061/072**：061明确允许同份数；072恢复互质完整周期下合法的比例捷径，保留容斥并补推广反例。23项数学回归通过，当前仍等待Mill复审。',
      f'8. **19项层级联动**：含006/010上调，其余17项降阶；level、t、cost、difficultyBasis、targetSeconds按实际层级联动。当前{counts}；逐条旧新值见手写百题v2_Mill复审差异.md/json。',
      '','## 旧报告19个数学阻断的处置','',
      '旧题已经淘汰，不是静默修正答案后仍当原题。最初18项旧错回归仍保留，重复模型共享回归；本轮另加061/072相关5项，共23项。详见数学审计。',
      '| 旧UID | 正确基准/回归 | 处置 |','|---|---|---|']
    for i,msg in sorted(defects.items()): changes.append(f'| hand100:{i:03d} | {msg} | 旧题淘汰，新UID替换，相关模型回归通过 |')
    changes += ['',
      '另保留旧038极值构造；4步均衡非负、5步非负终点不限、5步严格正分别核算2、10、6。独立2/3/4次至少一次全部覆盖。',
      '旧015的正数域、019的倍率措辞、045/065/085端点等有歧义题不沿用；新版逐条写明开闭区间、恒定效率、整日或分数末日、有名分组及放回条件。',
      '','## 100条旧新对应','']
    for i,(o,n) in enumerate(zip(old,new),1):
        oa=o['o'][o['a']] if isinstance(o.get('a'),int) and 0<=o['a']<len(o['o']) else '无数值答案'
        na=n['o'][n['a']]
        reason='逐题明确条件、识别信号、核心题解和陷阱；新UID重新计算'
        if i in defects: reason+='；旧题有确定数学阻断，淘汰'
        if i>=41: reason+='；清理原补齐循环的重复及跨层基础题'
        if i>=76: reason+='；原综合候选的耦合、现层级及路线见结构复核'
        changes += [f'### hand100:{i:03d} → {n["uid"]}',f'- 旧题面：{o["s"]}',f'- 新题面：{n["s"]}',
                    f'- 旧标记答案：{oa}；新精确答案：{na}（{chr(65+n["a"])}，见独立复算唯一性表）。',
                    f'- 层级：{o["level"]} → {n["level"]}；新结构：{n["family"]}。',f'- 原因：{reason}。','']
    (R/'手写百题v2变更清单.md').write_text('\n'.join(changes)+'\n',encoding='utf-8',newline='\n')

    files=['make_hand100.py','手写模拟题_100.js','audit_hand100.py','hand100_conditions_v2.json',
           '手写百题v2数学审计.md','手写百题v2数学审计.json','build_hand100_review.py',
           '手写百题v2结构复核.md','手写百题v2结构复核.json','手写百题v2变更清单.md',
           'hand100_v1_拒收快照.json','手写百题独立审计.md','hand100_v2_Mill初审快照.json','手写百题v2独立审计.md','手写百题v2_Mill复审差异.md','手写百题v2_Mill复审差异.json']
    handoff=['# 给主线程 / Mill 的手写百题v2冻结交接','',
      '> 日期：2026-09-09。作者侧数学复核已完成；**等待Mill独立审计，不表示独审通过**。不创建或修改放行manifest。','',
      '## 请审此LF版本，不要沿用此前CRLF或未修订快照','',f'```text\n教学/速刷/手写模拟题_100.js\nSHA-256: {bankhash}\n```','',
      '- 已包含052正确值144、046题面星期编码说明；本轮未改变052的数值和第100题任何内容。',
      '- 本轮落实Mill：061明确允许同份数，072明确互质且完整周期时可乘比例，全部19项分层建议及关联元数据已执行。',
      f'- 当前层数{counts}；相对Mill初审快照共21条记录变更，100题选项及答案均不变。',
      '- 已删除published/auditStatus，目标用时35/55/75/100秒；signal与targetSeconds保留供主线程normalize使用。',
      '- 新JS、生成器、数学审计器、条件锁及新审计输出均UTF-8/LF。原失败报告只保留，不改其原始换行和结论。主线程维护.gitattributes。',
      '- 冻结后不修改此JS；如果Mill要求修订，必须重新生成、重跑审计、更新hash再交接。',
      '- 无可用的代理间发送工具：本文件与主线程可见的进度消息用于同步，不虚构Mill已经收到或确认。',
      '','## 作者侧完成的检查','',
      f'- 精确expected与选项唯一性：{audit["passed"]}/100；记录100、精确唯一题面100；数字归一化重复组0。',
      f'- 旧错回归：{len(audit["regressions"])}项；故障注入：{len(audit["mutations"])}项。',
      f'- 作者保守结构归并：{len(groups)}类；当前综合19题，原076—100的25题逐条标注现层级和路线。',
      '- 数学结果来自按题面人工转录的公式/枚举，未导入生成器、未用a/e反推。',
      '- 尚待：Mill对本轮新hash的061/072与19项分层联动复审放行；页面与手机体验由主线程集成后验证。',
      '- 未修改页面、GLM文件、主线程原创复合24题；未自行commit/push/部署。',
      '','## 复现','',
      '```powershell\npython -X utf8 教学/速刷/make_hand100.py --check\npython -X utf8 教学/速刷/audit_hand100.py\npython -X utf8 教学/速刷/build_hand100_review.py\nnode --check 教学/速刷/手写模拟题_100.js\n```',
      '','## 文件指纹','', '| 文件 | SHA-256 |','|---|---|']
    for name in files:
        p=R/name; handoff.append(f'| `{name}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |')
    (R/'手写百题v2审计交接.md').write_text('\n'.join(handoff)+'\n',encoding='utf-8',newline='\n')
    print(f'结构家族{len(groups)}；当前层数{counts}；现综合{len(composite_review)}；19项调整、21条记录变更；JS未写入。')

if __name__=='__main__': main()
