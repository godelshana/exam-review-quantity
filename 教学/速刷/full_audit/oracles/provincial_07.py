"""Offline port of provincial_07 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_07'

def run(ctx):
    checks={}
    def ck(n,actual,expected):
        assert actual==expected,(n,actual,expected)
        row=int(str(n).split('_')[0])-1
        checks.setdefault(row,[]).append({'label':str(n),'value':actual,'regressionQuantity':expected})
    ck(2,7*200-sum([320,160,80,40,20,10,5]),765)
    ck(4,math.factorial(4)//2,12)
    ck(5,2016**2+73**2,2017**2+36**2)
    ck(6,F(6,10)*F(12,10)+F(4,10)*F(95,100),F(11,10))
    ck(8,max(8*min(n,10)+7*max(0,n-10) for n in [12]),94)
    ck(9,[d for d in range(59,90) if sum(d%k==0 for k in [3,4,5])==2],[72,75,80,84])
    ck(10,(4-F(5,3))/F(5,3),F(7,5))
    ck(14,math.comb(16,4)-math.comb(6,4)-10*math.comb(6,3),1605)
    ck(16,F(3,5)**2+2*F(3,5)*F(2,5)*F(3,5),F(81,125))
    ck(17,F(8*32,6)-F(5*20,6),26)
    ck(19,F(15,10)*F(1,2)+F(13,10)*F(1,5)+F(12,10)*F(1,4)-1-F(6,100),F(1,4))
    nums=[n for n in range(1,101) if n%10 not in [3,6,9]]
    ck(22,[(n,i) for i,n in enumerate(nums,1) if n%7==i%7==0],[(70,49)])
    ck(24,[(a,b,21-a-b) for a in range(1,21) for b in range(1,21-a) if 12*a+20*b+24*(21-a-b)==480],[(1,3,17)])
    ck(25,[n for n in range(1,407) if (185+n-1)//n==3 and (406+n-1)//n==5],list(range(82,93)))
    mx=0
    for lengths in set(itertools.permutations([6,6,6,1,1])):
     for crops in itertools.product(range(3),repeat=5):
      if len(set(crops))==3 and all(crops[i]!=crops[i+1] for i in range(4)):
       mx=max(mx,sum(l*[12,9,25][c] for l,c in zip(lengths,crops)))
    ck(26,mx,471)
    ck(27,(6*4+8*5+4*9)/4-(6*4+8*5+4*9)/5,5)
    ck(29,sum([47,94,93,92,91,83]),500)
    ck(30,sum(abs(p.index('A')-p.index('B'))==1 and p.index('D')<p.index('C')<p.index('E') and p[0]!='F' and p[-1]!='F' for p in itertools.permutations('ABCDEF')),24)
    ck(32,max(x*(28-x) for x in range(15,23)),195)
    ck(34,math.comb(50,2),1225)
    ck(35,60*F(7,8),F(105,2))
    ck(36,min(1000*a+500*b for a in range(8) for b in range(21) if 13*a+5*b==100),8500)
    ck(38,(F(8,10)*550+50)+(F(8,10)*850+50)-(F(8,10)*1400+50),50)
    ck(39,max(n*(n+1)//2 for n in range(1,20) if n*n<=200),105)
    ck(40,math.factorial(5)*2**5,3840)
    ck(41,4500*(F(1)+F(85,100)+F(7,10)-3*F(6,10)),3375)
    ck(42,(12*4*F(8,10)*F(1,10)+8*3*F(1,10)**2)*10000,40800)
    ck(43,84//5*10+sum([2,3,3,1,1][:84%5]),169)
    ck(44,{max(a,b,17-a-b) for a in range(4,10) for b in range(4,10) if 17-a-b>=4},{6,7,8,9})
    ck(45,150000+80000+45000+40000,315000)
    ck(48,(F(3,4)/30-F(1,120)-F(1,100))/F(1,120),F(4,5))
    ck(49,F(17,20)**2+F(3,20)**2,F(149,200))
    ck(52,max(c for a in range(15) for b in range(13) for c in range(13) if 28*a+32*b+33*c==400),4)
    solutions=[]
    for z in range(1,20):
     for l in range(7,20):
      for w in range(1,20):
       vals=[z,w,z+5,l,l-6]
       if sum(vals)==24 and len(set(vals))==5 and w==min(vals) and l<max(vals):solutions.append(vals)
    ck(54,solutions,[[4,1,9,8,2]])
    ck(55,sum(F(300,1)/(3-F(k,2)) for k in range(6)),1470)
    ck(57,(math.comb(7,3),math.comb(8,3)),(35,56))
    ck(58,F(9,8+9+8+5),F(3,10))
    ck(59,560*20,640*17+320)
    ck(60,F(14,10)*50*(1-F(9,10)**2),F(133,10))
    def chord2(i,j):
     # Squared chord equivalence on a regular nonagon is determined by smaller vertex step.
     return min((i-j)%9,(j-i)%9)
    iso=[p for p in itertools.combinations(range(9),3) if len({chord2(p[0],p[1]),chord2(p[0],p[2]),chord2(p[1],p[2])})<3]
    ck(62,len(iso),30)
    ck(63,[n for n in range(1,351) if n%13==0 and n%14==0],[182])
    ck(66,sum((0 in s)==(1 in s) for s in itertools.combinations(range(5),2)),4)
    ck(67,[(t,w,l,i) for t in range(1,35) for w in range(1,t) for l in range(1,w) for i in range(1,l) if t+w==34 and w+l==20 and l+i==16],[(23,11,9,7)])
    ck(68,3*37+9,120)
    ck(69,42*83+5*74+3*73,4075)
    ck(71,10000+9000+5600,24600)
    ck(72,[(32-y,y) for y in range(20,31) if 1<=32-y<=10 and (2*y-1)%7==0],[(7,25)])
    ck(73,F(1,3)+F(11,30)-F(3,10),F(2,5))
    ck(75,[8200*n-200*n*n-16200 for n in [5,6]],[19800,25800])
    ck(76,17*33-13*5,496)
    ck(77,(9*3+10*2+1,9+10+1),(48,20))
    ck(78,(20*2+10*F(3,2),20*F(5,2)+10*3),(55,80))
    year=2022
    ck('79_original_common_start',[(datetime.date(year,8,13)-datetime.date(year,6,14)).days%3,(datetime.date(year,8,14)-datetime.date(year,6,14)).days%4,(datetime.date(year,8,15)-datetime.date(year,6,14)).days%5],[0,1,2])
    ck('79_explicit_staggered_revision',[(datetime.date(year,8,13+k)-datetime.date(year,6,14+k)).days for k in range(3)],[60,60,60])
    ck(81,F(49)-F(126,5),F(119,5))
    sex=[]
    for ns in itertools.product(range(1,5),range(1,5),range(1,7),range(1,7)):
     if len(set(ns))==4 and len(set(t-n for t,n in zip([5,5,7,7],ns)))==4:
      sex.append((sum(max(0,n-f) for n,f in zip(ns,[2,2,3,3])),ns))
    ck(82,min(sex),(2,(1,3,2,4)))
    ck(83,F(70*5+88*4+74*3,12),77)
    ck(84,(80+4*8+7*12,10*18+16),(196,196))
    front={(x,y,z) for x,z in [(2,2),(1,1)] for y in range(4)}
    top={(x,y,z) for x,y in [(2,1),(2,2),(1,3)] for z in range(4)}
    right={(x,y,z) for y,z in [(1,1),(2,1),(2,2)] for x in range(4)}
    ck(86,(len(front),len(top),len(right),len(front&top),len(front&right),len(top&right),len(front&top&right),64-len(front|top|right)),(8,12,12,3,3,3,1,40))
    ck(87,(2*(6+8),2*(6+12),2*(8+12),6+8+12),(28,36,40,26))
    ck(89,1-F(math.comb(16,3),math.comb(40,3)),F(233,247))
    tri=[]
    for p in itertools.permutations(range(1,7)):
     a,b,c=[10*p[k]+p[k+1] for k in [0,2,4]]
     if a<b<c and a+c==2*b:tri.append((a,b,c))
    ck(90,len(tri),8)
    ck(91,sum(range(12,37)),600)
    ck(93,(F(64,10)*10/2),32)
    ck(94,2*(25*F(64,100)-5)+5,27)
    comb=[(a,b,c) for a in range(8) for b in range(4) for c in range(3) if a+2*b+3*c==7]
    ck(95,(len(comb),sum(c>0 for a,b,c in comb)),(8,4))
    ck(96,48*F(5,12),20)
    ck(97,[b for b in range(6) if 14*(5-b)+34*b<=120],[0,1,2])
    ck(98,(50-1)*(40-2),1862)
    ck(99,sum(a!=b and b!=c and c!=d and d!=a for a,b,c,d in itertools.product(range(4),repeat=4)),84)
    ck('100_explicit_uniform_congestion',F(21,8)-F(3,4)*F(3,5),F(87,40))
    ck('100_original_counterexample',F(21,8)-F(3,4)*F(6,5),F(69,40))

    for i,assertions in checks.items():
        ctx.add(i,[a['value'] for a in assertions],evidence=assertions,property_only=True,boundary='supplementary identities/subresults; not full answer matching; patterns conditional and variants distinct models')
    ctx.assertion_count=sum(map(len,checks.values()))
