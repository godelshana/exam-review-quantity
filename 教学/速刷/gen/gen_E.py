# -*- coding: utf-8 -*-
"""深钩卡（更深口算：等量代换/份数传导/守恒挪补）与跳过卡（该放弃的直觉）参数化出题器。
所有答案均由脚本独立暴力校验/枚举得出，assert 失败即报错退出。
输出: gen_E_output.json (UTF-8 无 BOM)
"""
import json, random, itertools, io, os

random.seed(20260909)
OUT = []
SEEN = set()

def add(h, t, s, o, a, e, tr=""):
    if s in SEEN:
        return False
    assert len(o) == 4 and len(set(o)) == 4, "选项重复: " + s
    if a >= 0:
        assert o[a] is not None
    SEEN.add(s)
    OUT.append({"h": h, "t": t, "s": s, "o": [str(x) for x in o], "a": a, "e": e, "tr": tr})
    return True

def shuffle_opts(ans, dis):
    """ans: 正确答案字符串; dis: 3 个干扰项字符串。返回(选项列表, 正确下标)"""
    opts = [ans] + list(dis)
    assert len(set(map(str, opts))) == 4, (ans, dis)
    random.shuffle(opts)
    return opts, opts.index(ans)

def brute_unique(cond, lo=1, hi=500):
    hits = [v for v in range(lo, hi + 1) if abs(cond(v)) < 1e-9]
    assert len(hits) == 1, "暴力解不唯一: %s" % hits
    return hits[0]

def num_dis(ans, deltas=None):
    deltas = deltas or [-1, 1, 2, -2, 3, -3, 5, -5, 10, -10]
    out = []
    for d in deltas:
        v = ans + d
        if v > 0 and v != ans and v not in out:
            out.append(v)
        if len(out) == 3:
            break
    assert len(out) == 3
    return out

SKIP_HINT = "（考场45秒内无法完成，正确动作是跳过）"

