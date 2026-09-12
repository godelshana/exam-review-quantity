# -*- coding: utf-8 -*-
"""
自编练习题生成器 gen_C.py
三大类：比例反比 50 / 假设法 40 / 周期余数 35，共 125 题。
每题附独立暴力校验（枚举/逐日模拟/datetime 复算），assert 失败即报错退出。
输出：gen_C_output.json（UTF-8 无 BOM）
"""
import json
import random
from fractions import Fraction
from math import gcd
from datetime import date, timedelta

random.seed(20260909)
OUT = r"E:\codeBase\examReview\教学\速刷\gen\gen_C_output.json"

WD = ["一", "二", "三", "四", "五", "六", "日"]  # index0=周一，与 date.weekday() 对齐

questions = []
VERIFIERS = []
used = set()

# 情境外壳机制：同一模板用不同情境开头，防模板单调
SHELL_USE = {}
STEM_SHELL = {}


def pick_shell(sids):
    return min(sids, key=lambda x: (SHELL_USE.get(x, 0), sids.index(x)))


def mark_shell(sid, stem, ok):
    if ok:
        SHELL_USE[sid] = SHELL_USE.get(sid, 0) + 1
        STEM_SHELL[stem] = sid

# 禁止与既有真题同结构同数字：(子串A, 子串B) 同时出现在题干即拒绝
BANNED_PAIRS = [
    ("3∶4", "2小时"),          # 效率3:4多用2h
    ("60千米", "40千米"),       # 去60返40平均48
    ("2∶3", "4∶5"),            # 甲乙2:3乙丙4:5
    ("8天", "10天"),            # A8天B10天合作4天
    ("40人", "4人"),            # 40人租船6人4人
    ("100人", "100个馒头"),     # 100人100馒头
    ("200件", "5元"),           # 200玻璃杯赔5元
    ("星期三", "100天"),        # 周三后100天
    ("红黄蓝绿", "2026"),       # 红黄蓝绿第2026
    ("3月1日", "星期六"),       # 3月1日周六
]


def add(h, t, s, ans_val, ans_str, dis, e, tr, vf):
    """dis: [(值, 选项串)]；统一查重、洗牌、记录。返回是否成功加入。"""
    cand = [(ans_val, ans_str)] + dis
    vals = [v for v, _ in cand]
    strs = [x for _, x in cand]
    if len(set(vals)) != 4 or len(set(strs)) != 4:
        return False
    if len(s) > 70 or len(e) > 80:
        return False
    for p, q in BANNED_PAIRS:
        if p in s and q in s:
            return False
    if s in used:
        return False
    items = cand[:]
    random.shuffle(items)
    a = [v for v, _ in items].index(ans_val)
    questions.append({"h": h, "t": t, "s": s, "o": [x for _, x in items],
                      "a": a, "e": e, "tr": tr})
    VERIFIERS.append(vf)
    used.add(s)
    return True


def lcm(a, b):
    return a * b // gcd(a, b)


