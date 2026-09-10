"""Offline port of provincial_04 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_04'
def ev(s):
    return numeric(s.replace("%","").replace("千米", "").strip())

def run(ctx):
    S=ctx.problems
    R=[dict(correctedStem=q["s"],correctedOptions=q["o"]) for q in S]
    def solve(i):
        q = S[i]
        review = R[i]
        o = review['correctedOptions'] or q['o']
        v = None
        proof = {}
        if i == 0:
            v = next((p for p in range(4, 100) if F(360, p - 3) - F(360, p) == 20))
        elif i == 1:
            a = [3, 35, 99, 195]
            dif = [b - a for a, b in zip(a, a[1:])]
            assert dif == [32, 64, 96]
            v = a[-1] + dif[-1] + 32
        elif i == 2:
            v = f'{23 - 3} {24 + 3}'
            assert [23, 22, 21, 20] == list(range(23, 19, -1))
        elif i == 3:
            assert [n ** (n - 1) for n in range(1, 6)] == [1, 2, 9, 64, 625]
            v = 6 ** 5
        elif i == 4:
            sums = [sum(map(int, str(x))) for x in [23, 14, 37, 55, 78]]
            assert sums == [5, 5, 10, 10, 15]
            v = next((int(x) for x in o if sum(map(int, x)) == 15))
        elif i == 5:
            a = [F(6, 6), F(4, 6), F(3, 6), F(2, 5)]
            assert [1 / x for x in a] == [F(1), F(3, 2), F(2), F(5, 2)]
            v = 1/(1/a[-1]+F(1,2))
        elif i == 6:
            v = F(25000) / (F(4, 5) * 12 + F(1, 5) * 10 - 9 - F(1, 10)) / 1000
        elif i == 7:
            v = 60 + (1 - 60 * (F(1, 200) + F(1, 300))) * 300
        elif i == 8:
            pairs = [(b, d) for b in range(11, 20) for d in range(11, b) if 20 + 2 * b + 2 * d + 10 <= 80]
            v = max((b for b, d in pairs))
            proof = {'bestAllocations': [(20, b, b, d, d, 10) for b, d in pairs if b == v]}
        elif i == 9:

            def pos(s):
                return 3 - abs(s % 6 - 3)
            times = sorted({F(6 * k, 6) for k in range(1, 20)} | {F(6 * k, 2) for k in range(1, 20)})
            t = times[6]
            v = pos(2 * t)
            assert pos(2 * t) == pos(4 * t)
            proof = {'first7Times': list(map(str, times[:7])), 'locations': list(map(str, [pos(2 * t) for t in times[:7]]))}
        elif i == 10:
            v = sum(((0 in c) != (1 in c) for c in itertools.combinations(range(6), 3)))
        elif i == 11:
            k = F(10, 8 - 3)
            v = 12 * k
            proof = {'original': [str(7 * k), str(5 * k)], 'new': [str(8 * k), str(3 * k)]}
        elif i == 12:
            plans = []
            for start in range(1, 21):
                n20 = sum(((d + 1) % 7 < 5 for d in range(start, 21)))
                n28 = sum(((d + 1) % 7 < 5 for d in range(start, 29)))
                if n20 > 0 and n20 * 30 == n28 * 20:
                    plans.append((start, n20, n28))
            assert plans == [(3, 12, 18)]
            v = plans[0][0]
            proof = {'validStarts': plans}
        elif i == 13:
            n = F(16800) / (20 - F(64, 1000) * 50)
            v = n * F(64, 1000)
            proof = {'total': str(n)}
        elif i == 14:
            k = 24 / (2 * (4 + 2))
            a, b, c = (4 * k, 2 * k, math.sqrt(3) * k)
            v = (a - math.sqrt(b * b - c * c)) * c
        elif i == 15:
            values = []
            for x in range(1, 60):
                up = F(10) + F(x, 6)
                down = 2 * up
                assert F(x) / up + F(60 - x) / down == 3
                values.append((x, up, down))
            truths = [all((up < 15 for x, up, down in values if x > 30)), all((up > 20 for x, up, down in values if x > 30)), all((down < 30 for x, up, down in values if x < 30)), all((down > 25 for x, up, down in values if x < 30))]
            assert truths == [False, False, True, False]
            v = 'downhill distance larger implies speed<30'
            proof = {'optionTruths': truths, 'counterexampleD': 'up6/down54, speeds11/22'}
        elif i == 16:
            v = 45 + 18
            assert [9 - 3, 18 - 9, 30 - 18, 45 - 30] == [6, 9, 12, 15]
        elif i == 17:
            assert [11 * n * n for n in range(1, 5)] == [11, 44, 99, 176]
            v = 11 * 25
        elif i == 18:
            assert all((sum(map(int, str(x))) == 20 for x in [389, 569, 479, 587, 299]))
            v = next((int(x) for x in o if sum(map(int, x)) == 20))
        elif i == 19:
            v = F(120, 1 + 3 + 4)
        elif i == 20:
            v = F(20 * 4 * 4, 10) - 20
        elif i == 21:
            v = 80 * (9 - 7 + (15 - 7 - 2))
        elif i == 22:
            red = [(0, 4), (8, 12), (16, 20)]
            green = [(5, 10), (15, 20)]
            intersections = [(max(a, c), min(b, d)) for a, b in red for c, d in green if max(a, c) < min(b, d)]
            v = len(intersections)
            proof = {'intersections': intersections}
        elif i == 23:
            rooms = F(7 + 3, 8 - 6)
            v = 6 * rooms + 7
        elif i == 24:
            k = F(5 * 24 - 6 * 8, 6 * 4 - 5 * 3)
            v = 3 * k + 24 - (4 * k + 8)
        elif i == 25:
            levels = [[11, 14, 26, 44, 65]]
            for _ in range(3):
                a = levels[-1]
                levels.append([b - a for a, b in zip(a, a[1:])])
            assert levels[-1] == [-3, -3]
            v = levels[0][-1] + levels[1][-1] + levels[2][-1] + levels[3][-1]
            proof = {'differenceTable': levels}
        elif i == 26:
            v = f'{88 * 2}，{168 * 2}'
            assert [22 * 2, 42 * 2, 44 * 2, 84 * 2] == [44, 84, 88, 168]
        elif i == 27:
            assert [(n, n * n + 1, n ** 3 + 2) for n in range(1, 4)] == [(1, 2, 3), (2, 5, 10), (3, 10, 29)]
            v = 4 ** 3 + 2
        elif i == 28:
            assert [int(f'{n}{n * n + 1}') for n in range(1, 5)] == [12, 25, 310, 417]
            v = int(f'{5}{26}')
        elif i == 29:
            assert [1 + 4 * (n // 3) + [0, -1, 0][n % 3] for n in range(7)] == [1, 0, 1, 5, 4, 5, 9]
            v = 1+4*(7//3)+[0,-1,0][7%3]
        elif i == 30:
            v = F(5, 100) * 200 + (F(5, 100) + F(3, 100)) * F(200, 4)
        elif i == 31:
            days = F(70 + 55, 55 - 50)
            v = 55 * (days - 1)
            proof = {'deadline': str(days)}
        elif i == 32:
            v = 40 + 46 - (80 - 10)
        elif i == 33:
            allocations = [x for x in itertools.product(range(3, 6), repeat=3) if sum(x) == 12]
            v = len(allocations)
            proof = {'allAllocations': allocations}
        elif i == 34:
            c = list(itertools.combinations(range(6), 3))
            good = [x for x in c if any((a < 2 for a in x)) and any((a >= 2 for a in x))]
            v = F(len(good), len(c))
            proof = {'total': len(c), 'mixed': len(good)}
        elif i == 35:
            v = 2 * (10 // 3 + 8 // 3)
            proof = {'tenMeterSegments': [3, 3, 4], 'eightMeterSegments': [4, 4]}
        elif i == 36:
            b = F(15, 2) / (4 - F(3, 2))
            v = 3 * b
            assert (4 * b + 15) / (b + 15) == F(3, 2)
            proof = {'乙WorkedAt938': str(b), '甲WorkedAt938': str(4 * b)}
        elif i == 37:
            v = (F(485, 10) + 5 * 5) / F(7, 10)
        elif i == 38:
            h = F(16, 10)
            ratio = (F(32, 10) - F(16, 10)) / 1
            v = h + h / ratio
            proof = {'height': str(v), 'shadowRatio': str(ratio)}
        elif i == 39:
            a = F(99 - 30 - 3, 3)
            v = sum((a + k for k in range(10)))
            assert sum((a + k for k in range(13))) - v == 99
            proof = {'originalTop': str(a), 'originalTotal': str(sum((a + k for k in range(13))))}
        elif i == 40:
            v = 39 + (39 - 27) + 2
        elif i == 41:
            assert [F(n, 4 * n + 4) for n in range(1, 5)] == [F(1, 8), F(1, 6), F(3, 16), F(1, 5)]
            v = F(5,4*5+4)
        elif i == 42:
            a = [6, 12, 19, 32, 52]
            assert all((a[n] == a[n - 1] + a[n - 2] + 1 for n in range(2, 5)))
            v = a[-1] + a[-2] + 1
        elif i == 43:
            seq = [123, 465, 987, None, 456, 897, 231, 645, 789]
            assert all((set(str(x)) == set(['123', '456', '789'][k % 3]) for k, x in enumerate(seq) if x is not None))
            v = next((int(x) for x in o if set(x) == set('123')))
        elif i == 44:
            v = 100 * F(math.comb(3, 2), math.comb(5, 2))
        elif i == 45:
            v = 2 * (45 - F(30, 2))
        elif i == 46:
            v = F(5 * 60, 60)
        elif i == 47:
            cells = {(x, y) for x in range(3) for y in range(3) if (x, y) != (1, 1)}
            exposed = sum(((x + dx, y + dy) not in cells for x, y in cells for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]))
            assert exposed == 16
            v = 'outer-only128; all-boundaries72'
            proof = {'outerEdges': 12, 'holeEdges': 4, 'allEdges': exposed, 'outerArea': 8 * (48 / 12) ** 2, 'allBoundaryArea': 8 * (48 / 16) ** 2}
        elif i == 48:
            sol = [(g, k, other) for g in range(1, 56) for k in range(1, 56) for other in [55 - g * k] if other > 0 and 2 * k + F(3, 10) * other == 20 and ((F(3, 10) * other).denominator == 1)]
            assert sol == [(5, 7, 20)]
            v = sol[0][0]
            proof = {'allIntegerSolutions': sol}
        elif i == 49:
            v = 16 / (F(3, 2) - 1) / F(2, 5)
        elif i == 50:
            v = 'cylinder height=diameter: circle top,square side'
            proof = {'construct': ['radius1', 'height2', 'side2x2'], 'excluded': ['truncated body top has square contour', 'sphere cannot show square', 'pyramid cannot show circle']}
        elif i == 51:
            seq = [10, 3, 13, 1, 14, 2, 16, 9]
            assert all((seq[k] == seq[k - 2] + seq[k - 1] for k in [2, 4, 6]))
            v = seq[-2] + seq[-1]
        elif i == 52:
            a = ['92.46', '84.42', '76.38', '68.34']
            assert all((int(x.split('.')[0]) == 2 * int(x.split('.')[1]) for x in a))
            hits = [k for k, x in enumerate(o) if int(x.split('.')[0]) == 2 * int(x.split('.')[1])]
            assert len(hits) == 1
            v = o[hits[0]]
            proof = {'alternativeArithmeticNext': str(F(6834, 100) - F(804, 100)), 'blockResiduals': [int(x.split('.')[0]) - 2 * int(x.split('.')[1]) for x in o]}
        elif i == 53:
            a = [F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(8, 9), F(27, 32)]
            assert all((a[k] == a[k - 2] / a[k - 1] for k in range(2, 6)))
            v = a[-2] / a[-1]
        elif i == 54:
            assert [n * (n - 1) for n in range(6)] == [0, 0, 2, 6, 12, 20]
            v = 1*(1-1)
        elif i == 55:
            assert all((a + c == 2 * b for a, b, c in [(2, 5, 8), (3, 6, 9), (4, 11, 18)]))
            v = 2 * 13 - 5
        elif i == 56:
            v = 20 * F(4, 5) * F(7, 10)
        elif i == 57:
            v = next((int(x) for x in o if int(x) % 3 == int(x) % 4 == 2))
        elif i == 58:
            old = 6 / (F(6, 5) / 3 - F(1, 4))
            v = old * F(6, 5) / 3
        elif i == 59:
            v = next((a for a in range(3, 30) if a * a * (a - 2) == 144))
        elif i == 60:
            possible = [200 - 72 * k for k in range(1, 3)]
            v = next((int(x) for x in o if int(x) in possible))
            proof = {'allPossibleUnsubscribedWithoutOptions': possible}
        elif i == 61:
            sheep = 1
            cow = 2
            assert 30 * sheep == 10 * cow + 10 * sheep
            growth=F(20*cow*20-(10*cow+10*sheep)*30,20-30)
            grass=(20*cow-growth)*20
            v=grass/(30*sheep-growth)
            proof={'initialGrass':str(grass),'growthPerDay':str(growth),'effectiveDailyConsumption':str(30*sheep-growth)}
        elif i == 62:
            rate = 300 * (1 / F(1, 5) - 1)
            v = 4 * rate
            proof = {'machineRate': str(rate)}
        elif i == 63:
            v = 2 * 3
            proof = {'identity': 'x/2+x/6+y/3=(2x+y)/3', 'totalTime': 2}
        elif i == 64:
            v = math.comb(6, 2) * math.comb(4, 2)
        elif i == 65:
            events = [day for day in range(36) if 0 in [5 * day % 12, (5 * day + 1) % 12]]
            gaps = [b - a for a, b in zip(events, events[1:])]
            v = max(gaps)
            proof = {'eventsZeroBased': events, 'gaps': gaps}
        elif i == 66:
            assert [(-1) ** (n + 1) * (2 * n + 9) for n in range(1, 6)] == [11, -13, 15, -17, 19]
            v = -21
        elif i == 67:
            assert all((sum(map(int, str(x))) == 8 for x in [35, 71, 53, 17, 62]))
            v = next((int(x) for x in o if sum(map(int, x)) == 8))
        elif i == 68:
            a = [f'{n}.{2 * n}{4 * n}' for n in range(1, 6)]
            assert a[:4] == ['1.24', '2.48', '3.612', '4.816']
            v = a[4]
            assert ev(o[0]) == ev(o[2])
            proof = {'stringSequence': a, 'realValuedDuplicateOptions': [0, 2]}
        elif i == 69:
            a = [10, 3, 13, 1, 14, 2, 16, 5]
            assert all((a[k] == a[k - 2] + a[k - 1] for k in [2, 4, 6]))
            v = a[-1] + a[-2]
        elif i == 70:
            assert [F(2, n) for n in range(8, 12)] == [F(1, 4), F(2, 9), F(1, 5), F(2, 11)]
            v = F(2,12)
        elif i == 71:
            v = 340 - F(340 - 10, 3)
        elif i == 72:
            v = 8 // 2
        elif i == 73:
            work = [F(12, 10), F(13, 10), F(2), F(25, 10)]
            v = sum(work) / 2
            assert work[0] + work[1] + 1 == v and 1 + work[3] == v
            proof = {'schedules': ['drone1:1.2+1.3+1', 'drone2:1+2.5'], 'unsplittableOptimum': str(min((max(sum((work[k] for k in range(4) if m >> k & 1)), sum((work[k] for k in range(4) if not m >> k & 1))) for m in range(16))))}
        elif i == 74:
            v = math.comb(4, 2) * math.comb(3, 2)
        elif i == 75:
            v = F(5, 60) / (F(1, 20) - F(1, 24))
        elif i == 76:
            assert 4 + 5 == 9 and 2 + 3 == 5 and (4 + 2 == 6) and (5 + 3 == 8)
            v = 6 + 8
            assert v == 9 + 5
        elif i == 77:
            assert [1 + 22 * (n // 2) + (10 if n % 2 else 0) for n in range(7)] == [1, 11, 23, 33, 45, 55, 67]
            v = 1+22*(7//2)+(10 if 7%2 else 0)
        elif i == 78:
            a = [F(8, 15) * F(3, 4) ** n for n in range(6)]
            assert a[:4] == [F(8, 15), F(2, 5), F(3, 10), F(9, 40)] and a[5] == F(81, 640)
            v = a[4]
        elif i == 79:
            rule = lambda x: int(x.split('.')[0]) - sum(map(int, x.split('.')[1]))
            assert all((rule(x) == 4 for x in ['21.98', '18.77', '17.49', '14.55']))
            selected = next((k for k, x in enumerate(o) if rule(x) == 4))
            v = o[selected]
        elif i == 80:
            a = [5]
            for n in range(1, 6):
                a.append(abs(a[-1]) * n + 2)
            assert a[:5] == [5, 7, 16, 50, 202]
            v = -a[-1]
        elif i == 81:
            v = next((t for t in range(2, 100) if F(300, t - 1) - F(300, t) == 10))
        elif i == 82:
            v = F(4000) / F(4, 5) - 4000
        elif i == 83:
            v = math.sqrt(6 * 6 + 6 * 6 - 2 * 6 * 6 * math.cos(math.pi / 3))
        elif i == 84:
            b = F(1260 - 100) / (1 + F(3, 5))
            v = 2 * b + 100
            proof = {'stock甲': str(b + 100), 'stock乙': str(b)}
        elif i == 85:
            valid = []
            for start in range(7):
                saturdays = [d for d in range(31) if (start + d) % 7 == 5]
                if len(saturdays) == 5:
                    valid.append((start, (start + 31) % 7, [x + 1 for x in saturdays]))
            assert {x[1] for x in valid} == {6, 0, 1}
            v = 'Tuesday'
            proof = {'MondayZeroMonthStartNextStartSatDates': valid}
        elif i == 86:
            v = sum((sum((k >= 3 for k in combo)) >= 2 for combo in itertools.combinations(range(6), 4)))
        elif i == 87:
            minwrong = min((sum(x) for x in itertools.product(range(1, 11), repeat=3) if len(set(x)) == 3 and sum(x) <= 10))
            v = 10 - minwrong
            proof = {'minimumWrongCounts': [1, 2, 3], 'constructionWrongQuestionSets': [[1], [2, 3], [4, 5, 6]]}
        elif i == 88:
            places = [x for x in range(1, 100) if x % 4 == 0 and x % 6 != 0]
            v = len(places)
            proof = {'all甲Positions': places}
        elif i == 89:
            v = 500 / (F(1, 2) - F(1, 3))
        elif i == 90:
            feasible = [(n, 10 * n + 5) for n in range(1, 100) if 10 * n + 5 <= 8 * (n + 2)]
            v = max((p for n, p in feasible))
            proof = {'maxOriginalVolunteers': max((n for n, p in feasible))}
        elif i == 91:
            assert [2 ** n + 3 ** (n - 1) for n in range(1, 6)] == [3, 7, 17, 43, 113]
            v = 2 ** 6 + 3 ** 5
        elif i == 92:
            a = [12, 13, 25, 37, 49]
            assert all((a[n] - a[n - 1] == a[0] for n in range(2, 5)))
            v = a[-1] + a[0]
            proof = {'firstAsFixedIncrement': a[0], 'seedSecond': a[1], 'notOrdinaryWholeSequenceArithmetic': a[1] - a[0]}
        elif i == 93:
            assert [n ** (3 if n % 2 else 2) for n in range(1, 7)] == [1, 4, 27, 16, 125, 36]
            v = 7 ** 3
        elif i == 94:
            assert [F(2 * n - 1, 15 * n - 9) for n in range(1, 5)] == [F(1, 6), F(1, 7), F(5, 36), F(7, 51)]
            v = F(2*5-1,15*5-9)
        elif i == 95:
            rows = [(F(5), F(5), F(5, 2)), (F(24), F(12), F(8)), (F(54), F(18), F(27, 2))]
            assert all((a / b == n and a / c == n + 1 for n, (a, b, c) in enumerate(rows, 1)))
            good = []
            for k, x in enumerate(o):
                a, b, c = map(F, x.split('，'))
                if a / b == 4 and a / c == 5:
                    good.append(k)
            assert len(good) == 1
            v = o[good[0]]
        elif i == 96:
            v = 5 * (10 - 1) + 1
        elif i == 97:
            v = F(41 - 28, 29 - 28)
        elif i == 98:
            v = 40 - 40 * F(60, 100 + 60)
        elif i == 99:
            b = F(15 - 5, 15)
            a = 1 - b
            c = (30 - 10 * a - 28 * b) / 8
            v = c / a
            proof = {'rate甲': str(a), 'rate乙': str(b), 'rate丙': str(c), 'actualDays': 28, 'teamWorkDays': [10, 28, 8]}
        else:
            raise AssertionError(('unhandled', i))
        return v, proof
    for i in range(len(S)):
        value,proof=solve(i)
        proof.pop('visualOption',None)
        candidates=proof.get('candidateValues') or proof.get('optionProbabilities')
        manual=False
        manual=i==50
        if i==15: value=True; candidates=proof['optionTruths']
        ctx.add(i,value,evidence=proof,candidates=candidates,mode='manual_only' if manual else 'computation',boundary='ported model; graph feature recognition and finite-prefix pattern selection remain manual')
