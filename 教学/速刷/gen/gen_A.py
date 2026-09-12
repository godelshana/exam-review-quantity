# -*- coding: utf-8 -*-
"""
公考数量关系 参数化出题生成器 A
输出: gen_A_output.json  (UTF-8 无 BOM, json 数组, 共 130 题)
分类: 整除倍数×50 / 百分应用×45 / 中项挪补×35
硬规则: 独立暴力校验 + 唯一性检查 + 成因干扰项 + 固定种子可复现
"""
import json
import math
import random
from fractions import Fraction
from pathlib import Path

OUT = Path(__file__).with_name("gen_A_output.json")
rng = random.Random(20260909)

# 已有题目防撞（情境+数字相同的结构直接跳过）
BANNED = ["203", "172", "165", "135", "96元", "多2人", "少20%后为96"]


def R(n):
    return rng.randrange(n)


def pick(seq):
    return rng.choice(seq)


def finish(h, t, s, ans, ds, e, tr, checker):
    """组卷: 校验答案/干扰项/格式, 洗牌选项, 返回题dict"""
    assert len(s) <= 70, "题干超70字: " + s
    assert len(e) <= 80, "解析超80字: " + e
    ans = Fraction(ans)
    assert ans.denominator == 1, "答案非整数: " + s
    assert checker(ans), "答案未通过独立校验: " + s
    ds2, seen = [], set()
    for d in ds:
        d = Fraction(d)
        if d.denominator != 1 or d <= 0 or d == ans or d in seen:
            continue
        if checker(d):
            continue  # 成因值碰巧也合法, 弃用, 由备选补位
        ds2.append(int(d))
        seen.add(d)
        if len(ds2) == 3:
            break
    assert len(ds2) == 3, "成因干扰项不足3个: " + s
    opts = [int(ans)] + ds2
    rng.shuffle(opts)
    return {"h": h, "t": t, "s": s, "o": [str(o) for o in opts],
            "a": opts.index(int(ans)), "e": e, "tr": tr}


# ============================================================
# 整除倍数
# ============================================================

def T1():  # 钩子 分组余数: 总数 ≡ r (mod a)
    a = pick([4, 5, 6, 7, 8, 9])
    r = 1 + R(a - 1)
    k = 9 + R(20)
    n = a * k + r
    who = pick(["某班同学", "参训学员", "春游学生"])
    s = "%s按每%d人一组分组，最后多%d人。下列哪个数可能是总人数？" % (who, a, r)
    e = "整除钩：总人数减%d应能被%d整除，逐项看余数即可。" % (r, a)
    tr = "误选不含余数的整倍数，忽略“多%d人”条件。" % r

    def ck(v):
        return v % a == r
    ds = [n - r, a * k - r, n + r, a * k + r - 1]
    return finish("整除倍数", "钩子", s, n, ds, e, tr, ck)


