"""Offline port of provincial_03 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_03'
def norm(s):
 s=re.sub(r'\s','',s).replace('：',':')
 m=re.fullmatch(r'(?:(\d+)小时)?(?:(\d+)分(?:钟)?)?',s)
 if m and (m[1] or m[2]):return int(m[1] or 0)*60+int(m[2] or 0)
 m=re.fullmatch(r'(\d+)[点:](\d+)?分?',s)
 if m:return int(m[1])*60+int(m[2] or 0)
 if '、' in s:return tuple(F(a) for a in s.split('、'))
 if s.startswith('星期'):return {'星期一':1,'星期二':2,'星期三':3,'星期四':4,'星期五':5,'星期六':6,'星期日':7}[s]
 if s.endswith('%'):return F(s[:-1])/100
 if 'π' in s:
  s=s.replace('π','*pi');assert re.fullmatch('[0-9pi*+/-]+',s);return numeric(s.replace('pi',str(math.pi)))
 return F(s)
def equal(a,b):
 if isinstance(a,tuple) or isinstance(b,tuple):return a==b
 return math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10)

def run(ctx):
    S=ctx.problems
    R=[dict(correctedStem=q["s"],correctedOptions=q["o"]) for q in S]
    checks=[]
    def C(i,value,options=None,evidence=None,approx=False):
        vals=options
        if vals is None:
            try: vals=[norm(x) for x in S[i]['o']]
            except (ValueError,TypeError,AssertionError): pass
        if approx:
            errors=[abs(float(value)-float(x)) for x in vals]
            ctx.add(i,min(errors),candidates=errors,evidence={'rawQuantity':str(value),'detail':evidence},boundary='nearest-option approximation, NOT exact equality or a unique sequence law')
        else:
            ctx.add(i,value,candidates=vals,evidence=evidence,boundary='ported model; finite sequence prefixes do not establish a unique continuation')
        checks.append({'index':i})
    def flags(i,bs,evidence):
        assert len(bs)==4
        C(i,True,bs,evidence)
    # 0-24
    C(0,18-sum(range(1,4)))
    C(1,F(1316-1016,10))
    v=F(2000+10*50,30-10);C(2,60*v/1000)
    x=(2*25-12);C(3,2*x)
    C(4,49+36+28-13-2*9)
    choices=[int(x) for x in S[5]['o']]
    valid=[d for d in range(1,16) if 400%d==0 and 400//math.lcm(16,d)==5];C(5,max(valid),evidence=valid)
    t=2/(F(1,6)+F(1,210));C(6,t*60)
    N=(153*(62-24)+59*(92-54))/(62-54);assert N==1007
    middle=F(62)*(N-153)-59*92;assert middle==47520
    C(7,N,evidence={'middleCount':N-153-59,'middleScoreTotal':str(middle)})
    C(8,F(102*2,3)+3)
    C(9,F(5000-500,4000-3500))
    C(10,F(160-110,3-1))
    C(11,41+(41-25)+4)
    C(12,8*4)
    a=[1,2,3,10,39];assert all(a[i]==a[i-2]*(a[i-1]+a[i-2]) for i in range(2,len(a)));C(13,a[-2]*(a[-1]+a[-2]))
    C(14,F(433+(433-311)+20,10))
    assert 9**2-2*17==47 and 4**2-2*26==-36;C(15,15**2-2*F(13,2))
    # 3/T+T/(T+5)=1 -> 3(T+5)=5T -> T=7.5
    C(16,F(3*5,5-3))
    shirts=[(x,y,z) for x in range(34) for y in range(34-x) for z in [33-x-y] if x+2*y+3*z==76 and 100*x+180*y+240*z==6460]
    assert shirts==[(4,15,14)];C(17,shirts[0][2],evidence=shirts)
    # Minimum full-return line delivery groups: take farthest 3 successively.
    pts=list(range(1000,1951,50));maxima=list(reversed(pts[1::3]));assert sorted(maxima)==[1050,1200,1350,1500,1650,1800,1950]
    closed=2*sum(maxima);opened=closed-max(pts)
    assert closed==21000 and opened==19050;C(18,opened,evidence={'sourceC_if_all_return':closed,'strict_no_final_return':opened,'groupMaxima':maxima})
    time_to_meet=F(240- F(20,3),1)/(1+F(1,3));assert time_to_meet==175
    C(19,time_to_meet+(time_to_meet-120))
    p=F(6*20,math.comb(27,2));C(20,p,approx=True,evidence='Stem explicitly says 概率约为; closest two-decimal option is .34.')
    remain=0
    for k in range(10):remain=2*(remain+1)
    C(21,remain)
    t1=F(66240,143);t2=F(74160,143)
    assert t1/2==(6*t2)%360 and t2/2==(6*t1)%360 and 480<t2<540
    C(22,t2-t1,evidence={'sourceNearestMinuteOption':'B=55','exact':str(F(720,13)),'t1':str(t1),'t2':str(t2)})
    n=23;byes=0
    while n>1:byes+=n%2;n=math.ceil(n/2)
    C(23,byes)
    C(24,(F(219,2)-F(3,2)*78)/(-5))
    # 25-49
    flight=F(6,2);offset=-flight;C(25,(12+offset)*60)
    C(26,-7);C(27,52+13)
    B=2*75+2*80-3*80;C(28,F(3*80-B,2))
    C(29,1/(F(1,10)+F(1,15)))
    C(30,F(2*48,60-48)*(60+48))
    C(31,F(5000*4,5)*F(6,5))
    C(32,60/(F(9,11)-F(3,5)))
    C(33,56*2);C(34,49+18+4);C(35,6**2)
    a=[1,2,6,16,44,120];assert all(a[j]==2*(a[j-1]+a[j-2]) for j in range(2,len(a)));C(36,2*(44+120))
    assert all(sum(map(int,str(n)))==10 for n in [325,118,721,604]);flags(37,[sum(map(int,o))==10 for o in S[37]['o']],'Digit sums of all given values equal 10.')
    k=F(480-70-90,70+90);C(38,max(70,90,70*k,90*k))
    C(39,9*60+2+5*6)
    C(40,F(1,2)/(F(1,4)+F(1,6)))
    fast=(F(720,18)+F(720,6))/2;C(41,720/fast)
    people=[(16-b,b,20-b,14+b) for b in range(1,16) if 16-b<b<20-b<14+b];assert people==[(7,9,11,23)];C(42,people[0][3],evidence=people)
    low=600*(F(30,100)-F(25,100))/(F(30,100)-F(15,100));C(43,(low,600-low))
    C(44,78+77-107,evidence='Under stated two-category-union interpretation; extra donation-only categories explicitly excluded by model boundary.')
    C(45,F(120,3))
    C(46,math.factorial(6)-math.factorial(4)*math.factorial(3))
    C(47,50-40//4)
    C(48,23-1);C(49,71+32+10)
    # 50-74
    seq=[F(1,2),3,8,18,38];assert all(seq[j]==2*seq[j-1]+2 for j in range(1,len(seq)));C(50,38*2+2)
    C(51,26**2+1);C(52,112*2)
    # 2a=3b and a+b=1050
    one=F(6300,6)/5;C(53,one)
    C(54,F((108-72)*1000,3600)*20/F(1,2))
    Ns=[n for n in range(101,200) if all((F(n)*r).denominator==1 for r in [F(1,5),F(2,5),F(1,4),F(1,15),F(1,30),F(1,36)])];assert Ns==[180];C(55,Ns[0],evidence=Ns)
    A=2;B=4*A;Cside=B-A;D=Cside;E=A+B;C(56,(B+Cside+D)*(B+E),evidence={'A':A,'B':B,'C':Cside,'D':D,'E':E})
    C(57,2*150*math.ceil((10+15+21+8+5+26+15)/60))
    C(58,len(range(0,100,8)))
    C(59,1000-(320+130+250+180))
    # Capacity-limited cycle route exact DP, no crossing the flowerbed.
    def dist(a,b):return min(abs(a-b),10-abs(a-b))*100
    closed_routes={};open_routes={}
    for k in [1,2,3]:
     for subset in combinations(range(1,10),k):
      mask=sum(1<<(x-1) for x in subset)
      variants=[(sum(dist(a,b) for a,b in zip((0,)+p,p)),p) for p in permutations(subset)]
      open_routes[mask]=min(cost for cost,p in variants)
      closed_routes[mask]=min(cost+dist(p[-1],0) for cost,p in variants)
    dp=[math.inf]*512;dp[0]=0
    for mask in range(1,512):dp[mask]=min(dp[mask^part]+cost for part,cost in closed_routes.items() if part&mask==part)
    minimum=min(dp[511^part]+cost for part,cost in open_routes.items());C(60,minimum,evidence={'masksEnumerated':512,'allReturn':dp[511]})
    lamps=sum(1 for p in combinations(range(20),10) if all(p[j+1]-p[j]>1 for j in range(9)));C(61,lamps)
    champ=2*7*3;others_min=2*math.comb(7,2)*2/7;C(62,champ-others_min)
    C(63,4*18/2)
    # Positive remaining black count: ratio has a nonzero base.
    C(64,3*(6+3)+1+2)
    C(65,600-3*F(600,4))
    scale=F(70,8+12+15);C(66,(15-8)*scale)
    C(67,F(850*6-800*3,3))
    C(68,(4-1+math.lcm(2,3,5))%7+1)
    C(69,F(200-50)*F(2,3))
    C(70,F(4*30-30,4*3-2))
    C(71,math.factorial(4)*math.factorial(3))
    C(72,2*(100/2-(45/360)*math.pi*100))
    C(73,math.factorial(3))
    C(74,85-F(10,2))
    # 75-99
    C(75,(20-3*2)-(30-3*6))
    C(76,(F(60,100)+F(50,100))/2)
    C(77,F(3600)/F(3,4))
    C(78,F(1200,100))
    C(79,1/(F(1,9)+F(2,9)))
    C(80,12*11)
    seq=[23,34,58,93,152];assert all(seq[j]==seq[j-1]+seq[j-2]+1 for j in range(2,len(seq)));C(81,93+152+1)
    decparts=[19,27,35,43];intparts=[9,4,5,2]
    assert all(intparts[i]==((v//10)*(v%10))%10 for i,v in enumerate(decparts))
    nxt=decparts[-1]+8;C(82,F((((nxt//10)*(nxt%10))%10)*100+nxt,100))
    assert [(n-1)*n*(n+1) for n in range(1,6)]==[0,6,24,60,120];C(83,5*6*7)
    assert all(c==3*a-b for a,b,c in [(4,5,7),(8,8,16),(12,9,27)]);C(84,16*3-10)
    C(85,((20+5)*2+10)*2)
    feasible=[(a,9000-a) for a in range(9001) if F(8,5)*a+2*(9000-a)<=15000]
    a,b=max(feasible,key=lambda p:F(7,10)*p[0]+p[1]);C(86,a,evidence={'B':b,'profit':str(F(7,10)*a+b)})
    nb=5+7-6;half=6*nb+6;C(87,2*half)
    r=F(5*60-6*40,60-40);N=60*(5-r);C(88,N/20+r)
    profits=[(p-15)*(80-2*p) for p in [22,20,18,16]];flags(89,[v==200 for v in profits],profits)
    C(90,F(750+1350,math.gcd(750,1350))+1)
    newspapers=[(a,b) for a in combinations(range(5),3) for b in combinations(range(5),3) if len(set(a)|set(b))==5];C(91,len(newspapers))
    C(92,F(3,10)*F(1,9)*F(2,8))
    bags=[(x,y) for x in range(7) for y in range(11) if 24*x+15*y==153];assert bags==[(2,7)];C(93,bags[0][0],evidence=bags)
    # Actual recovered PDF: a+u=60 and 6(a-u)=12(b-u) -> 2b=a+u.
    b=F(300,5)/2;assert b==30 and 5*(50+10)==300 and 6*(50-10)==12*(30-10);C(94,b)
    C(95,41+20)
    costs=[40*(15-x)+50*(5+x)+50*x+30*(8-x) for x in range(9)];C(96,min(costs),evidence=costs)
    C(97,(F(250)*F(4,100)+10)/(250+10-160))
    C(98,1-1/F(4,3)**2)
    C(99,F(60,3)-10+5)
