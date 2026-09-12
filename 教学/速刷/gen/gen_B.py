# -*- coding: utf-8 -*-
"""自编练习题生成器 B：奇偶 / 尾数 / 估算，共 100 题，全部带独立暴力校验。"""
import json
import math
import random

rng = random.Random(20260909)
OUT = r"E:\codeBase\examReview\教学\速刷\gen\gen_B_output.json"

PARITY_OPTS = ["奇数", "偶数", "无法确定", "奇偶性随具体数值变化"]
# 余0=偶、余1=奇（修复：原 PARITY_OPTS[s%2] 把偶映射成"奇数"）
PARITY_BY_MOD = {0: "偶数", 1: "奇数"}


def shuffle_opts(ans, dists):
    dists = [d for d in dists if d != ans]
    assert len(dists) >= 3, (ans, dists)
    opts = list(dists[:3]) + [ans]
    assert len(set(opts)) == 4, (ans, dists)
    rng.shuffle(opts)
    return opts, opts.index(ans)


def parity_opts(ans):
    """取其余三个奇偶类选项作干扰项。"""
    return [o for o in PARITY_OPTS if o != ans]


def make(qid, h, t, s, opts, a, e, tr):
    return {"h": h, "t": t, "s": s, "o": opts, "a": a, "e": e, "tr": tr}


def fmt(v):
    v = round(v, 2)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ("%.2f" % v).rstrip("0").rstrip(".")


# 情境外壳机制：同一类题用不同情境开头，防模板单调（每壳计数均衡）
SHELL_USE = {}
STEM_SHELL = {}


def pick_shell(sids):
    """sids: 候选壳 id 列表，返回当前使用次数最少的壳 id。"""
    return min(sids, key=lambda x: (SHELL_USE.get(x, 0), sids.index(x)))


def mark_shell(sid, stem, ok):
    if ok:
        SHELL_USE[sid] = SHELL_USE.get(sid, 0) + 1
        STEM_SHELL[stem] = sid


def sig2(v):
    if v == 0:
        return 0
    d = math.floor(math.log10(abs(v)))
    return round(v, -(d - 1))


def est_pack(V, ans, dists):
    """估算题打包：答案必须是最接近真值的选项，且第二接近距离 > 1.5 倍。"""
    vals = [ans] + list(dists)
    if len(set(vals)) < 4:
        return None
    ds = [abs(v - V) for v in vals]
    i = min(range(4), key=lambda j: ds[j])
    if i != 0 or abs(ds[0]) < 1e-12:
        return None
    rest = sorted(ds)[1]
    if rest <= 1.5 * ds[0]:
        return None
    if ds[0] > 0.06 * abs(V):
        return None
    strs = [fmt(v) for v in vals]
    if len(set(strs)) < 4:
        return None
    order = [0, 1, 2, 3]
    rng.shuffle(order)
    opts = [strs[j] for j in order]
    return opts, opts.index(strs[0])


# ---------------- 奇偶 ----------------

def p1_cont_range():  # 区间整数和的奇偶
    m = rng.randint(3, 40)
    n = m + rng.randint(6, 30)
    s = sum(range(m, n + 1))          # 暴力：直接求和
    assert s == (m + n) * (n - m + 1) // 2          # 等差公式独立复算
    nodd = sum(1 for x in range(m, n + 1) if x % 2)  # 奇数项个数
    assert s % 2 == nodd % 2                        # 和的奇偶=奇数个数的奇偶
    ans = PARITY_BY_MOD[s % 2]
    opts, a = shuffle_opts(ans, parity_opts(ans))
    s_txt = (f"从{m}到{n}的所有整数之和是（　）。")
    return make(0, "奇偶", "钩子", s_txt, opts, a,
                f"暴力求和={s}，为{'偶' if s%2==0 else '奇'}数。快路：数清奇数的个数，奇数个奇数相加为奇。",
                "多数考生逐个加和浪费时间，或误以为连续数之和必为偶。")

