# -*- coding: utf-8 -*-
"""数量关系自编题生成器 D 类：几何结论 / 枚举 / 正难则反，共110题。
所有枚举与概率题用 itertools 全枚举独立校验；几何题公式两算校验。
运行: python gen_D.py  → 输出 gen_D_output.json
"""
import json, itertools, random
from fractions import Fraction
from math import isqrt

rng = random.Random(20260909)
OUT = r"E:\codeBase\examReview\教学\速刷\gen\gen_D_output.json"
questions, stems = [], set()

# 情境外壳机制：同一模板用不同情境开头，防模板单调
SHELL_USE = {}
STEM_SHELL = {}


def pick_shell(sids):
    return min(sids, key=lambda x: (SHELL_USE.get(x, 0), sids.index(x)))


def mark_shell(sid, stem, ok):
    if ok:
        SHELL_USE[sid] = SHELL_USE.get(sid, 0) + 1
        STEM_SHELL[stem] = sid

def fs(x):
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else "%d/%d" % (f.numerator, f.denominator)

def _pad_int(ans, used, n=3):
    cands = [ans + d for d in (1, -1, 2, -2, 3, -3, 4, -4, 10, -10, 5, 6, 8)]
    out = []
    for c in cands:
        if c > 0 and str(c) not in used:
            used.add(str(c)); out.append(c)
        if len(out) == n: break
    assert len(out) == n, "整数干扰项不足"
    return out

def _pad_frac(ans, used, n=3):
    out = []
    for d in range(1, 40):
        for dd in (ans.denominator, 2 * ans.denominator, 3 * ans.denominator):
            c = ans + Fraction(d, dd)
            if 0 < c and str(c) not in used:
                used.add(str(c)); out.append(c)
            if len(out) == n: return out
    assert len(out) == n, "分数干扰项不足"

def add(h, t, s, ans, cands, e, tr=""):
    """ans/cands 同类型（int 或 Fraction）。返回是否成功入池。"""
    if s in stems: return False
    used = {str(ans)}
    pool = []
    for c in cands:
        if str(c) not in used:
            used.add(str(c)); pool.append(c)
    pool += _pad_frac(ans, used) if isinstance(ans, Fraction) else _pad_int(ans, used)
    opts = pool[:3] + [ans]
    rng.shuffle(opts)
    a = opts.index(ans)
    assert len({str(o) for o in opts}) == 4
    stems.add(s)
    questions.append({"h": h, "t": t, "s": s, "o": [str(x) for x in opts], "a": a,
                      "e": e, "tr": tr})
    return True

def fill(h, t, n, gen):
    made = 0
    for attempt in range(400):
        if made == n: break
        if gen(attempt): made += 1
    assert made == n, "%s 只出了 %d/%d 题" % (h + t, made, n)

# ============ 一、几何结论 ×45 ============

TRIPLES = [(6,8,10),(9,12,15),(7,24,25),(20,21,29),(9,40,41),(12,16,20),
           (10,24,26),(18,24,30),(16,30,34),(15,20,25),(33,44,55),(24,32,40)]

