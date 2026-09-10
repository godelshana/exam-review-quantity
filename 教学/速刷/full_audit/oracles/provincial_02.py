"""Offline port of provincial_02 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_02'

def run(ctx):
    checks={}
    def check(n,actual,expected):
        assert actual==expected,(n,actual,expected)
        row=int(str(n).split('_')[0])-1
        checks.setdefault(row,[]).append({'label':str(n),'value':actual,'regressionQuantity':expected})
    check(9,math.factorial(6)-2*math.factorial(3)**2,648)
    check(11,math.comb(6,3)-math.comb(4,3),16)
    check(13,sum(p[0]!=0 and p.index(2)<p.index(1) for p in itertools.permutations(range(6))),300)
    check(15,[k for k in range(3,100) if 66%(k-2)==0],[3,4,5,8,13,24,35,68])
    check(30,[min(10*a,5*b,6*c) for a,b,c in [(14,28,29),(15,31,25),(16,32,23),(17,33,21)]],[140,150,138,126])
    check(32,math.factorial(7)//2,2520)
    check(43,math.factorial(9)//math.factorial(4),15120)
    check(44,min(1200*x+800*(6-x)+900*(10-x)+600*(2+x) for x in range(7)),15000)
    check(46,sum(4*n-4 for n in [20,16,12,8,4]),220)
    check(65,sum(a+b+c==10 for a in range(1,6) for b in range(1,6) for c in range(1,6)),18)
    check(66,min(10*a+23*b for a in range(21) for b in range(8) if a+3*b>=20),158)
    check(71,len({10+5*a-2*b for a in range(6) for b in range(6-a)}),21)
    check(72,max((70-2*x)*(120+8*x) for x in range(36)),10000)
    check(93,[(2*a+c)**3==b*b for a,b,c in [(2,27,5),(21,512,22),(9,125,7)]],[True]*3)
    check(95,sum([580,562,517,543,529])/5,546.2)
    check(98,[n for n in range(181,211) if math.isqrt(n)**2==n],[196])
    m=[[13,14,19,102],[16,22,109,1],[12,101,5,30],[107,11,15,15]]
    check(99,[sum(x) for x in m]+[sum(x) for x in zip(*m)],[148]*8)

    for i,assertions in checks.items():
        ctx.add(i,[a['value'] for a in assertions],evidence=assertions,property_only=True,boundary='supplementary identities/subresults; not full answer matching; patterns conditional and variants distinct models')
    ctx.assertion_count=sum(map(len,checks.values()))
