# -*- coding: utf-8 -*-
"""逐题数学审计：不导入make_hand100，不读取a/e推导expected。

所有常数及假设从题面人工转录到CASES；Fraction保证精确运算。
有限计数直接枚举；优化题穷举可行域或同时证明下界和构造。
conditions锁文件绑定题面指纹，修改题面后拒绝沿用旧算式。
运行：python -X utf8 教学/速刷/audit_hand100.py
说明：这是同一编题代理的异实现复算，不冒充另一个审计员的放行。
"""
from __future__ import annotations
import argparse, collections, hashlib, itertools as it, json, math, re, sys
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Callable
ROOT=Path(__file__).resolve().parent
BANK=ROOT/'手写模拟题_100.js'
LOCK=ROOT/'hand100_conditions_v2.json'
REVIEW_LEVELS={6:'熟练',10:'熟练',36:'入门',37:'入门',38:'入门',39:'入门',40:'入门',52:'熟练',53:'熟练',59:'熟练',60:'入门',68:'熟练',69:'熟练',77:'深化',82:'深化',84:'深化',85:'深化',98:'深化',99:'深化'}
REVIEW_META={'入门':('钩子','低',35),'熟练':('转化钩','中',55),'深化':('二步钩','中',75),'综合':('综合建模','高',100)}

