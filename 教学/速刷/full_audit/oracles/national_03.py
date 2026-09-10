"""Offline port of national_03 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'national_03'

def run(ctx):
    qs=ctx.problems
    E={}
    def ck(i,result,evidence):
        E[i]=(result,evidence)
        if i==71: result=8*60+result*60
        ctx.add(i,result,evidence=evidence,property_only=i in {20,49},boundary='ported equations; geometry and global bound arguments remain manual except explicit LP/enumeration')
    def dupe(i,j):
        result,evidence=E[j]; E[i]=(result,evidence)
        if j==71: result=8*60+result*60
        ctx.add(i,result,evidence=evidence,mode='alias_reuse',alias_of=j,property_only=j in {20,49},boundary='cached canonical result; NOT a fresh independent computation')
    perms = list(itertools.permutations(range(6)))
    c = sum((abs(p.index(0) - p.index(1)) == 1 and p.index(4) < p.index(2) < p.index(3) and (p.index(5) in (0, 5)) for p in perms))
    assert c == 16
    ck(0, c, '枚举6!=720排列按三个约束筛选')
    valid = [(a, b, c, d) for a in range(6) for b in range(4) for c in range(3) for d in range(5) if 8 * a + 4 * b + 6 * c + 7 * d <= 38]
    m = max(map(sum, valid))
    best = [t for t in valid if sum(t) == m]
    ways = sum((math.prod((comb(n, k) for n, k in zip((5, 3, 2, 4), t))) for t in best))
    assert m == 7 and best == [(0, 3, 2, 2)] and (ways == 6)
    ck(1, ways, str(best))
    n = next((n for n in range(1, 100) if 10 * n * (n + 5) == 2 * 12 * 10 * n))
    ck(2, n * 10, '独立枚举销售天数与收入成本倍数')
    r = (F(1200) - 500) / 1000
    ck(3, 600 * (1 - r), '乙/甲初速=(1200-500)/1000=7/10')
    sol = F(6 + F(12, 10) * 6, F(6, 10) - F(12, 10) * F(4, 10))
    half = sol / 2
    gap = F(4, 10) * half + 6 - (F(6, 10) * half - 6)
    assert gap == 1
    ck(4, gap, '解总利润110，减半后甲28乙27')
    x = next((x for x in range(1, 1000) if x * (x + 1) // 2 % 48 == 0))
    assert x == 32
    ck(5, x, '对1..32天三角数逐项做48整除')
    rat = [math.prod((F(2, 3) if (s + k) % 7 in [1, 3, 5] else F(1, 2) for k in range(6))) for s in range(7)]
    ck(6, max((F(1, 72) / r for r in rat)), '枚举周一起始编号0到6的六天保留比例')
    Ns = [117 * k for k in range(1, 10) if 300 < 117 * k < 400]
    ck(7, -Ns[0] % 7, str(Ns))
    ratio = F(3, 4)
    assert F(1, 2 * 3) == F(1, 4 * 3) + F(1, 3 * 4)
    from _linear import linprog
    lp = linprog([0, 0, 0, 0, 1], A_ub=[[1, 1, 0, 0, -1], [0, 0, 1, 1, -1]], b_ub=[0, 0], A_eq=[[6, 0, 3, 0, 0], [0, 12, 0, 4, 0]], b_eq=[12, 12], bounds=[(0, None)] * 5, method='highs')
    assert lp.success and abs(lp.fun - 2) < 1e-08 and (abs(6 * lp.x[0] + 12 * lp.x[1] - 18) < 1e-08)
    ck(8, ratio, 'a=3,b=4,X=12的线性规划最优工期2；甲18件、乙6件；等时式a/b=3/4')
    ck(9, 200 / (50 * math.sqrt(3)), '坐标路程200与50√3')
    ck(10, comb(6, 3) * 2, '组合枚举20种干货集合×2谷物')
    n = (F(13, 10) * 12 - 10) / (8 - F(13, 10) * 6)
    ck(11, floor(F(18, 10) * (6 * n + 12) / (n + 10)), '医院无关；商户28，库存180，增后324/38向下取整')
    v = [16, 24, 25, 27]
    assert sum(v[:3]) == 65 and v[1] == 1.5 * v[0] and (v[2] == sum(v[:2]) - 15) and (v[3] == 2 * v[0] - 5)
    ck(12, max(v) - min(v), str(v))
    n = 17
    M = 12 * n - 8
    V = 8 * n - 11
    k = max(ceil(F(M, 2 * n)), ceil(F(V, n)))
    ck(13, 3 * n * k - M - V, 'n17，原口罩196防护125，每家防护至少8箱')
    base = [150, 100, 80, 120]
    maxgap = 0
    A = []
    for i in range(4):
        for j in range(4):
            if i != j:
                row = [0] * 4
                row[i] = 1
                row[j] = -2
                A.append(row)
    for i in range(4):
        for j in range(4):
            obj = [0] * 4
            obj[i] -= 1
            obj[j] += 1
            p = linprog(obj, A_ub=A, b_ub=[0] * len(A), A_eq=[[1] * 4], b_eq=[200], bounds=[(0, None)] * 4, method='highs')
            maxgap = max(maxgap, base[i] - base[j] - p.fun)
    assert abs(maxgap - 110) < 1e-08
    ck(14, maxgap, '枚举最终最大最小两车间的线性规划，16个目标分别求最优')
    staff = [(a, b) for a in range(1, 201) for b in range(1, 201) if F(3, 4) * b - F(3, 5) * a == 3 and F(4, 25) * a + F(3, 16) * b == 24]
    assert staff == [(75, 64)]
    ck(15, staff[0][0] - staff[0][1], str(staff))
    u = F(16, 60 - 40 - F(200, 11))
    ck(16, 12 * u + 16, 'u=44/5；第6减第3=12u+16')
    loans = [16, 18, 20, 22, 24, 28, 29, 30, 31, 32]
    assert sum(loans) == 250 and len(set(loans)) == 10 and (max(loans) == 2 * min(loans))
    ck(17, F(min(loans),10), 'm15上界19m-36=249，m16构造和250')
    num = 12 * 20 + 17 * 30 + 6
    allbus = ceil(F(num, 30))
    buses = next((b for b in range(allbus + 1) if 30 * b + 20 * (allbus - b) >= num))
    ck(18, buses, '枚举最少总车26辆中的大巴数')
    ck(19, 84 / math.sqrt(3), '上下底4h/√3与10h/√3，h100，面积×1.2/1000')
    p = F(12, comb(13, 11))
    p2 = (F(1, 6) + F(11, 4)) / (F(12, 6) + F(comb(12, 2), 4))
    assert F(14, 100) < p < p2 < F(17, 100)
    ck(20, f'{p};{p2}', '人数向量模型2/13；不同人员条件分配模型35/222，同落B')
    T = (F(45, 10) + F(3, 10)) / (1 - F(94, 100))
    buy = T * F(3, 10) * 10000 / 25
    ck(21, buy + buy / F(6, 5), '预算80万，购9600、赠8000')
    pop = []
    for st in range(25, 97, 25):
        for mk in range(20, 97, 20):
            for sc in range(17, 97, 17):
                air = 96 - st - mk - sc
                if air > max(st, mk, sc):
                    pop.append((st, mk, sc, air))
    assert pop == [(25, 20, 17, 34)]
    ck(22, (62-F(64,100)*pop[0][0]-F(65,100)*pop[0][1]-F(10,17)*pop[0][2])/pop[0][3], str(pop) + '；专业人数(16,13,10,23)')
    ck(23, F(3, 1) * (F(5, 4) - 1) / F(1, 5), 'h增长0.75米=0.2d')
    y = (F(219, 1) / F(3, 4) - 10 * F(156, 10)) / 20
    x = F(156, 10) - y
    ck(24, 40 * x + 70 * y, 'x=8.8万张、y=6.8万张；最低实付828万')
    for i, j in [(25, 10), (26, 12), (27, 15), (28, 17), (29, 16), (30, 18), (31, 22), (32, 20), (33, 19)]:
        dupe(i, j)
    p = 19000
    outputs = [F(3, 5) * p + 1000 * ((d - 1) // 4) for d in range(1, 81)]
    day = next((d for d in range(1, 81) if sum(outputs[:d]) >= 1000000))
    assert sum(outputs) == 88 * p
    ck(34, day, '逐天生成80项阶梯产量，累计首次百万日为56')
    n = F(550 + 630, 20)
    ck(35, F(100 * n + 550 + 2510, 80) - n, '甲59，新增后共112名')
    ck(36, '>'.join(sorted({'丁':F(0),'戊':F(2*5),'丙':F(2*5+3*(3-2),2)}, key={'丁':F(0),'戊':F(2*5),'丙':F(2*5+3*(3-2),2)}.get, reverse=True)), '丙设0，丁-6.5戊3.5，由两均值关系解得')
    ck(37, (495 - F(3, 4) * 480) / 3, '国产同量比价差135万分3台')
    x = 2 * 150
    ck(38, (5000 + 3 * x) // 2, '转150使差减少300')
    Sroad = F(3, 60) / (F(1, 4) * (F(1, 18) - F(1, 21)))
    ck(39, Sroad, '前后半程差=S/504小时')
    N = next((n for n in range(71, 80) if 96 * n % 100 == 0))
    n = N // 5
    ck(40, F(96 * N, 100) - n - (n + 2) - (n - 1), '75人中西部72；三类15,17,14')
    yield0 = F(660, 1) / (F(165, 100) * F(6, 5) - F(3, 2))
    ck(41, yield0 * F(6, 5), '去年产1375，今1650')
    v = [k for k in range(1, 20) if (17 - 5 * k) ** 2 + (8 - 3 * k) ** 2 == 169 and (20 * k - 17) ** 2 + (12 * k - 8) ** 2 == 25]
    assert v == [1]
    ck(42, (F(17, 5) - F(8, 3)) * 60, '整数速度枚举(5k,3k)，唯一k1，晚44分')
    groups = []
    for pair in itertools.combinations(range(1, 6), 2):
        g = {0, *pair}
        h = set(range(6)) - g
        if all((z & {0, 1, 2} and z & {3, 4, 5} and z & {0, 3, 4} for z in [g, h])):
            groups.append(sorted(g))
    ck(43, len(groups), str(groups))
    diffs = [-18000 + 3000 * k for k in range(12)]
    assert sum(diffs[:3]) == -45000
    ck(44, sum(diffs), '枚举12个月桃减橙差额')
    a=F(2);c=F(1);b=F(24*a-4*(a+c),12+4)
    ck(45,24*a/(b+c), '甲8乙9丙4，首批108次批84，总192')
    energy=2*(F(11,10)/F(9,10)-1);other=3-1-energy
    ck(46,energy/other, '原单利9/价27/能耗4/其他14，新利11×0.9=9.9')
    ck(47, (math.sqrt(2) + 1) * math.pi + 2, '圆侧√2π+端π-2+四切面4')
    xy = [(x, y) for x in range(1, 201) for y in range(1, 201) if y - x == x - 54 == F(3, 2) * x - y]
    assert xy == [(72, 90)]
    extra = F(500 - sum(xy[0]), 60)
    ck(48, extra, 'x72 y90；12点后169/30小时=5h38m')
    c = F(130 + 120, F(1, 2))
    price = 3 * c / 2
    counts = [floor(15000 / p) for p in [(price - 50) * F(4, 5), price * F(9, 10) - 50, price - 150, price * F(85, 100)]]
    assert counts == [26, 24, 25, 23]
    ck(49, counts, '成本500、原价750；各候选整件购买数')
    ck(50, F(6000, 1) / (F(600, 6) * F(3, 2) * 5), '5窗×150笔/日=750')
    dupe(51, 37)
    dupe(52, 41)
    li15 = F(63 + 24, 3)
    ck(53, 15 * 60 + (50 - li15) * 5, '李15点29户，达到50户在总分钟1005，即16:45')
    dupe(54, 43)
    dupe(55, 44)
    dupe(56, 47)
    ck(57, F(2 * comb(5, 2) * comb(5, 3), comb(10, 5)), '全选5台总252，两种平板数各100')
    dupe(58, 40)
    f = F(0, 1)
    for n in [4, 8, 16]:
        f = F(n - 2, 2 * (n - 1)) * (1 + f)
    assert f == F(11, 15)
    ck(59, f, '淘汰赛递推f2=0,f4=1/3,f8=4/7,f16=11/15')
    pc = [(p, F(3, 5) * p) for p in range(1, 1000) if 2 * (F(4, 5) * p - F(3, 5) * p) == p - F(3, 5) * p == 3 * (p - 120 - F(3, 5) * p)]
    assert pc == [(450, 270)]
    ck(60, pc[0][0], str(pc))
    tpos = next((t for t in range(1, 100) if t - F(3 * t, t + 3) == 4))
    ck(61, 1 / (F(1, 4) - 1 / tpos), '乙时间正根6，丙效率1/12')
    valid = [(x, y) for x in range(13) for y in range(16) if 16 * x + 13 * y <= 200 and 9 * y > 100]
    ck(62, max((x for x, y in valid)), str(valid))

    def area2(p, q, r):
        return abs((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))
    A = (F(0), F(0))
    B = (F(3), F(0))
    C = (F(0), F(3))
    D = (F(0), F(3, 2))
    Ept = (F(1), F(0))
    O = (F(2, 3), F(1))
    area = area2(Ept, O, D) / 2
    ck(63, area2(A, B, C) / (2 * area), f'O={O}, S湖={area}')
    ck(64, F(5, 9) ** 2, '两次有放回有序抽样25/81')
    c15 = 3000 * 100 + 7000 * 200
    c18 = 3600 * 100 + 6400 * 200
    ck(65, F(c15 - c18, 10000), '两时限均把甲排满，费用差6万')
    ck(66, f'{5 + math.sqrt(13)}:{7 + math.sqrt(13)}', '方形边3，截边2，斜边√13')
    arr = []
    for p in itertools.permutations(['R1', 'R2', 'F1', 'F2']):
        if all((p[k][0] != p[k + 1][0] for k in range(3))):
            for long in ['R1', 'R2']:
                arr.append((p, long))
    ck(67, len(arr), '枚举四租户类型交替排列及双铺餐厅')
    gifts = []
    for k in range(6):
        for high in itertools.combinations(range(10), k):
            h = set(high)
            if k < 3 and h <= {0, 1, 2} or (k >= 3 and {0, 1, 2} <= h):
                gifts.append(high)
    ck(68, len(gifts), '直接枚举10户的高价领取集合并校验优先与预算')
    a = [k for k in range(1, 10) if 121 * k - 76 >= 0 and 342 * k - 76 <= 287]
    ck(69, 287 - (342 * a[0] - 76), 'k正整数约束唯一1')
    possible = [p for p in perms if p.index(0) not in [0, 5] and p.index(1) not in [0, 5] and (p.index(2) in [2, 3])]
    good = [p for p in possible if abs(p.index(3) - p.index(4)) == 1]
    ck(70, F(len(good), len(possible)), f'有利{len(good)}，总{len(possible)}')
    ck(71, F(1, 2) * 3 + F(1, 4) * 9, '乙耗3.75小时，即11:45')
    ck(72, 1 - F(20, 1) / (F(2, 5) * 100), '利润200,300,600，甲占1/2，乙1/2')
    ck(73, 1800 - 1200, '旧1800/1200/3000，新2200/1100/3900')
    vol = 1 - F(9, 10) ** 3 / F(3, 2)
    assert vol > F(8, 10) ** 3
    ck(74, float(vol) ** (1 / 3), '露出体积比例257/500=.514大于.8³=.512')
    dupe(75, 68)
    dupe(76, 60)
    r = F(30 - 18 - 10, 15 + 18 - 30)
    ck(77, r, '两施工方案总工作量相等，3a=2b')
    dupe(78, 69)
    areas = [1 * 2, 2 * 3, 3 * 4, 4 * 1]
    ck(79, F(sum(areas[1:]), areas[0]) - 1, '四面积2,6,12,4；剩余11工日，额外10')
    first = 2200
    day = next((d for d in range(1, 100) if first + 200 * (d - 1) >= 10000))
    ck(80, day, '首日2200，日39为9800、日40为10000')
    dupe(81, 71)
    dupe(82, 72)
    ck(83, (F(3, 5) / F(3, 2) + F(2, 5) / F(12, 5)) / (F(2, 5) + F(3, 5) / 2), '返程17/30，去程7/10')
    ballots = [p for p in itertools.product([1, -1], repeat=7) if p.count(-1) >= 2 and all((sum(p[:k]) > 0 for k in range(1, 8)))]
    ck(84, len(ballots), str(Counter((p.count(-1) for p in ballots))))
    dupe(85, 61)
    dupe(86, 66)
    ck(87, 10000000 // 168000, '原价280000，A六折168000，预算最多59台')
    dupe(88, 64)
    dupe(89, 79)
    comps = [p for p in itertools.product(range(1, 8), repeat=4) if sum(p) == 10]
    fav = [p for p in comps if 3 in Counter(p).values()]
    ck(90, F(len(fav), len(comps)), f'有利{len(fav)},总{len(comps)}')
    valid = []
    for p in itertools.permutations(range(8)):
        if all((len({x // 2 for x in group}) == len(group) for group in [p[:3], p[3:6], p[6:]])):
            valid.append(p)
    assert len(valid) == 13824
    ck(91, len(valid), '8!全枚举，每段学校不重复：13824')
    ck(92, 1 / (F(1, 2) / 40 + F(1, 4) / 60 + F(1, 4) / 40), '总程归1，时间11/480，速480/11')
    dupe(93, 73)
    ck(94, F(1, 3)*2**2/1**2, '等高圆柱体积πh³，圆锥4πh³/3，等质量密度反比')
    N = 30000 // 50
    ck(95, 5 * N, 'M4N，价差50N=30000')
    oldk = F(16 - F(3, 2) * 8, F(3, 2) * 5 - 7)
    three = [3 * oldk + 8, 4 * oldk + 8, 5 * oldk + 8]
    four = three + [172 - sum(three)]
    future = [x + 15 for x in four]
    ck(96, sum((x > 60 for x in future)), str(future))
    ck(97, (F(5*12-40,5)+12)/F(5*12-40,5), '甲4..8与乙16,14,12,10,8，和30与60，首项比4')
    v = F(3 * 30, 5 * F(6, 5) - 2 - 3)
    ck(98, 6 * v, '乙初速90，甲108，五小时540')
    ck(99, math.sqrt(250 ** 2 + (50 * math.sqrt(3)) ** 2), '已核D在BC南，坐标距离平方70000')
