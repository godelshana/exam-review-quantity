"""Offline port of provincial_05_check: numerical checks vs manual off-module judgments.
Frozen geometry/sequence models are conditional, not automatic image interpretation.
"""
import math,itertools,calendar,datetime
from fractions import Fraction as F
from collections import Counter
from math import comb,ceil,floor
BATCH='provincial_05'

def run(ctx):
    def ck(i,value,proof,kind='independent_math'):
        manual=kind=='off_module_visual'
        # These values are vectors, witnesses, or competing-model quantities, not answers.
        property_only=isinstance(value,(dict,list,tuple))
        if i==1:
            ctx.add(i,max(value),candidates=value,evidence=proof,boundary='manual transcription of the four rebate table rows')
            return
        if i==10:
            assert len(value)==1
            value=value[0];property_only=False
        ctx.add(i,value,evidence={'kind':kind,'proof':proof},mode='manual_only' if manual else 'computation',property_only=property_only,boundary='manually justified model; sequence continuation is conditional; geometric proofs and search bounds are not reconstructed from images')
    ck(0, (12 + 16 + math.hypot(12, 16)) / 4, '树间距12/16/20，周界48')
    rebates = [2000 * F(7, 10) * F(15, 100), 1500 * F(9, 10) * F(2, 10), 3000 * F(6, 10) * F(15, 100), 1800 * F(8, 10) * F(2, 10)]
    ck(1, rebates, '原图四行逐一计算')
    skills = [(1, 0)] * 3 + [(0, 1)] * 2 + [(1, 1)] * 2
    valid = []
    for p in itertools.product(range(3), repeat=7):
        if all((tuple((sum((skills[j][k] for j in range(7) if p[j] == team)) for k in [0, 1])) == (2, 2) for team in [1, 2])):
            valid.append(p)
    assert len(valid) == 30
    ck(2, len(valid), '3^7完整枚举，甲乙与不派三个状态，能力各2')
    ck(3, F(4 + 20, 40 + 20), '加权增长方程蜜柚占2/5')
    brothers = [(t, d) for t in range(1, 50) for d in range(1, 30) if d == t + 2 and 40 + 2 * t + d == 8 * (2 * t + 2)]
    assert brothers == [(2, 4)]
    ck(4, brothers, '工龄年龄条件整数全枚举')
    pairs = list(itertools.combinations(range(6), 2))
    ways = sum((len(set(a + b + c)) == 5 for a, b, c in itertools.product(pairs, repeat=3)))
    assert ways == 1080
    ck(5, F(ways, len(pairs) ** 3), '3375组三次抽题全部枚举，覆盖5题1080组')
    ss = ['1231', '2311', '3112', '1123']
    assert all((b == a[1:] + a[0] for a, b in zip(ss, ss[1:])))
    ck(6, ss[-1][1:] + ss[-1][0], '每步数字左移')
    seq = [38, 6, 22, 14, 18, 16]
    ds = [seq[i + 1] - seq[i] for i in range(5)]
    assert all((F(ds[i + 1], ds[i]) == F(-1, 2) for i in range(4)))
    ck(7, seq[3]+(seq[3]-seq[2])*F(-1,2), str(ds))
    seq = [82, 68, 142, 208, 342, 548, 882]
    offset = [seq[i] + seq[i + 1] - seq[i + 2] for i in range(5)]
    assert offset == [8, 2, 8, 2, 8]
    ck(8, seq[-3]+seq[-2]-offset[-2]*4, str(offset))
    assert [5 * 4, 6 * 5, 9 * 8] == [20, 30, 72]
    ck(9, 14 * 13, '三项组第三数=b(a+1)')
    nums = [99, 67, 38, 29, 17, 10]
    dens = [75, 49, 25, 20, 11, 6]
    diff = [a - b for a, b in zip(nums, dens)]
    assert diff == [24, 18, 13, 9, 6, 4]
    ck(10, [o for o in ctx.problems[10]['o'] if '/' in o and int(o.split('/')[0])-int(o.split('/')[1])==diff[-1]-1], '分子分母差的变化-6,-5,-4,-3,-2，下一-1，差3')
    ck(11, F(120, F(35, 100) - (1 - F(40 + 35, 100))), '占比差10%对应120')
    ck(12, F(720, F(18, 10)) / F(40, F(25, 10)), '周日400万元/16家')
    ck(13, (20 * 5 - 20 * F(12, 24)) / 25, '90设备天/25台')
    valid = [(5 * x + 2 * y, x, y) for x in range(2001) for y in [2000 - x] if y >= 4 * x]
    best = max(valid)
    assert best == (5200, 400, 1600)
    ck(14, best, '固定产满后枚举x=0..2000，有效最大5200')
    ck(15, F(3, 10) * F(7, 10) + F(7, 10) * F(2, 10), '全概率7/20')
    e = F(40, F(14, 10) - 1)
    m = (e + 40 + 140) / F(14, 10)
    assert e == 100 and m == 200
    ck(16, m - e, '对顶乘积消元 e40/.4=100，m200')
    dates = [t for t in itertools.combinations(range(1, 8), 3) if t[1] - t[0] >= 2 and t[2] - t[1] >= 2]
    ck(17, len(dates), str(dates))
    scores = [(100 - b, b, 96 - b, b - 16) for b in range(17, 81) if 100 - b > b > 96 - b > b - 16 > 0]
    assert scores == [(51, 49, 47, 33)]
    ck(18, scores[0][-1], str(scores))
    orders = [(sum((sum(p[:i]) for i in range(4))) * 100, p) for p in itertools.permutations([4, 6, 7, 8])]
    ck(19, min(orders)[0], str(min(orders)))

    def shuttle(z):
        return 200 - abs(z % 400 - 200)
    assert shuttle(140 * 10) == shuttle(100 * 10) == 200 and shuttle(140 * 20) == shuttle(100 * 20) == 0
    ck(20, shuttle(140*F(2*2*200,140-100)), '同向追及(140-100)t=400k，前两次10/20分钟')
    exact = 0.45 * (math.sqrt(3) - math.sqrt(2)) / (2 - math.sqrt(3))
    approx = 3 * (F(17, 20) - F(5, 7))
    assert 0.53 < exact < 0.54 and 0.4 < float(approx) < 0.42
    ck(21, {'exact': exact, 'sourceApprox': str(approx)}, '精确余弦约.53378；特定粗近似57/140=.40714。给出不同计算路径不一致证据', 'mathematical_dispute')
    ck(22, comb(2, 1) * comb(4, 2) * comb(5, 3) * math.factorial(3), '原PDF第11页恢复2/4/5选1/2/3，再分三队')
    valid = []
    for A in range(1, 179):
        for B in range(1, 180 - A):
            C = 180 - A - B
            v1 = (A - B - C, 2 * B, 2 * C)
            if min(v1) < 0:
                continue
            a, b, c = v1
            v2 = (2 * a, b - a - c, 2 * c)
            if min(v2) < 0:
                continue
            a, b, c = v2
            v3 = (2 * a, 2 * b, c - a - b)
            if min(v3) >= 0 and 26 * v3[2] == 7 * v3[0]:
                valid.append((A, B, C, v3))
    assert valid == [(103, 51, 26, (104, 48, 28))]
    ck(23, 103, str(valid))
    ck(24, (201 - 1) // 7, 'n28保证；n29构造27×7+2×6=201且无人8箱')
    ck(25, F(sum(k not in (1,5) for k in range(1,6)),5), '固定大人，5个位置3个不相邻')
    fixed = math.factorial(6) // (math.factorial(1) * math.factorial(2) * math.factorial(3))
    free = 0
    for p in itertools.product(range(3), repeat=6):
        if sorted(Counter(p).values()) == [1, 2, 3]:
            free += 1
    assert fixed == 60 and free == 360
    ck(26, {'fixed': fixed, 'unspecified': free}, '固定学校人数分配60，3^6枚举学校可变人数360', 'mathematical_dispute')
    ps = [n for n in range(100, 1000) if str(n) == str(n)[::-1]]
    ck(27, F(sum((n % 2 == 1 for n in ps)), len(ps)), '90回文，50奇数')
    parking = [p for p in itertools.permutations(range(8), 4) if p[0] // 4 == p[1] // 4 and len({n // 4 for n in p}) == 2]
    assert len(parking) == 672
    ck(28, len(parking), '8P4全枚举，甲乙同排且两排均有车')
    ck(29, math.hypot(12, 4 + 1) + 2, '河宽2固定，平移后陆路13，加桥2为15')
    h = math.sqrt(8.5 ** 2 - (7 - 3) ** 2)
    tour = math.hypot(h, 3 + 7) + 8.5
    assert tour == 21
    ck(30, tour, 'h7.5，反射距离12.5加村间8.5，21km/60kmh=21min')
    ck(31, 36 * 260 + 4 * 24 * 180, 'AM-GM长宽6，底9360加侧17280')
    ck(32, F(3 * 1, 2) * 2 + F(6 * 1, 3), '中央三棱柱3，两端锥共2；另积分12-9+2=5')
    ck(33, F(comb(3, 1) * comb(3, 2), comb(6, 3)), '9/20')
    a = 2.5
    b = 25
    blue = math.pi * b * b - 4 * (a * math.sqrt(b * b - a * a) + b * b * math.asin(a / b)) + 4 * a * a
    cost = 30 * 112.5 * 900 * math.pi / blue
    assert all((abs(cost - v) > 300 for v in [3375, 6000, 6750, 8437.5]))
    ck(34, cost, '等宽圆环/十字带模型蓝面积1489.329996cm²，总6407.3024元，无精确匹配选项', 'mathematical_dispute')
    ck(35, None, 'abstract figure classification; manually judged off-module; no numerical oracle', 'off_module_visual')
    ck(36, None, 'abstract figure classification; manually judged off-module; no numerical oracle', 'off_module_visual')
    p = 1 - (1 - F(3, 4)) * (1 - F(1, 3))
    assert p == F(5, 6) and all((F(3, 4) > x for x in [F(1, 4), F(1, 2), F(2, 3)]))
    ck(37, p, '一般概率下界3/4排除ABC；独立模型精确5/6')
    ck(38, None, 'abstract figure classification; manually judged off-module; no numerical oracle', 'off_module_visual')
    trucks = [(350 * a + 450 * b, a, b) for a in range(9) for b in range(5) if a + b <= 10 and 24 * a + 20 * b >= 160]
    ck(39, min(trucks), str(min(trucks)))
    ck(40, F(7 * 2 * 4, 1) * F(6, 10) / (144 + 7 * 2 * 4 * 2), '增面积33.6π/原256π=.13125')
    sq = next((a for a in range(1, 100) if math.isqrt(1080 * a) ** 2 == 1080 * a))
    ck(41, sq, 'a1..30试平方，1080×30=180²')
    ck(42, F(746 + 726 + 700, 2), '每窗口恰计两次')
    grid = max(((r * s, r, s) for r in range(1, 7) for s in range(1, 7) if 25 * (r + s - 2) <= 100))
    ck(43, grid, '完整平行直线网格模型枚举，最大9；不外推任意曲线分割')

    def price(n):
        return 5 * min(n, 10) + 3 * max(n - 10, 0)
    nums = [(a, b) for a in range(1, 100) for b in range(1, a) if price(a) - price(b) == 19]
    assert nums == [(13, 8)]
    ck(44, sum(nums[0]), str(nums))
    ck(45, F(comb(2, 1) * comb(3, 2), comb(5, 3)), '6/10')
    comps = [p for p in itertools.product(range(1, 5), repeat=4) if sum(p) == 7]
    ck(46, len(comps), '正整数和7的四元组枚举20')
    j = 6
    ming = j + 6
    qiang = 2 * j - 2
    assert ming + qiang == 3 * j + 4 and ming + j == 2 * qiang - 2
    ck(47, ming, '明12强10军6代回三式')
    valid = [(3 * b, b, t) for b in range(1, 100) for t in range(1, 100) if b - 3 * t > 0 and 3 * b - 5 * t == 9 * (b - 3 * t)]
    ck(48, min(valid)[0], str(min(valid)))
    ck(49, F(5,10+5-5), '同体积石块引起甲降10乙升5，底面积反比1:2')
    ck(50, F(22, 14) - 1, '总/乙22/7=2(a+b)/b，a/b4/7')
    cd = F(1, F(7, 2)) - F(1, 8)
    ck(51, 8 - 1 / cd, 'AB1/8；AC=BD=1/7，两式相加四队2/7，减AB得CD9/56；提前16/9')
    ck(52, F(14, F(13, 8) - F(3, 4)), 'B总13n/8减已3n/4，余7n/8=14')

    def fridays(y, m):
        return sum((datetime.date(y, m, d).weekday() == 4 for d in range(1, calendar.monthrange(y, m)[1] + 1)))
    birth = set()
    for y in range(2000, 2400):
        if not calendar.isleap(y):
            continue
        for m in range(1, 13):
            prev = (y - 1, 12) if m == 1 else (y, m - 1)
            nxt = (y + 1, 1) if m == 12 else (y, m + 1)
            if fridays(*prev) == fridays(y, m) == fridays(*nxt) == 4:
                birth.add((datetime.date(y, 1, 1).weekday(), m, datetime.date(y, 6, 1).weekday()))
    assert birth == {(2, 3, 0)}
    ck(53, '星期一', str(birth) + '；枚举完整400年闰年模板含跨年相邻月')
    total = 6
    rear = F(2, 3) * 5
    front = total - rear
    v = 120 / front
    ck(54, v * total, '全程原6小时，前120km需8/3小时，速45，全程270')
    others = [20, 22, 23, 24]
    sales = [6, 7, 9, 10, 11, 12, 13, 14, 15, 16]
    after = [4, 5, 8, 17, 18]
    tech = [1, 2, 3, 19, 21]
    assert sorted(others + sales + after + tech) == list(range(1, 25)) and F(sum(sales), 10) == F(113, 10) and (F(sum(after), 5) == F(104, 10)) and (F(sum(tech), 5) == F(92, 10))
    ck(55, 89 - 24 - 23 - 22, '三部门10/5/5人，其他4人和89；完整可达构造已检查')
    ck(56, 20 / (F(1, 5) - F(1, 6)), '总速增20，对应圈长600')
    ck(57, F(3, 8) / F(3, 20), '乙3/8浓度，丁3/20浓度，比5/2')
    both = 12 + 10 - (50 - 34)
    ck(58, comb(both, 2), '双优6，选2=15')
    Ns = [n for n in range(90, 111) if n % 24 == 0]
    assert Ns == [96]
    ck(59, F(13 * 96, 24) - F(96, 6), '甲52，目标甲16，调36')
    prod = [p for p in itertools.combinations(range(1, 11), 3) if math.prod(p) == 144]
    assert prod == [(2, 8, 9), (3, 6, 8)]
    ck(60, max(map(sum, prod)), str(prod))
    n = next(n for n in range(1,101) if 7*n-6==2*(3*n+2))
    masks = 3 * n + 2
    gloves = 7 * n - 6
    assert gloves == 2 * masks
    ck(61, ceil(F(masks + gloves, n // 2)) * 5, '96件，5人每轮5分钟，20轮100分')
    x = (F(8,9)*500+400)/(2-F(8,9)*F(2,3))
    day1 = F(2, 3) * x + 500
    day2 = F(8, 9) * day1 + 400
    assert day2 == 2 * x
    ck(62, x, '600→900→1200')
    ck(63, F(sum((comb(4, k) for k in range(2, 5))), 16), '虚拟后4局至少2胜11/16')
    remain = 8 * 9 * (25 - 13)
    ck(64, ceil(F(remain - 8 * 9, 24)), '余864，原车再运72，792/24=33')
    pp = [(n, a, a + n) for n in range(11, 20) for a in range(1, 200) if n * (2 * a + n - 1) // 2 == 1023]
    assert pp == [(11, 88, 99)]
    ck(65, pp[0][2], str(pp))
    books = [(a, d, 7 * (a + 26) // 2) for d in range(5) for a in [26 - 6 * d] if a > 0 and 7 * (a + 26) > 200]
    ck(66, min((x[0] for x in books)), str(books))
    xa = (20000 + 200 + 500) // 2
    assert xa - 500 == 20000 - xa + 200
    ck(67, (xa, 20000 - xa), '两人净收入均9850')
    veh = [(c, v) for c in range(20) for v in range(12) if 4 * c + 7 * v == 79 and (c + v) % 2 == 0]
    assert veh == [(11, 5)]
    ck(68, veh[0][0]-veh[0][1], str(veh))
    three = [n for n in range(1, 51) if sum((n % f == 0 for f in range(1, 61))) == 3]
    ck(69, len(three), str(three))
    Dposs = [D for D in range(9, 27, 3) if all((t.denominator == 1 and 3 <= t <= 26 for t in [F(D, 3), F(D), F(3 * D, D - 3), F(4 * D, D - 4)]))]
    assert Dposs == [12]
    ck(70, 21 + F(12, 3 + 3), '相遇两小时，23:00；可行标准化路长唯一12')
    ck(71, 300 + 9 * 3, '抽水170=5段30+4休5，注水10段30+9休3=327')
    kk = F(340 + 60, 10)
    ck(72, 80 * kk + 340, '学校40，书3540')
    ck(73, F(80 - 6 - 18, 2), '行政28')
    fish = F(2100 - 900, F(3, 4) - F(1, 4))
    ck(74, fish, '同时交换900与600，各2700')
    ck(75, 5 * F(5, 100) + 5 * F(10, 100) + 10 * F(15, 100), '分档.25+.5+1.5=2.25')
    ck(76, 68 - 45 - 12, '原“68人参赛”与45未参加矛盾；修订共有68人后，仅歌11，并给5/11/7/45四区构造', 'mathematical_dispute')
    ck(77, F(100, 50 - 40), '相遇9:40，人行100分钟，车走相同距需10分钟，10倍')
    ck(78, 49 * 6 * 6, '有序红蓝49×36')
    ck(79, F(300 * 80, 60) - 300, '总量24000人天，新400人，增100')
    ck(80, 400 - 400 * F(220, 250), '丙完工352，余48')
    ck(81, 3000 / F(1, 5) / F(3, 8), '舞台计划15000，总预算40000')
    ck(82, (545 - 120 * F(9, 2)) / (5 - F(9, 2)), '多支5，每原价小时多.5，10小时')
    ck(83, F(210, 1600 + 600 - 450), '210/1750=3/25')
    period = math.lcm(8, 10, 15)
    ck(84, period % 7, '源答案空日口径周期8/10/15，120余1；另一每n天口径126余0已列边界')
    ck(85, F(30 * (16 + 1), 4 - 1), '车16狗1人4，背向30秒间距510，追速3，170秒')
    ck(86, F(5 + 3, 2 * comb(6, 2) + 7), '亚军8场/全赛事37，超20%')
    steps = []
    n = 140
    while n > 1:
        steps.append(n)
        n = (n + 1) // 2
    ck(87, sum((n % 2 == 0 for n in steps)), str(steps) + '；4个奇数阶段可轮空，4个偶数阶段必赛')
    ck(88, 200 / F(5, 6), '李200=5/6L，L240')
    ck(89, 15 * F(1, 3), '乙骑全程S、甲走S/3，同时间速5')
    ck(90, (2+2*F(3,5)/F(2,5))/(4*3-(2+2*F(3,5)/F(2,5))), '线下男2女2，线上男3女5，总5:7')
    ck(91, 380 * 26 - 400 * 8, '全部生产成本3200扣收入9880')
    T = F(600, F(1, 5))
    ck(92, T, '甲T/3，乙T/5，丙T/3-200，丁T/3-400')
    ck(93, F(750 - 200 - 350, 650 - 150 - 140), '总1400，丙男女200:360=5:9')
    ck(94, F(16+16*2,2)/(F(16+16*2,2)+16), '原24:40，租后8:24')
    cal = []
    for leap in [False, True]:
        lens = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for start in range(7):
            off = 0
            cts = []
            for k in range(4):
                days = sum(lens[3 * k:3 * k + 3])
                cts.append(sum(((start + off + i) % 7 < 5 for i in range(days))))
                off += days
            if len(set(cts)) == 1:
                cal.append((leap, start, (start + sum(lens[:9])) % 7, cts))
    assert all((c[2] == 6 for c in cal)) and len(cal) == 2
    ck(95, '星期日', str(cal))
    finish = next((F(t, 2) for t in range(1, 50) if 3 * (t // 2) + 2 * t >= 100))
    ck(96, finish, '交付3floor(t)+2floor(2t)，首次100在14.5h')
    c2 = 0
    ends = []
    for n in range(1, 1001):
        c2 += str(n).count('2')
        if c2 == 87:
            ends.append(n)
    assert ends == [232]
    diff = sum((str(n).count('3') - str(n).count('6') for n in range(1, 233)))
    ck(97, diff, '2累计87唯一末页232；3计46，6计43')
    s,d = next((s,d) for s in range(1,101) for d in range(1,101) if s+3*d-5==3*(s+d-5) and s+2*d+8==5*(s+8))
    ages = [s + i * d for i in range(4)]
    assert ages[3] - 5 == 3 * (ages[1] - 5) and ages[2] + 8 == 5 * (ages[0] + 8)
    ck(98, sum(ages), str(ages))
    regions=[(l,12,40-12-l,ld,lv,28-ld-lv,12) for l in range(29) for ld in range(29) for lv in range(29-ld) if (40-12-l)-l==16]
    ck(99, max(v+dv-l-ld for l,d,v,ld,lv,dv,all3 in regions), '只劳6只捐12只访22，捐访28三项12；访62劳18，差44，上界16+28')
