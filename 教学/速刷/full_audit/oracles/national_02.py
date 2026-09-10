"""Offline port of national_02 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'national_02'
def ev(s):
    return numeric(s.replace("%","").replace("千米", "").strip())

def numopt(t):
    return numeric(t.strip().replace("%", "").replace("年", "").replace("元", "").replace("厘米", "").replace("O", "0"))

def run(ctx):
    S=ctx.problems
    R=[dict(correctedStem=q["s"],correctedOptions=q["o"]) for q in S]
    canon = {25: 12, 26: 13, 27: 15, 28: 14, 29: 16, 30: 17, 31: 18, 32: 20, 33: 22, 34: 10, **{i: i - 15 for i in range(50, 60)}, **{i: i - 15 for i in range(75, 85)}}
    def check(i):
        j = canon.get(i, i)
        s = R[i]['correctedStem'] or S[i]['s']
        o = R[i]['correctedOptions'] or S[i]['o']
        e = {}
        v = None
        if j == 0:
            v = F(370) * F(15, 2) / (37 * 15)
        elif j == 1:
            b = F(1)
            football = 3 * b
            table = (football + b) / 2
            badminton = 2 * table
            candidates = [football + b, table + football, F(3, 2) * football, 3 * b]
            v = badminton
            e = {'groups': [str(x) for x in [badminton, table, football, b]], 'candidateValues': list(map(str, candidates))}
        elif j == 2:
            v = 1 + 30 // math.lcm(3, 4)
        elif j == 3:
            a = max((sum((1 for x in range(35) if (x + k) % 4 != 3)) for k in range(4)))
            b = max((sum((1 for x in range(35) if (x + k) % 5 == 0)) for k in range(5)))
            v = a + b
            e = {'sides': [a, b]}
        elif j == 4:
            bounds = []
            for n in range(1, 13):
                z = [max(a, b, n - a - b) for a in range(n + 1) for b in range(n - a + 1)]
                bounds.append([n, min(z), max(z)])
            assert all((lo == math.ceil(n / 3) and hi == n for n, lo, hi in bounds))
            v = 'linear upper, integer staircase lower'
            e = {'exhaustiveBounds': bounds, 'visualOption': 'C'}
        elif j == 5:
            start = min((F(360 * k + a) * 2 / 11 for k in range(20) for a in [120, 240] if F(360 * k + a) * 2 / 11 > 510))
            end = max((F(360 * k + 180) * 2 / 11 for k in range(20) if F(360 * k + 180) * 2 / 11 < 720))
            angles = [F(360 * k + a) * 2 / 11 for k in range(20) for a in [90, 270] if start < F(360 * k + a) * 2 / 11 < end]
            v = len(angles)
            e = {'startMinute': str(start), 'endMinute': str(end), 'rightAngles': list(map(str, angles))}
        elif j == 6:
            v = math.factorial(3) * math.factorial(3) * math.factorial(2) * math.factorial(4)
        elif j == 7:
            v = 2 * F(18, 5) / (F(2, 3) - F(1, 2))
        elif j == 8:
            v = 4 * F(6, 5) ** 2 - 3
        elif j == 9:
            ns = [n for n in range(15, 100) if F(14, n) - F(12, n - 2) == F(3, 100)]
            assert ns == [50]
            v = F(math.comb(12, 2), math.comb(ns[0] - 2, 2))
            e = {'originalN': ns}
        elif j == 10:
            v = 12 * F(4, 5) * F(1, 3) * 15
        elif j == 11:
            births = [b for b in range(1970, 1980) if any((all((y - b == sum(map(int, str(y))) for y in range(t, t + 10))) for t in range(b, 2050)))]
            assert births == [1971]
            v = next((y for y in range(2006, 2010) if (y - births[0]) % 9 == 0))
            e = {'birthYear': births[0]}
        elif j == 12:
            k = next((k for k in range(8) if (1 + 5 * k) % 4 == 0))
            day = 8 + 7 * k
            v = day
            e = {'mondayIndex': k}
        elif j == 13:
            v = 12 * 25 // math.gcd(20 * 14, 12 * 25)
        elif j == 14:
            scores = [10, 10, 10, 20, 20, 30]
            sub = [m for m in range(64) if sum((scores[k] for k in range(6) if m >> k & 1)) == 70]
            v = F(sum((not m >> 5 & 1 for m in sub)), len(sub))
            e = {'qualifyingMasks': sub}
        elif j == 15:
            n = next((n for n in range(1, 20) if sum((F(3) + F(k, 5) for k in range(n))) >= 13))
            v = n + 3
            e = {'businessMonths': n, 'before': str(sum((F(3) + F(k, 5) for k in range(n - 1)))), 'after': str(sum((F(3) + F(k, 5) for k in range(n))))}
        elif j == 16:
            n = 6 / (F(3, 4) - F(2, 3))
            v = int(n) - math.ceil(n / 10) - int(n * F(3, 4))
            e = {'total': str(n), 'reserve': math.ceil(n / 10)}
        elif j == 17:
            lens = [15, 53, 22, 47, 23]
            seq = [x for k in range(1, 6) for x in itertools.permutations(lens, k) if 80 <= sum(x) <= 90]
            v = len(seq)
            e = {'allSequences': seq}
        elif j == 18:
            px = F(2, 6)
            py = 2 * px
            areaABP = (2 - py) / 2
            areaBCE = F(1, 2)
            v = (areaABP + areaBCE) / 2
            e = {'intersection': [str(px), str(py)], 'areas': [str(areaABP), str(areaBCE)]}
        elif j == 19:
            total = list(itertools.permutations(range(5)))
            count = sum((sum((p[k] == k for k in range(5))) == 1 for p in total))
            v = F(count, len(total))
            e = {'exactlyOneFixed': count, 'all': len(total)}
        elif j == 20:
            t = (1 + F(5, 3) / 15) / (F(1, 10) + F(1, 15))
            share = t / 10 - (t - F(5, 3)) / 15
            v = 300 / share
            e = {'elapsed': str(t), 'shareDifference': str(share)}
        elif j == 21:
            v = 1 / (2 * (F(1, 5) - F(1, 6)))
        elif j == 22:

            def point(d):
                vertices = [(0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3) / 2)]
                d = d % 3
                k = int(d)
                u = d - k
                a = vertices[k]
                b = vertices[(k + 1) % 3]
                return (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
            vals = []
            for t in [k / 20 for k in range(61)]:
                a = point(2 * t)
                b = point(-t)
                dist = math.dist(a, b)
                expected = math.sqrt(3) * min(t % 1, 1 - t % 1)
                assert abs(dist - expected) < 1e-09
                vals.append([t, dist])
            v = 'periodic triangular wave'
            e = {'sampledDistances': vals, 'visualOption': 'D'}
        elif j == 23:
            v = next((a for a in range(1, 30) if a * a >= 200))
            e = {'aMinus1AreaCoefficient': (v - 1) ** 2 / 2, 'aAreaCoefficient': v * v / 2}
        elif j == 24:
            v = math.sqrt(500 ** 2 - (600 / 2) ** 2)
        elif j == 35:
            v = F(15000) / (200 * F(3, 5) + 100 * F(3, 10) - 100 * F(3, 10))
        elif j == 36:
            v = F(40 // 5 - 1, 40 - 1)
        elif j == 37:
            total = 369 + 412
            batches = next((b for b in range(2, total + 1) if total % b == 0))
            size = total // batches
            v = 412 % size
            e = {'batches': batches, 'size': size, 'remainders': [369 % size, v]}
        elif j == 38:
            possible = [float(numopt(x)) for x in o]
            feasible = [r for r in possible if r != 8]
            upper = {str(r): 256 + 2 * math.pi * r * r for r in feasible}
            v = max(feasible, key=lambda r: upper[str(r)])
            assert v == 4
            e = {'optionAreaUpperBounds': upper, 'r8Reason': 'both centers y=8; x separation<=8<16', 'r4ConstructedArea': 256 + 32 * math.pi}
        elif j == 39:
            energy = F(600, 400) / (F(1, 10) + 3 * F(3, 10))
            v = (3 * F(7, 10) - F(9, 10)) * energy
        elif j == 40:
            v = F(80 * 30 * 10 - 80 * (30 - 10 - 8) * 10, (80 + 70) * 8) - 10
        elif j == 41:
            profits = [45000 + 3 * x - F(18, 5) * max(0, x - 400) for x in range(10001)]
            v = max(profits)
            e = {'maximizingKg': profits.index(v)}
        elif j == 42:
            seq = sorted(set(itertools.permutations('AABBCC')))
            good = [''.join(t) for t in seq if all((t[k] != t[k + 1] for k in range(5)))]
            v = len(good)
            e = {'allValidSchedules': good}
        elif j == 43:
            plans = [(a, 24, c, d) for c in range(73) for a in [c - 6] for d in [72 - 24 - a - c] if min(a, c, d) > 0 and d < min(a, 24, c)]
            best = min(plans, key=lambda x: x[2])
            v = best[2]
            e = {'minimalPlan': best}
        elif j == 44:
            k = 100 / F(1, 2)
            remainingBlack = k / F(4)
            v = (100 + 900) * F(5, 10) - remainingBlack
            e = {'originalScale': str(k), 'remainingBlack': str(remainingBlack)}
        elif j == 45:
            v = math.dist((15, 0), (-15 / 2, 15 * math.sqrt(3) / 2))
        elif j == 46:
            v = 100 * (8 * F(3, 10) - F(6, 5) * 4 * F(4, 10)) / (F(6, 5) * 10 * F(3, 10) - 8 * F(2, 10))
        elif j == 47:
            residual = [39, 33, 14, 28, 26]
            edges = collections.Counter()
            need = residual[:]
            while sum(need):
                a, b = sorted(range(5), key=lambda k: need[k], reverse=True)[:2]
                assert need[b] > 0
                need[a] -= 1
                need[b] -= 1
                edges[tuple(sorted((a, b)))] += 1
            assert sum(edges.values()) == 70
            v = sum(edges.values())
            e = {'invalidAllFive': 30, 'validPairCounts': {f'{a + 1}-{b + 1}': c for (a, b), c in sorted(edges.items())}, 'residualDegrees': residual}
        elif j == 48:
            Y = 6
            vals = [[X, min(X, F(X + Y, 3)), max(0, F(X - 2 * Y, 3))] for X in range(19)]
            v = 'A1=min(X,(X+Y)/3), A2=max(0,(X-2Y)/3)'
            e = {'values': [[str(x) for x in row] for row in vals], 'visualOption': 'A'}
        elif j == 49:
            v = F(400) / (1 - F(10, 18))
        elif j == 60:
            old = F(15) / (F(6, 5) - 1)
            new = old * F(6, 5)
            v = old + new - 100
            e = {'oldExcellent': str(old), 'newExcellent': str(new)}
        elif j == 61:
            v = F(150) * (F(7, 5) - 1) / (F(3, 5) - F(7, 5) * F(2, 5))
        elif j == 62:
            seq = list(itertools.permutations(range(4), 3))
            equal = sum((a == b for a in seq for b in seq))
            v = F(equal, len(seq) ** 2)
            e = {'pairs': len(seq) ** 2, 'matches': equal}
        elif j == 63:
            v = 10 / F(10, 60) / 2
        elif j == 64:
            probs = [F(3, 5) ** 3 + F(2, 5) ** 3, F(2, 5) ** 3 * (1 + F(3, 5) + F(3, 5) ** 2), F(3, 5) ** 3 * F(2, 5) ** 2, 3 * F(3, 5) * F(2, 5) ** 3]
            v = max(probs)
            e = {'optionProbabilities': list(map(str, probs))}
        elif j == 65:
            rates = (3, 4, 5)
            assert 3 * (3 + 4) + 7 * (4 + 5) == 7 * sum(rates)
            v = F(10 * rates[2], rates[0] + rates[1])
        elif j == 66:
            v = F(8 * 3, 4) + F(24 * 1, 4)
        elif j == 67:
            vals = []
            for t in range(10):
                cycles, r = divmod(t, 4)
                work = cycles + min(r, 1)
                vals.append(5 * work - t)
            assert vals == [0, 4, 3, 2, 1, 5, 4, 3, 2, 6]
            v = 'slope +4 for 1h, -1 for 3h'
            e = {'hourlyDifferences': vals, 'visualOption': 'A'}
        elif j == 68:
            politics = sum((sum(bits) == 5 for bits in itertools.product([0, 1], repeat=8)))
            hours = [2] * 5 + [1] * 5
            technical = sum((sum((x * h for x, h in zip(bits, hours))) == 10 for bits in itertools.product([0, 1], repeat=10)))
            v = politics * technical
            e = {'politics': politics, 'technical': technical}
        elif j == 69:
            states = {(0, 0, 0): (0, [])}
            for day in range(1, 32):
                new = {}
                for (gap, hotrun, n), (cost, hotdays) in states.items():
                    for hot in [0, 1]:
                        g = gap + 1
                        run = hotrun + 1 if hot else 0
                        water = run >= 3 or g == 5
                        key = (0, 0, n + 1) if water else (g, run, n)
                        if key[2] > 8:
                            continue
                        val = (cost + hot, hotdays + ([day] if hot else []))
                        if key not in new or val[0] < new[key][0]:
                            new[key] = val
                states = new
            v, hotdays = min((val for key, val in states.items() if key[2] == 8))
            e = {'optimalHotDays': hotdays, 'algorithm': '31-day exhaustive dynamic programming over gap/hotrun/count'}
        elif j == 70:
            speed = (30 + math.sqrt(50 ** 2 - 30 ** 2)) / (2 - F(36, 60))
            v = 50 / speed
        elif j == 71:
            v = F(240 - 160, 2)
        elif j == 72:
            plans = []
            for a in range(1, 400):
                if a * 27 % 100:
                    continue
                for b in range(1, a):
                    if not 300 < a + b < 400 or b % 21 or b * 8 // 21 <= a * 27 // 100:
                        continue
                    plans.append((a, b, a * 73 // 100 + b * 13 // 21))
            v = min((c for a, b, c in plans))
            e = {'allPlans': plans}
        elif j == 73:
            acargo = 35 * 12
            bcargo = acargo + 10
            capacity = bcargo // 10
            v = (acargo + bcargo) % capacity
            e = {'total': acargo + bcargo, 'capacity': capacity}
        elif j == 74:
            ts = {k * (k + 1) // 2 for k in range(1, 500)}
            solutions = [m * m + 4 for m in range(2, 100) if m * m + 9 in ts]
            assert min(solutions) == 40
            N = 40
            layouts = [(a, N // a, 2 * (a + N // a) - 4) for a in range(2, math.isqrt(N) + 1) if N % a == 0]
            v = min((row[2] for row in layouts))
            e = {'firstSolutions': solutions[:5], 'N40Layouts': layouts, 'globalLowerBound': 4 * math.sqrt(40) - 4}
        elif j == 85:
            good = []
            for x in itertools.permutations('ABCDEF'):
                if x.index('F') not in [0, 5] or abs(x.index('A') - x.index('B')) != 1:
                    continue
                if x.index('E') < x.index('C') < x.index('D'):
                    good.append(''.join(x))
            v = len(good)
            e = {'allValidOrders': good}
        elif j == 86:
            v = 3 * 110 - 100 - 80 - 100
        elif j == 87:
            first = 2 * (2 * 12) - 6
            days = (first - 6) // 2 + 1
            v = 10 * days
            e = {'firstPrice': first, 'days': days, 'revenue': sum(range(6, first + 1, 2)) * 10, 'cost': 12 * v}
        elif j == 88:
            times = [8] * 5 + [4] * 3 + [6] * 2 + [7] * 4
            best = -1
            count = 0
            counts = set()
            for mask in range(1 << len(times)):
                used = [k for k in range(len(times)) if mask >> k & 1]
                if sum((times[k] for k in used)) > 38:
                    continue
                n = len(used)
                if n > best:
                    best = n
                    count = 0
                    counts = set()
                if n == best:
                    count += 1
                    counts.add(tuple((sum((times[k] == t for k in used)) for t in [8, 4, 6, 7])))
            v = count
            e = {'maxSamples': best, 'numberCombinations': count, 'classCounts': list(counts)}
        elif j == 89:
            ratio = F(1200 - 500, 1200) * F(6, 5)
            v = 600 * (1 - ratio)
            e = {'oldSpeedRatio乙甲': str(ratio)}
        elif j == 90:
            depths = [0, 1, 2, 3, 5, 10]
            chords = [2 * math.sqrt(25 - (5 - h) ** 2) for h in depths]
            assert chords[2] - chords[1] > chords[3] - chords[2]
            v = 'ellipse upper half, not triangle'
            e = {'r': 5, 'depths': depths, 'chords': chords, 'visualOption': 'A'}
        elif j == 91:
            tests = []
            for x in [501, 1000, 2000, 3000, 10000]:
                L = 3 * x
                first = x + 500
                assert L / 3 < first < 2 * L / 3
                secondPosition = 2 * L - 3 * first
                distFrom乙 = L - secondPosition
                assert distFrom乙 == 1500
                tests.append([L, first, secondPosition, distFrom乙])
            v = 3*500
            e = {'L_first_second_distance乙': tests}
        elif j == 92:

            def share(P):
                return F(4, 5) * min(P, 10) + F(3, 5) * max(0, min(P - 10, 10)) + F(2, 5) * max(0, P - 20)
            total = next((P for P in range(1, 1000) if P - share(P) == F(6, 5) * share(P)))
            a = share(F(total, 2))
            b = F(total, 2) - a
            v = a - b
            e = {'originalTotal': total, 'newA': str(a), 'newB': str(b)}
        elif j == 93:
            v = 3*(F(1,2)-F(1,4))
            X = 12
            a = 3
            b = 4
            T1 = F(X, 3 * b) + F(X // 2, 2 * a)
            T2 = F(X // 2, a)
            assert T1 == T2 == 2
            e = {'a': a, 'b': b, 'X': X, '甲Time': str(T1), '乙Time': str(T2), '甲Count': 18, 'dualTimeLowerBound': '(12/6+12/12)/(1+1/2)=2'}
        elif j == 94:
            A = F(2, 5)
            B = A * F(3, 5) + (1 - A) * F(3, 10)
            no = (1 - A) * F(7, 10)
            C = no * F(9, 10) + (1 - no) * F(1, 10)
            rank = sorted('ABC', key=lambda z: dict(A=A, B=B, C=C)[z], reverse=True)
            v = '>'.join(rank)
            e = {'probabilities': list(map(str, [A, B, C]))}
        elif j == 95:
            v = next((x for x in range(1, 1000) if x * (x + 1) // 2 % 48 == 0))
            e = {'totalProducts': v * (v + 1) // 2, 'boxes': v * (v + 1) // 2 // 48}
        elif j == 96:
            ns = []
            for c in range(1, 400):
                z = F(8, 5) * c
                l = F(4, 5) * (z + c)
                n = l + z + c
                if z.denominator == l.denominator == 1 and 300 < n < 400:
                    ns.append(int(n))
            assert ns == [351]
            v = -ns[0] % 7
            e = {'possibleTotal': ns}
        elif j == 97:
            remaining = [F(1, 2), F(2, 3), F(1, 2), F(2, 3), F(1, 2), F(2, 3), F(1, 2)]
            initials = [F(1, 72) / math.prod((remaining[(start + k) % 7] for k in range(6))) for start in range(7)]
            v = max(initials)
            e = {'all7StartDayInitials': list(map(str, initials))}
        elif j == 98:
            v = (150 + 100 * math.sin(math.pi / 6)) / (100 * math.cos(math.pi / 6))
        elif j == 99:
            v = math.sqrt((27 ** 2 - 23 ** 2) / 2)
        else:
            raise AssertionError(('unhandled', i, j))
        return v, e
    for i in range(len(S)):
        value,proof=check(i)
        proof.pop('visualOption',None)
        candidates=proof.get('candidateValues') or proof.get('optionProbabilities')
        manual=False
        ctx.add(i,value,evidence=proof,candidates=candidates,mode='manual_only' if manual else 'computation',boundary='ported model; graph feature recognition and finite-prefix pattern selection remain manual')