def T2():  # 钩子 比例份数: 甲:乙=a:b, 共C, 求甲
    while True:
        a, b = rng.sample(range(2, 10), 2)
        if math.gcd(a, b) == 1:
            break
    u = 3 + R(15)
    jia, yi = u * a, u * b
    C = jia + yi
    s = "甲、乙两车间人数之比为%d:%d，两车间共%d人，甲车间有多少人？" % (a, b, C)
    e = "设份：共%d份=记%d人，1份=%d人，甲=%d份×%d。" % (a + b, C, u, a, u)

    def ck(v):
        return (C - v) * a == v * b and v > 0
    ds = [yi, jia + u, jia - u, jia + yi // a]
    return finish("整除倍数", "钩子", s, jia, ds, e, tr2_T2(b, u), ck)


def tr2_T2(b, u):
    return "方向看反误选乙车间%d；或漏除总份数。" % (u * b)


def T3():  # 双钩 同余: ≡r(mod x) 且 ≡r(mod y)
    x, y = 6, 9
    while True:
        x, y = rng.sample(range(4, 13), 2)
        L = x * y // math.gcd(x, y)
        if L <= 130:
            break
    r = 1 + R(min(x, y) - 1)
    k = 1 + R(3)
    n = L * k + r
    hi = L * (k + 1) + r + (3 + R(6))
    s = "一批货物每次运%d箱剩%d箱，每次运%d箱也剩%d箱。总数不超%d箱，可能是多少箱？" % (x, r, y, r, hi)
    e = "双钩：总数-%d同时被%d和%d整除，找公倍数再+%d。" % (r, x, y, r)

    def ck(v):
        return v % x == r and v % y == r
    ds = [n - r, y * k + r, x * k + r, n + x, n - y, n + r]
    return finish("整除倍数", "双钩", s, n, ds, e, "只满足其中一个除数条件，漏验第二个钩。", ck)


def T4():  # 钩子 占比份数: 占p/q者N人, 求总数
    while True:
        q = pick([6, 7, 8, 9, 11, 12])
        p = 2 + R(q - 3)
        if math.gcd(p, q) == 1 and p * 2 < q:
            break
    u = 3 + R(18)
    total, N = u * q, u * p
    who = pick(["读书会会员中", "俱乐部成员中", "公司员工中"])
    s = "%s喜欢户外运动的占%d/%d，已知喜欢户外运动的有%d人，问总人数？" % (who, p, q, N)
    e = "整除钩：总人数必被%d整除，%d÷%d×%d即得。" % (q, N, p, q)

    def ck(v):
        return v * p == N * q
    ds = [total + u, total - u, N * q, N * q // p]
    return finish("整除倍数", "钩子", s, total, ds, e, "把占比当除数用反，或误将N乘分母当总数。", ck)


def T5():  # 深钩 差占比: 占a/b, 多出N人, 求总数
    b = pick([6, 7, 8, 9, 10])
    a = b // 2 + 1 + R(max(1, b - b // 2 - 2))
    if a >= b or 2 * a - b <= 0:
        return None
    d = 2 * a - b
    u = 2 + R(12)
    total = u * b
    N = u * d
    who = pick(["合唱队人数占全班的", "报名春令营的人数占全班的", "参加体检的人数占全班的"])
    s = "%s%d/%d，参加的比没参加的多%d人，全班有多少人？" % (who, a, b, N)
    e = "深在先收口：差占%d/%d-%d/%d=%d/%d，N÷%d/%d即总数。" % (a, b, b - a, b, d, b, d, b)

    def ck(v):
        return v * d == N * b
    ds = [N * b // a, N * b // (b - a), total + N, N * b // d * 2]
    return finish("整除倍数", "深钩", s, total, ds, e, "拿N直接除参加占比，漏掉“差的占比”这一步。", ck)


def T6():  # 钩子 降价: 降p%后M元, 求原价
    p = pick([10, 15, 25, 30, 40, 50])
    u = 2 + R(15)
    orig = u * 100
    M = orig * (100 - p) // 100
    if orig * (100 - p) % 100:
        return None
    item = pick(["某商品", "一件外套", "某款台灯"])
    s = "%s降价%d%%后售价%d元，原价是多少元？" % (item, p, M)
    e = "现价是原价的%d/100，%d÷%d/100；原价必被100整除。" % (100 - p, M, 100 - p)

    def ck(v):
        return v * (100 - p) == 100 * M
    ds = [M * 100 // (100 + p), M + M * p // 100, orig * (100 - p) // 100 + u * 10, M]
    return finish("整除倍数", "钩子", s, orig, ds, e, "方向反：按涨价%d%%还原。" % p, ck)


def T7():  # 双钩 余一缺一: ≡r(mod x) 且 ≡ -s(mod y), 区间唯一
    x = pick([5, 6, 7, 8])
    y = pick([7, 8, 9, 10, 12])
    r = 1 + R(x - 1)
    ss = 1 + R(min(y, 4) - 1)
    L = x * y // math.gcd(x, y)
    n = L * (1 + R(6)) + [v for v in range(1, L) if v % x == r and (v + ss) % y == 0][0]
    if n <= 25:
        return None
    # 窗口宽 L-1, 恰含唯一解
    lo = n - R(min(12, L - 1))
    hi = lo + L - 1
    sols2 = [v for v in range(lo, hi + 1) if v % x == r and (v + ss) % y == 0]
    if sols2 != [n]:
        return None
    s = "学生若每%d人一组多%d人，每%d人一组少%d人。人数在%d~%d之间，共多少人？" % (x, r, y, ss, lo, hi)
    e = "双钩：n-%d被%d整除，且n+%d被%d整除，区间内逐一验证。" % (r, x, ss, y)

    def ck(v):
        return v % x == r and (v + ss) % y == 0
    ds = [n - r, n + ss, n + x, n - y]
    return finish("整除倍数", "双钩", s, n, ds, e, "只验证一个条件；“少%d人”应转化为加%d再整除。" % (ss, ss), ck)


def T8():  # 深钩 倍数传导: 甲:乙=a:b, 乙:丙=c:d, 丙N本, 求甲比丙多几本
    a, b = rng.sample(range(2, 6), 2)
    c, d = rng.sample(range(2, 6), 2)
    u = 1 + R(4)
    bing = d * b * u
    yi = c * b * u
    jia = a * c * u
    if jia <= bing:
        return None
    N = bing
    ans = jia - bing
    s = "甲的藏书是乙的%d/%d，乙是丙的%d/%d，丙有%d本，甲比丙多几本？" % (a, b, c, d, N)
    e = "深在传导+收口：先由丙得乙=%d本，再得甲=%d本，最后作差%d。" % (yi, jia, ans)
    # 独立校验: 分数链逐步复算
    y2 = Fraction(N) * c / d
    j2 = y2 * a / b
    assert y2.denominator == 1 and j2.denominator == 1 and j2 - N == ans

    def ck(v):
        yv = Fraction(N) * c / d
        jv = yv * a / b
        return yv.denominator == 1 and jv.denominator == 1 and jv - N == v
    ds = [jia, yi, jia - yi, ans + bing // 2]
    return finish("整除倍数", "深钩", s, ans, ds, e, "算出甲就选，忘了问的是“比丙多几本”。", ck)


# ============================================================
# 百分应用
# ============================================================

def P1():  # 钩子 涨价: 涨a%后N元, 求原价
    a = pick([10, 15, 25, 40, 50])
    u = 2 + R(15)
    orig = u * 100
    N = orig * (100 + a) // 100
    item = pick(["某商品", "某款手机", "一门课程学费"])
    s = "%s涨价%d%%后需%d元，涨价前是多少元？" % (item, a, N)
    e = "现价是原价的%d/100，%d÷%d/100即原价。" % (100 + a, N, 100 + a)

    def ck(v):
        return v * (100 + a) == 100 * N
    ds = [orig * (100 - a) // 100, N - u * a, N + u * a, N * (100 - a) // 100]
    return finish("百分应用", "钩子", s, orig, ds, e, "方向反：错除以(1-a%)按降价还原。", ck)


def P2():  # 钩子 利润: 成本C, 加价a%, 打b折, 求售价
    a = pick([20, 25, 40, 50, 60, 80])
    bb = pick([7, 8, 9])
    u = 1 + R(6)
    C = u * 100
    price = C * (100 + a) // 100
    sale = price * bb // 10
    if C * (100 + a) % 100 or price * bb % 10:
        return None
    s = "某商品成本%d元，按加价%d%%定价，再打%d折出售，售价多少元？" % (C, a, bb)
    e = "成本×(1+%d%%)=定价%d，再×%d/10=%d，两步口算。" % (a, price, bb, sale)
    # 独立校验: 分数逐步复算
    assert Fraction(C, 1) * (100 + a) / 100 * bb / 10 == sale

    def ck(v):
        return Fraction(C, 1) * (100 + a) / 100 * bb / 10 == v
    ds = [price, sale // bb, price - (price - sale), sale - u * 20]
    return finish("百分应用", "钩子", s, sale, ds, e, "打折基准错用成本，或漏打折扣直接选定价。", ck)


def P3():  # 钩子 合格占比: 共M件, 合格p/q, 求不合格
    while True:
        q = pick([6, 7, 8, 9, 12])
        p = q - 1 - R(max(1, q // 3))
        if math.gcd(p, q) == 1 and 0 < p < q:
            break
    u = 3 + R(20)
    M = u * q
    ok = u * p
    bad = M - ok
    s = "质检抽查%d件产品，合格的占%d/%d，不合格的有多少件？" % (M, p, q)
    e = "不合格占%d/%d，%d÷%d×%d即得。" % (q - p, q, M, q, q - p)

    def ck(v):
        return v + Fraction(M) * p / q == M
    ds = [ok, bad + u, ok - u, M * (q - p) // p]
    return finish("百分应用", "钩子", s, bad, ds, e, "方向反：误求合格数%d。" % ok, ck)


def P3D():  # 深钩 合格差: 合格比不合格多N件, 求总数
    while True:
        q = pick([6, 7, 8, 9, 10, 12])
        p = q // 2 + 1
        if p < q and math.gcd(p, q) == 1:
            break
    d = 2 * p - q
    u = 3 + R(15)
    M = u * q
    N = u * d
    s = "抽查一批零件，合格的占%d/%d，合格比不合格多%d件，共抽查多少件？" % (p, q, N)
    e = "深在收口：差占%d/%d-%d/%d=%d/%d，%d÷%d/%d。" % (p, q, q - p, q, d, q, N, d, q)

    def ck(v):
        return v * d == N * q
    ds = [N * q // p, N * q // (q - p), M + N, N * q]
    return finish("百分应用", "深钩", s, M, ds, e, "拿N除合格占比，漏“差=占比差”这一步。", ck)


def P4():  # 钩子 占比: 男占a%, 男N人, 求总数
    a = pick([30, 40, 45, 55, 60, 70])
    u = 2 + R(15)
    total = u * 100
    N = u * a
    s = "某公司男员工占%d%%，男员工有%d人，公司共有多少名员工？" % (a, N)
    e = "%d÷%d%%即÷%d/100；总数必被100整除。" % (N, a, a)

    def ck(v):
        return v * a == 100 * N
    ds = [total + u, total - u, 100 * N // (100 - a), N * 100 // a + u]
    return finish("百分应用", "钩子", s, total, ds, e, "错用女工占比(1-a%)去除。", ck)


def P5():  # 钩子 涨降链: 涨a%再降b%, 现价M, 求原价
    a = pick([10, 20, 25])
    b = pick([10, 20, 25])
    k = (100 + a) * (100 - b)
    g = math.gcd(k, 10000)
    step = 10000 // g
    base = step * (2 + R(6))
    if base > 9999:
        return None
    M = base * k // 10000
    s = "某股票先上涨%d%%，再下跌%d%%，现价%d元，上涨前价格是多少元？" % (a, b, M)
    e = "现价=原价×(%d/100)(%d/100)，反除两步即得。" % (100 + a, 100 - b)
    # 独立校验: 分数逐步复算
    v2 = Fraction(base) * (100 + a) / 100
    v3 = v2 * (100 - b) / 100
    assert v3.denominator == 1 and v3 == M

    def ck(v):
        w = Fraction(v) * (100 + a) / 100
        w2 = w * (100 - b) / 100
        return w2.denominator == 1 and w2 == M
    ds = [M * 100 // (100 + a), M * 100 // (100 - b),
          M * 10000 // ((100 - a) * (100 + b)), M + base // 10]
    return finish("百分应用", "钩子", s, base, ds, e, "两步基准混用：降幅错用涨价后的价。", ck)


def P6():  # 深钩 百分链: A比B少a%, B比C多b%, A是C的百分之几
    pairs = [(20, 25, 100), (25, 20, 90), (50, 50, 75), (20, 50, 120),
             (40, 100, 120), (60, 100, 80), (10, 100, 99)]
    a, b, _ = pick(pairs)
    ans = (100 - a) * (100 + b) // 100
    if (100 - a) * (100 + b) % 100:
        return None
    s = "A公司人数比B公司少%d%%，B公司比C公司多%d%%，A是C的百分之几？" % (a, b)
    e = "深在传导：设C为100，B=%d，A=%d，即%d%%。" % (100 + b, ans, ans)
    # 独立校验: 实例化
    C = 200
    B = C * (100 + b) // 100
    A = B * (100 - a) // 100
    assert A * 100 == C * ans

    def ck(v):
        return A * 100 == C * v
    ds = [100 - a + b, 100 - a - b // 2, (100 + a) * (100 - b) // 100,
          ans + 10, 100 - a, (100 + a) * (100 + b) // 100]
    return finish("百分应用", "深钩", s, ans, ds, e, "百分点直接加减(%d)，忽略基准不同。" % (100 - a + b), ck)


# ============================================================
# 中项挪补
# ============================================================

def M1():  # 钩子 连续数之和: n个连续(奇/偶/自然)数和S, 求最大/中项
    kind = pick(["连续自然数", "连续奇数", "连续偶数"])
    step = 1 if kind == "连续自然数" else 2
    n = pick([5, 7, 9])
    mid = 30 + R(60)
    if step == 2:  # 奇数列中项须奇, 偶数列中项须偶
        mid = mid + 1 if mid % 2 != (0 if kind == "连续偶数" else 1) else mid
    small = mid - (n // 2) * step
    if small <= 0:
        return None
    S = n * mid
    ask = pick(["最大", "中项"])
    ans = mid + (n // 2) * step if ask == "最大" else mid
    what = {"连续自然数": "个连续自然数", "连续奇数": "个连续奇数", "连续偶数": "个连续偶数"}[kind]
    s = "已知%d%s的和是%d，其中%s的是多少？" % (n, what, S, ask)
    e = "中项=S÷%d=%d，最大数=中项+%d×%d。" % (n, mid, step, n // 2)
    # 独立校验: 暴力枚举首项, 唯一性
    sols = [f for f in range(0, 500) if sum(f + step * i for i in range(n)) == S]
    assert sols == [small]

    if ask == "最大":
        def ck(v):
            return sum(v - step * i for i in range(n)) == S
    elif ask == "最小":
        def ck(v):
            return sum(v + step * i for i in range(n)) == S
    else:
        def ck(v):
            return sum(v + step * (i - n // 2) for i in range(n)) == S
    ds = [mid, ans - step, mid - (n // 2) * step, ans + step]
    return finish("中项挪补", "钩子", s, ans, ds, e, "忘加(n-1)/2收口，或奇偶数步长当1。", ck)


def M2():  # 钩子 a_m+a_k=2*a_mid, 求前n项和 (m+k=n+1)
    n = pick([9, 11, 13])
    mid = 10 + R(40)
    X = 2 * mid
    half = [i for i in range(2, n) if i < n + 1 - i][0:1]
    m = pick(range(2, n))  # 1<=m<k<=n
    k = n + 1 - m
    if k <= m:
        return None
    S = n * mid
    s = "等差数列{an}中，a%d+a%d=%d，则其前%d项和S%d等于多少？" % (m, k, X, n, n)
    e = "a%d+a%d=2a%d，中项a%d=%d，S%d=%d×%d。" % (m, k, (n + 1) // 2, (n + 1) // 2, mid, n, n, mid)
    # 独立校验: 两组不同(a1,d)实例化, 和必相同
    for a1 in (0, 3, -5):
        d = Fraction(mid - a1, (n + 1) // 2 - 1)
        s2 = sum(a1 + d * i for i in range(n))
        assert s2.denominator == 1 and s2 == S

    def ck(v):
        return v == S
    ds = [mid, X, S - n, S + n, mid * (n - 2)]
    return finish("中项挪补", "钩子", s, S, ds, e, "只求出中项就选，漏乘项数n。", ck)


def M3():  # 钩子 情境连续数: 排座/台阶/楼层等差, 求中间或端点
    sc = pick([
        ("某影厅一排共%d个座位，座位号是连续奇数，最中间的座号是几？", "中项"),
        ("一串彩灯编号为连续偶数，共%d盏，编号和为%d，第一盏编号是几？", "最小"),
        ("%d名队员年龄恰为连续奇数，年龄总和%d岁，队长(年龄最大)多少岁？", "最大"),
    ])
    kind = "奇" if "奇" in sc[0] else "偶"
    step = 2
    n = pick([5, 7])
    mid = 25 + R(50)
    mid = mid + 1 if mid % 2 != (0 if kind == "偶" else 1) else mid
    small = mid - (n // 2) * step
    big = mid + (n // 2) * step
    S = n * mid
    txt, ask = sc
    s = txt % (n, S) if "%d" in txt and txt.count("%d") == 2 else txt % (n,)
    if txt.count("%d") == 2:
        s = txt % (n, S)
    else:
        s = txt % (n,)
    ans = {"中项": mid, "最小": small, "最大": big}[ask]
    # 独立校验: 暴力枚举首项唯一
    sols = [f for f in range(0, 400) if sum(f + step * i for i in range(n)) == S]
    assert sols == [small]

    if ask == "最大":
        def ck(v):
            return sum(v - step * i for i in range(n)) == S
    elif ask == "最小":
        def ck(v):
            return sum(v + step * i for i in range(n)) == S
    else:
        def ck(v):
            return sum(v + step * (i - n // 2) for i in range(n)) == S
    e = "和%d=中项%d×%d，%s=中项%+d。" % (S, mid, n, ask, ans - mid)
    ds = [mid, mid - step, big, small, ans + 2 * step]
    return finish("中项挪补", "钩子", s, ans, ds, e, "直接拿和除以2或忘挪补到端点。", ck)


def M4():  # 深钩 连续奇数+下一项
    n = pick([5, 7, 9])
    mid = 20 + 2 * R(25) + 1  # 奇数列中项须为奇
    step = 2
    S = n * mid
    nxt = mid + (n // 2 + 1) * step
    ans = S + nxt
    s = "%d个连续奇数之和为%d，再添上下一个连续奇数后，总和是多少？" % (n, S)
    e = "深在收口：中项%d，下一项=中项+%d×%d=%d，S+它。" % (mid, step, n // 2 + 1, nxt)
    # 独立校验: 暴力重建数列
    sols = [f for f in range(1, 300, 2) if sum(f + 2 * i for i in range(n)) == S]
    assert len(sols) == 1
    seq = [sols[0] + 2 * i for i in range(n)]
    assert seq[-1] + 2 == nxt and S + nxt == ans

    def ck(v):
        f = (v - S)
        return v - S > 0 and f - (sols[0] + 2 * n) == 0
    ds = [S + 2, S + mid + (n // 2) * step, S + n, ans - 2]
    return finish("中项挪补", "深钩", s, ans, ds, e, "下一项错当最大数加，或步长按1算。", ck)


def M5():  # 深钩 逆向收口: 前n项和S与公差d, 反求某项
    n = pick([7, 9])
    q = 3  # 求a3
    mid = 20 + R(40)
    d = pick([2, 3, 4, 5])
    S = n * mid
    a3 = mid + (3 - (n + 1) // 2) * d
    if a3 <= 0:
        return None
    s = "等差数列前%d项和为%d，公差为%d，则a3是多少？" % (n, S, d)
    e = "深在逆向：中项=S÷%d=%d，a3=中项-2×%d=%d。" % (n, mid, d, a3)
    # 独立校验: 由a3与d重建数列求和
    a1 = a3 - 2 * d
    assert a1 > 0 and sum(a1 + d * i for i in range(n)) == S

    def ck(v):
        a1v = v - 2 * d
        return a1v > 0 and sum(a1v + d * i for i in range(n)) == S
    ds = [mid, a3 + 2 * d, a3 - d, S // n - d]
    return finish("中项挪补", "深钩", s, a3, ds, e, "挪补方向反：错加2d得%d。" % (a3 + 2 * d), ck)


# ============================================================
# 驱动
# ============================================================

PLAN = [
    # (生成函数, 目标数量)
    (T1, 10), (T2, 10), (T4, 8), (T6, 6),          # 整除 钩子 34
    (T3, 4), (T7, 4),                               # 整除 双钩 8
    (T5, 4), (T8, 4),                               # 整除 深钩 8
    (P1, 8), (P2, 8), (P3, 6), (P4, 8), (P5, 8),    # 百分 钩子 38
    (P3D, 3), (P6, 4),                              # 百分 深钩 7
    (M1, 12), (M2, 8), (M3, 10),                    # 中项 钩子 30
    (M4, 3), (M5, 2),                               # 中项 深钩 5
]


def main():
    questions, seen = [], set()
    for func, quota in PLAN:
        got, tries = 0, 0
        while got < quota:
            tries += 1
            assert tries < 8000, "模板 %s 无法凑齐 %d 题" % (func.__name__, quota)
            try:
                q = func()
            except AssertionError:
                raise
            except Exception:
                q = None
            if q is None:
                continue
            if any(b in q["s"] for b in BANNED):
                continue
            if q["s"] in seen:
                continue
            assert len(q["o"]) == 4 and len(set(q["o"])) == 4
            assert 0 <= q["a"] <= 3
            assert len(q["e"]) <= 80 and len(q["s"]) <= 70
            seen.add(q["s"])
            questions.append(q)
            got += 1
    # 汇总校验
    assert len(questions) == 130, "总题数 %d != 130" % len(questions)
    from collections import Counter
    ch = Counter(q["h"] for q in questions)
    ct = Counter((q["h"], q["t"]) for q in questions)
    assert ch["整除倍数"] == 50 and ch["百分应用"] == 45 and ch["中项挪补"] == 35, ch
    assert ct[("整除倍数", "双钩")] == 8 and ct[("整除倍数", "深钩")] == 8, ct
    assert ct[("百分应用", "深钩")] == 7 and ct[("中项挪补", "深钩")] == 5, ct
    OUT.write_text(json.dumps(questions, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print("OK 130题 ->", OUT)
    print("分类:", dict(ch))
    print("题型:", {("%s|%s" % k): v for k, v in sorted(ct.items())})


if __name__ == "__main__":
    main()