# ============================================================
# 一、深钩代换 ×25
# ============================================================
def gen_daihuan():
    n = 0
    # G1 工程半程代换：甲m天完成，甲m天工作量=乙n天，甲做a天后乙接手到一半
    grids1 = [(8, 2, 12), (8, 3, 12), (10, 2, 15), (10, 4, 15), (10, 3, 20),
              (12, 3, 18), (12, 4, 16), (12, 2, 24), (9, 3, 12), (15, 5, 20),
              (12, 5, 18), (10, 1, 15), (8, 1, 16), (16, 4, 24), (9, 2, 15)]
    for (m, a, nn) in grids1:
        ans = nn * (0.5 - a / m)
        if ans != int(ans) or ans < 1:
            continue
        ans = int(ans)
        cond = lambda v, m=m, a=a, nn=nn: a / m + v / nn - 0.5
        chk = brute_unique(cond)
        assert chk == ans
        s = (f"甲单独{m}天完成一项工程，甲{m}天完成的工作量乙需要{nn}天。"
             f"甲先做{a}天，剩下的由乙单独做，恰好完成全部工程的一半时，乙做了多少天？")
        o, ai = shuffle_opts(str(ans), [str(x) for x in num_dis(ans)])
        if add("深钩代换", "深钩", s, o, ai,
               f"设总量1，甲速1/{m}，乙速1/{nn}。代换：一半1/2=甲{a}天+乙x天 → x={nn}×(1/2−{a}/{m})={ans}天。",
               "易把“甲m天=乙n天”误当效率比m:n（实为n:m）。"):
            n += 1
    # G2 打印折算：A机a分钟打b页，A机4分钟=B机5分钟，B机打P页需几分钟
    grids2 = [(4, 24, 90), (5, 30, 80), (6, 45, 96), (8, 40, 75), (5, 20, 96),
              (4, 30, 60), (6, 36, 100), (8, 48, 90), (5, 40, 54), (4, 36, 75)]
    for (a, b, P) in grids2:
        spB = (b / a) * 4 / 5
        ans = P / spB
        if ans != int(ans) or ans < 2:
            continue
        ans = int(ans)
        cond = lambda v, b=b, a=a, P=P: (b / a) * 4 / 5 * v - P
        assert brute_unique(cond) == ans
        s = (f"一台A型打印机{a}分钟打{b}页，A型机4分钟打印的页数等于B型机5分钟打印的页数。"
             f"B型机打{P}页需要多少分钟？")
        o, ai = shuffle_opts(str(ans), [str(x) for x in num_dis(ans, [-2, -1, 1, 2, 3, -3, 4, -4, 6, 8])])
        if add("深钩代换", "深钩", s, o, ai,
               f"代换：A速{b}/{a}页/分，B速=A速×4/5={spB:g}页/分 → {P}÷{spB:g}={ans}分钟。",
               "误把“4分钟=5分钟”当成速度比4:5。"):
            n += 1
    # G3 浓度折算：甲c1%取m克、乙c2%取n克混合得c3%，求乙浓度
    grids3 = [(20, 60, 40, 22), (15, 80, 45, 21), (30, 50, 90, 33), (12, 70, 35, 16),
              (24, 55, 44, 27), (18, 90, 30, 24), (10, 40, 60, 15), (28, 35, 77, 34)]
    for (c1, m, nn, c3) in grids3:
        c2 = ((m + nn) * c3 - c1 * m) / nn
        if c2 != int(c2) or not (0 < c2 < 100):
            continue
        c2 = int(c2)
        cond = lambda v, c1=c1, m=m, nn=nn, c3=c3: (c1 * m + v * nn) / (m + nn) - c3
        assert brute_unique(cond, 1, 99) == c2
        s = (f"甲溶液浓度为{c1}%，乙溶液浓度为q%。取甲溶液{m}克、乙溶液{nn}克混合，"
             f"得到浓度为{c3}%的溶液，则乙溶液的浓度q是多少？")
        o, ai = shuffle_opts(str(c2) + "%", [str(x) + "%" for x in num_dis(c2, [-2, -1, 1, 2, 3, -3, 4, 5])])
        if add("深钩代换", "深钩", s, o, ai,
               f"溶质守恒代换：{c1}%×{m}+q×{nn}={c3}%×{m + nn} → q={c2}%。",
               "忘记分母是混合后总质量" + str(m + nn) + "克。"):
            n += 1
    # G4 单价折算：3斤苹果的钱=4斤梨的钱，买苹果x斤梨y斤共P元，求梨每斤
    grids4 = [(2, 3, 102), (4, 3, 150), (2, 5, 92), (6, 3, 176), (4, 6, 190),
              (2, 6, 132), (8, 3, 250), (5, 3, 156)]
    for (x, y, P) in grids4:
        p = 3 * P / (4 * x + 3 * y)
        if p != int(p) or p < 2:
            continue
        p = int(p)
        cond = lambda v, x=x, y=y, P=P: x * (4 * v / 3) + y * v - P
        assert brute_unique(cond) == p
        s = (f"3千克苹果的价钱等于4千克梨的价钱。某人买苹果{x}千克、梨{y}千克，"
             f"共付{P}元，则梨每千克多少元？")
        o, ai = shuffle_opts(str(p), [str(v) for v in num_dis(p, [-2, -1, 1, 2, 3, -3, 4, 6])])
        if add("深钩代换", "深钩", s, o, ai,
               f"代换：苹果价=4/3梨价 → ({x}×4/3+{y})梨价={P} → 梨价={P}÷{4 * x + 3 * y}/3={p}元。",
               "把“3斤苹果=4斤梨”误写成苹果价是梨的3/4倍的反向。"):
            n += 1
    # G5 份数传导链：甲:乙=A:B，乙:丙=C:D，丙比甲多d，求丙
    grids5 = [((4, 5), (2, 3), 21), ((3, 4), (4, 5), 22), ((5, 6), (3, 4), 21),
              ((2, 3), (6, 7), 36), ((4, 7), (7, 9), 40), ((3, 5), (10, 12), 44),
              ((5, 8), (4, 5), 45), ((2, 5), (5, 6), 52)]
    for ((A, B), (C, D), d) in grids5:
        # 甲:丙 = A*C : B*D ; 丙-甲 = (BD-AC)份
        den = B * D - A * C
        if den <= 0 or d % den:
            continue
        unit = d // den
        bing = B * D * unit
        jia = A * C * unit
        if bing <= 0:
            continue
        cond = lambda v, A=A, B=B, C=C, D=D, d=d: (v - v * A * C / (B * D)) - d
        assert brute_unique(cond) == bing
        s = (f"甲:乙={A}:{B}，乙:丙={C}:{D}，丙比甲多{d}，则丙是多少？")
        o, ai = shuffle_opts(str(bing), [str(v) for v in num_dis(bing, [-3, -2, -1, 1, 2, 3, 4, 6])])
        if add("深钩代换", "深钩", s, o, ai,
               f"传导：甲:丙={A * C}:{B * D}，差{den}份={d} → 1份={unit}，丙={B * D}×{unit}={bing}。",
               "直接把两个比相加而不通过乙统一份数。"):
            n += 1
    # G6 效率代换合作：甲效率是乙k倍，乙单独n天，合作几天
    grids6 = [(2, 12), (3, 16), (2, 15), (3, 20), (2, 18), (4, 15), (3, 24), (2, 21), (4, 20)]
    for (k, nn) in grids6:
        if nn % (k + 1):
            continue
        ans = nn // (k + 1)
        cond = lambda v, k=k, nn=nn: v * (k + 1) / nn - 1
        assert brute_unique(cond) == ans
        s = (f"甲的效率是乙的{k}倍，乙单独完成一项工程需要{nn}天。两人合作完成这项工程需要多少天？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-2, -1, 1, 2, 3, -3, 5])])
        if add("深钩代换", "钩子", s, o, ai,  # 一步 nn÷(k+1) 即得，降级为钩子
               f"代换：甲={k}乙，合作效率=({k}+1)乙 → 天数={nn}÷({k}+1)={ans}天。",
               "误用“效率比k:1”直接除以k。"):
            n += 1
    # G7 货币/积分兑换折算：甲币3枚=乙币5枚价值，m枚甲币相当于乙币几枚
    grids7 = [(3, 5, 6), (3, 5, 12), (4, 7, 8), (2, 3, 6), (5, 3, 10), (4, 9, 12), (7, 5, 14)]
    for (a, b, m) in grids7:
        ans = m * a / b
        if ans != int(ans):
            continue
        ans = int(ans)
        cond = lambda v, a=a, b=b, m=m: v * b - m * a  # 乙v枚价值 v*b=甲m枚价值 m*a
        assert brute_unique(cond) == ans
        s = (f"某种积分规则下，{a}枚甲券的价值等于{b}枚乙券的价值。"
             f"{m}枚甲券可以兑换多少枚乙券？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-2, -1, 1, 2, 3, -3, 4, 5])])
        if add("深钩代换", "钩子", s, o, ai,  # 一步 m×a/b 即得，降级为钩子
               f"代换：甲券值={b}/{a}乙券 → {m}甲={m}×{a}/{b}={ans}枚乙券。",
               "兑换比方向取反（乘b/a）。"):
            n += 1
    assert n >= 25, "代换题不足: %d" % n
    # 超额的按生成顺序保留前25：截断
    return n

# 先生成到全局，再截断在 main 中处理

# ============================================================
# 二、深钩守恒 ×25
# ============================================================
def gen_shouheng():
    n = 0
    # H1 平均调动：甲组a人均x，乙组b人均y，甲调1人到乙后平均相同，求调走者分数
    grids1 = [(9, 86, 7, 78), (8, 90, 6, 76), (10, 84, 8, 74), (7, 92, 5, 70),
              (11, 82, 9, 68), (9, 88, 11, 76), (6, 94, 4, 72), (12, 80, 8, 62)]
    for (a, x, b, y) in grids1:
        t = (a * x * (b + 1) - (a - 1) * b * y) / (a + b)
        if t != int(t) or t >= x or t <= y:
            continue
        t = int(t)
        cond = lambda v, a=a, x=x, b=b, y=y: (a * x - v) / (a - 1) - (b * y + v) / (b + 1)
        assert brute_unique(cond) == t
        s = (f"甲组{a}人平均分{x}分，乙组{b}人平均分{y}分。从甲组调1人到乙组后，"
             f"两组平均分恰好相同，调走的这个人考了多少分？")
        o, ai = shuffle_opts(str(t), [str(v) for v in num_dis(t, [-3, -2, -1, 1, 2, 3, 4])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"守恒列等：(a{x}−t)/{a - 1}=({b}×{y}+t)/{b + 1} → t={t}分。",
               "分母误用原人数a、b而不是调动后的a−1、b+1。"):
            n += 1
    # H2 和差挪补：甲给乙d元后甲是乙k倍，求甲原有
    grids2 = [(3, 40, 560), (2, 60, 420), (3, 50, 800), (4, 30, 510), (2, 80, 640),
              (5, 40, 800), (3, 70, 1030), (2, 45, 405)]
    for (k, d, S) in grids2:
        # 甲' + 乙' = S, 甲' = k*乙' → 甲' = kS/(k+1)
        jia2 = k * S / (k + 1)
        if jia2 != int(jia2):
            continue
        jia2 = int(jia2)
        jia0 = jia2 + d
        cond = lambda v, k=k, d=d, S=S: (v - d) - k * (S - v + d)
        assert brute_unique(cond, 1, 3000) == jia0
        s = (f"甲、乙两人共有{S}元。甲给乙{d}元后，甲的钱数恰好是乙的{k}倍。"
             f"甲原来有多少元？")
        o, ai = shuffle_opts(str(jia0), [str(v) for v in num_dis(jia0, [-30, -20, -10, 10, 20, 30, 40])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"和守恒：给钱后总和仍{S}，乙'={S}/{k + 1}，甲'={jia2}，甲原={jia2}+{d}={jia0}元。",
               "忘记把给的{d}元加回去（问的是“原来”）。".format(d=d) if False else "忘记把给的d元加回去（问的是“原来”）。"):
            n += 1
    # H3 平均速度守恒：去v1回v2，求往返平均速度
    grids3 = [(40, 60, 48), (30, 60, 40), (45, 60, 51.428571), (50, 75, 60), (36, 45, 40),
              (20, 30, 24), (60, 90, 72), (24, 40, 30)]
    for (v1, v2, ans) in grids3:
        if ans != int(ans):
            continue
        ans = int(ans)
        cond = lambda v, v1=v1, v2=v2: 2 / (1 / v1 + 1 / v2) - v
        assert brute_unique(cond) == ans
        s = (f"某人驾车往返A、B两地，去程速度每小时{v1}千米，返程速度每小时{v2}千米。"
             f"往返全程的平均速度是多少千米/小时？")
        dis = []
        for cand in [str((v1 + v2) // 2)] + [str(v) for v in num_dis(ans, [-6, -4, 4, 6, 8, -8, -3, 3])]:
            if cand != str(ans) and cand not in dis:
                dis.append(cand)
        dis = dis[:3]
        o, ai = shuffle_opts(str(ans), dis)
        if add("深钩守恒", "深钩", s, o, ai,
               f"调和平均：2×{v1}×{v2}÷({v1}+{v2})={ans}千米/小时。",
               "误取算术平均(%d+%d)/2。"):
            n += 1
    # H4 混合守恒：浓度a的x克+浓度b的y克=c%，求x
    grids4 = [(30, 12, 20, 500), (25, 10, 18, 450), (40, 16, 22, 600), (18, 42, 26, 480),
              (50, 20, 28, 520), (15, 45, 24, 560), (35, 11, 19, 480)]
    for (a, b, c, Y) in grids4:
        x = (c - b) * Y / (a - c)
        if x != int(x) or x <= 0:
            continue
        x = int(x)
        cond = lambda v, a=a, b=b, c=c, Y=Y: (a * v + b * Y) / (v + Y) - c
        assert brute_unique(cond, 1, 2000) == x
        s = (f"有甲、乙两种糖水，甲的浓度为{a}%，乙的浓度为{b}%。取甲糖水x克与乙糖水{Y}克混合，"
             f"得到浓度为{c}%的糖水，则取甲糖水多少克？")
        o, ai = shuffle_opts(str(x), [str(v) for v in num_dis(x, [-40, -20, -10, 10, 20, 40, 60])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"溶质守恒：{a}%x+{b}%×{Y}={c}%×(x+{Y}) → x={x}克。",
               "漏掉右端总质量(x+%d)中未知数x。"):
            n += 1
    # H5 打折利润守恒：原利润率r定价卖m件；改d折后多卖n件总利润不变，求进价
    grids5 = [(0.25, 10, 15, 9, 200), (0.2, 10, 15, 9, 250), (0.5, 8, 16, 8, 120),
              (0.25, 12, 18, 9, 160), (0.2, 15, 10, 8.8, 300), (0.5, 6, 12, 8, 90)]
    for (r, m, nn, d, cost) in grids5:
        # m*r*cost = (m+n)*(d*(1+r)*cost - cost)
        lhs_k = m * r
        rhs_k = (m + nn) * (d * (1 + r) - 1)
        if abs(lhs_k - rhs_k) > 1e-9 or rhs_k <= 0 or cost != int(cost):
            continue
        profit = r * cost
        cond = lambda v, r=r, m=m, nn=nn, d=d: m * r * v - (m + nn) * (d * (1 + r) * v - v)
        assert brute_unique(cond, 1, 2000) == cost
        s = (f"某商品按利润率{int(r * 100)}%定价，每天可卖出{m}件。若改按{d}折出售，"
             f"每天可卖出{m + nn}件，总利润与原来恰好相同，则该商品每件进价是多少元？")
        o, ai = shuffle_opts(str(cost), [str(v) for v in num_dis(cost, [-40, -20, 20, 40, 50, -50, 25])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"利润守恒：{m}×{int(r * 100)}%×进价=({m + nn})×({d}×1.{int(r * 100)}−1)×进价 → 进价={cost}元。",
               "打折价基数是定价(1+r)×进价，不是进价。"):
            n += 1
    # H6 往返时间守恒：去v1回v2共t小时，求单程路程
    grids6 = [(40, 60, 5, 120), (30, 20, 10, 120), (45, 30, 8, 144), (60, 40, 10, 240),
              (36, 24, 10, 144), (50, 30, 8, 150), (72, 48, 10, 288)]
    for (v1, v2, t, s_) in grids6:
        if abs(s_ / v1 + s_ / v2 - t) > 1e-9:
            continue
        cond = lambda v, v1=v1, v2=v2, t=t: v / v1 + v / v2 - t
        assert brute_unique(cond) == s_
        s = (f"一辆汽车往返甲、乙两地，去程每小时{v1}千米，返程每小时{v2}千米，"
             f"往返共用{t}小时。甲乙两地相距多少千米？")
        o, ai = shuffle_opts(str(s_), [str(v) for v in num_dis(s_, [-40, -30, -20, 20, 30, 40, 60])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"时间守恒：s/{v1}+s/{v2}={t} → s={t}×({v1}×{v2})/({v1}+{v2})={s_}千米。",
               "误用平均速度%d乘%d小时（平均速度是全程/全程时间）。" % (2 * v1 * v2 // (v1 + v2), t)):
            n += 1
    # H7 库存守恒：每天进a出b，x天后剩c，求初始库存
    grids7 = [(60, 85, 12, 430), (45, 70, 14, 590), (80, 95, 16, 670), (50, 62, 20, 830),
              (35, 44, 15, 580), (70, 88, 10, 610)]
    for (inn, out, days, left) in grids7:
        init = left - (inn - out) * days
        if init <= 0:
            continue
        cond = lambda v, inn=inn, out=out, days=days, left=left: v + (inn - out) * days - left
        assert brute_unique(cond, 1, 5000) == init
        s = (f"某仓库原有若干吨货物，现在每天运进{inn}吨、运出{out}吨，{days}天后仓库恰好剩{left}吨。"
             f"仓库原有货物多少吨？")
        o, ai = shuffle_opts(str(init), [str(v) for v in num_dis(init, [-60, -30, 30, 60, 90, -90, 120])])
        if add("深钩守恒", "深钩", s, o, ai,
               f"净流量守恒：原有+({inn}−{out})×{days}={left} → 原有={left}−{out - inn}×{days}={init}吨。",
               "净流出算错方向（运出大于运进）。"):
            n += 1
    assert n >= 25, "守恒题不足: %d" % n
    return n

# ============================================================
# 三、跳过卡 ×25（真实答案由暴力枚举/递推算出）
# ============================================================
def pair_pairs(N):
    pairs = []
    for a in range(2, N):
        if N % a:
            continue
        b = N // a
        if b > a:
            pairs.append((a, b))
    return pairs

def count_divisors(N):
    return sum(1 for i in range(1, N + 1) if N % i == 0)

def factorize_str(N):
    """程序实时质因数分解，返回 '2^4×3×5×7' 形式字符串。"""
    fac, n, p = {}, N, 2
    while p * p <= n:
        while n % p == 0:
            fac[p] = fac.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    return "×".join(f"{q}^{e}" if e > 1 else str(q) for q, e in sorted(fac.items()))

def stairs_dp(n):
    # 每步1或2级，不能连续两步都是2级
    from functools import lru_cache
    @lru_cache(None)
    def f(left, last2):
        if left == 0:
            return 1
        tot = f(left - 1, False)
        if left >= 2 and not last2:
            tot += f(left - 2, True)
        return tot
    return f(n, False)

def sock_guarantee(caps, k):
    """n只袜子(各色最多caps[i]只)任意取法都含k双(颜色不同的两双或同色4只算两双)"""
    def ok(counts):
        pairs = sum(c // 2 for c in counts)
        return pairs >= k
    for nn in range(0, sum(caps) + 1):
        bad = any(not ok(c) for c in itertools.product(*[range(cap + 1) for cap in caps]) if sum(c) == nn)
        if not bad:
            return nn
    return None

def gen_tiaoguo():
    n = 0
    # K1 乘积因数对枚举
    for N, extra in [(960, "其中两数都不等于20"), (720, None), (1800, None), (1440, None)]:
        pairs = pair_pairs(N)
        if extra:
            pairs = [p for p in pairs if 20 not in p]
        ans = len(pairs)
        assert ans >= 6
        s = f"两个大于1且不相等的正整数，乘积等于{N}" + ("，且都不等于20，" if extra else "，") + "这样的数对共有多少对？（不计顺序）"
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-3, -2, -1, 1, 2, 3, 4])])
        e = f"真解：需枚举{N}的全部因数对{ans}对（如{pairs[0]}…），口算无法完成。考场45秒内做不完，应跳过。"
        if add("跳过卡", "跳过", s, o, -1, e, "枚举型：估不出来，硬算超时。"):
            n += 1
    # K2 约数个数（分解式由程序实时生成，杜绝硬编码模板错配）
    for N in [2880, 1680, 2520]:
        ans = count_divisors(N)
        s = f"正整数{N}的正约数共有多少个？"
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-4, -2, -1, 1, 2, 3, 4])])
        e = f"真解：{N}={factorize_str(N)}，约数个数=指数+1连乘，口算易错；考场应跳过。"
        if add("跳过卡", "跳过", s, o, -1, e, "分解+乘法原理，两分钟题。"):
            n += 1
    # K3 三位数分类计数
    def cnt3(pred):
        return sum(1 for x in range(100, 1000) if pred(x))
    preds = [
        ("恰有一个数字是6", lambda x: len(set(str(x))) == 3 and str(x).count('6') == 1),
        ("各位数字均为偶数", lambda x: all(int(c) % 2 == 0 for c in str(x)) and len(set(str(x))) == 3),
        ("十位数字比个位数字大2", lambda x: len(set(str(x))) == 3 and int(str(x)[1]) - int(str(x)[2]) == 2),
        ("能被5整除", lambda x: x % 5 == 0 and len(set(str(x))) == 3),
    ]
    for desc, f in preds:
        ans = cnt3(f)
        s = f"各位数字互不相同的三位数中，{desc}的三位数共有多少个？"
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-9, -6, -5, 5, 6, 9, 10, -10, 12])])
        e = f"真解：程序枚举100~999验证为{ans}个；分类加法需逐位讨论，45秒内极易漏类，考场应跳过。"
        if add("跳过卡", "跳过", s, o, -1, e, "多类分类计数，漏类高发。"):
            n += 1
    # K4 逻辑嵌套（说谎者）：暴力找自洽指派
    stmts = {
        'A': lambda h: not h['D'],
        'B': lambda h: not h['C'],
        'C': lambda h: (not h['A']) and (not h['D']),
        'D': lambda h: not h['B'],
    }
    sols = []
    for bits in itertools.product([True, False], repeat=4):
        h = dict(zip('ABCD', bits))
        if all(h[p] == stmts[p](h) for p in 'ABCD'):
            sols.append(bits)
    liars = {sum(1 for b in sol if not b) for sol in sols}
    assert len(sols) >= 1 and len(liars) == 1, "说谎题不自洽"
    ans = liars.pop()
    names = '甲乙丙丁'
    s = ("甲、乙、丙、丁四人中有人说谎。甲说：“丁在说谎。”乙说：“丙在说谎。”"
         "丙说：“甲和丁都在说谎。”丁说：“乙在说谎。”已知每人的话要么全真要么全假，"
         "则四人中说谎的有多少人？")
    o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-1, 1, 2, -2])])
    e = (f"真解：设每人为真/假共16种组合逐一验证，自洽解中说谎者{ans}人；"
         f"多重逻辑嵌套口算极易绕晕，考场应跳过。")
    if add("跳过卡", "跳过", s, o, -1, e, "2^4种指派，嵌套自指，口算灾难。"):
        n += 1
    # K5 递推计数（台阶）
    for nn in [10, 12, 11]:
        ans = stairs_dp(nn)
        s = (f"爬一段{nn}级台阶，每步只能上1级或2级，且不能连续两步都上2级，"
             f"共有多少种不同的爬法？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-5, -3, -2, 2, 3, 5, 8, -8, 13])])
        e = f"真解：递推f(余n,上步是否2级)程序算得{ans}种；普通跳台阶是斐波那契但加限制后需二维递推，考场应跳过。"
        if add("跳过卡", "跳过", s, o, -1, e, "带限制递推，直接斐波那契会掉坑。"):
            n += 1
    # K6 抽屉保证（最不利构造）
    for caps, k in [((8, 6, 4), 2), ((10, 8, 6), 2), ((6, 6, 6, 6), 2)]:
        ans = sock_guarantee(caps, k)
        assert ans and not sock_guarantee(caps, k) is None
        colors = len(caps)
        cname = "黑、白、灰" if colors == 3 else "黑、白、灰、蓝"
        cword = "三种" if colors == 3 else "四种"
        s = (f"抽屉里混放着{cname}{cword}颜色的袜子若干只（分别有{'、'.join(map(str, caps))}只），"
             f"袜子不分左右。至少取多少只才能保证一定有两双袜子（两双颜色可以不同）？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-2, -1, 1, 2, 3])])
        e = (f"真解：程序枚举所有取法验证，最不利情况为{'、'.join(map(str, [c for c in caps]))}各取后仍差一双，"
             f"需取{ans}只才保证两双；最不利构造枚举量大，考场应跳过。")
        if add("跳过卡", "跳过", s, o, -1, e, "最不利构造需穷举验证，直觉常差1。"):
            n += 1
    # K7 圆桌排列约束
    def circle_perms(m, cond):
        cnt = 0
        for perm in itertools.permutations(range(1, m)):
            arr = (0,) + perm
            pos = {p: i for i, p in enumerate(arr)}
            ok = True
            if abs(pos[0] - pos[1]) in (1, m - 1):
                ok = False
            if abs(pos[2] - pos[3]) in (1, m - 1):
                ok = False
            if cond == 'adj' and not ok:
                continue
            cnt += ok
        return cnt
    ans = circle_perms(6, 'adj')
    s = "6人围圆桌而坐（旋转视为相同），要求甲与乙不相邻，且丙与丁也不相邻，共有多少种坐法？"
    o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-12, -6, -3, 3, 6, 12, 18])])
    e = f"真解：固定甲后枚举5!=120种圆排，程序验证满足条件的有{ans}种；双重不相邻容斥易错，考场应跳过。"
    if add("跳过卡", "跳过", s, o, -1, e, "环形+双重约束容斥，正难则反也难。"):
        n += 1
    # K8 网格路径（避障）。坐标约定：禁点 av=(i, j)，i=从下往上第 i+1 行、j=从左往右第 j+1 列（0 起）；
    # 题干中的点(x,y)表示"从左往右第 x 列、从下往上第 y 行"，对应 av=(y-1, x-1)。
    def grid_paths(W, H, avoid):
        dp = [[0] * (W + 1) for _ in range(H + 1)]
        dp[0][0] = 1
        for i in range(H + 1):
            for j in range(W + 1):
                if (i, j) == avoid or (i, j) == (0, 0):
                    continue
                dp[i][j] = (dp[i - 1][j] if i else 0) + (dp[i][j - 1] if j else 0)
        return dp[H][W]
    from math import comb
    for (W, H, av, desc) in [(4, 4, (2, 2), "但不经过中心格（第3行第3列的交叉点）"),
                             (5, 3, (1, 2), "但不经过点(3,2)（从左往右第3列、从下往上第2行）"),
                             (4, 3, (2, 1), "但不经过点(2,3)（从左往右第2列、从下往上第3行）")]:
        total = grid_paths(W, H, (-1, -1))
        ans = grid_paths(W, H, av)
        # 第二种公式交叉验证：总路径 C(W+H,W) 减去经禁点的 C(i+j,i)×C((H-i)+(W-j), W-j)
        assert total == comb(W + H, W)
        assert ans == total - comb(av[0] + av[1], av[0]) * \
            comb((H - av[0]) + (W - av[1]), W - av[1]), (W, H, av, ans)
        s = (f"在{W}×{H}的方格网格中，从左下角走到右上角，每步只能向右或向上，{desc}，"
             f"共有多少条不同路径？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-10, -6, -4, 4, 6, 10, 14])])
        e = f"真解：全部{total}条，扣去经过禁点的{total - ans}条，程序递推得{ans}条；减法容斥易重复，考场应跳过。"
        if add("跳过卡", "跳过", s, o, -1, e, "避障路径需分域递推，加法原理分情况繁琐。"):
            n += 1
    # K9 不定方程/运输方案枚举
    for (big, small, total, at_least_one) in [(7, 4, 89, True), (8, 5, 103, True), (6, 4, 74, True), (9, 5, 112, True)]:
        sols = [(a, total - a) for a in range(0, total // big + 1)
                if (total - a * big) >= 0 and (total - a * big) % small == 0
                and (a >= 1 or not at_least_one) and (total - a >= 1 or not at_least_one)]
        ans = len(sols)
        assert ans >= 2
        s = (f"用大车和小车一起运{total}吨货物，大车每次运{big}吨，小车每次运{small}吨，"
             f"每车都装满且两种车都要用。共有多少种派车方案（不同的大车次数即不同方案）？")
        o, ai = shuffle_opts(str(ans), [str(v) for v in num_dis(ans, [-3, -2, -1, 1, 2, 3, 4])])
        e = (f"真解：设大车a次，则a需使{total}−{big}a是{small}的倍数，逐一试数得{ans}组解；"
             f"枚举型二元构造，45秒试不完，考场应跳过。")
        if add("跳过卡", "跳过", s, o, -1, e, "整除性试数，枚举量大。"):
            n += 1
    # K10 逻辑嵌套 ×2（与K4说谎者链不同结构，答案均由程序枚举得出）
    # K10a 名次推断：4人赛跑无并列，每人一句话，恰有一人说真话，问第一名
    people = "甲乙丙丁"
    best = None
    for _ in range(6000):
        stmts = [(random.randrange(4), random.randrange(4), random.random() < 0.5)
                 for _ in range(4)]
        sols = []
        for perm in itertools.permutations(range(4)):   # perm[i]=第i人的名次(0起)
            truth = sum(1 for (p, kk, neg) in stmts
                        if (perm[p] == kk) != neg)
            if truth == 1:
                sols.append(perm)
        firsts = {s0[0] for s0 in sols}
        if len(sols) == 1:
            best = (stmts, sols[0])
            break
    assert best is not None, "K10a 未找到唯一解的陈述组合"
    stmts, win_perm = best
    qtxt = []
    for idx, (p, kk, neg) in enumerate(stmts):
        core = f"{people[p]}{'不是' if neg else '是'}第{kk + 1}名"
        qtxt.append(f"{people[idx]}说：“{core}。”")
    s = ("甲、乙、丙、丁四人赛跑（无并列名次）。" + "".join(qtxt) +
         "已知只有一人说了真话，则第一名是谁？")
    first = people[win_perm[0]]
    o, ai = shuffle_opts(first, [p for p in people if p != first])
    e = (f"真解：程序枚举4!=24种名次组合逐一验真，仅1组恰有1句真话，第一名={first}；"
         f"多重嵌套口算极易绕晕，考场应跳过。")
    if add("跳过卡", "跳过", s, o, -1, e, "2层嵌套+全排列枚举，口算灾难。"):
        n += 1
    # K10b 五人依次说"恰有k人是骗子"，求骗子数（自指计数结构）
    valid = [L for L in range(6)
             if sum(1 for i in range(5) if (i + 1 != L)) == L]  # 假话数=骗子数才自洽
    assert valid == [4], valid
    ansL = valid[0]
    s = ("某岛五人每人只说真话或只说假话。甲说：“我们中恰有1人是骗子。”乙说：“恰有2人。”"
         "丙说：“恰有3人。”丁说：“恰有4人。”戊说：“恰有5人。”则说谎的共有多少人？")
    o, ai = shuffle_opts(str(ansL), [str(v) for v in num_dis(ansL, [-1, 1, 2, -2])])
    e = (f"真解：程序枚举骗子数L=0~5逐个验证自洽，只有L={ansL}时假话条数恰为{ansL}；"
         f"自指计数结构口算易错，考场应跳过。")
    if add("跳过卡", "跳过", s, o, -1, e, "自指嵌套计数，直觉常答3或5。"):
        n += 1
    # K11 整数线性规划/最优化 ×2（真解由程序枚举算出）
    # K11a 费用最省：租船组合
    for (N, bx, by, bp, sp) in [(32, 6, 4, 50, 30), (29, 5, 3, 42, 24)]:
        costs = sorted({a * bp + b2 * sp
                        for a in range(N // bx + 2) for b2 in range(N // by + 2)
                        if a * bx + b2 * by >= N and (a or b2)})
        assert len(costs) >= 4 and costs[0] < costs[1], costs
        ansC = costs[0]
        s = (f"某班{N}名师生租船出游，大船每条坐{bx}人、租金{bp}元，小船每条坐{by}人、"
             f"租金{sp}元，船可以坐不满。人人有座的情况下最少要花多少元？")
        o, ai = shuffle_opts(str(ansC), [str(v) for v in costs[1:4]])
        e = (f"真解：程序枚举大船a条小船b条全部组合（{bx}a+{by}b≥{N}），租金最低{costs[:3]}…"
             f"最省{ansC}元；直觉选错船型就掉坑，考场应跳过。")
        if add("跳过卡", "跳过", s, o, -1, e, "整型两变量最优化，枚举量大。"):
            n += 1
    # K11b 至少几间：两种房型住满且都要订
    for N in [26, 30]:
        sols = [(x, (N - 4 * x) // 3) for x in range(1, N // 4 + 1)
                if (N - 4 * x) > 0 and (N - 4 * x) % 3 == 0]
        assert len(sols) >= 2, (N, sols)
        ansX = min(x for x, _ in sols)
        s = (f"某公司{N}名员工入住宾馆，只有4人间和3人间，每间都必须住满，"
             f"且两种房型都要订。4人间至少要订几间？")
        o, ai = shuffle_opts(str(ansX), [str(v) for v in num_dis(ansX, [-2, -1, 1, 2, 3])])
        e = (f"真解：程序枚举4x+3y={N}的全部正整数解得{sols[:3]}…，x最小={ansX}；"
             f"同余试数+最值二步，45秒内难完成，考场应跳过。")
        if add("跳过卡", "跳过", s, o, -1, e, "整除约束+最优化，枚举型。"):
            n += 1
    assert n >= 29, "跳过卡不足: %d" % n
    return n

def main():
    gen_daihuan()
    gen_shouheng()
    gen_tiaoguo()
    # 截断每类：深钩两类25、跳过卡30（含新增逻辑嵌套与整型规划卡）
    final = []
    cnt = {}
    CAP = {"跳过卡": 30}
    for q in OUT:
        c = cnt.get(q["h"], 0)
        if c < CAP.get(q["h"], 25):
            final.append(q)
            cnt[q["h"]] = c + 1
    # 去重二次确认 + 格式校验
    assert len(set(q["s"] for q in final)) == len(final)
    for q in final:
        assert q["t"] == ("跳过" if q["h"] == "跳过卡" else ("深钩" if q["t"] == "深钩" else "钩子"))
        assert len(q["o"]) == 4 and len(set(q["o"])) == 4
        if q["h"] == "跳过卡":
            assert q["a"] == -1
        else:
            assert 0 <= q["a"] <= 3
            assert len(q["e"]) <= 80, (q["e"], len(q["e"]))
    from collections import Counter
    print("分布:", dict(Counter(q["h"] for q in final)))
    print("t分布:", dict(Counter(q["t"] for q in final)))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_E_output.json")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=1)
    print("共 %d 题 -> %s" % (len(final), path))

if __name__ == "__main__":
    main()
