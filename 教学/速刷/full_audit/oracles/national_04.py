"""Offline port of national_04 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product, accumulate
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'national_04'
DUP = {17: 8, 20: 10, 22: 11, 23: 16, 24: 14, 26: 8, 27: 18, 28: 19, 49: 36, 50: 37, 52: 38, 53: 43, 54: 44, 55: 35, 56: 46, 57: 51, 58: 41, 59: 45, 61: 40, 62: 42, 63: 48, 80: 68, 85: 72, 86: 74, 87: 75, 88: 77, 90: 83, 91: 81, 92: 82, 95: 72, 96: 76, 97: 73, 98: 74, 99: 77}

def fmt(v):
    if isinstance(v, F):
        return str(v.numerator) if v.denominator == 1 else str(v)
    return str(v)

def solve(i):
    k = DUP.get(i, i)
    d = {}
    if k == 0:
        b = F(1, 4) / 11
        bc = F(1, 2) / 15
        ab = F(1, 4) / 6
        a = ab - F(11, 10) * b
        c = bc - F(11, 10) * b
        v = 1 / (a + c + F(11, 10) * b)
        d = dict(a=a, b_alone=b, c=c, b_coop=F(11, 10) * b, total_rate=1 / v)
    elif k == 1:
        sol = [(a, b, 50 - a - b) for a in range(1, 49) for b in range(1, 50 - a) if 733 * a + 700 * b + 800 * (50 - a - b) == 37460]
        assert len(sol) == 1
        v = sol[0][1]
        d = {'integer_solutions': sol}
    elif k == 2:
        t = F(2)
        L = F(5)
        h = t / 2
        s = L - t
        tri = t * t / 2
        trap = (L - 2 * t + s) * h / 2
        assert tri == trap
        v = 4 * tri / (s * s)
        d = dict(outer=L, corner_leg=t, inner=s, triangle=tri, trapezoid=trap)
        v = '8:9' if v == F(8, 9) else str(v)
    elif k == 3:
        groups = [g for g in combinations(range(3, 22), 6) if sum(g) == 36 and max(g) <= 3 * min(g)]
        assert len(groups) == 1
        n = groups[0][-2]
        v = (1 - F(comb(36 - n, 2), comb(36, 2))) * 100
        d = dict(groups=groups, second=n)
        v = fmt(v) + '%'
    elif k == 4:
        t = F(1 + F(3, 5) * 4, 2 - F(3, 5) * 3)
        n = 5 * t - 4 - (4 * t + 1)
        v = '多' + fmt(n) + '辆'
        d = dict(unit=t, after=[5 * t - 4, 4 * t + 1, 3 * t + 4, 2 * t - 1])
    elif k == 5:
        x = (172 - F(15, 100) * 960) / F(5, 100)
        y = 960 - x
        diff = F(4, 5) * x - F(17, 20) * y
        v = '多' + fmt(diff) + '万元'
        d = dict(last_half=[x, y], this_half=[F(4, 5) * x, F(17, 20) * y])
    elif k == 6:
        b = F(6000 - 240 * 20, 2 * (30 - 20) + (24 - 20))
        v = 240 - 3 * b
        d = dict(quantities=[2 * b, b, v], revenue=30 * 2 * b + 24 * b + 20 * v)
    elif k == 7:
        sol = []
        for a in range(21):
            for e in range(a + 1, 21 - a):
                for j in range(21):
                    for f in range(21 - j):
                        if 3 * a + 20 - a - e + 3 * j + 20 - j - f == 82:
                            sol.append((a, e, 20 - a - e, j, f, 20 - j - f))
        v = min((t[3] for t in sol))
        d = dict(minimum=v, witnesses=[t for t in sol if t[3] == v], tested='all nonnegative counts in both 20-question sections')
    elif k == 8:
        triple = 50
        r = 2 * triple
        er = r - triple
        ef = 100 - er
        eng = 2 * (ef + triple)
        eonly = eng - er - ef - triple
        fonly = 150 - eonly
        v = fonly + ef + triple
        d = dict(ER_only=er, EF_only=ef, E_only=eonly, F_only=fonly, all3=triple)
    elif k == 9:
        buildings = F(65 + 43, 8 - 5)
        n = 5 * buildings + 65
        v = -n % buildings
        d = dict(buildings=buildings, original=n, added=v, new_per_building=(n + v) / buildings)
    elif k == 10:
        v = F(300, 1) / (F(2, 100) - F(8, 1000)) / 10000
        d = dict(revenue_yi=v, profit_wan=v * 10000 * F(12, 1000))
        v = str(float(v))
    elif k == 11:
        interview = [40, 100 - 40 - 50, 50]
        written = [F(1, 2), F(interview[1], 100) + F(15, 100), 0]
        written[2] = 1 - sum(written[:2])
        v = '2：1：1'
        assert written == [F(1, 2), F(1, 4), F(1, 4)]
        d = dict(interview=interview, written=written)
    elif k == 12:
        va = F(1)
        vb = F(20, 15)
        period = 80 / vb
        elapsed = 80
        v = period * (elapsed // period + 1) - elapsed
        d = dict(speed_A=va, speed_B=vb, lap_B=period, elapsed=elapsed, next_return=elapsed + v)
        v = fmt(v) + '秒'
    elif k == 13:
        counts = {m: comb(6, m) * (m - 1) * (5 - m) for m in (2, 3, 4)}
        v = sum(counts.values())
        brute = sum(((len(a) - 1) * (5 - len(a)) for m in (2, 3, 4) for a in combinations(range(6), m)))
        assert v == brute
        d = counts
    elif k == 14:
        configs = [(63 * t, 50 * t, 50 * t + 6) for t in range(1, 10) if 300 < 163 * t + 6 < 400]
        assert len(configs) == 1
        a, b, c = configs[0]
        c -= 3
        v = next((x for x in range(a + 1) if c + x >= 2 * (a - x)))
        d = dict(original=configs[0], after_first=[a, b + 3, c], moved=v, final=[a - v, c + v], one_less_fails=c + v - 1 < 2 * (a - v + 1))
    elif k == 15:
        sol = [(2 * z - 2, z, l) for z in range(1, 100) for l in range(1, 100) if 2 * (z + 2) == 3 * (l + 2) and z + l + 14 == 2 * z - 2 + 7]
        assert len(sol) == 1
        s = sum(sol[0])
        y = 2023 + (120 - s) // 3 + 1
        v = str(y) + '年'
        d = dict(ages_2023=sol[0], sum=s, before=s + 3 * (y - 1 - 2023), first_exceeds=s + 3 * (y - 2023))
    elif k == 16:
        ps = list(permutations(range(3)))
        f = [(a, b, c) for a, b, c in product(ps, repeat=3) if all((len({a[j], b[j], c[j]}) == 3 for j in range(3)))]
        v = F(len(f), len(ps) ** 3)
        d = dict(favorable=len(f), total=len(ps) ** 3, fixed_first_favorable=sum((a == (0, 1, 2) for a, b, c in f)))
    elif k == 18:
        count = lambda st, n: sum(((st + j) % 7 in [1, 4, 6] for j in range(n)))
        starts = [st for st in range(7) if count(st, 30) == 13 and count((st + 30) % 7, 31) == 14]
        assert len(starts) == 1
        dec = (starts[0] + 30 + 31 + 30) % 7
        last = max((day for day in range(1, 32) if (dec + day - 1) % 7 in [1, 4, 6]))
        v = '12月' + str(last) + '日'
        d = dict(september_first_weekday_Mon0=starts[0], december_first=dec, last=last)
    elif k == 19:
        bc = 60 * sqrt(2) - 50
        ed = 40 + (bc - 50) / sqrt(2)
        P = 40 + bc + 50 + ed + 60
        assert 210 < P < 220
        v = '在210~220米之间'
        d = dict(BC=bc, ED=ed, perimeter=P, exact='200+10√2')
    elif k == 21:
        t = F(4, F(1, 2))
        after = [3 * t + 8, 4 * t + 8, 5 * t + 8]
        after.append(4 * 43 - sum(after))
        later = [a + 15 for a in after]
        v = sum((a > 60 for a in later))
        d = dict(after_8_years=after, after_another_15=later)
    elif k == 25:
        v = int(sqrt(10 ** 2 + 24 ** 2))
        d = dict(reflected_horizontal=10, reflected_vertical=24, squared=10 ** 2 + 24 ** 2, minimizer_distances=[13, 13])
    elif k == 29:
        seq = [x for x in product('ABC', repeat=5) if set(x) == set('ABC') and x[0] != 'A' and (x[1] != 'A')]
        v = len(seq)
        assert v == 4 * 27 - 32 - 7 - 7
        d = dict(enumerated=v, inclusion_exclusion='108-32-7-7')
    elif k == 30:
        v = F(15, 10 * F(1, 2))
        d = dict(increase_small_cars=15, increase_in_big_car_units=5, load_ratio=v)
    elif k == 31:
        march = F(4, F(5, 6) - F(2, 3))
        jan = march / F(6, 5)
        feb = march / F(3, 2)
        v = jan + feb + march
        d = dict(january=jan, february=feb, march=march)
    elif k == 32:
        L = 3 * (1 + F(1, 2))
        t = L / 2
        v = f'{int(t)}分{int((t - int(t)) * 60)}秒'
        d = dict(lap=L, speed_A=1, second_interval_minutes=t, speed_B_after=L / 2 / t)
    elif k == 33:
        v = F(2, F(60, 100) + F(45, 100) - 1)
        d = dict(intersection_minus_neither_rate=F(5, 100), people=v)
    elif k == 34:
        sol = [(a, b, c) for a in range(1, 100) for b in range(1, a) for c in range(1, b) if a + b + c == a + 10 and a - b > b - c]
        v = min((x[0] for x in sol))
        d = dict(minimum=v, witnesses=[x for x in sol if x[0] == v])
    elif k == 35:
        noon = 50 - 3 * 2 * 4
        b = F(noon + 6, 4)
        a = F(3, 2) * b
        c = a - 6
        start = 12 - b / 2
        v = fmt(start) + '：00'
        d = dict(noon_areas=[a, b, c], start_B=start, at_16=sum([a, b, c]) + 24)
    elif k == 36:
        seq = [x for x in product([1, -1], repeat=5) if min(accumulate(x)) >= 1]
        v = len(seq)
        d = dict(valid_sequences=seq, enumerated_all=32)
    elif k == 37:
        T = F(80 + 3 * 20, 3 + 2)
        v = T
        d = dict(days=T, A_workshop_days=[20, T - 20], B_workshop_days=[0, T], A_modules=6 * 20, B_modules=3 * (T - 20) + 2 * T, lower_bound='A requires loss >=120/2=60 B modules; 5T-60>=80')
    elif k == 38:
        n = F(120, 2)
        timeA = 6
        v = n / timeA
        d = dict(distance_A=n, distance_B='60√3', time_A=timeA, time_B=3, speed_A=v)
    elif k == 39:
        starts = [st for st in range(7) if sum((2 if (st + j) % 7 >= 5 else 1 for j in range(16))) == 22]
        assert len(starts) == 1
        v = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][starts[0]]
        d = dict(first_weekday_Mon0=starts, day8_weekday=starts[0])
    elif k == 40:
        after = sum((40 + 10 * j for j in range(1, 16)))
        before = 40 * 20
        c = (F(4, 5) * after - before) / (after - before)
        v = fmt(100 * c) + '%'
        d = dict(after_units=after, before_units=before, cost_ratio=c, profit_before=before * (1 - c), profit_after=after * (F(4, 5) - c))
    elif k == 41:
        comps = [(a, b, 5 - a - b) for a in range(1, 4) for b in range(1, 5 - a)]
        sol = [(x, y) for x, y in product(comps, repeat=2) if x[0] + y[0] > max(x[1] + y[1], x[2] + y[2]) and x[1] > y[1]]
        v = len(sol)
        d = dict(solutions_alpha_beta=sol, all_positive_pairs=len(comps) ** 2)
    elif k == 42:
        v = F(240 * 100, 2 * 10000)
        d = dict(area_m2=12000, area_wan=v, identity='EB=x, AG=24000/(240+x); S=(240+x)AG/2=12000')
        v = str(float(v))
    elif k == 43:
        seq = set(permutations('ABRRR'))
        good = [x for x in seq if all((not x[j] == x[j + 1] == 'R' for j in range(4)))]
        v = F(len(good), len(seq))
        d = dict(total=len(seq), favorable=sorted((''.join(x) for x in good)), probability=v)
    elif k == 44:
        cone_time = F(12, 6) ** 3
        cylinder_time = 31 - cone_time
        flow_per_base = F(6, 3) * F(6, 12) ** 2
        cylinder_height = cylinder_time * flow_per_base
        v = 12 + cylinder_height
        d = dict(cone_minutes=cone_time, cylinder_minutes=cylinder_time, flow_per_base=flow_per_base, cylinder_height=cylinder_height, height=v)
        v = str(float(v))
    elif k == 45:
        AC = F(1, 2)
        BC = F(13, 10) * F(1, 2) / 2
        v = AC / BC
        d = dict(speed_before=1, AC=AC, BC=BC, ratio=v, second_halfhour_distance=2 * BC)
    elif k == 46:
        a = F(210, 10) * 3
        dn = F(210, 10) * 4
        do = a - 10
        v = dn - do + 20
        d = dict(A=a, D_before=do, D_after=dn, B_before=v, C_before=a - 20, total=a + do + v + a - 20)
    elif k == 47:
        values = [F(1, 5) * 60, F(1, 5) * 60 + F(1, 2) * 60, F(1, 5) * 60 + F(1, 2) * 60 + 80]
        v = [F(2,10), F(5,10), F(1)]
        d = dict(breakpoints=[(0, 0), (60, values[0]), (120, values[1]), (200, values[2])], slopes=[F(1, 5), F(1, 2), 1], other_options='B smooth curve; C horizontal segments; D decreasing slopes')
    elif k == 48:
        union = 65 * F(4, 5)
        ab_union = union - 3
        intersection = 65 - ab_union
        v = intersection - 6
        d = dict(at_least_one=union, AB_union=ab_union, A_plus_B=65, AB_intersection=intersection, AB_only=v)
    elif k == 51:
        z = F(112 - 27 + 2, 3)
        w = z - 2
        l = z + w - 25
        ch = l and z + 27 - l
        v = max(z, w, l, ch) - min(z, w, l, ch)
        d = dict(ages_Z_W_L_Zhao=[z, w, l, ch], sum=z + w + l + ch)
    elif k == 60:
        ct = lambda start, n: sum(((start + j) % 7 < 4 for j in range(n)))
        fits = [(n, st) for n in [28, 29] for st in range(7) if ct(st, n) == 17 and ct((st + n) % 7, 31) == 19]
        assert len(fits) == 1
        n, st = fits[0]
        ap = (st + n + 31) % 7
        v = ct(ap, 30)
        d = dict(february_days=n, february_first_Mon0=st, april_first_Mon0=ap, april_nights=v)
    elif k == 64:
        smallest = F(1)
        largest = 3 * smallest
        middle = (largest + smallest) / 2 * F(9, 16)
        v = largest / middle
        d = dict(face_areas=[smallest, middle, largest], length_width_ratio=v)
    elif k == 65:
        b = F(10 + 2, 4)
        v = b - 2
        d = dict(areas=[2 * b, b, v], sum=2 * b + b + v)
    elif k == 66:
        nm = F(3, F(1, 2))
        constant = F(-5, F(1, 2))
        v = f'm={fmt(nm)}n{fmt(constant)}'
        d = dict(m_n_coefficient=nm, m_constant=constant, checked_samples=[(6 * n - 10, n, 5 * (6 * n - 10 + 1) == 3 * (F(3, 2) * (6 * n - 10) + n)) for n in [2, 3, 4]])
    elif k == 67:
        domestic = (2 + F(6, 5)) / (F(6, 5) - 1)
        v = fmt(domestic) + 'm'
        d = dict(domestic_multiple=domestic, profits=[domestic - 1, domestic + 2], ratio=(domestic + 2) / (domestic - 1))
    elif k == 68:
        sol = [(a, b, 54 - a - b) for a in range(1, 54) for b in range(1, 54 - a) if 20 * a == 13 * b]
        assert len(sol) == 1
        diff = sol[0][2] - sol[0][1]
        v = '多' + str(diff) + '台'
        d = dict(integer_solutions=sol)
    elif k == 69:
        p = F(18, 100) / (1 - F(4, 10)) / 2
        v = str(float(p))
        d = dict(P_B_beats_A=F(3, 5), P_B_beats_C=2 * p, P_C_beats_D=p, joint=F(3, 5) * 2 * p)
    elif k == 70:
        sz = 2 * 4 - 1
        sw = 5
        v = F(sz, sw)
        d = dict(Z_distance_in_L=sz, W_distance_in_L=sw, speed_ratio=v)
    elif k == 71:
        sum_h = (F(2) / F(1, 5) - 4) / 4
        b = sum_h * F(2, 5)
        v = min(b, 1) / max(b, 1)
        d = dict(n=1, hA=sum_h - b, hB=b, surface_before=4 + 4 * sum_h, surface_removed=2, ratio=v)
    elif k == 72:
        sol = [n for n in range(3, 200) if 2 * comb(n - 2, 2) == 30 * comb(n - 2, 1)]
        assert len(sol) == 1
        v = sol[0]
        d = dict(n=v, exactly_one_ways=2 * comb(v - 2, 2), both_ways=comb(v - 2, 1), sample_space=comb(v, 3))
    elif k == 73:
        sol = [c for n in range(1, 12) for c in combinations(range(90, 101), n) if 92 in c and sum(c) * 5 == 469 * n]
        ranks = [1 + sum((s > 92 for s in c)) for c in sol]
        v = max(ranks)
        d = dict(all_qualifying_subsets=sol, maximum_rank=v, witnesses=[c for c, r in zip(sol, ranks) if r == v], exam_others='fill remaining 25 positions with distinct scores 0..24')
    elif k == 74:
        ratio = F(3, 5)
        old = (1 + ratio) / 2
        v = fmt((1 - old) / old * 100) + '%'
        d = dict(AB_over_CD=ratio, old_area_over_CD_h=old, new_area_over_CD_h=1, increase=(1 - old) / old)
    elif k == 75:
        moved = 5 * (32 + 2) - 4 * 32
        old = moved + 3 * 2
        v = old + 2
        d = dict(moved_age=moved, A_before_mean=old, A_after_mean=v, A_before_total=old * 4, A_after_total=old * 4 - moved)
    elif k == 76:
        T = F(60 + 45 + 60, 6 + 5)
        v = ceil(T)
        d = dict(exact_days=T, weights=[60, 45, 60], A_max_weighted_rate=6, B_max_weighted_rate=5, schedule_A={'C': 10, 'A': 5}, schedule_B={'B': 9, 'A': 6}, A_done=F(5, 10) + F(6, 12), B_done=F(9, 9), C_done=F(10, 10))
    elif k == 77:
        fits = [st for st in range(7) if sum(((st + offset) % 7 == 0 for offset in [9, 19, 40, 50])) == 2]
        assert len(fits) == 1
        sept = (fits[0] + 31) % 7
        v = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][sept]
        d = dict(Aug1_weekday_Mon0=fits[0], Sept1=sept, visit_weekdays=[(fits[0] + j) % 7 for j in [9, 19, 40, 50]])
    elif k == 78:
        L = F(5, F(1, 10) - F(1, 11))
        t = L / (5 - 4)
        assert 540 < t < 600
        v = '9分钟～10分钟之间'
        d = dict(lap=L, first_AC=L / 10, first_BC=L / 11, catch_seconds=t)
    elif k == 79:
        goal = F(9, F(48, 100) - 2 * F(18, 100))
        w = (F(18, 100) * goal - 3) / 3
        annual = 12 * w + 66
        v = fmt(annual - goal) + 'k'
        d = dict(goal_over_k=goal, w_over_k=w, annual_over_k=annual, extra_over_k=annual - goal)
    elif k == 81:
        remaining = range(5)
        sol = [c for n in range(6) for c in combinations(remaining, n) if 7 - (2 + n) > F(7, 2)]
        v = len(sol)
        d = dict(extra_people_in_B=sol, group_size_pairs=[(7 - 2 - len(c), 2 + len(c)) for c in sol])
    elif k == 82:
        back = F(3, F(5, 2) - 1)
        go = F(5, 2) * back
        v = 40 * (go + back) / 2
        d = dict(go_hours=go, back_hours=back, distance=v, go_speed=v / go, back_speed=v / back)
    elif k == 83:
        cost = (F(5, 4) * 90 - 100) / (F(5, 4) - 1)
        v = cost
        d = dict(cost=cost, before_margin=100 - cost, after_margin=90 - cost, after_profit_per_m=F(5, 4) * (90 - cost))
    elif k == 84:
        a = (F(6, 5) * 2000 - 2260) / (F(6, 5) - F(11, 10))
        v = a
        d = dict(A=a, B=2000 - a, new_total=F(11, 10) * a + F(6, 5) * (2000 - a))
    elif k == 89:
        table = [['AI', 'NET', 'AI'], ['NET', 'CHIP', 'CHIP'], ['6G', 'AI', 'NET'], ['6G', 'NET', 'AI']]
        sol = [rooms for rooms in product(range(3), repeat=4) if len({table[j][rooms[j]] for j in range(4)}) == 4]
        v = len(sol)
        d = dict(table=table, valid_room_sequences_0based=sol, total_room_sequences=81)
    elif k == 93:
        sol = [(z, l, u) for z in range(1, 100) for l in range(1, 100) for u in range(1, 60) if z * 2 == 3 * l and z == 2 * u + 4 and (z + l - 8 == 4 * (u - 4))]
        assert len(sol) == 1
        y = 2028 + 60 - sol[0][0]
        v = str(y) + '年'
        d = dict(ages_2028=sol[0], age_Z_60_year=y)
    elif k == 94:
        sol = []
        for t in range(101, 200):
            a = F(24, 100) * t
            c = (t - a) / F(5, 2)
            b = F(3, 2) * c
            if all((z.denominator == 1 for z in [a, b, c])):
                sol.append((a, b, c))
        assert len(sol) == 1
        v = sol[0][2] - sol[0][0]
        d = dict(integer_solutions=sol, total=sum(sol[0]))
    else:
        raise ValueError(i)
    return (fmt(v), d)
def run(ctx):
    for i in range(len(ctx.problems)):
        value,details=solve(i)
        ctx.add(i,value,evidence=details,property_only=DUP.get(i,i)==47,boundary='frozen equations; manual diagram coordinates/formulas; duplicate parameters rerun, not independent evidence')