def p2_sum_of_odds():  # 若干个奇数之和
    k = rng.randint(4, 9)
    odds = [rng.randrange(1, 99, 2) for _ in range(k)]
    total = sum(odds)                 # 暴力：构造具体奇数求和
    assert total % 2 == k % 2
    ans = PARITY_BY_MOD[total % 2]
    opts, a = shuffle_opts(ans, parity_opts(ans))
    s_txt = f"{k}名选手每人答对的题数都是奇数，他们答对题数的总和（　）。"
    return make(0, "奇偶", "钩子", s_txt, opts, a,
                f"{k}个奇数之和为{total}。快路：k个奇数之和的奇偶性只由k决定，k={k}为{'奇' if k%2 else '偶'}数。",
                "误以为与每人具体题数有关，其实与具体数值无关。")

def p3_two_primes_even_sum():  # 两质数和为偶 → 积为奇
    S = rng.choice([14, 18, 22, 24, 28, 30, 34, 36, 40, 42, 46])
    pairs = [(p, S - p) for p in range(3, S // 2 + 1)
             if all(p % i for i in range(2, int(p ** .5) + 1))
             and all((S - p) % i for i in range(2, int((S - p) ** .5) + 1))]
    assert pairs and all((p % 2 and q % 2) for p, q in pairs)
    for p, q in pairs[:1]:
        assert (p * q) % 2 == 1
    ans = "奇数"
    opts, a = shuffle_opts(ans, ["偶数", "无法确定", "取决于两数大小"])
    s_txt = f"两个大于2的质数之和为{S}，它们的乘积一定是（　）。"
    return make(0, "奇偶", "钩子", s_txt, opts, a,
                "和为偶，2不能入选，两质数均为奇数，奇×奇=奇。",
                "忽略\"大于2\"条件时2可能混入，错选无法确定。")

def p4_parity_chain():  # 奇偶传递
    x = rng.randrange(3, 29, 2)
    y = rng.randint(2, 15) * 2
    a_ = rng.randrange(1, 9, 2)
    forms = [
        (f"{x}×{y}+{x}", lambda: x * y + x),
        (f"{x}×{y}+{y}", lambda: x * y + y),
        (f"{x}×{a_}+{y}", lambda: x * a_ + y),
        (f"{x}²+{y}²", lambda: x * x + y * y),
        (f"{x}×{y}−{x}+{y}", lambda: x * y - x + y),
    ]
    txt, fn = rng.choice(forms)
    val = abs(fn())
    expr = txt.replace("²", "**2").replace("×", "*").replace("−", "-")
    assert val == abs(eval(expr))     # 按题面字面式子独立复算
    ans = PARITY_BY_MOD[val % 2]
    opts, ai = shuffle_opts(ans, parity_opts(ans))
    s_txt = f"已知甲={x}，乙={y}，则式子 {txt} 的结果是（　）。"
    return make(0, "奇偶", "钩子", s_txt, opts, ai,
                f"直接按奇偶传递：结果为{val}，是{'奇' if val%2 else '偶'}数，无需精算数值。",
                "减奇加奇同号看反，导致奇偶判断颠倒。")

def p5_prime_pair_odd_sum():  # 深钩：和为奇 → 必有2
    S = rng.choice([s for s in (29, 31, 37, 41, 43, 47, 53, 59, 61, 67)
                    if all((s - 2) % i for i in range(2, int((s - 2) ** .5) + 1))])
    q = S - 2
    assert all(q % i for i in range(2, int(q ** .5) + 1)), S
    prod = 2 * q
    assert prod % 2 == 0
    opts, a = shuffle_opts(prod, [q, S, q - 2])
    s_txt = f"已知p、q均为质数，且p+q={S}，则p×q的值为（　）。"
    return make(0, "奇偶", "深钩", s_txt, opts, a,
                f"和为奇必一奇一偶，偶质数只有2，故q={q}，积={prod}。先定2再回代验质。",
                "漏用\"和为奇⇒含2\"的锁定，四下去猜；或把和当积错选。")

def p6_consec_odds_sum():  # 深钩：连续奇数和求最大
    n = rng.choice([5, 7])
    mid = rng.randrange(11, 49, 2)
    S = n * mid
    start = mid - (n - 1)
    assert start > 0 and sum(range(start, mid + n, 2)) == S
    mx = mid + (n - 1)
    opts, a = shuffle_opts(mx, [mid, mx - 2, mx + 2])
    s_txt = f"{n}个连续奇数之和为{S}，其中最大的奇数是（　）。"
    return make(0, "奇偶", "深钩", s_txt, opts, a,
                f"和÷个数={mid}为中项，最大=中项+{n-1}={mx}。由和先定中项再向两端展开。",
                "把中项当最大项，是本考点最常见失误。")

def p7_divisor_count():  # 深钩：完全平方数约数个数为奇
    k = rng.randint(4, 15)
    n = k * k
    cnt = sum(1 for i in range(1, n + 1) if n % i == 0)  # 暴力枚举
    assert cnt % 2 == 1
    opts, a = shuffle_opts(cnt, [cnt - 2, cnt + 2, cnt + 4])
    s_txt = f"正整数{n}的正约数共有多少个？（　）"
    return make(0, "奇偶", "深钩", s_txt, opts, a,
                f"{n}={k}²是完全平方数，约数成对出现仅√n落单，故个数为奇数{cnt}。",
                "漏数1和n本身，或不知平方数约数个数为奇。")


# ---------------- 尾数 ----------------

def w1_poly_units():
    sid = pick_shell(["w1a", "w1b", "w1c", "w1d", "w1e"])
    if sid == "w1e":  # 平方差外壳
        a, c = rng.randint(12, 99), rng.randint(12, 99)
        if a == c:
            return None
        u = (a * a - c * c) % 10
        assert u == ((a % 10) ** 2 - (c % 10) ** 2) % 10
        s_txt = f"{a}²−{c}² 的计算结果的个位数字是（　）。"
        e_txt = f"只取个位：{a%10}²−{c%10}² 的个位为{u}。"
    else:
        a, b = rng.randint(12, 99), rng.randint(12, 99)
        c, d = rng.randint(12, 99), rng.randint(12, 99)
        if a * b < c * d:
            a, b, c, d = c, d, a, b
        u = (a * b - c * d) % 10
        assert u == ((a % 10) * (b % 10) - (c % 10) * (d % 10)) % 10
        stems = {
            "w1a": f"{a}×{b}−{c}×{d} 的计算结果的个位数字是（　）。",
            "w1b": f"甲车间每天生产{a}个零件，生产了{b}天；乙车间每天生产{c}个，生产了{d}天。两车间产量之差的个位数字是（　）。",
            "w1c": f"影院甲厅有{a}排、每排{b}座，乙厅有{c}排、每排{d}座。两厅容量之差的个位数字是（　）。",
            "w1d": f"苹果每箱{a}元共买{b}箱，梨每箱{c}元共买{d}箱，两笔货款之差的个位数字是（　）。",
        }
        s_txt = stems[sid]
        e_txt = f"只取个位：{a%10}×{b%10}−{c%10}×{d%10} 的个位为{u}。"
    dists = [x for x in ((u + 1) % 10, (u + 5) % 10, (u - 1) % 10) if x != u]
    while len(set(dists)) < 3:
        cand = rng.randint(0, 9)
        if cand != u and cand not in dists:
            dists.append(cand)
    opts, ai = shuffle_opts(u, dists)
    q = make(0, "尾数", "钩子", s_txt, opts, ai, e_txt,
             "减法借位不影响个位差，但直接丢弃负号会出错。")
    mark_shell(sid, s_txt, q is not None)
    return q


def w2_power_units():
    base = rng.choice([3, 4, 7, 8, 9, 12, 13, 17, 18, 19])
    e = rng.randint(15, 60)
    u = pow(base, e, 10)
    cyc = []
    v = 1
    for i in range(1, 5):
        v = (base % 10) ** i % 10
        if v not in cyc:
            cyc.append(v)
    dists = [c for c in cyc if c != u][:3]
    filler = rng.randint(0, 9)
    while len(set(dists)) < 3:
        if filler != u and filler not in dists:
            dists.append(filler)
        filler = (filler + 1) % 10
    # 独立校验：逐次乘法模拟（非 pow 同式复算）
    sim = 1
    for _ in range(e):
        sim = sim * base % 10
    assert sim == u
    sid = pick_shell(["w2a", "w2b", "w2c", "w2d"])
    stems = {
        "w2a": f"{base}^{e} 的个位数字是（　）。",
        "w2b": f"某种细胞每分钟都由1个分裂成{base}个，{e}分钟后细胞总数的个位数字是（　）。",
        "w2c": f"已知等比数列首项为1、公比为{base}，则其第{e}项的个位数字是（　）。",
        "w2d": f"一条消息每转发一轮数量就变为原来的{base}倍，{e}轮后数量的个位数字是（　）。",
    }
    s_txt = stems[sid]
    opts, ai = shuffle_opts(u, dists)
    q = make(0, "尾数", "钩子", s_txt, opts, ai,
             f"{base%10}的幂个位以{len(cyc)}为周期循环，{e}≡{e%len(cyc) or len(cyc)}(mod {len(cyc)})，个位为{u}。",
             "周期取错或余数为0时忘记取周期末位。")
    mark_shell(sid, s_txt, q is not None)
    return q


def w3_factorial_units():
    k1 = rng.randint(2, 4)
    k2 = rng.randint(8, 12)
    if (k1, k2) == (1, 10):
        k2 = 11
    total = sum(math.factorial(i) for i in range(k1, k2 + 1))
    u = total % 10
    assert u == (sum(math.factorial(i) for i in range(k1, min(k2, 4) + 1))) % 10
    dists = [x for x in (math.factorial(k1) % 10, (u + 3) % 10, (u + 7) % 10) if x != u]
    while len(set(dists)) < 3:
        cand = rng.randint(0, 9)
        if cand != u and cand not in dists:
            dists.append(cand)
    opts, ai = shuffle_opts(u, dists)
    sid = pick_shell(["w3a", "w3b", "w3c"])
    stems = {
        "w3a": f"{k1}!+{k1+1}!+…+{k2}! 的个位数字是（　）。",
        "w3b": f"已知 S={k1}!+{k1+1}!+…+{k2}!，则 S 的个位数字是（　）。",
        "w3c": f"数学兴趣小组计算阶乘和 {k1}!+{k1+1}!+…+{k2}!，所得结果的个位数字是（　）。",
    }
    s_txt = stems[sid]
    q = make(0, "尾数", "钩子", s_txt, opts, ai,
             f"5!起个位全为0，只需算{k1}!到4!之和的个位={u}。",
             "硬算到高阶阶乘浪费时间，或忘了5!以后个位为0。")
    mark_shell(sid, s_txt, q is not None)
    return q


def w4_money_units():
    n = rng.choice([12, 16, 18, 24, 25, 30, 36])
    m = rng.randint(3, 9)
    k = rng.randint(23, 88)
    total = n * m * k
    # 独立校验：逐箱累加复算 + 尾数交叉验证
    brute = 0
    for _ in range(k):
        brute += n * m
    assert brute == total
    assert total % 10 == (n * m % 10) * (k % 10) % 10
    dists = [total - n * m, total + n * m, total - m * 10]
    dists = [d for d in dists if d > 0]
    opts, ai = shuffle_opts(total, dists)
    sid = pick_shell(["w4a", "w4b", "w4c", "w4d", "w4e"])
    units = {
        "w4a": ("瓶", "饮料每箱{n}瓶，每瓶{m}元，某单位采购{k}箱，共需付款多少元？（　）"),
        "w4b": ("本", "笔记本每包{n}本，每本{m}元，学校统一采购{k}包，共需付款多少元？（　）"),
        "w4c": ("块", "巧克力礼盒每盒{n}块，每块{m}元，某公司订{k}盒作为年会礼品，共需付款多少元？（　）"),
        "w4d": ("枚", "螺丝每盒{n}枚，每枚{m}元，工地采购{k}盒，共需付款多少元？（　）"),
        "w4e": ("张", "贴纸每卷{n}张，每张{m}元，文具店到货{k}卷全部按包售出，共可收款多少元？（　）"),
    }
    s_txt = units[sid][1].format(n=n, m=m, k=k)
    q = make(0, "尾数", "钩子", s_txt, opts, ai,
             f"{n}×{m}={n*m}，{n*m}×{k}={total}元；用尾数即可锁定选项。",
             "少乘一箱或漏乘瓶数，恰对应错误选项。")
    mark_shell(sid, s_txt, q is not None)
    return q


def w5_two_powers_sum():
    b1, b2 = rng.sample([2, 3, 4, 6, 7, 8, 9, 11, 13], 2)
    e1, e2 = rng.randint(9, 30), rng.randint(9, 30)
    u = (pow(b1, e1, 10) + pow(b2, e2, 10)) % 10
    assert u == (pow(b1, e1) + pow(b2, e2)) % 10
    dists = [x for x in ((u + 1) % 10, (u + 6) % 10, (u + 4) % 10) if x != u]
    while len(set(dists)) < 3:
        cand = rng.randint(0, 9)
        if cand != u and cand not in dists:
            dists.append(cand)
    opts, ai = shuffle_opts(u, dists)
    sid = pick_shell(["w5a", "w5b", "w5c"])
    stems = {
        "w5a": f"{b1}^{e1}+{b2}^{e2} 的个位数字是（　）。",
        "w5b": f"两个等比数列首项均为1，公比分别为{b1}和{b2}，取它们各自的第{e1}项与第{e2}项相加，和的个位数字是（　）。",
        "w5c": f"两瓶细菌初始均为1个，甲瓶每分钟分裂为{b1}个，乙瓶每分钟分裂为{b2}个。甲瓶培养{e1}分钟、乙瓶培养{e2}分钟，两瓶数量之和的个位数字是（　）。",
    }
    s_txt = stems[sid]
    q = make(0, "尾数", "深钩", s_txt, opts, ai,
             f"分别定个位（{b1%10}^…个位与{b2%10}^…个位）再相加取个位={u}，两次循环叠加。",
             "只算一个幂的个位，或两幂相加后忘记再取个位。")
    mark_shell(sid, s_txt, q is not None)
    return q


def w6_power_minus_factorial():
    b = rng.choice([3, 7, 8, 9, 12, 17])
    e = rng.randint(7, 25)
    k = rng.randint(5, 9)
    u = (pow(b, e, 10) - math.factorial(k)) % 10
    assert u == (pow(b, e) - math.factorial(k)) % 10
    dists = [x for x in ((u + 2) % 10, (u + 5) % 10, (u - 3) % 10) if x != u]
    while len(set(dists)) < 3:
        cand = rng.randint(0, 9)
        if cand != u and cand not in dists:
            dists.append(cand)
    opts, ai = shuffle_opts(u, dists)
    sid = pick_shell(["w6a", "w6b"])
    stems = {
        "w6a": f"{b}^{e}−{k}! 的个位数字是（　）。",
        "w6b": f"某程序先算出 {b}^{e}，再从中减去 {k}!，所得结果的个位数字是（　）。",
    }
    s_txt = stems[sid]
    q = make(0, "尾数", "深钩", s_txt, opts, ai,
             f"{k}!含2×5因子个位必为0，故个位即{b}^{e}的个位={u}。深在识破阶乘项归零。",
             "给阶乘项强行算个位再相减，反而出错。")
    mark_shell(sid, s_txt, q is not None)
    return q


# ---------------- 估算 ----------------

def g1_big_product():
    a = rng.randrange(2100, 8800, 10)
    b = rng.randrange(23, 89)
    V = a * b
    ans = sig2(V)
    # 干扰项：同量级的错误估算（零件数/单件利润各自估偏约一成）
    dists = [(a + a // 12) * b, a * (b + max(2, b // 10)), (a - a // 9) * b]
    r = est_pack(V, ans, dists)
    if r is None:
        return None
    opts, ai = r
    s_txt = f"某工厂年产零件约{a}件，单件利润约{b}元，年利润总额约多少元？（　）"
    return make(0, "估算", "估算", s_txt, opts, ai,
                f"{a}×{b}≈{fmt(ans)}元，取两位有效数字即可秒定。",
                "四个选项同量级，比的是估算精度，不是数量级排查。")

def g2_percent():
    A = rng.randrange(2400, 8900, 10)
    p = rng.randint(13, 87)
    V = A * p / 100
    ans = sig2(V)
    # 干扰项：比例估偏约一成（截断/读数误差的产物）
    dists = [A * p * 1.15 / 100, A * p * 0.87 / 100, A * (p + max(2, p // 12)) / 100]
    r = est_pack(V, ans, dists)
    if r is None:
        return None
    opts, ai = r
    s_txt = f"某市常住人口约{A}千人，其中网购比例约{p}%，网购人数约多少千人？（　）"
    return make(0, "估算", "估算", s_txt, opts, ai,
                f"{A}×{p}%≈{fmt(ans)}千人：{A}×{p}后小数点左移两位。",
                "选项均为同量级估算值，选最接近的，凭两位有效数字锁定。")

def g3_circle_area():
    r = rng.choice([5.5, 6.5, 7.5, 8.5, 9.5, 7.2, 8.8, 6.8])
    area = math.pi * r * r
    ans = sig2(area)
    # 干扰项：同量纲错误估算（π取3、半径估偏一成的产物），不再放周长值
    dists = [3 * r * r, 3.14 * (r * 1.09) ** 2, 3.14 * (r * 0.9) ** 2]
    r2 = est_pack(area, ans, dists)
    if r2 is None:
        return None
    opts, ai = r2
    s_txt = f"圆形花坛半径约{r}米，其面积最接近多少平方米？（　）"
    return make(0, "估算", "估算", s_txt, opts, ai,
                f"πr²≈3.14×{fmt(r*r)}≈{fmt(ans)}平方米。",
                "π取3或半径估偏一成都落在干扰项里，选最接近的。")

def g4_interval():
    a = rng.randint(23, 88) * 10
    b = rng.randint(2, 9)
    c = rng.randint(3, 9)
    V = a * b / c          # 题面"b倍"与计算一致（修复：原题面写 b% 但按 b 倍算）
    w = 100 if V > 400 else 50
    k = int(V // w)
    lo, hi = k * w, (k + 1) * w
    if not (lo + 0.18 * w < V < hi - 0.18 * w):
        return None
    opts4 = [f"{lo}~{hi}", f"{lo-2*w}~{lo-w}", f"{lo-w}~{lo}", f"{hi}~{hi+w}"]
    rng.shuffle(opts4)
    ai = opts4.index(f"{lo}~{hi}")
    if len(set(opts4)) < 4:
        return None
    assert lo < V < hi
    for iv in opts4:       # 真值不得落入任何干扰区间
        if iv != f"{lo}~{hi}":
            l2, h2 = map(int, iv.split("~"))
            assert not (l2 < V < h2), (iv, V)
    s_txt = f"甲走路程{a}米，乙走路程是甲的{b}倍再除以{c}，则乙走路程在哪个范围内？（　）"
    return make(0, "估算", "估算", s_txt, opts4, ai,
                f"{a}×{b}÷{c}={fmt(V)}，落于{lo}~{hi}且远离边界，区间锁定。",
                "区间题防边界思维：真值靠近端点时慎选，本题留有裕量。")

def g5_division():
    A = rng.randrange(1200, 9800, 10)
    P = rng.randrange(200, 920, 10)
    V = A / P              # 亿元÷万人=万元/人
    ans = sig2(V)
    # 干扰项：人口/GDP估偏一至两成的错误估算（同量级，不再用量级凑数）
    dists = [A / (P * 1.15), A / (P * 0.87), A / (P + P // 7)]
    r = est_pack(V, ans, dists)
    if r is None:
        return None
    opts, ai = r
    s_txt = f"某市2026年GDP约为{A}亿元，常住人口约{P}万人，人均GDP最接近多少万元？（　）"
    return make(0, "估算", "估算", s_txt, opts, ai,
                f"{A}亿元÷{P}万人={fmt(V)}万元/人（亿元÷万人=万元）。",
                "选项均为同量级估算，比的是首两位有效数字的精度。")

def g6_base_year():
    A = rng.randrange(3200, 9600, 10)
    g = rng.randint(6, 24)
    V = A / (1 + g / 100)
    ans = sig2(V)
    r = est_pack(V, ans, [A * g / 100, A * (1 - g / 100), A * (1 + g / 100)])
    if r is None:
        return None
    opts, ai = r
    s_txt = f"今年某项支出为{A}万元，同比增长{g}%，该项支出去年约为多少万元？（　）"
    return make(0, "估算", "深钩", s_txt, opts, ai,
                f"基期=今年÷(1+{g}%)≈{fmt(ans)}万元。深在增长模型回除，而非乘减。",
                "把增长量当基期，或用(1−g%)回除（方向看反），皆预设干扰。")

def g7_multi_step():
    A = rng.randrange(2100, 8900, 10)
    p = rng.randint(14, 68)
    q = rng.randint(3, 8)
    V = A * p / 100 / q
    ans = sig2(V)
    r = est_pack(V, ans, [A * p / 100, A * p / 100 * q, A * p / q])
    if r is None:
        return None
    opts, ai = r
    s_txt = f"全年营收约{A}万元，其中{p}%来自线上，线上收入分给{q}个团队，每队约多少万元？（　）"
    return make(0, "估算", "深钩", s_txt, opts, ai,
                f"{A}×{p}%÷{q}≈{fmt(ans)}万元。深在百分比与均分两步连算，先约分再估。",
                "漏除q或把除当乘，量级立刻翻倍，对应预设干扰项。")


TEMPLATES = {
    "p1": (p1_cont_range, 7), "p2": (p2_sum_of_odds, 6), "p3": (p3_two_primes_even_sum, 6),
    "p4": (p4_parity_chain, 7), "p5": (p5_prime_pair_odd_sum, 2), "p6": (p6_consec_odds_sum, 1),
    "p7": (p7_divisor_count, 1),
    "w1": (w1_poly_units, 8), "w2": (w2_power_units, 9), "w3": (w3_factorial_units, 5),
    "w4": (w4_money_units, 8), "w5": (w5_two_powers_sum, 3), "w6": (w6_power_minus_factorial, 2),
    "g1": (g1_big_product, 6), "g2": (g2_percent, 7), "g3": (g3_circle_area, 6),
    "g4": (g4_interval, 6), "g5": (g5_division, 5), "g6": (g6_base_year, 3), "g7": (g7_multi_step, 2),
}

BANNED = ["123×456", "2^20", "1!+…+10!", "498×502", "3.2", "847.6", "147", "=25", "1+…+50"]

def main():
    questions, stems = [], set()
    for name, (fn, quota) in TEMPLATES.items():
        got, tries = [], 0
        while len(got) < quota:
            tries += 1
            assert tries < 500, f"{name} 重试过多"
            q = fn()
            if q is None:
                continue
            if q["s"] in stems or any(b in q["s"] for b in BANNED):
                continue
            assert len(set(q["o"])) == 4 and 0 <= q["a"] <= 3
            assert len(q["e"]) <= 80
            stems.add(q["s"])
            got.append(q)
        questions.extend(got)
    assert len(questions) == 100, len(questions)
    # 奇偶一致性断言：答案选项为"奇数/偶数"时，解析声明的奇偶必须与之一致
    import re
    for q in questions:
        ans_txt = q["o"][q["a"]]
        if ans_txt in ("奇数", "偶数"):
            decls = re.findall(r"[为是]([奇偶])数", q["e"])
            assert decls and set(decls) == {ans_txt[0]}, ("奇偶答案与解析声明矛盾", q)
    # 尾数类情境外壳统计：开头≥12个，单壳占比≤15%
    from collections import Counter
    tail = [q for q in questions if q["h"] == "尾数"]
    sh = Counter(STEM_SHELL[q["s"]] for q in tail)
    assert len(sh) >= 12, ("尾数情境开头不足12个", sh)
    assert max(sh.values()) <= int(0.15 * len(tail)), ("尾数单壳超15%", sh)
    print("尾数情境外壳:", dict(sh))
    print("分类:", Counter(q["h"] for q in questions))
    print("题型:", Counter(q["t"] for q in questions))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=1)
    print("写出", OUT, len(questions), "题")


if __name__ == "__main__":
    main()