def expected_level(i):
    return REVIEW_LEVELS.get(i,('入门','熟练','深化','综合')[(i-1)//25])


@dataclass(frozen=True)
class Case:
    conditions: str
    method: str
    solve: Callable[[], object]

CASES: dict[int,Case]={}
def case(i, conditions, method, fn):
    if i in CASES: raise ValueError(f'duplicate case {i}')
    CASES[i]=Case(conditions,method,fn)

def only(xs):
    s=set(xs)
    if len(s)!=1: raise ValueError(f'模型没有唯一结果: {sorted(s)}')
    return next(iter(s))

def cross(a,b):
    if F(a)!=F(b): raise ValueError(f'异算法不一致: {a} != {b}')
    return F(a)

def solve2(a,b,c,d,e,f):
    det=a*e-b*d
    if not det: raise ValueError('singular equations')
    return F(c*e-b*f,det), F(a*f-c*d,det)

def prefixes(xs):
    return tuple(it.accumulate(xs))

def path_enum(n, floor=0, end=None, midpoint=None):
    return sum(all(x>=floor for x in prefixes(s)) and
               (end is None or sum(s)==end) and
               (midpoint is None or sum(s[:midpoint[0]])==midpoint[1])
               for s in it.product((-1,1),repeat=n))

def path_dp(n, floor=0, end=None, midpoint=None):
    state={0:1}
    for step in range(1,n+1):
        nxt=collections.Counter()
        for balance,count in state.items():
            for shift in (-1,1):
                new=balance+shift
                if new>=floor and (midpoint is None or step!=midpoint[0] or new==midpoint[1]):
                    nxt[new]+=count
        state=nxt
    return state.get(end,0) if end is not None else sum(state.values())

def probability(universe, event, condition=lambda x:True):
    den=[x for x in universe if condition(x)]
    if not den: raise ValueError('条件样本空间为空')
    return F(sum(bool(event(x)) for x in den),len(den))

def sqrt_exact(x):
    v=F(x); a=math.isqrt(v.numerator); b=math.isqrt(v.denominator)
    if a*a!=v.numerator or b*b!=v.denominator: raise ValueError('非有理平方根')
    return F(a,b)

case(1,'原8人均76，增加1人后9人均78；总分可加。','两个总分相减',lambda:9*78-8*76)
case(2,'两队总96，原3:5；乙调6给甲。','比例份数后定量转移',lambda:F(96*3,8)+6)
case(3,'件数固定、单价加2元、总价加120元。','变化量方程',lambda:F(120,2))
case(4,'人数n为正整数且75<n<85，实操占精确3/8且人数整数。','范围内逐个检验整除',lambda:only(n for n in range(76,85) if 3*n%8==0))
case(5,'两人独做12、18天，效率恒定相加，合作3天，求未完成比例。','有理数工作量',lambda:1-3*(F(1,12)+F(1,18)))
case(6,'三对合工期12、15、20天，各效率恒定相加，求三人全做工期。','成对效率和除2',lambda:2/(F(1,12)+F(1,15)+F(1,20)))
case(7,'同一路线等距离往返，不停留，速度60、40。','总路程/总时间',lambda:F(2)/(F(1,60)+F(1,40)))
case(8,'环长400，同点同时反向，匀速3和5，首次再会。','一圈/速度和',lambda:F(400,3+5))
case(9,'5红4蓝，不放回，保证至少一红。','枚举所有取球顺序的首红最坏位置',lambda:max(next(i+1 for i,c in enumerate(p) if c=='R') for p in set(it.permutations('RRRRRBBBB'))))
case(10,'26人，各组互异正整数，求最大组数。','最小序列下界及余量并入末组',lambda:max(k for k in range(1,27) if k*(k+1)//2<=26))
case(11,'6个不同人选无序2人，索引0和1禁止同选。','枚举2子集',lambda:sum(not {0,1}.issubset(s) for s in map(set,it.combinations(range(6),2))))
case(12,'5个不同人全排列，0和1相邻，内部次序不限。','枚举120个排列',lambda:sum(abs(p.index(0)-p.index(1))==1 for p in it.permutations(range(5))))
case(13,'3红2蓝，5个球各有唯一索引，等可能不放回选2球。','枚举10个等可能子集',lambda:probability(it.combinations(range(5),2),lambda s:all(x<3 for x in s)))
case(14,'甲成功3/5，乙成功1/2，独立，求至少一个成功。','5×2等可能微样本直接枚举',lambda:probability(it.product(range(5),range(2)),lambda s:s[0]<3 or s[1]<1))
case(15,'三角形两边中点，共角小三角形面积9。','面积行列式缩放',lambda:F(9)/(F(1,2)*F(1,2)))
case(16,'矩形周长40，长宽为正实数，最大面积。','平方非负证明乘积上界并取等号',lambda:F(40,4)**2)
case(17,'31天，首日周五，求周日个数。','逐日取模',lambda:sum((4+d)%7==6 for d in range(31)))
case(18,'第1天共同检查，日期差周期4、6，求下一共同日期编号。','正天数逐日检验',lambda:min(d for d in range(2,30) if (d-1)%4==(d-1)%6==0))
case(19,'成本80，按成本加价25%，再按定价九折，求利润元。','精确倍率相乘减成本',lambda:80*F(5,4)*F(9,10)-80)
case(20,'单价乘4/5，总收入不变，求次数增幅的百分数数值。','反比例倍率',lambda:(1/F(4,5)-1)*100)
case(21,'两人今年总54，6年前甲2倍乙，每年各+1，求年龄差。','统一到6年前的总量再比例分解',lambda:F(54-2*6,3))
case(22,'10千克20%盐水，加5千克水，无损失，求质量分数。','溶质/最终总质量',lambda:F(10)*F(1,5)/15)
case(23,'全集60，A38，B32，两项都不参加10，求交集。','集合恒等式',lambda:38+32-(60-10))
case(24,'等差7项总140，公差3，求末项。','首末均值关系',lambda:F(140,7)+3*3)
case(25,'整数数量40<n<70，n%6=5且n%8=5。','完整范围枚举所有解',lambda:only(n for n in range(41,70) if n%6==5 and n%8==5))
case(26,'原四部门共240，甲=丁+12；乙转24给丙后全并丁，最终甲丙丁3:3:4。','反推未变部门和总量',lambda:F(240*4,10)-(F(240*3,10)-12)+24)
case(27,'20人均80，剔除2人后18人均81，求剔除者均分。','总分差除被剔人数',lambda:F(20*80-18*81,2))
case(28,'两类票全价40优惠25，共30张总990，求全价整数张数。','全可行张数枚举',lambda:only(x for x in range(31) if 40*x+25*(30-x)==990))
case(29,'100件成本各50，80件售价60、20件售价45，无附费，求总利润。','逐批收入减总成本',lambda:80*60+20*45-100*50)
case(30,'恒定效率独做12、18天，合作3天后乙退出，求自开始总工期。','分段工作守恒',lambda:3+(1-3*(F(1,12)+F(1,18)))/F(1,12))
case(31,'AB合6天，AC合8天，BC合12天，恒定可加，求B工期。','解三人线性效率',lambda:2/(F(1,6)+F(1,12)-F(1,8)))
case(32,'进水6小时满，排水12小时空，空池同开4小时再仅进水，流量恒定。','净流量再切换',lambda:4+(1-4*(F(1,6)-F(1,12)))/F(1,6))
case(33,'初始乙领先300，乙速4先走20秒，甲速6才启，求甲启动后追上用时。','在甲启动时统一位置',lambda:F(300+4*20,6-4))
case(34,'静水船速恒定，水速3，同河段顺3小时逆5小时。','解3(v+3)=5(v-3)',lambda:solve2(3,-1,-9,5,-1,15)[1])
case(35,'前段50后段75，全程150，耗时5/2，无停留，求慢段距离。','一元时间方程',lambda:(F(5,2)-F(150,75))/(F(1,50)-F(1,75)))
case(36,'95箱，每车至多8箱，一趟可不满载，求最少整数车数。','枚举容量阈值',lambda:min(n for n in range(96) if n*8>=95))
case(37,'5项各为0..90整数，总410，无互异要求，求第5项最小。','其余4项最大占用且构造可行',lambda:max(0,410-4*90))
case(38,'5人选两个有名岗位不兼任，0不能第一个岗位。','枚举有序不同人',lambda:sum(a!=0 for a,b in it.permutations(range(5),2)))
case(39,'3男3女中选3人恰2女，选人无顺序。','枚举三人子集',lambda:sum(sum(x>=3 for x in s)==2 for s in it.combinations(range(6),3)))
case(40,'数字1..4选两个不同者形成两位偶数。','枚举两位整数',lambda:sum((10*a+b)%2==0 for a,b in it.permutations(range(1,5),2)))
case(41,'4红3蓝，等可能不放回抽2；条件至少1红，事件全红。','先过滤条件再数事件',lambda:probability(it.combinations(range(7),2),lambda s:all(x<4 for x in s),lambda s:any(x<4 for x in s)))
case(42,'两个独立公平六面骰，条件点数不同，事件和8；有序样本。','枚举36有序对',lambda:probability(it.product(range(1,7),repeat=2),lambda s:sum(s)==8,lambda s:s[0]!=s[1]))
case(43,'矩形12×8，内部四边含四角统一宽1，求步道面积。','外矩形减内矩形',lambda:12*8-(12-2)*(8-2))
case(44,'圆柱等高，半径大:小=2:1；同恒定体积流量，小满需9分钟。','体积比映射时间比',lambda:9*2**2)
case(45,'ABC面积96，AD:DB=1:2，AE:EC=1:3，求ADE面积。','共角双边比乘积',lambda:96*F(1,3)*F(1,4))
case(46,'30天月份，周一和周二各5次，求月末星期编号1..7。','遍历7种月初并要求结果唯一',lambda:only((s+29)%7+1 for s in range(7) if sum((s+d)%7==0 for d in range(30))==5 and sum((s+d)%7==1 for d in range(30))==5))
case(47,'工作2休1，统计开始为工作首日，前17天每工作日10件。','逐日模拟循环',lambda:10*sum(d%3<2 for d in range(17)))
case(48,'固定成本300，单位成本20售价35，整数接待人数，利润严格正。','搜索严格利润阈值',lambda:min(n for n in range(100) if 35*n-20*n-300>0))
case(49,'100千克20%盐水加水至16%，无损失，求所加水量。','溶质守恒精确有理数',lambda:100*F(1,5)/F(4,25)-100)
case(50,'整数n>50，n%5=2且n%7=3，求最小。','穷举至一个完整35天余类区间',lambda:min(n for n in range(51,86) if n%5==2 and n%7==3))

def oracle51():
    na=only(n for n in range(11,50) if n*82+(50-n)*76==50*F('79.6'))
    nb=50-na
    return F(nb*76+10*80,nb+10)
case(51,'两组共50，均82/76，总均79.6精确；甲调10人均80给乙，求乙新均。','枚举初始人数再转移真实总分',oracle51)
case(52,'原5:4，从甲转8到乙后相等；人数整数，求总数。','独立枚举比例份数',lambda:only(9*k for k in range(1,100) if 5*k-8==4*k+8))
case(53,'100件成本40，先20件各卖60，余80件同整数价，总利润≥1200。','全整数候选价搜索最小',lambda:min(p for p in range(101) if 20*60+80*p-100*40>=1200))
case(54,'甲20天乙30天，合作3天，乙退后甲效率乘3/2，求总工期。','分阶段精确速率',lambda:3+(1-3*(F(1,20)+F(1,30)))/(F(1,20)*F(3,2)))

def oracle55():
    done=F(0); t=F(0)
    while done<1:
        rate=F(1,12) if int(t)%2==0 else F(1,18)
        span=min(F(1),(1-done)/rate)
        done+=rate*span; t+=span
    return t
case(55,'甲12乙18天效率恒定，每人交替1天甲先，可部分末日，求总工期。','逐日推进直到剩余量不足一天',oracle55)

def oracle56():
    # 首次相遇时间单位化为1，则甲速度150；第二次共走3倍全路程。
    # 各折返一次时，甲距B=3*150-L=100。此线性方程在实数域唯一，
    # 不能仅枚举整数长度就声称题目连续长度域唯一。
    L=F(3*150-100)
    da,db=F(450),3*(L-150)
    if not (L<da<2*L and L<db<2*L and 2*L-da==db-L and L-(2*L-da)==100):
        raise ValueError('长度不满足两人折返次数/位置/会面条件')
    return L

case(56,'直线两端同时相向，端点折返，首遇距A150，再遇距B100且各折返一次。','实数域线性方程唯一根，再核两人路程与折返位置',oracle56)
case(57,'600环道同点同向5/3，60秒后慢者立即反向，求转向后首次会面。','解相对位置模600，正根最小',lambda:min(F(600*k-(5-3)*60,5+3) for k in range(1,4) if 600*k>(5-3)*60))
case(58,'420直路，甲60先出发，乙80晚1小时相向，求甲出发至会面。','总路程时间方程',lambda:F(420+80,60+80))
case(59,'50人5组互异，每组≥3，最大组尽可能大。','其他四组最小占用并验构造',lambda:50-sum(range(3,7)))
case(60,'4色各10个，不放回，保证某色至少3个。','禁止目标时最大抽屉容量+1',lambda:sum(min(10,3-1) for _ in range(4))+1)
case(61,'12相同物资分3有名部门，各≥2，甲≤5；各部门份数允许相同，至少一部门数量变化才视为不同方案。','穷举有序三元组',lambda:sum(a+b+c==12 for a,b,c in it.product(range(2,13),repeat=3) if a<=5))
case(62,'7人选4，0/1恰选1，2/3不同时选。','枚举35个4人子集',lambda:sum(len(set(s)&{0,1})==1 and not {2,3}.issubset(s) for s in it.combinations(range(7),4)))
case(63,'6步±1，从0出发各3步，每个前缀≥0。','全64条路径和DP交叉',lambda:cross(path_enum(6,end=0),path_dp(6,end=0)))
case(64,'5步±1，从0出发，每步后严格>0，终点不限。','全32条路径和严格边界DP交叉',lambda:cross(path_enum(5,floor=1),path_dp(5,floor=1)))
case(65,'5红3蓝，等可能不放回取3，事件红球数≥2。','枚举56个3球子集',lambda:probability(it.combinations(range(8),3),lambda s:sum(x<5 for x in s)>=2))
case(66,'等可能选2红1蓝或1红3蓝盒，盒内等可能选1；条件红，求来源甲。','12公分母的先验加权并归一化',lambda:F(1,2)*F(2,3)/(F(1,2)*F(2,3)+F(1,2)*F(1,4)))

def oracle67():
    # A=(0,0),B=(1,0),C=(0,1),D=(1/2,0),E=(0,1/3)
    x,y=solve2(1,3,1,2,1,1)
    small=F(1,2)*F(1,2)*y; whole=F(1,2)
    return 80*small/whole
case(67,'ABC面积80，D为AB中点，AE:EC=1:2，P=BE∩CD，求BDP面积。','归一化坐标解线性方程与面积行列式',oracle67)
case(68,'边长6立方体沿面平行切2厚和4厚两块，无损，求两块表面积和。','分别直接计算两个长方体表面',lambda:2*(6*6+6*2+6*2)+2*(6*6+6*4+6*4))
case(69,'圆柱r3h8无损熔铸圆锥r2h6，求完整个数。','两体积有理系数相除，π约掉',lambda:math.floor(F(3**2*8)/(F(1,3)*2**2*6)))
case(70,'31日，周一二三天数总和15，求首周五日期。','遍历月初星期及日历',lambda:only(next(d+1 for d in range(7) if (s+d)%7==4) for s in range(7) if sum((s+d)%7 in {0,1,2} for d in range(31))==15))
case(71,'检查周期6和8，首日1，要求同检且同星期，求下个日期。','枚举同余交集',lambda:min(d for d in range(2,1000) if (d-1)%6==(d-1)%8==(d-1)%7==0))
case(72,'甲3工作1休息，乙2工作1休息，同从首个工作日开始，统计12日交集；周期4和3互质，12为完整共同周期。','逐日模拟与互质完整周期的比例法交叉',lambda:cross(sum(d%4<3 and d%3<2 for d in range(12)),12*F(3,4)*F(2,3)))
case(73,'成本20，价50销量100；整数降k次每次2元销量+20，0≤k≤10，求最大利润。','枚举全部11个允许价格档',lambda:max((50-2*k-20)*(100+20*k) for k in range(11)))
case(74,'大8箱500，小5箱350，41箱一趟可不满，非负整数车辆不限，求最小成本。','完整非支配辆数组合枚举',lambda:min(500*a+350*b for a in range(7) for b in range(10) if 8*a+5*b>=41))
case(75,'初100kg浓度1/5；取混合物20补水20，再取混合物20补浓度2/5溶液20，求百分数。','逐次精确更新溶质量与总质量',lambda:((100*F(1,5))*F(4,5)*F(4,5)+20*F(2,5)))

def oracle76():
    n=only(n for n in range(4,101) if 80*n+10*92==86*(n+10))
    return F(3*n*90-10*92,3*n-10)
case(76,'人数比1:2:3，甲均80丙均90，丙转10人均92给甲后甲均86，求丙新均。','枚举人数尺度，独立转移丙总分',oracle76)

def oracle77():
    out=[]
    for a in range(4,180,4):
        for b in range(1,180-a):
            c=180-a-b
            if (b+a//4)%7: continue
            transfer=(b+a//4)//7
            final=(a*3//4,b+a//4-transfer,c+transfer)
            if final[1]==2*final[0] and final[2]==3*final[0]: out.append(b)
    return only(out)
case(77,'原三队180，先甲1/4给乙，后按新乙的1/7给丙，最终1:2:3，各转移人数整数。','枚举原人数再正向执行两次调动',oracle77)
case(78,'两阶段各36，阶段一甲3乙2/天、阶段二甲3/2乙3/天；甲t0乙t2，之后合作，无切换延迟可部分天。','按事件时刻计算两个阶段的完成时刻',lambda:2+F(36-2*3,3+2)+F(36)/(F(3,2)+3))

def oracle79():
    # 总量下界以及不同时加工同一任务的可达排程，两者均验证。
    T=F(24+20,6+4); swap=(24-4*T)/(6-4)
    if not (0<=swap<=T and 6*swap+4*(T-swap)==24 and 4*swap+6*(T-swap)==20):
        raise ValueError('容量下界无法用合法换机计划达到')
    return T
case(79,'任务24/20，机器6/4每小时，同任务禁并机，随时可抢占换机、无损。','总容量下界+双任务互换排程的精确验证',oracle79)

def oracle80():
    plans=[]
    for w in (20,26,28):
        choices=[]
        for a in range(math.ceil(F(w,6))+1):
            b=max(0,math.ceil(F(w-6*a,4)))
            choices.append((a,b))
        plans.append(choices)
    best=min(max(sum(p[0] for p in allocation),sum(p[1] for p in allocation)) for allocation in it.product(*plans))
    if best<math.ceil(F(74,10)): raise ValueError('违反总容量下界')
    return best
case(80,'三任务20/26/28，甲6乙4每整日，每组一天一任务可次日换，允许两组同任务且余力不转用。','穷举各任务整数甲日数、补足最少乙日数，求最短共同工期',oracle80)
case(81,'600环道，初位0/0/300，速度6/4/3同向，求首次三人同点的正时间。','甲乙重合时间300k上验证甲丙位置同余',lambda:min(F(600*k,6-4) for k in range(1,4) if ((6-3)*F(600*k,6-4)-300)%600==0))
case(82,'往返速60/40，停1/2小时，总≤4小时，耗油去0.10回0.08L/km，总油14.4L，求最大单程。','两个线性预算上界的交集',lambda:min((4-F(1,2))/(F(1,60)+F(1,40)),F('14.4')/(F('0.10')+F('0.08'))))
case(83,'A料2时3利70，B料3时2利80，料≤30时≤29，非负整数件数。','穷举整个有限整数可行域',lambda:max(70*a+80*b for a in range(16) for b in range(11) if 2*a+3*b<=30 and 3*a+2*b<=29))

def subset_sums(nums,max_count):
    dp=[set() for _ in range(max_count+1)]; dp[0].add(0)
    for x in nums:
        for k in range(max_count,0,-1): dp[k].update(s+x for s in dp[k-1])
    return dp

def oracle84():
    above=subset_sums(range(91,101),5); below=subset_sums(range(90),5)
    ranks=[k+1 for k in range(6) if any(550-90-s in below[5-k] for s in above[k])]
    return max(ranks)
case(84,'6个互异0..100整数总550，其中90分；按降序求90的最大名次数值。','有界子集和DP，分高于90和低于90分别计人数总分',oracle84)
case(85,'4组互异正整数共30，最大恰为最小2倍，求最小组最大值。','枚举所有递增四元组',lambda:max(s[0] for s in it.combinations(range(1,31),4) if sum(s)==30 and s[-1]==2*s[0]))

def oracle86():
    count=0
    for first in map(set,it.combinations(range(7),3)):
        if 0 not in first: continue
        for second in map(set,it.combinations(set(range(7))-first,2)):
            third=set(range(7))-first-second
            if all(not {1,2}.issubset(g) for g in (first,second,third)): count+=1
    return count
case(86,'7人分有名3天人数3/2/2，甲0在首日，乙1丙2不同日，组内无序。','逐组枚举有名划分',oracle86)
case(87,'6人全排列，甲0在乙1之前，丙2丁3不邻，戊4不在端点。','720排列直接筛三条件',lambda:sum(p.index(0)<p.index(1) and abs(p.index(2)-p.index(3))>1 and p.index(4) not in (0,5) for p in it.permutations(range(6))))
case(88,'8步±1各4，从0非负，第四步后余额2，末0。','256路径与带中途约束DP交叉',lambda:cross(path_enum(8,end=0,midpoint=(4,2)),path_dp(8,end=0,midpoint=(4,2))))
case(89,'卡1..6等可能不放回选3，条件至少一偶；事件最大5且和偶。','全20个子集按条件与事件筛选',lambda:probability(it.combinations(range(1,7),3),lambda s:max(s)==5 and sum(s)%2==0,lambda s:any(x%2==0 for x in s)))

def oracle90():
    # 两盒各4球，盒等概率，所以盒标识+有序双球为24个等可能原子。
    samples=[(box,a,b) for box in (0,1) for a,b in it.permutations(range(4),2)]
    isred=lambda box,ball:ball<(2 if box==0 else 3)
    return probability(samples,lambda s:isred(s[0],s[2]),lambda s:isred(s[0],s[1]))
case(90,'等概率选2红2蓝或3红1蓝盒，连续不放回取2；条件首红，事件次红。','枚举带盒标签的24个等可能有序样本',oracle90)

def oracle91():
    # 归一化公共底面积1；锥总V=3，1分钟到1/3高度的V=1/9。
    base=F(1); cone=base*9/3; flow=cone*F(3,9)**3
    total=flow*81
    return 9+(total-cone)/base
case(91,'倒锥高9，上圆柱同半径，恒体积流量；第1分钟水高3，总81分钟满，求总高。','底面积单位化、锥相似体积与柱体积守恒',oracle91)
case(92,'直角三角形高落斜边分9/16，过半高平行斜边截去含直角顶点小三角形，求余梯形周长。','射影关系求两腰、相似比1/2计算4边',lambda:25+F(25,2)+(sqrt_exact(25*9)+sqrt_exact(25*16))/2)

def oracle93():
    volume=F(10**3)*(1-F(84,100)); side=sqrt_exact(volume/10)
    return 6*10**2-2*side**2+4*side*10
case(93,'边10立方体正方形直孔垂直贯通，剩体积84%，孔侧面平行原侧面，求含孔壁总表面。','体积损失求孔边，再外面减孔口加内壁',oracle93)
case(94,'30天第1天周一，同时为工作3休1首工作日；仅工作日且周一到周五办理。','逐日交叉日历模拟',lambda:sum(d%4<3 and d%7<5 for d in range(30)))

def oracle95():
    def actual(d):
        weekday=(d-1)%7
        return d+(7-weekday if weekday>=5 else 0)
    schedules=[{actual(d) for d in range(1,254,period)} for period in (4,7,9)]
    return min(set.intersection(*schedules)-{1})
case(95,'第1天周一，原始日程周期4/7/9从1开始，周六日顺延到下一周一且不重置周期，求下次三者实际同日。','分别生成原计划与顺延日期，再取交集最小正后继',oracle95)
case(96,'成本30初价70需求100，降价次数整数0..10，每次降3需求+20，要求需求全满足且供应≤160。','先过滤产能再枚举利润',lambda:max((70-3*k-30)*(100+20*k) for k in range(11) if 100+20*k<=160))
case(97,'小包7件100、大包11件150，整数包数，总件数在闭区间80..83，最小费用。','全包数组合枚举',lambda:min(100*a+150*b for a in range(12) for b in range(8) if 80<=7*a+11*b<=83))

def oracle98():
    candidate=only(y for y in range(101) for x in range(101) if x+y+40==100 and 2*x+3*y+40==60+55+50)
    # 同时检查指定各集合边际人数可真实构造，不能仅满足总参与次数。
    feasible=False
    for ab in range(101):
        for ac in range(101-ab):
            bc=100-40-candidate-ab-ac
            singles=(60-candidate-ab-ac,55-candidate-ab-bc,50-candidate-ac-bc)
            if bc>=0 and min(singles)>=0 and sum(singles)==40: feasible=True
    if not feasible: raise ValueError('边际人数无法实现')
    return candidate
case(98,'100人并集，3集合人数60/55/50，恰一项40，求三项交集且边际须可实现。','参与次数分层整数方程+三集合Venn区域可行性枚举',oracle98)

def oracle99():
    first,d=solve2(3,3,1800,6,15,4500)
    return sum(first+(month-1)*d for month in range(7,13))
case(99,'月经费等差递增，前三月1800前六月4500，求第7..12月和。','精确解首项公差，再逐目标月份求和',oracle99)

def oracle100():
    schedules=[]
    for a in range(7):
        for b in range(6):
            A=set(range(a,a+2)); B=set(range(b,b+3))
            if A&B: continue
            rest=sorted(set(range(8))-A-B)
            schedules.append(rest)
    return probability(schedules,lambda rest:all(y-x>1 for x,y in zip(rest,rest[1:])))
case(100,'8天甲连续2乙连续3不重叠，其余3休，等可能原日程，事件休息日不相邻。','直接枚举两课程原日程起点，不用捆绑公式',oracle100)


def read_bank(path=BANK):
    text=path.read_text(encoding='utf-8-sig')
    match=re.search(r'window\.HAND_LADDER_100\s*=\s*(\[.*\]);\s*$',text,re.S)
    if not match: raise ValueError('未找到严格JSON数据数组')
    return json.loads(match.group(1))

def digest(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()
def fstr(x):
    v=F(x)
    return str(v.numerator) if v.denominator==1 else f'{v.numerator}/{v.denominator}'

def regression_tests():
    tests={
      '061允许同份数':(sum(a+b+c==12 for a,b,c in it.product(range(2,13),repeat=3) if a<=5),F(22)),
      '061错误附加互异条件的反例':(sum(a+b+c==12 and len({a,b,c})==3 for a,b,c in it.product(range(2,13),repeat=3) if a<=5),F(14)),
      '072互质完整窗口比例法':(cross(sum(d%4<3 and d%3<2 for d in range(12)),12*F(3,4)*F(2,3)),F(6)),
      '072非互质同相位反例实际共同工作':(sum(d%2<1 and d%2<1 for d in range(2)),F(1)),
      '072非互质反例不可当答案的乘积':(2*F(1,2)*F(1,2),F(1,2)),
      '旧004余数最小正解':(min(n for n in range(1,100) if n%8==5 and n%11==10),F(21)),
      '旧004的37负例':(37%11,F(4)),
      '旧006相遇':(F(180,50+40),F(2)),
      '旧007折扣利润':(80*F(5,4)*F(9,10)-80,F(10)),
      '旧008整除计数':(sum(n%3==0 and n%5!=0 for n in range(1,51)),F(13)),
      '旧018余数选项':(only(n for n in (18,24,31,36) if n%7==4),F(18)),
      '旧031精确均值不得近似':(F(10*86-7*82,3),F(286,3)),
      '旧033互异组数':(max(k for k in range(31) if k*(k+1)//2<=30),F(7)),
      '旧034四步均衡非负':(cross(path_enum(4,end=0),path_dp(4,end=0)),F(2)),
      '五步非负终点不限':(cross(path_enum(5),path_dp(5)),F(10)),
      '五步严格正终点不限':(cross(path_enum(5,floor=1),path_dp(5,floor=1)),F(6)),
      '旧037环道':(F(600,4+6),F(60)),
      '旧038最小最大数及构造':(min(max(s) for s in it.combinations(range(1,11),5) if sum(s)==35),F(9)),
      '旧040有名三组禁甲乙同组':(len({tuple(tuple(sorted(p[i:i+2])) for i in (0,2,4)) for p in it.permutations(range(6)) if p.index(0)//2!=p.index(1)//2}),F(72)),
      '旧042062082面积不能整除截断':(15*F(3,2)**2,F(135,4)),
    }
    for n in (2,3,4):
        tests[f'独立{n}次至少一次']=(probability(it.product((0,1),repeat=n),any),1-F(1,2)**n)
    for name,(actual,expected) in tests.items():
        if F(actual)!=F(expected): raise ValueError(f'回归失败{name}: {actual}!={expected}')
    return [{'name':k,'expected':fstr(e),'actual':fstr(a),'pass':True} for k,(a,e) in tests.items()]


def audit(bank, locks):
    rows=[]; errors=[]
    ids=[q.get('uid') for q in bank]
    if len(bank)!=100: errors.append(f'记录数非100: {len(bank)}')
    if len(set(ids))!=len(ids): errors.append('UID重复')
    if len({q.get('s') for q in bank})!=len(bank): errors.append('精确题面重复')
    # 数字归一化只作结构疑似重复检测，不把family标签数量当独立结构数。
    normalized=collections.defaultdict(list)
    for q in bank:
        normalized[re.sub(r'\d+(?:\.\d+)?','<数>',q.get('s',''))].append(q.get('uid'))
    for uid in (f'hand100:v2:{i:03d}' for i in range(1,101)):
        found=[q for q in bank if q.get('uid')==uid]
        if len(found)!=1: errors.append(f'{uid}: 缺失或重复'); continue
        q=found[0]; i=int(uid.rsplit(':',1)[1]); c=CASES[i]
        issues=[]
        lock=locks.get(uid,{})
        if lock.get('stemSha256')!=digest(q['s']): issues.append('题面与人工转录锁不一致，必须重读条件并更新模型/锁')
        if lock.get('conditions')!=c.conditions: issues.append('人工转录条件与锁不一致')
        expected=None; matches=[]; actual=None
        try:
            # 严格在读选项/答案之前复算，解析从不参与计算。
            expected=F(c.solve())
        except Exception as exc: issues.append(f'求解器失败: {exc}')
        opts=q.get('o',[])
        if len(opts)!=4: issues.append('非4选项')
        try:
            values=[F(x) for x in opts]
            if len(set(values))!=4: issues.append('数值等价的重复选项')
            matches=[j for j,v in enumerate(values) if v==expected]
        except Exception as exc: issues.append(f'非精确数值选项: {exc}'); values=[]
        if len(matches)!=1: issues.append(f'正确值匹配{len(matches)}个选项')
        a=q.get('a')
        if isinstance(a,bool) or not isinstance(a,int) or not 0<=a<4: issues.append('答案下标非法')
        elif len(values)==4:
            actual=values[a]
            if actual!=expected: issues.append('标记答案与独立计算不同')
        for field in ('s','e','tr','signal','family','level'):
            if not isinstance(q.get(field),str) or not q[field].strip(): issues.append(f'缺少{field}')
        if re.search(r'需校正|需校验|选项需|故应选|故选[A-D]|\{[a-zA-Z_]+\}',q.get('e','')): issues.append('解析含编辑残留/固定选项字母')
        lv=expected_level(i)
        if q.get('level')!=lv: issues.append('层级未落实Mill逐题建议（不以原编号分段凑25题）')
        for field,expected_meta in zip(('t','cost','targetSeconds'),REVIEW_META[lv]):
            if q.get(field)!=expected_meta: issues.append(f'{field}与当前层级不一致')
        if not q.get('difficultyBasis','').strip(): issues.append('缺少分层依据')
        if i in REVIEW_LEVELS and ('本题：' not in q.get('difficultyBasis','') or len(q['difficultyBasis'])<25):
            issues.append('调整层级但未提供该题的实质分层依据')
        if 'published' in q or 'auditStatus' in q: issues.append('题目不得自批发布状态，应由外部release_manifest绑定独审hash')
        if q.get('sourceType')!='mock': issues.append('原创模拟题来源标记不是mock')
        if q.get('replacesUid')!=f'hand100:{i:03d}': issues.append('旧新UID映射错误')
        rows.append({'uid':uid,'conditions':c.conditions,'method':c.method,
                     'stemSha256':digest(q['s']),'expected':fstr(expected) if expected is not None else None,
                     'level':q.get('level'),'t':q.get('t'),'cost':q.get('cost'),'targetSeconds':q.get('targetSeconds'),'difficultyBasis':q.get('difficultyBasis'),'options':opts,'markedIndex':a,'markedValue':fstr(actual) if actual is not None else None,
                     'satisfyingOptionIndices':matches,'satisfyingOptions':[chr(65+j) for j in matches],
                     'uniqueOption':len(matches)==1,'pass':not issues,'issues':issues})
        errors.extend(f'{uid}: {x}' for x in issues)
    return rows, errors, [v for v in normalized.values() if len(v)>1]


def mutation_tests(bank, locks):
    # 验证器必须能抓错，不仅能接受当前答案；不落盘修改题库。
    import copy
    results=[]
    for name, change, must_error in [
        ('改错答案下标',lambda q:q.update(a=(q['a']+1)%4),True),
        ('移除正确值',lambda q:q['o'].__setitem__(q['a'],'999999'),True),
        ('替换题面数字',lambda q:q.update(s=q['s'].replace('76','77')),True),
        ('伪造解析不影响expected',lambda q:q.update(e='测试：忽略所有条件，声称结果为999999。'),False),
    ]:
        altered=copy.deepcopy(bank); change(altered[0])
        # 只执行第一题的逻辑使用完整入口；expected仍出自CASES。
        rows,errors,_=audit(altered,locks)
        first=next(x for x in rows if x['uid']=='hand100:v2:001')
        if bool(first['issues'])!=must_error or first['expected']!='94':
            raise ValueError(f'变异测试失败: {name}')
        results.append({'name':name,'pass':True,'expectedStill':'94','caught':bool(first['issues'])})
    return results


def write_reports(rows,errors,dup,regressions,mutations):
    bank=read_bank()
    result={'scope':'作者异实现数学复算，不等于独立审计员放行；未运行页面',
            'bankSha256':hashlib.sha256(BANK.read_bytes()).hexdigest(),
            'solverSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'count':len(bank),'levelCounts':dict(collections.Counter(q['level'] for q in bank)),'exactUniqueStems':len({x['s'] for x in bank}),
            'passed':sum(r['pass'] for r in rows),'errors':errors,
            'normalizedDuplicateCandidates':dup,'regressions':regressions,'mutations':mutations,'rows':rows}
    (ROOT/'手写百题v2数学审计.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    text=['# 手写百题v2：100条精确expected及选项唯一性表','',
          '> 同一编题代理的异实现复算：条件在求解器中人工转录，不导入生成器，不读取答案或解析求expected。数值通过不代表独立审计员已批准发布。','',
          f'- 题库 SHA-256：`{result["bankSha256"]}`',
          f'- 求解器 SHA-256：`{result["solverSha256"]}`',
          f'- 记录 {len(bank)}；精确唯一题面 {result["exactUniqueStems"]}；数学/选项通过 {result["passed"]}/100。',
          f'- 旧错回归 {len(regressions)} 项；故障注入 {len(mutations)} 项。',
          '- 每个选项按精确有理数解释；没有“接近就算对”，也不把整数除法用于面积截断。',
          '- 格式审计不读取解析来证明正确性；解析文字、实质结构和梯度另需教学复审。','',
          '| UID | 精确expected | 满足条件的选项集合 | 标记值 | 选项唯一 | 核对 |',
          '|---|---:|---|---:|---|---|']
    for r in rows:
        text.append(f'| {r["uid"]} | {r["expected"]} | '+', '.join(f'{chr(65+j)}={r["options"][j]}' for j in r['satisfyingOptionIndices'])+f' | {r["markedValue"]} | {"是" if r["uniqueOption"] else "否"} | {"通过" if r["pass"] else "; ".join(r["issues"])} |')
    text+=['','## 条件转录与复算路径','']
    for r in rows: text+= [f'### {r["uid"]}',f'- 条件：{r["conditions"]}',f'- 复算：{r["method"]}。得到 `{r["expected"]}`。','']
    text+=['## 旧错回归','']
    text += [f'- {r["name"]}：`{r["actual"]}`，通过。' for r in regressions]
    text+=['','## 故障注入','']+[f'- {r["name"]}：通过（是否检出问题：{r["caught"]}；第一题expected仍为{r["expectedStill"]}）。' for r in mutations]
    if errors: text+=['','## 阻断问题','']+['- '+e for e in errors]
    (ROOT/'手写百题v2数学审计.md').write_text('\n'.join(text)+'\n',encoding='utf-8',newline='\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-mutations',action='store_true',help='临时诊断时跳过故障注入；最终验收不可跳过')
    args=parser.parse_args()
    if set(CASES)!=set(range(1,101)): raise SystemExit('每题必须有独立求解器')
    locks=json.loads(LOCK.read_text(encoding='utf-8'))
    bank=read_bank()
    rows,errors,dup=audit(bank,locks)
    for path in (BANK,Path(__file__),ROOT/'make_hand100.py',LOCK):
        if b'\r' in path.read_bytes():
            errors.append(f'{path.name}: 含CR/CRLF，违反跨平台hash的LF约定')
    reg=regression_tests()
    mutations=[] if args.no_mutations else mutation_tests(bank,locks)
    result=write_reports(rows,errors,dup,reg,mutations)
    print(f'100题逐题复算：通过{result["passed"]}，错误{len(errors)}；精确唯一{result["exactUniqueStems"]}；数字归一化疑似重复组{len(dup)}')
    print(f'旧错回归{len(reg)}；故障注入{len(mutations)}；详情见手写百题v2数学审计.md/json')
    for e in errors: print('ERROR',e)
    return 1 if errors else 0
if __name__=='__main__': sys.exit(main())
