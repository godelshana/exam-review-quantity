#!/usr/bin/env python3
"""Second-reviewer checks for the admitted dataset snapshot (stdlib only).

Read-only inputs: datasets/banks.js, summary.json, quarantine.json (D30 only), core.js.
Never imports/runs build_datasets.py, make_certificates.py or their oracles;
never reads certificates.json, mathAudit expressions, or source answers as
solver inputs. All models below were reconstructed from stems by this reviewer.
Only --write-report writes anything, to datasets_independent_review.md.
Exit 0 = reviewed release clean; 1 = stale/missing/model/test failure.
The rejected D30 partition counterexample remains a mandatory negative test.
No automatic baseline refresh: changed stems/methods need renewed human review.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date, datetime
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product, accumulate
import json
from pathlib import Path
import re
import subprocess
import sys

if not __debug__:
    raise SystemExit('INDEPENDENT AUDIT FAILED: assertions disabled; do not use python -O')

ROOT = Path(__file__).resolve().parent
MODELS = {}
ALIASES = {}


def register(uid, proof, conditions='普通考试理想模型；无额外缺失条件。', methods='快法、常规法、边界及陷阱已逐项人工检查，未发现错误。'):
    def wrap(fn):
        MODELS[uid] = dict(solve=fn, proof=proof, conditions=conditions, methods=methods)
        return fn
    return wrap


def unique(values):
    values = set(values)
    if len(values) != 1:
        raise AssertionError(f'expected unique projected result, got {values}')
    return next(iter(values))


def linear(matrix, rhs):
    """Independent exact Gauss-Jordan solver; no expression evaluator."""
    n = len(rhs)
    assert len(matrix) == n and all(len(r) == n for r in matrix)
    a = [[F(v) for v in row] + [F(b)] for row, b in zip(matrix, rhs)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if a[i][col])
        a[col], a[pivot] = a[pivot], a[col]
        f = a[col][col]
        a[col] = [v/f for v in a[col]]
        for i in range(n):
            if i != col:
                f = a[i][col]
                a[i] = [v-f*w for v, w in zip(a[i], a[col])]
    x = [a[i][-1] for i in range(n)]
    assert all(sum(F(c)*v for c, v in zip(row, x)) == b for row, b in zip(matrix, rhs))
    return x


@register('real:2011:合卷:66', '取步速1、跑速2、骑速4（距离单位/小时）。骑行加步行2小时给单程8/5；跑步耗时4/5小时=48分钟。', '同程、各速度恒定；慢50%的参照分别不同。')
def t01():
    distance, = linear([[F(1, 4)+1]], [2])
    return distance / 2 * 60


@register('real:2011:合卷:67', '穷举丙在A的整天数0—16，比较两工程最终工作量；只有6天使两边都为120份。', '丙连续工作16天且只从A转B一次。')
def t02():
    return unique(d for d in range(17) if 16*6+4*d == 16*5+4*(16-d))


@register('real:2011:合卷:69', '穷举去年男性0—830；94m+105(830−m)=83300仅m=350，今年0.94m=329。', '人数取整数；今年而非去年是所问。')
def t03():
    return unique(F(94*m, 100) for m in range(831) if 94*m+105*(830-m) == 83300)


@register('real:2011:合卷:70', '从非原料成本反推：旧总15、新总16；非原料份额下降1/40，K/15−K/16=1/40给K=6。原料9→10，涨1/9。', '默认其他成本和原材料用量不变；否则价格涨幅不唯一。边界已明确成本不变，可补用量不变。')
def t04():
    unchanged, = linear([[F(1, 15)-F(1, 16)]], [F(1, 40)])
    return F(1)/(15-unchanged)


@register('real:2011:合卷:71', '独立按100件计：每件成本100、标价125，前30件收入3750；后70件单价应75，75/125=0.6。', '同质商品或每件定价成本比例与数量份额一致；余货一律同折扣。')
def t05():
    price, = linear([[70]], [9000-30*125])
    return price/125


@register('real:2011:合卷:72', '编码甲女0,1/甲男2,3/乙女4,5/乙男6,7，枚举70个四人子集；至少2女且两科室均有人，得到51个。')
def t06():
    return sum(len(set(c) & {0, 1, 4, 5}) >= 2 and any(i < 4 for i in c) and any(i >= 4 for i in c) for c in combinations(range(8), 4))


@register('real:2011:合卷:76', '将总人数归一为1，联立8A−6B=0、−10B+8C=0、A+B+C=1，人数份额1/4,1/3,5/12；加权年龄35。')
def t07():
    a,b,c = linear([[8,-6,0],[0,-10,8],[1,1,1]], [0,0,1])
    return 38*a+24*b+42*c


@register('real:2011:合卷:79', '9月30天总温855。对n个≥30日，最小可能总温为30n+20(30−n)，故26天不可行；25个30℃加5个21℃达到855且极差9，最大25。', '日平均温度可为实数，不要求整度；构造用于证明可达而非只验选项。')
def t08():
    feasible = []
    for n in range(1, 30):
        low = F(855-30*n, 30-n)
        if 20 <= low < 30:
            assert 30*n+(30-n)*low == 855
            feasible.append(n)
    assert 30*26+20*4 > 855
    return max(feasible)


@register('real:2012:合卷:66', '设去年上半年100份，解两季基数和100且11X=9Y，得45和55；增量4.95+4.95，共9.9%。')
def t09():
    x,y = linear([[1,1],[11,-9]],[100,0])
    return (F(11,100)*x+F(9,100)*y)/100


@register('real:2012:合卷:67', '甲本金10000、乙15000；损失15000中甲承担10000、乙5000，乙净回款10000，甲为0，合计等于实际回款。')
def t10():
    a,b = linear([[1,1],[1,-2]], [15000,0])
    assert 10000-a+15000-b == 10000
    return 15000-b


@register('real:2013:合卷:61', '不依赖选项，行政人数x从1递增：其余六部门容量6(x−1)，能容纳65−x的第一个x为11；11+6×9=65可达。')
def t11():
    return next(x for x in range(1,66) if 0 <= 65-x <= 6*(x-1))


@register('real:2013:合卷:62', '从光线斜率解：人的竖直/水平=2，杆顶到墙上影顶下降14米，再加墙上1米，高15米。', '地面水平、墙及杆竖直、光线平行；题干无依赖缺图标记，文字足以建立标准模型。')
def t12():
    slope,height = linear([[F(9,10),0],[-7,1]],[F(18,10),1])
    return height


@register('real:2013:合卷:65', '逐天现金流：6天售200、4天售175；每天均扣200份成本。合计收入19950、支出9000、净10950。', '过期余货没有残值；损耗成本不能漏扣。')
def t13():
    return sum(F(21,2)*sold - 200*F(9,2) for sold in [200]*6+[175]*4)


@register('real:2013:合卷:66', '实际枚举四项培训的六个无序组合，每组合放4人仍可避免5人同组；容量24，第25人必触发。', '保证出现，不是可能出现；培训对不计顺序。')
def t14():
    buckets = list(combinations(range(4), 2))
    return sum(4 for _ in buckets)+1


@register('real:2014:合卷:61', '以成交价S和本金C为变量，S=1.2C，0.95S−C=7；解C=50（万元）。')
def t15():
    cost,sale = linear([[-F(6,5),1],[-1,F(19,20)]],[0,7])
    return cost


@register('real:2014:合卷:66', '逐一检查原党员0—45：比例差6个百分点仅原18人；调入5、原职工又2人入党，最终25/50=50%。')
def t16():
    initial = unique(p for p in range(46) if F(p+5,50)-F(p,45) == F(6,100))
    return F(initial+7, 50)


@register('real:2015:副省级:61', '穷举男性党员0—30，要求女党员35−m在0—20；最大m=30，女党员5可行，概率3/5。')
def t17():
    return max(F(m,50) for m in range(31) if 0 <= 35-m <= 20)


@register('real:2015:副省级:62', '从甲、乙人数反解：甲/乙=4/3且甲−乙=6，得24/18，总75，丙33，比甲多9。')
def t18():
    a,b = linear([[3,-4],[1,-1]],[0,6])
    n = a/F(32,100)
    return n-a-b-a


@register('real:2018:副省级:61', '逐件累加三段售价倍率，收入520c，400件成本400c；利润15000给c=125。不使用“后两批抵消”作为程序前提。')
def t19():
    revenue = sum([F(8,5)]*200+[F(13,10)]*100+[F(7,10)]*100)
    cost, = linear([[revenue-400]], [15000])
    return cost


@register('real:2019:副省级:61', '枚举去年优x/今年优y均在0—100，y=1.2x且y−x=15，只能75/90。再枚举交集合法范围，最小65，余下去年独优10/今年独优25/均非优0。')
def t20():
    x,y = unique((x,y) for x in range(101) for y in range(101) if 5*y == 6*x and y-x == 15)
    return min(z for z in range(101) if 0 <= x-z and 0 <= y-z and 0 <= 100-x-y+z)


@register('real:2019:副省级:62', '把两种总费用作为变量：T6=0.6p+150，T4=0.4p+150，T6=1.4T4；精确线性消元p=1500。')
def t21():
    p,_,_ = linear([[-F(3,5),1,0],[-F(2,5),0,1],[0,1,-F(7,5)]],[150,150,0])
    return p


@register('real:2021:副省级:61', '枚举6位0/1干货掩码且恰取3，再附主粮二选一；不同内容的集合大小40。', '干货与主粮按题目分作两类独立选择，不考虑摆放顺序。')
def t22():
    contents = {(tuple(i for i,b in enumerate(mask) if b),grain) for mask in product((0,1), repeat=6) if sum(mask)==3 for grain in ('小米','红豆')}
    return len(contents)


@register('real:2021:副省级:62', '联立库存S−6n=12、13S−80n=100，得S=180,n=28；扩80%得324，38户，每户8瓶余20，9瓶则不足。', '按整瓶分配且允许余瓶；最多分8不代表全部均分完。')
def t23():
    stock,n = linear([[1,-6],[13,-80]], [12,100])
    total = stock*F(9,5)
    k = total//(n+10)
    assert k*(n+10) <= total < (k+1)*(n+10)
    return k


@register('real:2022:副省级:61', '同时求原资金M、甲村n、乙村z：M−100n=550；M−120n=−630；M−80n−80z=−2510。解n59、M6450、z53。')
def t24():
    _,_,z = linear([[1,-100,0],[1,-120,0],[1,-80,-80]],[550,-630,-2510])
    return z


@register('real:2023:副省级:61', '设单件原价p、成本c和共同总毛利g；1.6p−2c=g、p−c=g、3p−3c−360=g。三元消元p450,c270,g180，三场景均回代。')
def t25():
    p,_,_ = linear([[F(8,5),-2,-1],[1,-1,-1],[3,-3,-1]],[0,0,360])
    return p


@register('real:2023:副省级:62', '乙用时b满足b−3b/(b+3)=4，即b²−4b−12=0，根6和−2；舍负根。乙效率1/6，丙效率1/4−1/6=1/12，丙12小时。', '二次式全根已列出，非以有限整数搜索替代实数域唯一性；效率相加模型。')
def t26():
    # Rational root factorization proved above; certify both roots and signs.
    roots = (F(6), F(-2))
    assert all(b*b-4*b-12 == 0 for b in roots)
    b = unique(b for b in roots if b > 0)
    assert b - 1/(F(1,3)+1/b) == 4
    return 1/(F(1,4)-1/b)


@register('glm:A:0', '可能人数全集为4k+1，选项区间55—58内构造得到57；55/58/56余数分别3/2/0。', '题目只问选项中可能者，不能宣称题干确定唯一总人数。')
def g01():
    return unique(4*k+1 for k in range(15) if 55 <= 4*k+1 <= 58)


@register('glm:C:50', '穷举鸡0—21，对应兔21−鸡；逐只计腿为64的唯一配对鸡10、兔11。')
def g02():
    return unique(c for c in range(22) if sum([2]*c+[4]*(21-c)) == 64)


@register('glm:C:70', '逐一枚举破损0—150，完好件贡献+5、破损件贡献−16；净687只有破损3。', '“共收运费”按已扣赔偿的净收款理解；建议原创表述改“扣除赔款后净收款687元”以更清楚，现属常见题型惯例。')
def g03():
    return unique(d for d in range(151) if sum([5]*(150-d)+[-16]*d) == 687)


@register('glm:D:0', '勾股平方和225，在正实数域平方函数严格递增；正根15，非只穷举给定选项。')
def g04():
    c = 15
    assert c > 0 and c*c == 9*9+12*12
    return c


@register('glm:D:10', '用两面积S,L作未知量：25S−4L=0、L−S=252；消元S48,L300。')
def g05():
    small,_ = linear([[25,-4],[-1,1]],[0,252])
    return small


@register('glm:D:20', '横截面独立核验：归一高度z，圆锥截面积为底面积×z²，体积系数∫₀¹z²dz=1/3；84/3=28。', '等底等高；体积题无需图；圆锥截面相似适用于直圆锥标准模型。')
def g06():
    # Antiderivative z^3/3 evaluated at endpoints, not certificate expression.
    cone_fraction = F(1,3)-F(0,3)
    return 84*cone_fraction


@register('glm:D:30', '在5×5×5全等小正方体模型中枚举125个坐标，三坐标都不在边界的有27；但题干仅“125等份”，125等体积薄片同样满足而内部块0，字面答案不唯一。', '【阻断】缺“125个全等小正方体/每棱均分5份”条件。题解边界不能补题干。', '两条解法在规则网格前提下正确；前提不由当前题干保证，建议补题干后再放行。')
def g07():
    cube_interior = sum(all(0 < x < 4 for x in xyz) for xyz in product(range(5), repeat=3))
    slab_interior = sum(False for _ in range(125))  # Every slab has painted y/z boundary.
    assert cube_interior == 27 and slab_interior == 0
    return cube_interior


@register('glm:D:50', '用有序编号i<j直接产生不同两人集合15个；没有额外职位区分。')
def g08():
    return len({frozenset((i,j)) for i in range(6) for j in range(6) if i != j})


@register('glm:E:10', '按水而非溶质守恒：总水78g、甲水48g，乙水30g/液40g，水占75%，溶质占25%。', '同一种溶质、质量浓度、混合无损失无反应。')
def g09():
    water = 100*F(78,100)-60*F(80,100)
    return 1-water/40


@register('glm:E:20', '将任务按乙日产1分成16份；同时累计甲乙日产各3/1份，完成时t满足3t+t=16，t4天。')
def g10():
    t, = linear([[3+1]],[16])
    return t


@register('real:2024:副省级:61', '独立采用双单位方程30M−120N=0、20M−30N=30000，解M2400,N600，共3000。')
def v01():
    m,n = linear([[30,-120],[20,-30]],[0,30000])
    return m+n


@register('real:2024:副省级:62', '直接以8年后年龄A,B,C,D为变量：4(A−8)=3(B−8)、5(B−8)=4(C−8)、2A+2B=3C、总172；得32/40/48/52，再15年47/55/63/67，两人>60。', '“再过15年”承接8年之后，不从最初年份起算；题解已说明，建议教学时画时间轴。')
def v02():
    ages = linear([[4,-3,0,0],[0,5,-4,0],[2,2,-3,0],[1,1,1,1]],[8,8,0,172])
    assert ages == [32,40,48,52]
    return sum(a+15 > 60 for a in ages)


@register('real:2024:副省级:63', '令第5天共同产量为1，甲五日产量为1−4m至1；乙为1+8m至1。两总量关系5+20m=2(5−10m)给m=1/8，首日乙2/甲1/2=4倍。', '每日增加/减少意味着m>0，等差模型；只取前5天，所有日产量为正。')
def v03():
    m, = linear([[40]],[5])
    a = [1-i*m for i in (4,3,2,1,0)]
    b = [1+2*i*m for i in (4,3,2,1,0)]
    assert sum(b) == 2*sum(a) and min(a+b) > 0
    return b[0]/a[0]


@register('real:2024:副省级:64', '取甲速度u、乙原速v和路程s；5u=s、5v+90=s、5u=6v，三元消元u108/v90/s540，后段乙120。')
def v04():
    _,_,s = linear([[5,0,-1],[0,5,-1],[5,-6,0]],[0,-90,0])
    return s


@register('real:2024:副省级:70', '直接解调后四数a,b,c,d：4(a+4)=5(b−1)、3(b−1)=4(c−4)、2(c−4)=3(d+1)、5d=3c，得81/69/55/33，差12。')
def v05():
    a,b,c,d = linear([[4,-5,0,0],[0,3,-4,0],[0,0,2,-3],[0,0,-3,5]],[-21,-13,11,0])
    assert (a,b,c,d) == (81,69,55,33)
    return a-b


@register('real:2024:副省级:71', '直接以今年上下支出u,v建模：u+v=1200−(1200−960+172)=788，u/0.8+v/0.85=960，解448/340，差108。')
def v06():
    u,v = linear([[1,1],[F(5,4),F(20,17)]],[788,960])
    return u-v


@register('real:2024:副省级:72', '不依赖捆绑口算：枚举丙0—240和乙0—80，甲2乙，筛总包数240及收入6000，唯一甲100/乙50/丙90。')
def v07():
    return unique(c for c in range(241) for b in range(81) if 3*b+c == 240 and 30*2*b+24*b+20*c == 6000)


@register('real:2024:副省级:74', '互斥区域：俄英法50；俄英不法50；英法不俄50；仅英50；仅法100。俄100半会法，英200半会法，恰两语100/恰一语150均回代，法200。', '俄语集合包含于英语；不需假定学院无人三语皆不会，该区域不影响答案。')
def v08():
    # x=R+E only, y=E+F only, z=E only, w=F only.
    x,y,z,w = linear([[1,0,0,0],[1,1,0,0],[1,-1,1,0],[0,0,1,1]],[50,100,50,150])
    assert x+50 == 100 and z+x+y+50 == 2*(y+50)
    return y+w+50


@register('real:2024:地市级:61', '设收入x亿元，税惠0.02x减原亏损0.008x=0.03亿元净利；解x=2.5。', '题目直接给税惠影响利润，不另引入企业所得税等现实制度。')
def v09():
    income, = linear([[F(2,100)-F(8,1000)]],[F(3,100)])
    return income


@register('real:2025:副省级:66', '按第二趟运量拆原10辆大车与新增15辆小车，取大车载量1，小车s：10+15s=15，s1/3，大/小=3。', '“又增派”表示原10辆大车仍在；默认同型相同载重且同一装载口径，快法边界已给出。')
def v14():
    small, = linear([[15]],[5])
    return 1/small


@register('real:2025:副省级:69', '用四个互斥区域逆建模。总N时A+B−N=交集−空白=2；0.05N=2给N40。枚举交集2—18均可构造，N唯一而分区不唯一。')
def v15():
    n, = linear([[F(60,100)+F(45,100)-1]],[2])
    patterns = [(24-i,18-i,i,i-2) for i in range(2,19)]
    assert all(sum(p)==40 and min(p)>=0 for p in patterns)
    return n


@register('real:2025:副省级:70', '消甲得乙+丙10。正整数且乙>丙，丙仅1—4，逐一取满足甲−乙>乙−丙的最小甲，结果18/15/12/9；最小9见甲乙丙9/6/4。', '默认年龄为正整数周岁。若按实数年龄解释不存在该最小值；考试年龄题惯例、当前边界均说明。')
def v16():
    minima = []
    for c in range(1,5):
        b = 10-c
        a = 2*b-c+1
        assert a>b>c>0 and a-b>b-c and a+b+c==a+10
        minima.append(a)
    return min(minima)


@register('real:2025:副省级:71', '以三台开始时刻a,b,c（小时）直接列12−a=1.5(12−b)、2(c−a)=6、2[(16−a)+(16−b)+(16−c)]=50，解a6,b8,c9。', '开始后连续作业至16时；上午先后开始三时刻6/8/9满足题意。')
def v17():
    a,b,c = linear([[-2,3,0],[-2,0,2],[1,1,1]],[12,6,23])
    assert a < b < c < 12
    return b


@register('real:2025:副省级:72', '独立枚举32个±1序列，对每个前缀而非仅终分筛≥1，6条：+++++、++++−、+++−+、+++−−、++−++、++−+−。', '起始0不属于“答完每道题”检查点；第一题开始才要求≥1。')
def v18():
    good = [seq for seq in product((-1,1), repeat=5) if min(accumulate(seq)) >= 1]
    assert len(good) == 6
    return len(good)


@register('real:2025:副省级:76', '直接生成折后逐日销量50,60,…190共1800；折前800。取标价100，逐日累计折后收入144000，比较折前80000；(1800−800)c=64000得成本64即64%。', '折后第一天已加10件，不能从40起算；单位成本不变。', '初审发现常规法比例方向错误，最终已人工确认改为折前/折后销量800∶1800=4∶9、单件毛利9∶4；当前快法、常规法及64%答案均正确。')
def v19():
    daily = [40+10*d for d in range(1,16)]
    units = sum(daily)
    c, = linear([[units-20*40]],[sum(80*q for q in daily)-100*20*40])
    assert units == 1800 and c == 64
    return c/100


@register('real:2026:副省级:69', '对正整数A,B,C且总54进行全域穷举，20A=13B只有(13,20,21)，C−B=1。', '三个品牌都采购意味着数量为正；即使允许C为0也不改变此题唯一解。')
def v22():
    triples = [(a,b,54-a-b) for a in range(1,54) for b in range(1,54-a) if 20*a == 13*b]
    a,b,c = unique(triples)
    return c-b


@register('real:2026:副省级:73', '把恰含张李一人的每个三人组映射到一个双中组：保留第三人，在其余n−3人中选择另一人，并选择保留张或李；每个恰一组有两个逆像，计数比n−3=30得n33。再实际枚举C(33,3)=5456组，恰一930/双中31，比30。', '等可能不放回选3人；用双计数证明全域唯一，再枚举33人验证而非截断搜索。')
def v23():
    n = 30+3
    counts = Counter(sum(x < 2 for x in group) for group in combinations(range(n),3))
    assert counts[1] == 930 and counts[2] == 31 and counts[1] == 30*counts[2]
    return n


@register('real:2026:副省级:78', '不用证书的手写偏移列表；用Gregorian日历遍历一个400年周期，逐年检查8/10、8/20、9/10、9/20中周一恰2次，所有可行年的9/1均周六，且存在可行年。', '“当年”是题设的未知年，不等于卷名2026年；只依赖8/9月日历，与二月闰平无关。')
def v24():
    weekdays = []
    for y in range(2000,2400):
        if sum(date(y,m,d).weekday()==0 for m,d in ((8,10),(8,20),(9,10),(9,20))) == 2:
            weekdays.append(date(y,9,1).weekday())
    return unique(weekdays)


@register('real:2026:地市级:68', '令单程归一为1，去返时间满足tout/tback=2.5且差3，解5/2小时；总路程2S、总时7，平均40给S140。', '往返同程，无停留，各程速度恒定。')
def v26():
    out,back = linear([[1,-F(5,2)],[1,-1]],[0,3])
    return 40*(out+back)/2


@register('real:2026:地市级:69', '为避免分数销量取原销量4件、降后5件；设同利润P：400−4c=P、450−5c=P，消元c50。', 'm>0且单位成本不随销量变动。')
def v27():
    c,_ = linear([[4,1],[5,1]],[400,450])
    return c


@register('real:2026:地市级:70', '将甲乙原产量作为未知：甲+乙2000；11甲+12乙22600。消元甲1400乙600；逐车间增加140/120合计260。')
def v28():
    a,b = linear([[1,1],[11,12]],[2000,22600])
    assert F(a,10)+F(b,5) == 260
    return a


# Rejected item is NOT part of approved coverage; retain its two constructions.
REJECTED_MODELS = {'glm:D:30': MODELS.pop('glm:D:30')}

ALIASES.update({
    'real:2024:地市级:68': 'real:2024:副省级:74',
    'real:2024:行政执法类:61': 'real:2024:地市级:61',
    'real:2024:行政执法类:62': 'real:2024:副省级:62',
    'real:2024:行政执法类:67': 'real:2024:副省级:74',
    'real:2025:行政执法类:66': 'real:2025:副省级:71',
    'real:2025:行政执法类:72': 'real:2025:副省级:76',
    'real:2026:地市级:66': 'real:2026:副省级:69',
    'real:2026:地市级:71': 'real:2026:副省级:73',
    'real:2026:地市级:74': 'real:2026:副省级:78',
})

# The pins are filled once after this review, never refreshed by the test runner.
REVIEW_FIELDS = ('uid','dataset','sourceType','year','exam','paper','number',
                 's','o','a','h','t','e','tr','level','fastMethod','fastValue',
                 'skipDecision','fastPath','normalPath','fastBoundary',
                 'answerStatus','imageStatus','explanationStatus','validationStatus',
                 'usable','scorable','familyId','leakageRisk')
APPROVED_CONTENT_SHA256 = '1f466364facf6999fa620b6419e5472e9fd8553d484b18bf8f3ec78cebff19bb'  # APPROVED_LF_DIGEST
PINS = {
    "glm:A:0": "d54737832e86fa725dd6f9cbdcf93682c50c96588c42a60db04ece310ee85476",
    "glm:C:50": "dd10c2a7dd190b8f15b2dc40035356a3108087363a652e48f0ba1f28055f782b",
    "glm:C:70": "a81741bfd9e9205f91eec6ffc295ce904b1c8423d5eea04911ac3f984aa46766",
    "glm:D:0": "e92e57794854d913ea4afda3cf6cc2e9d975a37c2fb5fd961ec108026f21a1ea",
    "glm:D:10": "d0da243a8fc02fa499dc719932ae203cfce898956c5f18149ede12301e62fb90",
    "glm:D:20": "3e0dec6de74faf3c01702424076d68613a9d49f0a0858544a5cbcad18614c91d",
    "glm:D:50": "fa491747f4db119a9590ff2c28c07059011598ed190c613f6a705e8ef3b3ee39",
    "glm:E:10": "69290fca6966b852cad3848b9a7423d709cff7b0be1b35bcb74c810d0b6039cc",
    "glm:E:20": "f7370c89a37d4c30f2cdbf771c7c1cc18931a88086f7efc5f14942472bb07011",
    "real:2011:合卷:66": "62e79e6d16f545d515d8f8e008078010cee160929d37aff8a7dcc3cbb6a65601",
    "real:2011:合卷:67": "8858bc785442dae4c61dcd101fcb52fc0d521f29d2808d100153a52b258eb4c9",
    "real:2011:合卷:69": "92f02b31d0a648dbafdbc560b4340fc74bd8a7f0c3b24b1a079c10810985caa5",
    "real:2011:合卷:70": "8a7acd0ae4c7500f3bc90d578050f8459ff66548a2063497148bc23848a181e3",
    "real:2011:合卷:71": "afa6f389698af4a661856aca06121a9e6b29f686b83462985ed355209e29762b",
    "real:2011:合卷:72": "a1a7bc81cefa88485442e84051aa6cf50d17d545d9f49ad4d59222cf8c125fb6",
    "real:2011:合卷:76": "1aba5f94c2d34600e56ced881440057cac4b8166e4934454faa7d69ea51a2bcf",
    "real:2011:合卷:79": "e0996c43c7534ad5099ba226fd4db5cd05cdad20e7b79d410abc05cc009751fd",
    "real:2012:合卷:66": "876b42c8c409072589cbefc2e6697b84b77575645d1a2184f5f8e88c5423e746",
    "real:2012:合卷:67": "76d5c02f89055c28d925b8a1d3f1b7565c51b083aab18ad5e1a3dc5fe9f7f1e1",
    "real:2013:合卷:61": "fe6596bda9e4860c5024f15b52c8c56d6736b60754599bf398b248bf1bf934ab",
    "real:2013:合卷:62": "2db8f99918dbb418fb2e200c1d1e1c6a5ba9420977ca86d28063a1169fade927",
    "real:2013:合卷:65": "6df3d9c9fdf177b183e8177c9ecfbaf291ec1139941396c46b685ef0a7b73ade",
    "real:2013:合卷:66": "cd4beba7b8960617f825a6a3250c8a7f90e1d0c4bb14a4b7543dde80378d49eb",
    "real:2014:合卷:61": "2f33ded9bc740c6d837c80f6541ae74b1740bbed4869d272ccfb7ddee18defff",
    "real:2014:合卷:66": "06b7ddccb5e8ce904f4e311f4c27dc8d08cf63f5b622b89ae0cf67deb7cad229",
    "real:2015:副省级:61": "d2d5722f7dbc623f34702d69db2bac6c66a66f8b031cccae6230970556946715",
    "real:2015:副省级:62": "79fc758ab44e9f5e47fc9fed7abe28bb61db2a6d0394188e55c4c82a048681f1",
    "real:2018:副省级:61": "697bb2a78db72da6ae9b77ecbd6d93cd799b2bcc284ac909c46f69e5c66ce137",
    "real:2019:副省级:61": "8a160eb5b94c970bc799d09711200416d59c0799ff9bcc993f0eddcd91ee9f6a",
    "real:2019:副省级:62": "49654a4503d9546cf624c2a5739c9f4f215c078045c0b552bbbcebadae74f4fa",
    "real:2021:副省级:61": "a393ea589b723c5c64bb8c08474ae4d273d07345047441edbbd206e89046fd7c",
    "real:2021:副省级:62": "7e8391ceb9dd663c368f79f0fbb3dd24ebe4286aed4851aedf07330cb384f87a",
    "real:2022:副省级:61": "0a8939ebc99029ad517fb97050d5b9ed31c28864c0f306d1322f054b76a1480a",
    "real:2023:副省级:61": "6c88551d6c77c2c741bdd69eb2246d3abf3dd618528bed25595ba694864e1dfd",
    "real:2023:副省级:62": "1a227a9cfe10bce3bf57f88691e784f299bb37b91b288c4be5de903fa3e914ff",
    "real:2024:副省级:61": "c8c7726d7d239c0de905d5a862cdaabcbe1dc0a895fa7df016f77e6167d7b0f5",
    "real:2024:副省级:62": "b5f293248fce2dbb7aa88c0c6ae4edada811d9fe1e69fad572b7fd99ed91d321",
    "real:2024:副省级:63": "de2cad6adc6bdcc255e67bd5c292c6714c3cb2e2f1a2531915d559ef4c014c9f",
    "real:2024:副省级:64": "a947ef2b25624ba576253fba1d7556f2e0a2b2c6525b020f1f518c08eeaccddb",
    "real:2024:副省级:70": "932d79ea5dd0b4b1efd4885ff2a22151e84f083f7f80aad14c1d463db9c73151",
    "real:2024:副省级:71": "63f48a61a5caf872db0217ab2d474bf8fd899325517345eff25d4f63626d3e11",
    "real:2024:副省级:72": "f8f16b0aa839534408459ba0e52548d1b7e9e843141014dd76399e6e60a2fa33",
    "real:2024:副省级:74": "1543c6ca3226193e9873ec213c66ed453b379609c0c8aaccbb652aecf573e4b3",
    "real:2024:地市级:61": "acde1d3bdd820c6b9ad2d441d8969a1738b5e3692163330c47b7fc7ceb010073",
    "real:2024:地市级:68": "d6575fcd29770dc6163a084b9a55ddcf6139fa9f0f2ff8adb180ae5cb5736672",
    "real:2024:行政执法类:61": "dcd3c1a07864af4297bbf5c64aae6cec0d53cedd8e75302e0ffe2608906c6b72",
    "real:2024:行政执法类:62": "938a0ef4d12224905932b489a456b8469132633715c5324671a84d75b99d8c40",
    "real:2024:行政执法类:67": "322e5770f9f4fcef3e28a39572ee04f1577ca7ebb582f7216e34eeea91f3a730",
    "real:2025:副省级:66": "2d6a2ce3b09d7923b6678c99ea2d63088f7de52869b14b1428d01d98514d7da9",
    "real:2025:副省级:69": "bc9111367a96a7b37ebc82ffd984d20bfb54fd2a0f7a3132fcb95248d8d4d68e",
    "real:2025:副省级:70": "0d7b7b9275ff0ca8c7be7ab31439e6ccebd53539b07a1337fb83b09bd1516306",
    "real:2025:副省级:71": "140d4bec2a84449ed97f721ec3f4f9ed38198a722473b9a067cb728a3fbb3ea6",
    "real:2025:副省级:72": "67173effadb8809bca49a9d3fc6cc2beb2b24f8c23c315e696bc4746219f8450",
    "real:2025:副省级:76": "f6a070b35f48654401171c1e7947501a34ca6ce006fb7ef33b27b9629397fe7c",
    "real:2025:行政执法类:66": "6b507e04699dabedc19352160ec34db6af71f029d59d0ce3b303916fdd87438b",
    "real:2025:行政执法类:72": "d736dec65b897c0461c861fc10a5a333e4177402b4ff68833243e26e18ced439",
    "real:2026:副省级:69": "1f7a9bf42a1418adcbe9bb87792f8b50fc6fd9b662872a8669396a23d842d2e1",
    "real:2026:副省级:73": "bfa31fac8267ccf18afd3f43c1dd36255794a9bcb9cbe3e1c491c48b3a9a3e3c",
    "real:2026:副省级:78": "0764fbf94fb233a8b1a6c8052f1114a8d26c748772557913af218d556dbfe675",
    "real:2026:地市级:66": "7995a9aa05d14636d6cbed8a119311257e9decbcffb3967d7712854cfa689caf",
    "real:2026:地市级:68": "7f317f4a0e93a8940b6402ea1b80553d18b8ec946f264af88f299dad621342f0",
    "real:2026:地市级:69": "003c3aba498d79465fe09c48a3faaae188a218f3661e2f3be5772351784f8118",
    "real:2026:地市级:70": "fa6120a3e19e8800ad8ca4f232973e0ba4bdb2a1d9e99adfe8499e5486092ce4",
    "real:2026:地市级:71": "65db1a6899046e9b774c8262a2e7e1ae10879649b8dc593ec7b0dbcd697f4ad2",
    "real:2026:地市级:74": "14d49049d8a44ab2d933c743da33d9b980c523567281f45cdca3495271630957",
}  # REVIEWED_SNAPSHOT_PINS


def lf(value):
    if isinstance(value,str):
        return value.replace('\r\n','\n').replace('\r','\n')
    if isinstance(value,list):
        return [lf(v) for v in value]
    if isinstance(value,dict):
        return {k:lf(v) for k,v in value.items()}
    return value


def fingerprint(q):
    payload = lf({k:q.get(k) for k in REVIEW_FIELDS})
    return sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def approved_digest(pins):
    manifest = ''.join(f'{uid}\t{pins[uid]}\n' for uid in sorted(pins))
    return sha256(manifest.encode('utf-8')).hexdigest()


def load_banks():
    raw = (ROOT/'datasets/banks.js').read_bytes()
    text = raw.decode('utf-8-sig')
    decoder = json.JSONDecoder()
    banks = {}
    for name in ('DATASET_TRAIN','DATASET_VALIDATION'):
        start = re.search(r'window\.'+name+r'\s*=\s*',text)
        if not start:
            raise ValueError(f'missing {name}')
        data, end = decoder.raw_decode(text[start.end():])
        assert text[start.end()+end:].lstrip().startswith(';')
        assert isinstance(data,list)
        banks[name] = data
    return banks['DATASET_TRAIN'], banks['DATASET_VALIDATION'], sha256(lf(text).encode('utf-8')).hexdigest()


def option_value(text):
    """Small, explicit Chinese-unit parser written independently of certificates."""
    text = re.sub(r'\s+','',text).replace('：',':')
    discounts = {'九折':F(9,10),'七五折':F(3,4),'六折':F(3,5),'四八折':F(12,25)}
    if text in discounts:
        return discounts[text]
    if text in ('周一','周二','周三','周四','周五','周六','周日'):
        return ('周一','周二','周三','周四','周五','周六','周日').index(text)
    if re.fullmatch(r'\d+:\d{2}',text):
        hour,minute = map(int,text.split(':'))
        assert 0 <= minute < 60
        return hour+F(minute,60)
    if text.endswith('%'):
        return F(text[:-1])/100
    if text.startswith(('多','少')):
        sign = 1 if text[0]=='多' else -1
        return sign*F(re.sub(r'(万元|辆|台|人)$','',text[1:]))
    if text.endswith(('万','千')):
        return F(text[:-1]) * (10000 if text[-1]=='万' else 1000)
    return F(re.sub(r'(分钟|小时|米|元|岁|天|人|辆|台|瓶)$','',text))


def norm(text, numbers=False):
    text = ''.join(c for c in str(text) if c.isalnum())
    return re.sub(r'\d+', '#', text) if numbers else text


def coverage_check(usable):
    by_uid = {q['uid']:q for q in usable}
    assert len(by_uid)==len(usable), 'duplicate UID'
    expected = set(MODELS)|set(ALIASES)
    assert approved_digest(PINS)==APPROVED_CONTENT_SHA256, 'review manifest constant was modified'
    assert set(by_uid)==expected==set(PINS), f'admission coverage changed: new={set(by_uid)-expected}, missing={expected-set(by_uid)}'
    return by_uid


def check_rejected_d30():
    records = json.loads((ROOT/'datasets/quarantine.json').read_text(encoding='utf-8-sig'))
    matches = [q for q in records if q.get('uid')=='glm:D:30']
    assert len(matches)==1, 'D30 quarantine record missing/duplicated'
    q = matches[0]
    assert q.get('usable') is False and q.get('scorable') is False and q.get('a') is None
    assert q.get('admission')=='quarantine'
    assert q.get('mathAudit',{}).get('status')=='failed'
    assert 'nonunique_equal_volume_partition' in q.get('quarantineReasons',[])
    assert q['s']=='棱长为5的正方体表面涂色后切成125等份，没有任何涂色的小块有几块？'


def row_audit(q, by_uid):
    uid = q['uid']
    base = ALIASES.get(uid,uid)
    if base not in MODELS:
        raise ValueError(f'unreviewed admitted uid {uid}')
    if PINS.get(uid) != fingerprint(q):
        raise ValueError(f'stale human-review pin: {uid}; re-review changed wording/options/methods')
    if uid in ALIASES:
        assert lf(q['s']) == lf(by_uid[base]['s']), f'alias stem changed {uid}'
    model = MODELS[base]
    # No question/answer/certificate is passed into the solver.
    result = model['solve']()
    values = [option_value(t) for t in q['o']]
    assert len(values)==4 and len(set(values))==4, f'non-distinct options {uid}'
    matches = [i for i,v in enumerate(values) if v==result]
    assert len(matches)==1, f'nonunique or missing correct option {uid}: {result}, {values}'
    assert q['a']==matches[0], f'wrong bank answer {uid}: expected {matches[0]}, got {q["a"]}'
    assert q.get('usable') is True and q.get('scorable') is True, f'inconsistent admission flags {uid}'
    assert q.get('answerStatus')=='confirmed' and q.get('imageStatus')=='complete', f'incomplete usable question {uid}'
    if q['dataset']=='validation':
        assert q.get('validationStatus')=='V1'
    else:
        assert q.get('year') not in (2024,2025,2026)
    answer = 'ABCD'[matches[0]]
    source_match = q.get('sourceAnswer') == answer
    if not source_match:
        raise ValueError(f'new local-source disagreement: {uid} source={q.get("sourceAnswer")} independently={answer}')
    status = '通过'
    if base=='real:2025:副省级:76':
        assert '1800∶800的反比9∶4' not in q['normalPath']+q['e']
        assert '折前/折后销量比800∶1800=4∶9' in q['normalPath']
        assert '折前/折后单件毛利比9∶4' in q['normalPath']
    return dict(uid=uid,base=base,answer=answer,result=str(result),option=q['o'][matches[0]],
                values=list(map(str,values)),status=status,sourceMatch=source_match,
                proof=model['proof'],conditions=model['conditions'],methods=model['methods'])


def leakage_audit(train, validation):
    """Limited to admitted training and 105 reserved stems; no 945-bank expansion."""
    hits = []
    for t in train:
        for v in validation:
            if not v.get('s'):
                continue
            why = []
            if norm(t['s'])==norm(v['s']):
                why.append('exact_normalized_stem')
            elif norm(t['s'],True)==norm(v['s'],True):
                why.append('same_wording_with_numbers_removed')
            if t.get('familyId') and t.get('familyId')==v.get('familyId'):
                why.append('same_declared_family')
            if why:
                hits.append((t['uid'],v['uid'],why))
    assert not hits, f'train/validation exact or declared-family overlaps: {hits}'
    groups = defaultdict(list)
    for v in validation:
        if v.get('usable'):
            groups[norm(v['s'])].append(v['uid'])
    dupes = [g for g in groups.values() if len(g)>1]
    return dict(hits=hits,duplicates=dupes,uniqueV1=len(groups),comparisons=len(train)*len(validation))


def core_exposure_test(train, validation):
    """Only a leakage regression. Not counted as independent math verification."""
    js = r'''
const fs=require('fs');
const core=require(process.argv[1]);
const [train,validation]=JSON.parse(fs.readFileSync(0,'utf8'));
const good=validation.filter(q=>q.usable);
const key=q=>q.s.replace(/\s+/g,'');
const groups=new Map();
for(const q of good){const k=key(q);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(q);}
const dupeGroups=[...groups.values()].filter(g=>g.length>1);
for(const group of dupeGroups){
 const id=core.validationIdentity(group[0]);
 for(const q of group)if(core.validationIdentity(q)!==id)throw Error('duplicate identity differs '+q.uid);
 const out=core.sample([...train,...validation],{size:1000,mode:'validation',exposures:[id],rng:()=>.5}).questions;
 if(out.some(q=>key(q)===key(group[0])))throw Error('exposed cross-paper duplicate reappears');
}
const all=core.sample([...train,...validation],{size:1000,mode:'validation',rng:()=>.5}).questions;
if(all.length!==groups.size||new Set(all.map(key)).size!==groups.size)throw Error('V1 independent stem count not respected');
const tr=core.sample([...train,...validation],{size:1000,mode:'train',rng:()=>.5}).questions;
if(tr.some(core.isValidation))throw Error('reserved item entered training');
console.log(JSON.stringify({duplicatesProtected:dupeGroups.length,firstUnseenV1:all.length,trainOnlyCount:tr.length}));
'''
    proc = subprocess.run(['node','-e',js,str(ROOT/'core.js')],input=json.dumps([train,validation],ensure_ascii=False),text=True,encoding='utf-8',capture_output=True)
    if proc.returncode:
        raise AssertionError('core leakage regression failed: '+proc.stderr)
    return json.loads(proc.stdout)


def self_tests(by_uid):
    assert linear([[2,1],[1,-1]],[7,2]) == [3,1]
    assert option_value('七五折') == F(3,4)
    assert option_value('少108万元') == -108
    assert option_value('8：00') == 8
    assert option_value('周六') == 5
    assert option_value('1 万') == 10000
    assert option_value('9.9%') == F(99,1000)
    # Mutations use copies in RAM only; never touch datasets or snapshots.
    q = dict(by_uid['glm:D:50'])
    q['a'] = (q['a']+1)%4
    try:
        row_audit(q,by_uid)
    except ValueError as e:
        assert 'stale human-review pin' in str(e)
    else:
        raise AssertionError('wrong answer mutation escaped')
    q = dict(by_uid['glm:D:50'])
    q['s'] += '（变更条件）'
    try:
        row_audit(q,by_uid)
    except ValueError as e:
        assert 'stale human-review pin' in str(e)
    else:
        raise AssertionError('stem mutation escaped')
    q = dict(by_uid['glm:D:50'])
    q['normalPath'] += '错误的新解释'
    try:
        row_audit(q,by_uid)
    except ValueError as e:
        assert 'stale human-review pin' in str(e)
    else:
        raise AssertionError('method mutation escaped')
    q = dict(by_uid['glm:D:50'])
    q['o'] = [q['o'][0]]*4
    try:
        row_audit(q,by_uid)
    except ValueError as e:
        assert 'stale human-review pin' in str(e)
    else:
        raise AssertionError('options mutation escaped')
    for field in ('e','tr','fastPath','fastBoundary'):
        q = dict(by_uid['glm:D:50']); q[field] += '错误注入'
        try:
            row_audit(q,by_uid)
        except ValueError as e:
            assert 'stale human-review pin' in str(e)
        else:
            raise AssertionError(f'{field} mutation escaped')
    assert 'glm:D:30' not in by_uid
    assert REJECTED_MODELS['glm:D:30']['solve']()==27  # Also asserts slabs give 0.
    # Equal-volume slab construction: every box reaches y=0/5 and z=0/5.
    slabs = [(F(i,25),F(i+1,25),F(0),F(5),F(0),F(5)) for i in range(125)]
    volumes = [(x1-x0)*(y1-y0)*(z1-z0) for x0,x1,y0,y1,z0,z1 in slabs]
    assert set(volumes)=={F(1)} and sum(volumes)==125
    assert sum(all((x0>0,x1<5,y0>0,y1<5,z0>0,z1<5)) for x0,x1,y0,y1,z0,z1 in slabs)==0
    # Same contents with CRLF inside every text field must have the same pin.
    def crlf(x):
        if isinstance(x,str): return x.replace('\n','\r\n')
        if isinstance(x,list): return [crlf(v) for v in x]
        if isinstance(x,dict): return {k:crlf(v) for k,v in x.items()}
        return x
    assert all(fingerprint(crlf(q))==fingerprint(q) for q in by_uid.values())
    # Added UID must NOT be implicitly admitted by coverage set comparisons.
    added = dict(by_uid['glm:D:50']); added['uid']='glm:NEW:0'
    try:
        coverage_check(list(by_uid.values())+[added])
    except AssertionError as e:
        assert 'admission coverage changed' in str(e)
    else:
        raise AssertionError('added UID escaped production coverage guard')
    try:
        coverage_check([q for q in by_uid.values() if q['uid']!='glm:D:50'])
    except AssertionError as e:
        assert 'admission coverage changed' in str(e)
    else:
        raise AssertionError('removed UID escaped production coverage guard')
    # Specifically inject the historical method defect into each fixed V1 copy.
    for uid in ('real:2025:副省级:76','real:2025:行政执法类:72'):
        q = dict(by_uid[uid]); q['normalPath']='毛利比1800∶800的反比9∶4'
        try:
            row_audit(q,by_uid)
        except ValueError as e:
            assert 'stale human-review pin' in str(e)
        else:
            raise AssertionError('historical ratio text defect escaped')
    return '精确解算器/单位解析/LF归一通过；错答案、改题干、normalPath/e/tr/fastPath/fastBoundary修改、重复选项及两个历史毛利误文均被拒绝；D30的27块/0块等体积反例通过；新增UID不被放行。'


def render_report(train, validation, rows, bank_hash, leakage, exposure, test_result):
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    sections = [
        '# 当前可用真题 / GLM 数据集独立复审（最终批准版）',
        '',
        f'- 完成时间：{now}（本机北京时间）。',
        f'- 最终批准内容指纹（UTF-8，规范LF）：`{APPROVED_CONTENT_SHA256}`。',
        f'- 本次完整 banks.js 文件指纹（去BOM、规范LF）：`{bank_hash}`。文件指纹仅标记观察快照，实际门禁对下面65题位批准字段逐项锁定；隔离题元数据改动不会冒称放行内容改动。',
        '- 只修改本报告和 `audit_datasets_independent.py`，不修改数据或其他文件，不commit。',
        '- 已发现问题通过本线程和报告即时同步；主代理已明确确认转发数据agent `01a08c8a-ec62-7991-95ac-5149411dfec8`。本侧没有跨代理send工具，未虚报独立送达。',
        '',
        '## 一、最终放行结论',
        '',
        '**批准当前35道训练（26旧真题+9GLM）和30个V1验证题位，共65条记录。** 56个不同题干分别有独立数学模型；9个跨卷重复题位显式逐项核对。不扩展批准到945候选库。',
        '',
        '- 65题位：从题干独立算出的答案均与当前库答案相同；四选项的语义值各不相同，且恰有1项等于所求值；本地来源答案字母亦一致。',
        '- 65题位：当前快法、常规法、边界和陷阱已人工逐项读过；无尚未处理的确定性计算/方法错误。普通考试理想化假设及个别措辞改进建议见下文，不把计算符合等同于自然语言无任何可能歧义。',
        '- **V1的30个题位只有21个不同题干**，独立首次见题迁移统计必须按21题口径去重。另75个V3验证题位不计分、不在本次数学放行范围。',
        '- 门禁实际执行成功，**退出码0**；新增/删除放行UID、题干/选项/答案/解析等批准字段改变、模型结果错误、来源冲突或隔离回归失败均退出1。',
        '',
        '### 初审发现及最终复核闭环',
        '',
        '| 问题 | 最终处置与复核 |',
        '|---|---|',
        '| `glm:D:30`：只写“切成125等份”，不能保证125个全等小正方体；27不是题干唯一推论 | **拒收并隔离，不补题**。已核实不在训练或V1放行集；quarantine中usable=false、scorable=false、a=null、mathAudit.status=failed且理由包含nonunique_equal_volume_partition。独立反例测试仍保留：规则5×5×5得到27个不涂色块；切125个5×5×(5/125)等体积薄片则0个，两者每块体积均1。测试自己重建反例，不读取该条mathAudit的反例结果来求值。 |',
        '| `real:2025:副省级:76`、`real:2025:行政执法类:72`：常规法原写“1800∶800的反比9∶4” | **已修正并重新人工阅读最终内容**：折前/折后销量比800∶1800=4∶9，单件毛利比9∶4；两题normalPath及e同步正确。快法和64%答案原本正确。历史误文作为内存故障注入必须被指纹拒绝。 |',
        '',
        '### 次要措辞与必要模型假设',
        '',
        '- `real:2011:合卷:70` 原料价格涨幅计算默认原料用量与其他成本不变；边界已写其他成本不变，可再明确单位产品原料用量不变。',
        '- `glm:C:70` 按常见破损赔付题惯例，把“共收运费687元”理解为扣除赔偿后的净收款。净收入模型下破损3件唯一；建议未来新版本措辞写“扣除赔款后净收款687元”，若修改需重审指纹。',
        '- `real:2025:副省级:70` 年龄为整数周岁必要；实数年龄不应宣称同样的最小值。当前边界已披露，依年龄题惯例认可9岁。',
        '- `real:2024:副省级:62` 和执法62的“再过15年”承接8年之后。现解析一致，教学用时间轴避免混淆。',
        '- 匀速、恒效率、同成本、独立同等可能选取、水平地面等常见前提逐题注明；不同真实场景不能无条件沿用模型。快法时间收益是教学判断，未做考生群体实测。',
        '',
        '## 二、独立实现与批准指纹规则',
        '',
        '1. 集中抽取题干/选项并自行建立数量关系后，再逐条比较快法、常规法、边界和陷阱；**不读取certificates.json，不导入或运行既有生成器/oracle**。',
        '2. 56个放行模型以精确有理数高斯消元、有限全域枚举、互斥区域、日历400年周期、构造达界等独立实现。求解函数不接收题库对象，故不能以a/sourceAnswer/mathAudit表达式为输入；先算数值再用自写中文单位解析器比较选项。',
        '3. 9个同题跨卷题位复用同一模型，但各自检查题干相同、选项语义唯一、答案匹配及全部批准字段指纹，不伪称9个新数学样本。',
        '4. 程序不能自动理解自然语言方法；方法文本是本次人工审读。指纹保证后续文本变化不会静默继承人审批准。部分常规法提到程序枚举，考场应使用其分类组合表达而非逐一枚举数十个集合。',
        '5. 只核对本地来源答案，不重新访问粉笔/高教/原卷，也不把机构答案叫考试官方答案；来源真实性外部复核不在本次完成声明内。',
        '',
        '**每题批准字段**：',
        '',
        '`'+', '.join(REVIEW_FIELDS)+'`',
        '',
        '**规范化算法**：递归把字段内字符串CRLF/CR换为LF；按字段名排序，用UTF-8无BOM、ensure_ascii=False、separators=(",",":")序列化JSON并SHA-256。65个UID按Python字符串升序排列，将每行写成UID + TAB + 每题SHA256 + LF，再SHA-256得到上方总批准指纹。数组顺序保留，所以选项调序也触发重审。',
        '',
        'PINS及总批准常量均固定在脚本中，运行时不自动刷新。新增UID、缺少UID或内容变动直接失败；没有自动批准/重新绑定参数。LF/CRLF平台换行差异不影响批准指纹。整个banks文件的规范LF快照hash另列，不用未审元数据替代批准字段。',
        '',
        '## 三、泄漏与首次曝光审查',
        '',
        f'- 当前35训练×105保留验证题位，共{leakage["comparisons"]}次比较，未命中规范化完全同题、文字相同仅换数字、相同现有familyId。75个V3的题干仅作隔离比对，不算完成数学审查。',
        '- 人工检查相近模型：三场景同利润与近期折价增量利润都使用毛利守恒，但未知量和销量条件不同；基础圆锥圆柱体积与倒锥注水共享1/3知识，后者额外需要液面高度立方和分段注水；一般工程/比例同理。未发现直接换数换名模板泄漏的确定实例；基础知识的正常迁移不应一概拒收。不能仅凭familyId不同证明语义零泄漏。',
        '- 30个V1中跨卷重复组如下；正式新题正确率不应把同一题记多次：',
        '',
    ]
    sections.extend('- '+' ↔ '.join('`'+uid+'`' for uid in group) for group in leakage['duplicates'])
    sections += [
        '',
        f'- 独立数学审查以外，另只读运行core隔离回归：`{json.dumps(exposure,ensure_ascii=False)}`。每组跨卷同题曝光后其他题位不再作为未见题返回，一次抽完只有21个不同V1题干；训练模式无保留验证题。当前未发现此重复曝光漏洞。',
        '- 隔离是正常UI/本地学习记录的口径，不是保密承诺。banks.js、审计报告包含答案，清除存储、跨设备、以前看过旧题库或外部APP也无法保证真实未见。**本报告给维护代理使用，考生正式摸底前不要阅读V1解答**。',
        '- 广东近三年资料缺口未解决，无法承诺对未知广东真题零泄漏。未重新数学审查其余隔离训练候选或原创124题。',
        '',
        '## 四、65题位逐题批准记录',
        '',
        '下列每题均完成题干解算、全部选项比较和人工方法审读。百分数独立值按比例表示，星期一编码0，时刻编码小时；答案展示仍用原选项文字。',
    ]
    for idx,r in enumerate(rows,1):
        sections += [
            '',
            f'### {idx:02d}. `{r["uid"]}` — 通过',
            f'- **答案：{r["answer"]}（{r["option"]}）**；独立值 `{r["result"]}`；A/B/C/D语义值 `{r["values"]}`，恰1项匹配且本地来源字母一致。',
            '- 独立推导：'+r['proof'],
            '- 题面与边界：'+r['conditions'],
            '- 方法审查：'+r['methods'],
            '- 批准字段SHA-256（规范LF）：`'+PINS[r['uid']]+'`。',
        ]
        if r['uid'] in ALIASES:
            sections.append('- 跨卷重复：与 `'+r['base']+'` 同题，已单独核对本题位，不作为新题样本。')
    rejected = [q for q in validation if not q.get('usable')]
    sections += [
        '',
        '## 五、拒收题及未审清单',
        '',
        '- `glm:D:30`：本次已独立审查并拒收。反例见第一节；不在65放行UID/批准hash中，不补写题干，不允许以后悄悄恢复放行。',
        f'- 下列{len(rejected)}个V3题位：只检查保留/不可计分状态和题干泄漏匹配，**未完成数学审查**。',
        '',
    ]
    sections.extend('- `'+q['uid']+'` — '+str(q.get('validationStatus'))+'；未审数学。' for q in rejected)
    sections += [
        '',
        '- 全库945候选的其他条目、原始PDF图像、外部来源真实性、原创124题均不在本次数学批准范围。隔离训练805条中只有D30是本次独立给出拒收反例，其余不外推。',
        '',
        '## 六、发布门禁与测试',
        '',
        '```powershell',
        '# CI / build_site：只读，成功退出0；任何新增/变化/失败退出1',
        'python 教学/速刷/audit_datasets_independent.py',
        '# 维护侧需要重生成本报告时（只写本Markdown）',
        'python 教学/速刷/audit_datasets_independent.py --write-report',
        '```',
        '',
        '- 运行要求：Python 3.10+标准库与Node.js（Node只用于core隔离回归，不参与数学求解）。禁止-O：断言被禁用时脚本主动失败。',
        '- 本次实际成功：56个放行模型、65个题位、35训练、30 V1、21个V1独立题干；全部选项与本地来源答案一致。',
        '- '+test_result,
        '- 105验证槽位完整读取；75个未放行必须usable=false、scorable=false、a=null；summary数量一致；只定点核对quarantine里的D30隔离状态，不执行其中的数学表达式或反例值。',
        '- 默认只读；--write-report只改指定Markdown。测试副本全在内存，没有临时数据文件、没有pycache输出。',
        '',
        '## 七、维护交接',
        '',
        '最终批准的是本报告指纹所绑定的65题位，不是所有未来版本。新增题、改题、改解析应由独立审查者重新推导并审阅，再人工修改模型/指纹/总批准hash；不可让数据生成器自动更新本脚本的批准常量。主代理可将默认命令接入CI/build_site，当前退出0，无遗留阻断。',
    ]
    return '\n'.join(sections)+'\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-report',action='store_true',help='Write only the designated independent review markdown')
    args = ap.parse_args()
    try:
        train,validation,bank_hash = load_banks()
        usable = train+[q for q in validation if q.get('usable')]
        by_uid = coverage_check(usable)
        check_rejected_d30()
        assert len(validation)==105
        for q in validation:
            assert q['dataset']=='validation' and q['year'] in (2024,2025,2026)
            if not q.get('usable'):
                assert q.get('scorable') is False and q['a'] is None
        summary = json.loads((ROOT/'datasets/summary.json').read_text(encoding='utf-8-sig'))
        assert summary['train']['total']==len(train)
        assert summary['validation']['scorable']==sum(q.get('scorable') is True for q in validation)
        assert summary['validation']['withStem']==sum(bool(q.get('s')) for q in validation)
        rows = [row_audit(q,by_uid) for q in usable]
        assert approved_digest({uid:fingerprint(q) for uid,q in by_uid.items()})==APPROVED_CONTENT_SHA256
        tests = self_tests(by_uid)
        leakage = leakage_audit(train,validation)
        exposure = core_exposure_test(train,validation)
        report = render_report(train,validation,rows,bank_hash,leakage,exposure,tests)
        if args.write_report:
            (ROOT/'datasets_independent_review.md').write_text(report,encoding='utf-8')
        print(json.dumps(dict(bankSHA256_LF=bank_hash,approvedContentSHA256_LF=APPROVED_CONTENT_SHA256,reviewedSlots=len(rows),independentModels=len(MODELS),
                              status=dict(Counter(r['status'] for r in rows)),independentV1Stems=leakage['uniqueV1'],
                              leakageComparisons=leakage['comparisons'],coreRegression=exposure,
                              selfTests=tests,reportWritten=args.write_report),ensure_ascii=False,indent=2))
        return 0
    except Exception as exc:
        print(f'INDEPENDENT AUDIT FAILED: {type(exc).__name__}: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