def rp(a, b):
    """约简比例对"""
    g = gcd(a, b)
    return (a // g, b // g)


def dstr(d):
    return f"{d.month}月{d.day}日"


def pick(pool, ans, k=3):
    """从干扰候选池里挑 k 个互不相同且不等于答案的 (值, str)"""
    dis = []
    for v in pool:
        if v is None:
            continue
        if v > 0 and v != ans and all(v != d for d, _ in dis):
            dis.append((v, str(v)))
        if len(dis) == k:
            break
    return dis if len(dis) == k else None


# ============================ 比例反比 ============================

def g_speed():
    """速度比⇒时间反比"""
    r1, r2 = sorted(random.sample(range(2, 10), 2))
    k = random.randint(2, 12)
    T = k * r2          # 慢者（速度r1）用时多
    ans = k * r1        # 快者（速度r2）用时少
    dis = pick([T, T - (r2 - r1) * k, k * r1 + k, k * r1 - k, T + k], ans)
    if not dis:
        return False
    sid = pick_shell(["sp1", "sp2", "sp3", "sp4", "sp5"])
    stems = {
        "sp1": f"甲、乙的速度比为{r1}∶{r2}，甲走完全程要{T}小时，乙走完全程要多少小时？",
        "sp2": f"客车与货车的速度比为{r1}∶{r2}，客车行完全程要{T}小时，货车行完全程要多少小时？",
        "sp3": f"高铁与动车的速度比为{r1}∶{r2}，高铁行完全程要{T}小时，动车行完全程要多少小时？",
        "sp4": f"骑行与步行的速度比为{r1}∶{r2}，骑车走完全程要{T}小时，步行走完全程要多少小时？",
        "sp5": f"快艇渡江去程与回程的速度比为{r1}∶{r2}，去程用了{T}小时，回程要用多少小时？",
    }
    s = stems[sid]
    e = f"路程相同，速度比{r1}∶{r2}⇒时间比反比{r2}∶{r1}，={T}×{r1}/{r2}={ans}小时。"
    tr = "把时间比顺写成速度比（时间没反过来）。"

    def vf():
        hit = [t for t in range(1, 5000) if t * r2 == T * r1]
        assert hit == [ans], (hit, ans, r1, r2, T)
    ok = add("比例反比", "钩子", s, ans, str(ans), dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_price():
    """总价相同，量价反比"""
    a, b = random.sample(range(2, 16), 2)
    if a > b:
        a, b = b, a
    g = gcd(a, b)
    j = random.randint(2, 9)
    m = (b // g) * j          # 保证总价能被 b 整除
    S = a * m
    ans = S // b
    dis = pick([m, m + (b - a), ans + a // g, ans - a // g, m + b], ans)
    if not dis:
        return False
    sid = pick_shell(["pr1", "pr2", "pr3", "pr4"])
    stems = {
        "pr1": f"苹果每斤{a}元，{S}元正好买{m}斤；若改买每斤{b}元的橙子，同样的钱能买多少斤？",
        "pr2": f"钢笔每支{a}元，{S}元正好买{m}支；若改买每支{b}元的圆珠笔，同样的钱能买多少支？",
        "pr3": f"彩带每米{a}元，{S}元正好买{m}米；若改买每米{b}元的丝带，同样的钱能买多少米？",
        "pr4": f"普通车搬运一次收{a}元，{S}元正好搬{m}次；若改请每次{b}元的车队，同样的钱能搬多少次？",
    }
    s = stems[sid]
    e = f"总价相同，单价与数量成反比：{ans}={m}×{a}/{b}。"
    tr = "误按正比换算（单价高反而算得多）。"

    def vf():
        hit = [q for q in range(1, 100000) if b * q == S]
        assert hit == [ans], (hit, ans)
        assert a * m == S
    ok = add("比例反比", "钩子", s, ans, str(ans), dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_harmonic():
    """平均速度：调和平均"""
    pairs = [(10, 15), (15, 30), (20, 30), (18, 36), (24, 48),
             (30, 60), (45, 90), (16, 48)]
    v1, v2 = random.choice(pairs)
    ans = 2 * v1 * v2 // (v1 + v2)
    dis = pick([(v1 + v2) // 2, v1, v2, ans + 2, ans - 2], ans)
    if not dis:
        return False
    sid = pick_shell(["ha1", "ha2", "ha3", "ha4"])
    stems = {
        "ha1": f"司机沿原路往返运货，去程每小时{v1}千米，回程每小时{v2}千米，全程平均速度是多少？",
        "ha2": f"登山队上山每小时{v1}千米，沿原路下山每小时{v2}千米，往返全程平均速度是多少？",
        "ha3": f"轮渡去程每小时{v1}千米，返程沿原线每小时{v2}千米，往返全程平均速度是多少？",
        "ha4": f"邮车把邮件送到山下再原路返回，去程每小时{v1}千米，回程每小时{v2}千米，全程平均速度是多少？",
    }
    s = stems[sid]
    e = f"调和平均：2×{v1}×{v2}/({v1}+{v2})={ans}，不等于算术平均{(v1 + v2) // 2}。"
    tr = f"用算术平均{(v1 + v2) // 2}替代调和平均。"

    def vf():
        D = lcm(v1, v2)
        t = Fraction(D, v1) + Fraction(D, v2)
        assert Fraction(2 * D) / t == Fraction(ans)
    ok = add("比例反比", "钩子", s, ans, str(ans), dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_bridge():
    """比例过桥传导（钩子：中间份数已相同）"""
    a, b, d = random.sample(range(2, 10), 3)
    if gcd(a, b) > 1 or gcd(b, d) > 1:
        return False
    ansv = Fraction(a, d)
    pa, pb = rp(a, d)
    dis = []
    for (x, y) in [(a, b), (b, d), (a + b, b + d)]:
        x2, y2 = rp(x, y)
        if Fraction(x2, y2) != ansv and all((x2, y2) != dd for dd, _ in dis):
            dis.append(((x2, y2), f"{x2}∶{y2}"))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    sid = pick_shell(["br1", "br2", "br3", "br4"])
    stems = {
        "br1": f"甲∶乙={a}∶{b}，乙∶丙={b}∶{d}，则甲∶丙等于多少？",
        "br2": f"一车间与二车间人数比为{a}∶{b}，二车间与三车间人数比为{b}∶{d}，一车间与三车间人数之比是多少？",
        "br3": f"甲种蔬菜与乙种蔬菜产量比为{a}∶{b}，乙种与丙种产量比为{b}∶{d}，甲种与丙种产量之比是多少？",
        "br4": f"圆A与圆B的半径比为{a}∶{b}，圆B与圆C的半径比为{b}∶{d}，圆A与圆C的半径之比是多少？",
    }
    s = stems[sid]
    e = f"过桥：甲/丙=甲/乙×乙/丙=({a}/{b})×({b}/{d})={a}/{d}，约简为{pa}∶{pb}。"
    tr = "直接抄某一单比，或把两比对应项相加。"

    def vf():
        assert Fraction(a, b) * Fraction(b, d) == ansv
        for dd, _ in dis:
            assert Fraction(dd[0], dd[1]) != ansv
    ok = add("比例反比", "钩子", s, ansv, f"{pa}∶{pb}", dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_bridge_deep():
    """深钩：中间份数不同，需统一公共份数（双比例链）"""
    a, b, c, d = random.sample(range(2, 10), 4)
    if b == c or gcd(a, b) > 1 or gcd(c, d) > 1:
        return False
    ansv = Fraction(a * c, b * d)
    pa, pb = rp(a * c, b * d)
    dis = []
    for (x, y) in [(a, d), (b, d), (a + c, b + d)]:
        x2, y2 = rp(x, y)
        if Fraction(x2, y2) != ansv and all((x2, y2) != dd for dd, _ in dis):
            dis.append(((x2, y2), f"{x2}∶{y2}"))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    sid = pick_shell(["bd1", "bd2", "bd3"])
    stems = {
        "bd1": f"甲∶乙={a}∶{b}，乙∶丙={c}∶{d}，则甲∶丙等于多少？",
        "bd2": f"一车间与二车间人数比为{a}∶{b}，二车间与三车间人数比为{c}∶{d}，一车间与三车间人数之比是多少？",
        "bd3": f"圆A与圆B半径比为{a}∶{b}，圆B与圆C半径比为{c}∶{d}，圆A与圆C半径之比是多少？",
    }
    s = stems[sid]
    e = f"深在乙的份数不同：先按{lcm(b, c)}统一乙的份数，再连乘约简得{pa}∶{pb}。"
    tr = f"没统一公共份数，直接写{rp(a, d)[0]}∶{rp(a, d)[1]}。"

    def vf():
        assert Fraction(a, b) * Fraction(c, d) == ansv
        for dd, _ in dis:
            assert Fraction(dd[0], dd[1]) != ansv
    ok = add("比例反比", "深钩", s, ansv, f"{pa}∶{pb}", dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_mandays():
    """工作量相同：人数⇒天数反比"""
    n1 = random.randint(4, 20)
    d1 = random.randint(3, 15)
    W = n1 * d1
    cands = [n for n in range(2, 41) if n != n1 and W % n == 0 and 2 <= W // n <= 30]
    if not cands:
        return False
    n2 = random.choice(cands)
    ans = W // n2
    dis = pick([d1, d1 + (n2 - n1), ans + abs(n2 - n1), ans - abs(n2 - n1), n2], ans)
    if not dis:
        return False
    sid = pick_shell(["md1", "md2", "md3", "md4"])
    stems = {
        "md1": f"修一段路，{n1}个工人{d1}天修完；若改为{n2}个工人一起修（效率相同），几天修完？",
        "md2": f"粉刷一面墙，{n1}个工人{d1}天刷完；若改为{n2}个工人一起刷（效率相同），几天刷完？",
        "md3": f"装配一批玩具，{n1}个人{d1}天完成；若改为{n2}个人一起做（效率相同），几天完成？",
        "md4": f"把一批图书打包入库，{n1}个人需{d1}天；若改为{n2}个人一起打包（效率相同），需多少天？",
    }
    s = stems[sid]
    e = f"工作量不变，人数与天数成反比：{n1}×{d1}/{n2}={ans}天。"
    tr = "把反比当正比（人多反而算得天多）。"

    def vf():
        hit = [t for t in range(1, W + 1) if n2 * t == W]
        assert hit == [ans], (hit, ans)
    ok = add("比例反比", "钩子", s, ans, str(ans), dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


def g_alloc_deep():
    """深钩：三连比分配，需统一公共份数求甲所得"""
    a, b, c, d = random.sample(range(2, 10), 4)
    g = gcd(b, c)
    A = a * (c // g)
    B = b * (c // g)
    C = b * d // g
    if len({A, B, C}) < 3:
        return False
    S0 = A + B + C
    k = random.randint(2, 9)
    M = S0 * k
    ans = A * k
    pool = [(B * k, f"{B * k}元"), (C * k, f"{C * k}元"), (M - ans, f"{M - ans}元"),
            (ans + k, f"{ans + k}元")]
    dis = []
    for v, sv in pool:
        if v != ans and all(v != dd for dd, _ in dis):
            dis.append((v, sv))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    sid = pick_shell(["al1", "al2", "al3"])
    stems = {
        "al1": f"共{M}元奖金按甲∶乙={a}∶{b}、乙∶丙={c}∶{d}分给三人，甲得多少元？",
        "al2": f"共{M}元劳务费按甲∶乙={a}∶{b}、乙∶丙={c}∶{d}分给三人，甲分得多少元？",
        "al3": f"三个班组共承担{M}元费用，分担比为甲∶乙={a}∶{b}、乙∶丙={c}∶{d}，甲班组承担多少元？",
    }
    s = stems[sid]
    e = f"深在双链求三连比：统一乙的份数得{A}∶{B}∶{C}共{S0}份，甲={M}×{A}/{S0}={ans}元。"
    tr = "只用甲∶乙这一个比就直接分配。"

    def vf():
        assert M == k * (A + B + C)
        assert Fraction(A, B) == Fraction(a, b)
        assert Fraction(B, C) == Fraction(c, d)
        for dd, _ in dis:
            assert dd != ans
    ok = add("比例反比", "深钩", s, ans, f"{ans}元", dis, e, tr, vf)
    mark_shell(sid, s, ok)
    return ok


# ============================ 假设法 ============================

def g_chicken():
    """鸡兔同笼"""
    H = random.randint(10, 30)
    x = random.randint(2, H - 2)          # 鸡
    y = H - x                              # 兔
    L = 2 * x + 4 * y
    ans = x
    dis = pick([y, L // 4, H - L // 4, x - 1, y + 1], ans)
    if not dis:
        return False
    s = f"笼子里鸡兔共{H}个头、{L}条腿，鸡有多少只？"
    e = f"假设全兔：{4 * H}条腿，多{4 * H - L}条，每只鸡少2条，鸡=({4 * H}-{L})/2={ans}只。"
    tr = "假设全鸡全兔后除数弄反（除以4而非2）。"

    def vf():
        hit = [i for i in range(H + 1) if 2 * i + 4 * (H - i) == L]
        assert hit == [ans], (hit, ans)
    return add("假设法", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_rent():
    """租船坐满"""
    B, S = random.sample(range(3, 10), 2)
    x = random.randint(2, 8)
    y = random.randint(2, 8)
    N = x + y
    P = B * x + S * y
    if P == 40 and {B, S} == {6, 4}:
        return False
    ans = x
    dis = pick([y, P // B, P // S, N, x + 1], ans)
    if not dis:
        return False
    s = f"某班{P}人划船，大船坐{B}人、小船坐{S}人，共租{N}条船正好坐满，大船租了几条？"
    e = f"假设全大船：{B * N}座，多{B * N - P}座，每换一条小船少{B - S}座，小船={y}条。"
    tr = "除数误用某船人数而不是两船人数差。"

    def vf():
        hit = [i for i in range(N + 1) if B * i + S * (N - i) == P]
        assert hit == [ans], (hit, ans)
    return add("假设法", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_score():
    """答题计分"""
    n = random.randint(8, 20)
    X = random.randint(3, 10)
    Y = random.randint(1, X - 1)
    x = random.randint(2, n - 2)          # 答对
    S = X * x - Y * (n - x)
    ans = x
    dis = pick([n - x, x + 1, S // X, n - x + 1, x - 1], ans)
    if not dis:
        return False
    s = f"竞赛共{n}题，答对得{X}分，答错或不答扣{Y}分，小张得了{S}分，他答对了几题？"
    e = f"假设全对：{X * n}分，每错一题损失{X + Y}分，错题=({X * n}-{S})/{X + Y}={n - x}。"
    tr = "每错一题的损失是X+Y，不是只扣Y。"

    def vf():
        hit = [i for i in range(n + 1) if X * i - Y * (n - i) == S]
        assert hit == [ans], (hit, ans)
    return add("假设法", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_fragile():
    """运破损赔款"""
    m = random.choice([100, 150, 250, 300, 400])
    a = random.randint(2, 6)
    c = random.randint(10, 30)
    b = random.randint(1, m // 25)        # 破损
    S = a * (m - b) - c * b
    if S <= 0:
        return False
    ans = b
    dis = pick([m - b, b + 1, b - 1, (a * m - S) // (a + c) + 1, m], ans)
    if not dis:
        return False
    s = f"物流公司运{m}件瓷器，每件运费{a}元，破损一件不但不收运费还要赔{c}元，共收运费{S}元，破损几件？"
    e = f"假设全完好：{a * m}元，每破一件差{a + c}元，破损=({a * m}-{S})/{a + c}={b}件。"
    tr = "每件差额漏加运费部分（只算赔款c）。"

    def vf():
        hit = [i for i in range(m + 1) if a * (m - i) - c * i == S]
        assert hit == [ans], (hit, ans)
    return add("假设法", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_dumpling():
    """大人小孩吃点心"""
    d = random.randint(3, 6)
    c = random.randint(1, d - 1)
    D = random.randint(3, 25)
    C = random.randint(3, 25)
    N = D + C
    M = d * D + c * C
    if N == 100 and M == 100:
        return False
    ans = C
    dis = pick([D, N, C + 1, D - 1, M // d], ans)
    if not dis:
        return False
    s = f"大人每人吃{d}块饼，小孩每人吃{c}块，共{N}人正好吃完{M}块饼，小孩有多少人？"
    e = f"假设全大人：{d * N}块，多{d * N - M}块，每小孩少{d - c}块，小孩=({d * N}-{M})/{d - c}={C}人。"
    tr = "除数误用大人食量而不是食量之差。"

    def vf():
        hit = [i for i in range(N + 1) if d * (N - i) + c * i == M]
        assert hit == [ans], (hit, ans)
    return add("假设法", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_deep_subst():
    """深钩：先代换再假设（鸡比兔多k只）"""
    x = random.randint(5, 15)             # 鸡
    y = random.randint(1, x - 2)          # 兔
    k = x - y
    L = 2 * x + 4 * y
    ans = x
    dis = pick([y, x + y, L // 4, x - 1, y + 1], ans)
    if not dis:
        return False
    s = f"鸡比兔多{k}只，鸡兔共{L}条腿，鸡有多少只？"
    e = f"深在先代换再假设：鸡=兔+{k}⇒腿=6兔+{2 * k}，兔={L - 2 * k}/6={y}，鸡={x}只。"
    tr = "不先代换，直接按总头数做普通假设。"

    def vf():
        hit = [(i, j) for i in range(L // 2 + 1) for j in range(L // 2 + 1)
               if i - j == k and 2 * i + 4 * j == L]
        assert hit == [(x, y)], (hit, (x, y))
    return add("假设法", "深钩", s, ans, str(ans), dis, e, tr, vf)


def g_deep_tri():
    """深钩：三态计分（对/错/不答），需先代换排除"""
    for _ in range(200):
        n = random.randint(6, 12)
        X = random.randint(3, 6)
        Y = random.randint(1, 2)
        x = random.randint(1, n - 2)
        y = random.randint(1, n - x - 1)
        S = X * x - Y * y
        sols = set()
        for i in range(n + 1):
            for j in range(n + 1 - i):
                if X * i - Y * j == S:
                    sols.add(i)
        if len(sols) == 1 and sols == {x} and y >= 1 and (n - x - y) >= 1:
            break
    else:
        return False
    ans = x
    dis = pick([x + 1, n - x, x - 1, y, n], ans)
    if not dis:
        return False
    s = f"测验{n}题，答对得{X}分，答错扣{Y}分，不答不得分；小王有题未答且得{S}分，他答对几题？"
    e = f"深在三态两未知：设对x错y，{X}x-{Y}y={S}且x+y<{n}，枚举仅一组：对{x}错{y}。"
    tr = "当成对错两态直接假设，忽略有不答的题。"

    def vf():
        sols = set()
        for i in range(n + 1):
            for j in range(n + 1 - i):
                if X * i - Y * j == S:
                    sols.add(i)
        assert sols == {ans}, (sols, ans)
    return add("假设法", "深钩", s, ans, str(ans), dis, e, tr, vf)


# ============================ 周期余数 ============================

def g_week():
    """星期推算（逐日模拟校验）"""
    w0 = random.randrange(7)
    N = random.randint(30, 400)
    if w0 == 2 and N == 100:
        return False
    ansi = (w0 + N) % 7
    dis = []
    for i in [(ansi + 1) % 7, (ansi - 1) % 7, (w0 + N % 7 + 1) % 7, (w0 - N) % 7]:
        if i != ansi and all(i != dd for dd, _ in dis):
            dis.append((i, "星期" + WD[i]))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    s = f"今天是星期{WD[w0]}，再过{N}天是星期几？"
    e = f"{N}÷7={N // 7}余{N % 7}，从星期{WD[w0]}往后数{N % 7}天，为星期{WD[ansi]}。"
    tr = "把商当余数用，或往后数时多数一天。"

    def vf():
        cur = w0
        for _ in range(N):
            cur = (cur + 1) % 7
        assert cur == ansi, (cur, ansi)
    return add("周期余数", "钩子", s, ansi, "星期" + WD[ansi], dis, e, tr, vf)


def g_cycle():
    """循环排列取余"""
    seqs = [list("甲乙丙丁"), list("甲乙丙丁戊"), list("金木水火土"),
            list("东西南北中"), list("春夏秋冬"), list("ABCDEF")]
    seq = random.choice(seqs)
    L = len(seq)
    M = random.randint(80, 500)
    if seq == ["红", "黄", "蓝", "绿"] and M == 2026:
        return False
    ansi = (M - 1) % L
    dis = []
    for i in [M % L, (M + 1) % L, (M - 2) % L, (M - 1) % (L + 1)]:
        i = i % L
        if seq[i] != seq[ansi] and all(seq[i] != dd for dd, _ in dis):
            dis.append((seq[i], seq[i]))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    s = f"彩灯按“{''.join(seq)}”的顺序循环排列，第{M}个是什么？"
    e = f"周期{L}：({M}-1)÷{L}余{ansi}，对应周期内第{ansi + 1}个，即“{seq[ansi]}”。"
    tr = "用M÷L的余数直接当位置（差1）。"

    def vf():
        idx = 0
        for _ in range(M - 1):
            idx = (idx + 1) % L
        assert seq[idx] == seq[ansi]
    return add("周期余数", "钩子", s, seq[ansi], seq[ansi], dis, e, tr, vf)


def g_baoshu():
    """循环报数取余"""
    k = random.randint(3, 7)
    M = random.randint(70, 400)
    ans = ((M - 1) % k) + 1
    pool = [(M - 1) % k, (M % k) + 1, k - ((M - 1) % k), (M % k) + 2]
    norm = []
    for v in pool:
        v = (v - 1) % k + 1
        if v not in norm:
            norm.append(v)
    dis = []
    for v in norm:
        if v != ans and all(v != dd for dd, _ in dis):
            dis.append((v, str(v)))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    s = f"同学们围成一圈按1到{k}循环报数，第{M}号同学报到几？"
    e = f"周期{k}：({M}-1)÷{k}余{ans - 1}，报数=余数+1={ans}。"
    tr = "余0时忘记报k（差1处理错）。"

    def vf():
        cur = 1
        for _ in range(M - 1):
            cur = cur % k + 1
        assert cur == ans, (cur, ans)
    return add("周期余数", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_everyN():
    """隔N天陷阱：每隔m天=每m+1天"""
    m = random.randint(2, 6)
    n = random.randint(2, 9)
    ans = lcm(m + 1, n)
    if ans == lcm(m, n) or ans == (m + 1) * n or ans == m * n:
        return False
    dis = pick([lcm(m, n), (m + 1) * n, m * n, ans + n], ans)
    if not dis:
        return False
    s = f"小王每隔{m}天去一次球场，小李每{n}天去一次，今天两人都去了，下次同去是多少天后？"
    e = f"深点在“每隔{m}天”=每{m + 1}天，周期取lcm({m + 1},{n})={ans}天。"
    tr = f"把每隔{m}天当每{m}天，误答{lcm(m, n)}。"

    def vf():
        d = 1
        while not (d % (m + 1) == 0 and d % n == 0):
            d += 1
        assert d == ans, (d, ans)
    return add("周期余数", "钩子", s, ans, str(ans), dis, e, tr, vf)


def g_crossmonth():
    """大小月跨月推星期（datetime 独立复算）"""
    base = date(2026, 1, 1)
    o1 = random.randint(0, 100)
    off = random.randint(20, 250)
    if o1 + off > 364:
        return False
    d1 = base + timedelta(days=o1)
    d2 = d1 + timedelta(days=off)
    if dstr(d1) == "3月1日":
        return False
    i1, i2 = d1.weekday(), d2.weekday()
    ansv = i2
    dis = []
    for i in [(i2 + 1) % 7, (i2 - 1) % 7, i1]:
        if i != ansv and all(i != dd for dd, _ in dis):
            dis.append((i, "星期" + WD[i]))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    s = f"2026年{dstr(d1)}是星期{WD[i1]}，那么{dstr(d2)}是星期几？"
    e = f"先数相隔{off}天（跨大小月），{off}÷7余{off % 7}，从星期{WD[i1]}推得星期{WD[i2]}。"
    tr = "跨月时大小月天数记错导致差一天。"

    def vf():
        cur, cnt = d1, 0
        while cur < d2:
            cur += timedelta(days=1)
            cnt += 1
        assert cnt == off and cur == d2 and cur.weekday() == ansv
    return add("周期余数", "钩子", s, ansv, "星期" + WD[ansv], dis, e, tr, vf)


def g_deep_date():
    """深钩：隔天周期+跨月日期，两步复合"""
    m = random.randint(2, 6)
    n = random.randint(2, 9)
    per = lcm(m + 1, n)
    if per == lcm(m, n) or per == (m + 1) * n or per == m * n:
        return False
    base = date(2026, 1, 1)
    o1 = random.randint(0, 350 - per)
    d1 = base + timedelta(days=o1)
    d2 = d1 + timedelta(days=per)
    alts = [d1 + timedelta(days=lcm(m, n)), d1 + timedelta(days=(m + 1) * n),
            d2 - timedelta(days=1), d2 + timedelta(days=1)]
    dis = []
    for dv in alts:
        if dv != d2 and dstr(dv) != dstr(d2) and all(dstr(dv) != dd for dd, _ in dis):
            dis.append((dv, dstr(dv)))
        if len(dis) == 3:
            break
    if len(dis) < 3:
        return False
    s = f"2026年{dstr(d1)}两人同去健身房，此后甲每隔{m}天去一次，乙每{n}天去一次，下次同去是几月几日？"
    e = f"深在两步：先求周期lcm({m + 1},{n})={per}天，再从{dstr(d1)}加{per}天跨月推得{dstr(d2)}。"
    tr = f"每隔{m}天当每{m}天，或加天数时跨月算错。"

    def vf():
        d = d1
        while True:
            d += timedelta(days=1)
            if (d - d1).days % (m + 1) == 0 and (d - d1).days % n == 0:
                break
        assert d == d2, (d, d2)
    return add("周期余数", "深钩", s, d2, dstr(d2), dis, e, tr, vf)


# ============================ 主流程 ============================

def fill(fn, n, budget=4000):
    got, tries = 0, 0
    while got < n and tries < budget:
        tries += 1
        if fn():
            got += 1
    if got < n:
        raise RuntimeError(f"模板 {fn.__name__} 只生成 {got}/{n} 题")


def main():
    # 比例反比 50（深钩10）
    fill(g_speed, 8)
    fill(g_price, 8)
    fill(g_harmonic, 8)
    fill(g_bridge, 8)
    fill(g_mandays, 8)
    fill(g_bridge_deep, 5)
    fill(g_alloc_deep, 5)
    # 假设法 40（深钩8）
    fill(g_chicken, 7)
    fill(g_rent, 6)
    fill(g_score, 7)
    fill(g_fragile, 6)
    fill(g_dumpling, 6)
    fill(g_deep_subst, 4)
    fill(g_deep_tri, 4)
    # 周期余数 35（深钩5）
    fill(g_week, 8)
    fill(g_cycle, 6)
    fill(g_baoshu, 5)
    fill(g_everyN, 5)
    fill(g_crossmonth, 6)
    fill(g_deep_date, 5)

    # 全量独立暴力校验（任一失败 assert 报错退出）
    for vf in VERIFIERS:
        vf()

    # 结构校验
    assert len(questions) == 125, len(questions)
    assert len(set(q["s"] for q in questions)) == 125, "题干重复"
    for q in questions:
        assert len(q["o"]) == 4 and len(set(q["o"])) == 4
        assert 0 <= q["a"] <= 3
        assert q["o"][q["a"]]  # 非空
        assert len(q["s"]) <= 70 and len(q["e"]) <= 80
    hs = {}
    ts = {}
    for q in questions:
        hs[q["h"]] = hs.get(q["h"], 0) + 1
        ts[q["t"]] = ts.get(q["t"], 0) + 1
    assert hs == {"比例反比": 50, "假设法": 40, "周期余数": 35}, hs
    assert ts == {"钩子": 102, "深钩": 23}, ts
    # 比例反比情境外壳统计：开头≥12个，单壳占比≤15%
    from collections import Counter as _Cnt
    rp = [q for q in questions if q["h"] == "比例反比"]
    sh = _Cnt(STEM_SHELL[q["s"]] for q in rp)
    assert len(sh) >= 12, ("比例反比情境开头不足12个", sh)
    assert max(sh.values()) <= int(0.15 * len(rp)), ("比例反比单壳超15%", sh)
    print("比例反比情境外壳:", dict(sh))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=1)
    print("OK", len(questions), hs, ts)


if __name__ == "__main__":
    main()