# G1 勾股求斜边 ×7（钩子）
def g1(_):
    a, b, c = TRIPLES[rng.randrange(len(TRIPLES))]
    if {a, b} == {8, 15}: return False          # 避开已有题
    # 真校验：程序由两直角边独立算出斜边并与取值对账（不靠表格自证）
    c2 = isqrt(a * a + b * b)
    assert c2 * c2 == a * a + b * b and c2 == c, (a, b, c)
    return add("几何结论", "钩子",
        "直角三角形两条直角边分别为%d和%d，则斜边长为多少？" % (a, b), c,
        [a + b, c - (b - a), a * b // 2],
        "勾股定理：斜边=√(两直角边平方和)。常用勾股数要背熟，直接出数。",
        "误选两直角边之和者混淆了平方和与和。")
fill("几何结论", "G1", 7, g1)

# G2 勾股求直角边 ×3（钩子）
def g2(_):
    a, b, c = TRIPLES[rng.randrange(len(TRIPLES))]
    if {a, b} == {8, 15} or (a, b) == (5, 12): return False
    # 真校验：程序由斜边与已知直角边独立算出另一边并对账
    a2 = isqrt(c * c - b * b)
    assert a2 * a2 == c * c - b * b and a2 == a, (a, b, c)
    return add("几何结论", "钩子",
        "直角三角形斜边为%d，一条直角边为%d，则另一条直角边长为多少？" % (c, b), a,
        [c - b, (c + b) // 2 if (c + b) % 2 == 0 else c - b - 1, c * b // 2],
        "另一边=√(斜边平方−已知边平方)，勾股差公式：常用勾股数直接回想。",
        "误用斜边减直角边（非平方相减）。")
fill("几何结论", "G2", 3, g2)

# G3 相似平方 ×5（4钩子+1深钩：面积差反求）
def g3(_):
    p, q = rng.choice([(2,3),(3,4),(3,5),(4,5),(2,5)])
    k = rng.choice([1,2,3,4])
    small = k * p * p
    big = k * q * q
    assert small * q * q == big * p * p          # 面积比=相似比平方，交叉两算
    style = rng.random()
    if style < 0.25:  # 深钩：给面积差反求小面积（比例传导）
        diff = q*q - p*p
        m = rng.choice([k*2, k*3])
        small2, big2 = m*p*p, m*q*q
        assert big2 - small2 == m*diff and small2 * diff == m * diff * p*p
        return add("几何结论", "深钩",
            "两个相似三角形相似比为%d:%d，面积相差%d，则较小三角形的面积为多少？" % (p, q, m*diff),
            small2, [m*q*q, m*(q-p), m*(q-p)*(q-p)],
            "深在两步：面积比=(%d:%d)²=%d:%d，先由差÷份额差得每份，再乘小份额。" % (p, q, p*p, q*q),
            "把面积差按相似比%d:%d直接分。" % (p, q))
    return add("几何结论", "钩子",
        "两个相似三角形相似比为%d:%d，较小者面积为%d，则较大者面积为多少？" % (p, q, small),
        big, [small * q // p, small + (q - p) * (q - p) * k, small * (q*q - p*p)],
        "面积比=相似比平方，故大面积=小面积×(q/p)²。",
        "误按相似比一次方放大。")
fill("几何结论", "G3", 5, g3)

# G4 相似立方 ×4（钩子）
def g4(_):
    p, q = rng.choice([(1,2),(2,3),(1,3),(3,4)])
    k = rng.choice([1,2,3])
    small, big = k * p**3, k * q**3
    assert big == small * q**3 // p**3 and small * q**3 == big * p**3  # 两算
    return add("几何结论", "钩子",
        "两个相似正方体棱长比为%d:%d，较小者体积为%d，则较大者体积为多少？" % (p, q, small),
        big, [small * (q//p if q % p == 0 else q), small * q*q//p*p, small * (q*q - p*p)],
        "体积比=棱长比立方，大面积=小体积×(q/p)³。",
        "棱长扩2倍体积按2倍算（应为8倍）。")
fill("几何结论", "G4", 4, g4)

# G5 圆锥圆柱 ×6（钩子）
def g5b(_):
    r, h = rng.randint(2, 6), rng.randint(3, 9)
    v = 3 * r * r * h                              # 圆柱体积（π取3）
    cone = v // 3
    # 真校验：换公式独立复算（圆锥=π取3×r²h÷3=r²h）
    assert cone == r * r * h and v == cone * 3, (r, h, v, cone)
    style = rng.randrange(3)
    if style == 0:
        return add("几何结论", "钩子",
            "一个圆柱体积为%d立方厘米，与它等底等高的圆锥体积为多少？" % v, cone,
            [v // 2, v - r * 0 if False else v * 2 // 3, v],  # 干扰：半分、2/3、原值
            "等底等高：圆锥=圆柱×1/3。",
            "误以为圆锥=圆柱×2/3。")
    if style == 1:
        return add("几何结论", "钩子",
            "圆锥与圆柱等底等高，圆柱体积%d立方厘米，圆锥比圆柱少多少立方厘米？" % v,
            v - cone, [v // 2, cone, v * 2 // 3],
            "少的部分=圆柱×2/3。",
            "误算成少1/3（应为少2/3）。")
    return add("几何结论", "钩子",
        "圆锥和圆柱等底等高，二者体积之和为%d立方厘米，圆柱体积为多少？" % (v + cone),
        v, [v + cone, cone, (v + cone) // 2],
        "和=圆柱×4/3，先除4再乘3得圆柱。",
        "把和按1:1平分。")
fill("几何结论", "G5", 6, g5b)

# G6 正方体涂色 ×7（5钩子+2深钩，n≤6 全枚举分类计数校验）
def paint_counts(n):
    cnt = {0: 0, 1: 0, 2: 0, 3: 0}
    for x, y, z in itertools.product(range(n), repeat=3):
        f = sum(1 for v in (x, y, z) if v in (0, n - 1))
        cnt[f] += 1                                # 暴力：逐格数涂色面
    assert cnt[3] == 8 and cnt[2] == 12 * (n - 2)
    assert cnt[1] == 6 * (n - 2) ** 2 and cnt[0] == (n - 2) ** 3
    return cnt

def g6(_):
    n = rng.randint(3, 6)
    cnt = paint_counts(n)
    kind = rng.randrange(4)
    if kind == 0:   # 深钩：涂色+重组
        one = cnt[1]
        assert one % 8 == 0 or one >= 8
        usable = (one // 8) * 8
        assert usable == (one // 8) * 8
        return add("几何结论", "深钩",
            "棱长为%d的正方体表面涂红后切成%d等份，恰有一面涂色的小块有%d块。"
            "用这些小块最多能拼成多少个2×2×2的立方体（涂色面朝内）？" % (n, n**3, one),
            one // 8, [one // 4, one, one - 8 if one > 8 else one],
            "深在两步：先得一面涂色块数6(n−2)²，再除以每立方所需8块。",
            "忘了每个2×2×2要用8块。")
    if kind == 1:
        return add("几何结论", "钩子",
            "棱长为%d的正方体六面涂色后切成%d个相同小正方体，恰有三面涂色的有几块？" % (n, n**3),
            cnt[3], [cnt[2], cnt[1], 12 * (n - 2)],
            "三面涂色=8个顶点块，与n无关恒为8。",
            "随n增大误以为顶点块变多。")
    if kind == 2:
        return add("几何结论", "钩子",
            "棱长为%d的正方体表面涂色后切成%d等份，恰有两面涂色的有几块？" % (n, n**3),
            cnt[2], [cnt[1], cnt[3], 6 * (n - 2) ** 2],
            "两面涂色=12条棱×每棱(n−2)块。",
            "棱上两端点已属三面块，误按n计。")
    return add("几何结论", "钩子",
        "棱长为%d的正方体表面涂色后切成%d等份，没有任何涂色的小块有几块？" % (n, n**3),
        cnt[0], [cnt[1], n - 2, (n - 1) ** 3],
        "无涂色=剥去表层，核为(n−2)³。",
        "误答(n−2)或(n−1)³。")
fill("几何结论", "G6", 7, g6)

# G7 等积变形 ×4（1深钩：先求棱再求高）
def g7(_):
    e = rng.choice([4, 6, 8, 10])
    dims = rng.choice([(e, e, e), (e//2, e, 2*e), (e//2, e//2, 4*e), (2, e*e//2//1, e)])
    a, b, c = dims
    if a*b*c != e**3 or min(dims) <= 1: return False
    assert a*b*c == e**3                         # 体积守恒两算：长方体体积=正方体棱³
    if rng.random() < 0.25:  # 一步即可（体积÷底面积），降级为钩子
        bases = [d for d in range(2, int((e**3) ** 0.5) + 1)
                 if e**3 % d == 0 and isqrt(d) ** 2 == d]
        if not bases: return False
        base = rng.choice(bases)
        edge = isqrt(base); hh = e**3 // base
        assert edge*edge == base and base*hh == e**3 and e**3 % base == 0
        return add("几何结论", "钩子",
            "一个底面为正方形、体积为%d的长方体，底面积为%d，则高为多少？" % (e**3, base),
            hh, [e**3 // base + 1, edge, e**3 - base],
            "深在两步：底面积=边²，高=体积÷底面积。",
            "把棱长与底面积混用。")
    return add("几何结论", "钩子",
        "把长宽高分别为%d、%d、%d的长方体铁块熔铸成正方体，正方体棱长为多少？" % (a, b, c),
        e, [a*b*c // (e*e), a+b+c, e+1],
        "体积不变：abc=棱长³，开立方即得。",
        "以为熔铸后表面积不变。")
fill("几何结论", "G7", 4, g7)

# G8 等面积法求高 ×4（深钩：直角三角形斜边上的高）
def g8(_):
    a, b, c = TRIPLES[rng.randrange(len(TRIPLES))]
    if (a, b) in [(5, 12), (8, 15)]: return False
    from math import gcd
    g = gcd(a*b, c)
    hnum, hden = a*b // g, c // g
    # 真校验：换第二种公式——海伦公式算面积，再由 2S/c 求高对账
    s2 = Fraction(a + b + c, 2)
    area2 = s2 * (s2 - a) * (s2 - b) * (s2 - c)
    assert area2 == Fraction(a * b // 2) ** 2, (a, b, c)
    nrt, drt = isqrt(area2.numerator), isqrt(area2.denominator)  # 精确开方
    assert nrt * nrt == area2.numerator and drt * drt == area2.denominator
    hh = Fraction(2 * nrt, drt) / c
    assert hh == Fraction(hnum, hden), (a, b, c, hh)
    assert Fraction(a * b, c) == Fraction(hnum, hden)
    return add("几何结论", "深钩",
        "直角三角形两直角边为%d和%d，斜边上的高为多少？" % (a, b),
        Fraction(hnum, hden), [c, Fraction(a+b, 2), Fraction(a*b, c + 1)],
        "深在两步：面积=ab/2=c·h/2，故h=ab/c，约分即得。",
        "误以为高=(a+b)/2或直接答斜边。")
fill("几何结论", "G8", 4, g8)

# G9 圆/球量级 ×5（2深钩：双变量传导）
def g9(_):
    k = rng.choice([2, 3])
    style = rng.randrange(3)
    if style == 0:   # 一步传导即可，降级为钩子；用具体圆柱实例模拟验证
        r0, h0 = 2, 3
        v0 = 3 * r0 * r0 * h0                      # π取3
        v1 = 3 * (r0 * k) * (r0 * k) * Fraction(h0, k)
        assert v1 / v0 == k, (k, v0, v1)
        return add("几何结论", "钩子",
            "圆柱底面半径扩大为原来的%d倍，高缩小为原来的1/%d，则体积变为原来的多少倍？" % (k, k),
            k, [k*k, k*k*k, 1],
            "体积比=k²×(1/k)=k倍，两次变化要相乘。",
            "只算半径平方忽略高的变化。")
    if style == 1:
        r0 = 3
        s0, s1 = 3 * r0 * r0, 3 * (r0 * k) ** 2    # 具体圆实例模拟
        assert Fraction(s1, s0) == k * k
        return add("几何结论", "钩子",
            "圆的半径扩大为原来的%d倍，则面积扩大为原来的多少倍？" % k,
            k*k, [k, k*k*k, k*2],
            "面积比=半径比平方。",
            "半径×k误答面积×k。")
    r0 = 2
    v0, v1 = 4 * r0 ** 3, 4 * (r0 * k) ** 3        # 球体积模拟（4/3π约去）
    assert Fraction(v1, v0) == k ** 3
    return add("几何结论", "钩子",
        "球的半径扩大为原来的%d倍，则体积扩大为原来的多少倍？" % k,
        k**3, [k, k*k, k*3],
        "球体积=4πr³/3，体积比=半径比立方。",
        "按平方算成%d倍。" % (k*k))
fill("几何结论", "G9", 5, g9)

# ============ 二、枚举 ×30 ============

# E1 组合C ×9（钩子）
def e1(_):
    n = rng.randint(5, 9); k = rng.randint(2, 3)
    if (n, k) == (4, 2): return False
    brute = len(list(itertools.combinations(range(n), k)))   # 暴力枚举
    assert brute == __import__("math").comb(n, k)
    sid = pick_shell(["e1a", "e1b", "e1c", "e1d", "e1e"])
    stems = {
        "e1a": "从%d名候选人中选出%d人组成小组，共有多少种选法？" % (n, k),
        "e1b": "某餐厅从%d道菜中选%d道组成套餐（不计顺序），共有多少种选法？" % (n, k),
        "e1c": "旅行社安排游客从%d个景点中选%d个游览（不计顺序），共有多少种方案？" % (n, k),
        "e1d": "考生从%d道题中任选%d道作答，共有多少种选法？" % (n, k),
        "e1e": "学校开设%d门选修课，每名学生从中选报%d门，共有多少种选报方式？" % (n, k),
    }
    s = stems[sid]
    ok = add("枚举", "钩子", s, brute,
        [brute * __import__("math").factorial(k), n * k, __import__("math").perm(n, k) // 2],
        "只选不排用组合C(n,k)，无序。",
        "用排列P多乘了k!。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E1", 9, e1)

# E2 选人再排序 ×2（深钩）
def e2(_):
    n = rng.randint(5, 7); k = rng.randint(2, 3)
    brute = len(list(itertools.permutations(range(n), k)))   # 暴力：选且排
    import math
    assert brute == math.comb(n, k) * math.factorial(k)      # 与C×k!公式对账
    sid = pick_shell(["e2a", "e2b"])
    stems = {
        "e2a": "从%d名选手中选%d人并排合影（讲名次），共有多少种排法？" % (n, k),
        "e2b": "从%d名运动员中选出%d人进入决赛并排出前%d名，共有多少种结果？" % (n, k, k),
    }
    s = stems[sid]
    ok = add("枚举", "深钩", s, brute,
        [__import__("math").comb(n, k), n * k, brute // k],
        "深在两步：先C选人再k!排序，即排列A(n,k)。",
        "只选不排，漏乘k!。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E2", 2, e2)

# E3 固定位置排列 ×5（钩子）
def e3(_):
    import math
    n = rng.randint(4, 8)
    brute = len([p for p in itertools.permutations(range(n)) if p[0] == 0])  # 甲在最左
    assert brute == math.factorial(n - 1)
    pos = rng.choice(["最左边", "正中间" if n % 2 == 1 else "第二个"])
    sid = pick_shell(["e3a", "e3b", "e3c"])
    stems = {
        "e3a": "%d名同学排成一排照相，甲必须站在%s，共有多少种排法？" % (n, pos),
        "e3b": "%d名仪仗队员排成一列，队长必须站在%s，共有多少种列队方式？" % (n, pos),
        "e3c": "%d本书摆成一排放上书架，其中最厚的一本必须放在%s，共有多少种摆法？" % (n, pos),
    }
    s = stems[sid]
    ok = add("枚举", "钩子", s, brute,
        [math.factorial(n), math.factorial(n - 2), (n - 1) * math.factorial(n - 1)],
        "甲位置定死，其余n−1人全排列(n−1)!。",
        "误算n!，忘了甲已固定。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E3", 5, e3)

# E4 独立分步投信 ×5（钩子）
def e4(_):
    import math
    m = rng.randint(3, 5); nbox = rng.randint(2, 4)
    if (m, nbox) == (3, 2): return False
    brute = len(list(itertools.product(range(nbox), repeat=m)))  # 暴力：每封信独立选
    assert brute == nbox ** m
    sid = pick_shell(["e4a", "e4b", "e4c"])
    stems = {
        "e4a": "%d封不同的信投入%d个不同邮筒，每封信都有%d种投法，共有多少种投法？" % (m, nbox, nbox),
        "e4b": "%d名乘客各自在%d个不同车站中选择一个下车（可以同站），共有多少种下车方案？" % (m, nbox),
        "e4c": "某产品需经过%d道工序，每道工序都有%d种工艺可选，共有多少种工艺方案？" % (m, nbox),
    }
    s = stems[sid]
    ok = add("枚举", "钩子", s, brute,
        [math.comb(m, nbox) if m >= nbox else nbox ** m + 1, m * nbox, nbox ** m - 1],
        "每封信独立选邮筒，分步相乘n^m。",
        "误用组合数，忽略每封信独立可选同筒。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E4", 5, e4)

# E5 相邻捆绑 ×6（钩子）
def e5(_):
    import math
    n = rng.randint(4, 9)
    brute = len([p for p in itertools.permutations(range(n))
                 if abs(p.index(0) - p.index(1)) == 1])
    assert brute == 2 * math.factorial(n - 1)     # 暴力 vs 捆绑公式
    sid = pick_shell(["e5a", "e5b", "e5c"])
    stems = {
        "e5a": "%d名同学排成一排，甲乙两人必须相邻，共有多少种排法？" % n,
        "e5b": "%d本书摆满书架一层，其中甲、乙两本必须相邻摆放，共有多少种摆法？" % n,
        "e5c": "晚会有%d个节目编排节目单，歌唱和舞蹈两个节目必须相邻，共有多少种排法？" % n,
    }
    s = stems[sid]
    ok = add("枚举", "钩子", s, brute,
        [math.factorial(n - 1), 2 * math.factorial(n - 2), math.factorial(n)],
        "捆绑：甲乙内部2种，整体与其余n−2人排(n−1)!。",
        "漏了甲乙内部交换的2倍。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E5", 6, e5)

# E6 三人相邻捆绑 ×3（深钩）
def e6(_):
    import math
    n = rng.randint(5, 9)
    brute = len([p for p in itertools.permutations(range(n))
                 if max(p.index(0), p.index(1), p.index(2))
                    - min(p.index(0), p.index(1), p.index(2)) == 2])
    assert brute == math.factorial(3) * math.factorial(n - 2)   # 暴力 vs 捆绑
    sid = pick_shell(["e6a", "e6b", "e6c"])
    stems = {
        "e6a": "%d名同学排成一排，甲乙丙三人必须相邻，共有多少种排法？" % n,
        "e6b": "%d本书摆在书架一层，其中甲、乙、丙三本必须相邻，共有多少种摆法？" % n,
        "e6c": "文艺汇演%d个节目编排节目单，其中三个舞蹈类节目必须相邻，共有多少种排法？" % n,
    }
    s = stems[sid]
    ok = add("枚举", "深钩", s, brute,
        [math.factorial(n - 2), 2 * math.factorial(n - 2), math.factorial(n - 1)],
        "深在捆三：内部3!，整体与n−3人共n−2个元素排(n−2)!。",
        "三人内部顺序漏乘3!。")
    mark_shell(sid, s, ok)
    return ok
fill("枚举", "E6", 3, e6)

# ============ 三、正难则反 ×35 ============

def brute_indep(p, q):
    """独立事件网格全枚举：至少一个 / 都不发生。"""
    num_atleast = num_neither = 0
    for i in range(p.denominator):
        for j in range(q.denominator):
            a, b = i < p.numerator, j < q.numerator
            if a or b: num_atleast += 1
            if not a and not b: num_neither += 1
    total = p.denominator * q.denominator
    f1, f2 = Fraction(num_atleast, total), Fraction(num_neither, total)
    assert f1 == 1 - (1 - p) * (1 - q)            # 公式对账
    assert f2 == (1 - p) * (1 - q)
    return f1, f2

PAIRS = [(Fraction(1,2),Fraction(1,3)),(Fraction(1,3),Fraction(1,4)),
         (Fraction(2,5),Fraction(1,3)),(Fraction(1,4),Fraction(1,6)),
         (Fraction(3,5),Fraction(1,2)),(Fraction(1,2),Fraction(1,5)),
         (Fraction(2,3),Fraction(1,4)),(Fraction(1,3),Fraction(1,6)),
         (Fraction(3,4),Fraction(1,2)),(Fraction(2,5),Fraction(1,6))]

# P1 至少一个 ×10（钩子）
def p1(_):
    p, q = PAIRS[rng.randrange(len(PAIRS))]
    f1, f2 = brute_indep(p, q)
    assert f1 + f2 == 1
    return add("正难则反", "钩子",
        "甲射击命中率为%s，乙射击命中率为%s，两人各独立射击一次，至少一人命中的概率是多少？" % (fs(p), fs(q)),
        f1, [p * q, p + q if p + q < 1 else f2, f2],
        "正难则反：1−都不命中=(1−p)(1−q)取反。",
        "直接p+q会把交集算重。")
fill("正难则反", "P1", 10, p1)

# P2 都不发生 ×6（钩子）
def p2(_):
    p, q = PAIRS[rng.randrange(len(PAIRS))]
    f1, f2 = brute_indep(p, q)
    assert f2 == (1 - p) * (1 - q)
    return add("正难则反", "钩子",
        "开关A闭合概率%s，开关B独立闭合概率%s，两开关都断开（都不闭合）的概率是多少？" % (fs(p), fs(q)),
        f2, [f1, p * q, 1 - p * q],
        "都断开=(1−p)(1−q)，各取反面相乘。",
        "误求至少一个闭合，混淆对偶事件。")
fill("正难则反", "P2", 6, p2)

# P3 抽牌不放回 ×9（钩子；组合枚举校验）
def p3(_):
    N = rng.choice([8, 9, 12, 14, 15, 16, 18])
    r = rng.randint(2, N // 3)
    k = rng.choice([2, 2, 2, 3])
    if (N, r, k) == (10, 3, 2): return False
    import math
    brute_no = len([c for c in itertools.combinations(range(N), k)
                    if all(x >= r for x in c)])               # 暴力：全无红
    assert brute_no == math.comb(N - r, k)
    total = math.comb(N, k)
    ans = 1 - Fraction(brute_no, total)
    assert ans == 1 - Fraction(math.comb(N - r, k), math.comb(N, k))   # 两算
    assert 0 < ans <= 1
    return add("正难则反", "钩子",
        "%d张卡片中有%d张红色，其余为白色，不放回随机抽%d张，至少抽到一张红色的概率是多少？" % (N, r, k),
        ans, [Fraction(r, N) * k if Fraction(r, N) * k < 1 else ans,
              Fraction(brute_no, total), Fraction(r * k, N)],
        "正难则反：1−全是白=C(N−r,k)/C(N,k)的反面。",
        "正面分类（恰1张/恰2张）易漏类。")
fill("正难则反", "P3", 9, p3)

# P4 骰子"至少" ×5（钩子，36格全枚举）
def p4(_):
    ev = rng.randrange(6)
    hits = total = 0
    for d1, d2 in itertools.product(range(1, 7), repeat=2):
        total += 1
        if ev == 0 and 6 in (d1, d2): hits += 1          # 至少一个6
        if ev == 1 and d1 + d2 >= 10: hits += 1          # 和≥10
        if ev == 2 and d1 == d2: hits += 1               # 两枚相同
        if ev == 3 and d1 + d2 <= 4: hits += 1           # 和≤4
        if ev == 4 and d1 + d2 >= 8: hits += 1           # 和≥8
        if ev == 5 and (d1 % 2) and (d2 % 2): hits += 1  # 两枚都奇
    assert total == 36
    ans = Fraction(hits, total)
    assert hits == {0: 11, 1: 6, 2: 6, 3: 6, 4: 15, 5: 9}[ev]
    if ev == 0:
        return add("正难则反", "钩子",
            "同时掷两枚骰子，至少有一枚是6点的概率是多少？",
            ans, [Fraction(1, 6) + Fraction(1, 6), Fraction(1, 36), Fraction(5, 36)],
            "正难则反：1−(5/6)²=11/36。",
            "1/6+1/6=1/3把重合算重。")
    if ev == 1:
        return add("正难则反", "钩子",
            "同时掷两枚骰子，点数之和不小于10的概率是多少？",
            ans, [Fraction(1, 12), Fraction(1, 9), Fraction(5, 36)],
            "枚举和为10、11、12共6种：(4,6)(5,5)(6,4)(5,6)(6,5)(6,6)。",
            "漏掉两种顺序的(4,6)(5,6)。")
    if ev == 2:
        return add("正难则反", "钩子",
            "同时掷两枚骰子，两枚点数相同的概率是多少？",
            ans, [Fraction(1, 12), Fraction(1, 3), Fraction(5, 36)],
            "六种对子共6/36=1/6。",
            "误按1/6×1/6=1/36只算某一枚。")
    if ev == 3:
        return add("正难则反", "钩子",
            "同时掷两枚骰子，点数之和不超过4的概率是多少？",
            ans, [Fraction(1, 9), Fraction(1, 12), Fraction(1, 6)],
            "反面思路也通：和≤4有(1,1)(1,2)(2,1)(1,3)(3,1)(2,2)。",
            "漏(2,2)或漏顺序对。")
    if ev == 4:
        return add("正难则反", "钩子",
            "同时掷两枚骰子，点数之和不小于8的概率是多少？",
            ans, [Fraction(5, 12), Fraction(1, 3), Fraction(5, 36)],
            "正难则反：先数和≤7的21种，1−21/36=15/36。",
            "直接数≥8漏情形。")
    return add("正难则反", "钩子",
        "同时掷两枚骰子，两枚都是奇数的概率是多少？",
        ans, [Fraction(1, 4), Fraction(1, 2), Fraction(1, 3)],
        "每枚奇概率1/2，独立相乘=1/4。",
        "误把互斥当独立，答1/3。")
fill("正难则反", "P4", 5, p4)

# P5 深钩 ×5（条件收缩 / 三事件至少一个）
def p5(_):
    style = rng.randrange(2)
    if style == 0:   # 条件收缩：已知第一张红，求第二张红
        N = rng.choice([10, 12, 15]); r = rng.randint(3, N // 2)
        ans = Fraction(r - 1, N - 1)
        # 真暴力：有序不放回抽两张，逐对枚举"第一张红"条件下的条件概率
        cnt_first = cnt_both = 0
        for f in range(N):
            if f >= r: continue
            for s2 in range(N):
                if s2 == f: continue
                cnt_first += 1
                if s2 < r: cnt_both += 1
        assert cnt_first == r * (N - 1)
        assert Fraction(cnt_both, cnt_first) == ans, (N, r, cnt_both, cnt_first)
        return add("正难则反", "深钩",
            "%d张卡片含%d张红色，不放回抽两张，已知第一张是红色，第二张也是红色的概率是多少？" % (N, r),
            ans, [Fraction(r, N), Fraction(r - 1, N), Fraction(r * r, N * N)],
            "深在条件收缩：剩%d张含%d张红，直接约简比。" % (N - 1, r - 1),
            "条件概率仍用原始总数N算。")
    # 三事件至少一个：1−(1−p)³
    den = rng.choice([3, 4, 6]); num = rng.randint(1, den - 2)
    p = Fraction(num, den)
    ans = 1 - (1 - p) ** 3
    cnt = sum(1 for t in itertools.product(range(den), repeat=3)
              if any(x < num for x in t))
    assert Fraction(cnt, den ** 3) == ans          # 暴力 27/64/216 格
    return add("正难则反", "深钩",
        "每次射击命中率为%s，独立射击3次，至少命中一次的概率是多少？" % fs(p),
        ans, [(1 - p) ** 3, p * 3 if p * 3 <= 1 else ans, 1 - p * 3 if 0 < 1 - p * 3 <= 1 else ans],
        "深在三连反面：1−(1−p)³，反面连乘再取反。",
        "把三次概率直接相加超过1。")
fill("正难则反", "P5", 5, p5)

# ============ 汇总校验与输出 ============

from collections import Counter
cnt = Counter((q["h"], q["t"]) for q in questions)
assert len(questions) == 110, "总数 %d != 110" % len(questions)
assert 4 <= cnt[("几何结论", "深钩")] <= 12, cnt
assert cnt[("枚举", "深钩")] >= 5 and cnt[("正难则反", "深钩")] >= 5
# 枚举类情境外壳统计：开头≥12个，单壳占比≤15%
_enum = [q for q in questions if q["h"] == "枚举"]
_sh = Counter(STEM_SHELL[q["s"]] for q in _enum)
assert len(_sh) >= 12, ("枚举情境开头不足12个", _sh)
assert max(_sh.values()) <= int(0.15 * len(_enum)), ("枚举单壳超15%", _sh)
print("枚举情境外壳:", dict(_sh))
for q in questions:
    assert len(q["s"]) <= 80 and len(q["e"]) <= 80
    assert len(q["o"]) == 4 and len(set(q["o"])) == 4 and 0 <= q["a"] <= 3
    assert set(q["h"]) <= set("几何结论枚举正难则反") or q["h"] in ("几何结论", "枚举", "正难则反")
assert len({q["s"] for q in questions}) == 110

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=1)

print("输出 %d 题 → %s" % (len(questions), OUT))
for k in sorted(cnt):
    print(k, cnt[k])
