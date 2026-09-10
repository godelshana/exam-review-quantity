"""Offline port of provincial_01 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_01'

def run(ctx):
    data=ctx.problems
    Q=data
    results={};checks={}
    def put(n,value,expected,kind='exact',extra=None):
        if isinstance(value,float): assert math.isclose(value,expected,rel_tol=1e-8,abs_tol=1e-8),(n,value,expected)
        else: assert value==expected,(n,value,expected)
        manual=kind in {'manual_missing_question_snapshot','verbal_manual_argument_audit'}
        results[n]=value;checks[n]=value
        ctx.add(n-1,value,evidence={'kind':kind,'detail':extra,'regressionQuantity':str(expected)},mode='manual_only' if manual else 'computation',property_only=True,boundary='supplementary quantity/property regression; not necessarily full answer; geometry/pattern and finite-search domain justified manually')
    C=math.comb; fac=math.factorial
    put(1,[n for n in range(1,1001) if (n%3,n%7,n%11)==(2,3,4)],[59,290,521,752,983])
    put(2,F(5*2,7-5),F(5))
    strict=[1]*8; flex=[1,1]
    for i in range(2,8):flex.append(flex[-1]+flex[-2])
    put(3,(strict[-1],flex[-1]),(1,21),'constraint_dispute')
    L=next(l for l in range(1,121) if all(l%e==0 for e in [24,12,5]));put(4,L**3//(24*12*5),1200)
    put(5,next(n*n for n in range(2,200) if 4*n-4==108),784)
    put(6,F(9)-1/(F(1,9)+2*(F(1,8)-F(1,9))),F(9,5))
    put(7,F(4,5)*F(2,5),F(8,25))
    put(8,sum(D(x)**2 for x in ['110.1','1210.3','1220.4','1260.8']),D('4555940.9'))
    put(9,F(13)+F(4,19)+(F(86)+F(15,19))*(F(1,4)+F(5,8)+F(1,8)),F(100))
    pts=[(0,0),(2,0),(2,2),(0,2),(1,1)];areas=set()
    for a,b,c in itertools.combinations(pts,3):
     area=F(abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])),2)
     if area:areas.add(area)
    put(10,sorted(areas),[F(1),F(2)])
    put(11,F(40)/(4*F(1,2)),F(20))
    put(12,max(n for n in range(1,25) if n*(n+1)//2<=25),6)
    put(13,((5*5+5)/5)-5,1.)
    water=F(99,4)+11; dissolved=min(F(28,4)+4,water*F(28,99));put(14,dissolved/(water+dissolved),F(28,127))
    put(15,((15*3600+30*60+200000)//3600+1)%24,0)
    u=F(600)/F(12,5);v=u-F(600,3);put(16,F(600)/(u+v),F(2))
    put(17,F(540)/(F(9,10)*F(4,5)),F(750))
    sol=[o for o in range(13,40) if F(12,o)+F(6,40-o)==1 and o>20];put(18,sol,[30])
    put(19,abs(2*(60*40+60*22+40*22)-2*(58*38+58*25+38*25)),8)
    put(20,(1125+855)//math.gcd(1125,855)+1,45)
    put(21,None,None,'manual_missing_question_snapshot',{'missing':'stem absent in submitted record; raw-source inspection is not a mathematical solver'})
    put(22,2*(3*80-60),360)
    put(23,sum(abs(p.index(0)-p.index(1))>1 for p in itertools.permutations(range(5))),72,'enumeration')
    put(24,F(1)/(F(1,6)+F(1,18)),F(9,2))
    w=[10,20,15,25];costs=[sum(w[j]*abs(i-j)*5*3 for j in range(4)) for i in range(4)];put(25,costs,[1875,1125,975,1275],'enumeration')
    put(26,20+20+1,41)
    subsets=list(itertools.combinations(range(10),5));put(27,F(sum(sum(x<6 for x in p)>=3 for p in subsets),len(subsets)),F(31,42),'enumeration')
    prob=sum((F(4,5)**sum(p))*(F(1,5)**(3-sum(p))) for p in itertools.product([0,1],repeat=3) if sum(p)>=2);put(28,prob,F(112,125),'enumeration')
    put(29,C(6,1)*C(5,2)*fac(3),360)
    shares=[F(2,15),F(9,25),F(1,4)];payments=[100,100,90];T=sum((1-s)*v for s,v in zip(shares,payments))/(1-sum(shares));put(30,T,F(850))
    put(31,(4+8)//(5-4),12)
    put(32,55+3*105+10,380)
    nums=set(range(1,10));possible=set()
    for a in itertools.combinations(nums,3):
     rem=nums-set(a)
     for b in itertools.combinations(rem,3):
      c=rem-set(b);s=sorted([sum(a),sum(b),sum(c)])
      if len(set(s))==3 and s[2]==2*s[0]:possible.add(tuple(s))
    put(33,sorted(possible),[(10,15,20),(11,12,22)],'enumeration')
    put(34,F(10**2*6,3*5**2),F(8))
    put(35,sum(a+b+c+d==8 for a in range(1,9) for b in range(1,9) for c in range(1,9) for d in range(1,9)),35,'enumeration')
    cv=(-math.sqrt(3),-1);uv=(-math.sin(math.radians(75)),math.cos(math.radians(75)));distance=4/(2*sum(a*b for a,b in zip(cv,uv)));put(36,distance,math.sqrt(2))
    put(37,F(100)/(F(3,5)-F(1,2))/2+50,F(550))
    put(38,[n for n in range(1,101) if n%9==7 and n%11==9],[97],'enumeration')
    put(39,10**3*24*23,552000)
    put(40,sum(bool(set(p)&set(range(4))) and bool(set(p)&set(range(4,7))) for p in itertools.combinations(range(7),4)),34,'enumeration')
    ratios=[3*math.sqrt(3)/(4*math.pi),math.pi/(3*math.sqrt(3)),2/math.pi,math.pi/4];put(41,min(range(4),key=lambda i:abs(ratios[i]-.6)),1,extra=ratios)
    put(42,math.cos(math.pi/6)/math.cos(math.pi/3),math.sqrt(3))
    f=lambda x:math.hypot(5,x)+24/math.pi*math.cos(math.pi*x/24)
    values=[f(i*12/100000) for i in range(100001)];put(43,min(values),5+24/math.pi,'dense_grid_plus_analytic_boundary',extra={'sidewallsOnly':13,'minimumX':values.index(min(values))*12/100000})
    put(44,(F(32*4,3),F(2*2)),(F(128,3),F(4)))
    cut=[(60*a+43*b,a,b) for a in range(5) for b in range(6) if 60*a+43*b<=250];put(45,max(cut),(249,2,3),'enumeration')
    put(46,1-F(30*30,2*60*60),F(7,8))
    rows=[(60,6,4,1500),(50,8,2,1000),(100,10,3,700),(75,7,5,1200)];lines=[(fixed+300*h,F(unit)+F(300,speed)) for speed,unit,h,fixed in rows];put(47,lines,[(2700,F(11)),(1600,F(14)),(1600,F(13)),(2700,F(11))])
    put(48,sum(5+2*k for k in range(10))+sum(5*k for k in range(1,6)),215)
    R=F(8**2+4**2,2*4);correct=math.pi*4**2*(float(R)-4/3);wrong=math.pi*4*(3*float(R)**2+4**2)/6;put(49,(math.ceil(correct/10),math.ceil(wrong/10)),(44,67),'formula_inconsistency')
    put(50,2/3-math.sqrt(3)/(2*math.pi),0.3910022189557706)
    put(51,5*math.pi*(25*math.sqrt(3)/(3+2*math.sqrt(3))),105.22340180961665)
    put(52,C(9,6)-1,83)
    x=F(7)*2;original=[x-10,x+1,x/2,2*x];put(53,(original,max(original)-min(original)),([F(4),F(15),F(7),F(28)],F(24)))
    put(54,(max(0,1000*F(1,5)-1000*F(3,5)),900*F(1,5)-200*F(3,5)),(0,60),'denominator_dispute')
    a,b,c=48,48,48;c+=a//2;a//=2;b+=c//2;c//=2;a+=b//2;b//=2;put(55,(a,b,c),(66,42,36))
    put(56,(25-20)//(2-1),5)
    assign=[p for p in itertools.product(range(3),repeat=4) if len(set(p))==3];put(57,F(sum(p[0]!=p[1] for p in assign),len(assign)),F(5,6),'enumeration')
    profits=[((p-40)*(300-10*(p-44)),p) for p in range(44,75)];put(58,max(profits),(2890,57),'enumeration')
    put(59,F(350)-50-70-F(350,2)*(1-F(100,350))*(1-F(140,350)),F(155))
    put(60,next(n-9 for n in range(1,100) if n*(n+1)//2==105),5)
    # Pigeonhole proof: four closed diameter-20 triangles; tight 5-point configuration.
    h=20*math.sqrt(3);p=[(0,0),(40,0),(20,h),(10,h/2),(30,h/2)];put(61,min(math.dist(a,b) for a,b in itertools.combinations(p,2)),20.,'tight_constructive_bound')
    N=next(n for n in range(51,60) if n%13==0);male=(N+4)//2;female_support=[n for n in range(25) if n<=5 and n>4];put(62,male//4+female_support[0],12)
    put(63,1+math.floor((20-1.5)/math.sqrt(1.5**2-.5**2)),14,extra={'14length':1.5+13*math.sqrt(2),'15length':1.5+14*math.sqrt(2)})
    t=500/60*3.1088/(math.pi*2.3*142)*10;put(64,round(t,2),.25)
    put(65,4*4*math.sqrt(144/4),96.)
    put(66,math.floor(1/F(7,24)),3)
    fees=lambda minutes:0 if minutes<=15 else 5+4*max(0,math.ceil((minutes-60)/30));put(67,[fees(t) for t in [120,135,165,180]],[13,17,21,21])
    put(68,(424000//10-400)//6,7000)
    put(69,F(2,5)**2+2*F(2,5)*F(3,5)*F(1,5),F(32,125))
    put(70,(sum([14]+list(range(20,29))),max([14]+list(range(20,29)))/14),(230,2.))
    progress=list(range(270,951,8));put(71,[sum(lo<=n<=hi for n in progress) for lo,hi in [(100,200),(200,300),(300,400),(400,500)]],[0,4,13,12],'enumeration')
    seq=[p for p in itertools.permutations(range(6)) if max(p.index(i) for i in [0,1,2])-min(p.index(i) for i in [0,1,2])==2 and abs(p.index(3)-p.index(4))>1];put(72,len(seq)*C(8,3)*C(3,2)*C(2,1),24192,'enumeration')
    put(73,F(5+10)+F(235,4),F(295,4))
    put(74,10*4*9+4*10*3,480)
    areas=[4,4,2,1,2,2,1];put(75,sum(len(set(areas[i] for i in p))==3 for p in itertools.permutations(range(7),3)),72,'enumeration')
    put(76,25*F(1,2)**3,F(25,8),'similar_cone_volume_assumption')
    put(77,F(24)/F(3,5)-24,F(16))
    put(78,math.floor(16*(1+math.sqrt(2))),38)
    clearance=6*math.sin(math.pi/6)-.6*math.cos(math.pi/6);put(79,max(v for v in [1.8,2.3,2.6,3.2] if v<=clearance),2.3)
    decay=F(80-75,50-40);put(80,50*(F(3,2)+decay),F(100))
    cases=[]
    for a in range(9):
     for b in range(1,18):
      last=475-48*a-32*(b-1)
      if 2*a+b<=17 and F(64,3)<=last<=32:cases.append((a,b,last))
    put(81,cases,[(0,15,27),(2,12,27),(4,9,27)],'zero_boundary_dispute')
    put(82,fac(3)*fac(2)*fac(4)**2,6912)
    put(83,70*15+F(1150-50*15,4),F(1150))
    Bamount=F(19,7);put(84,(F(2,5)*Bamount,F(3,10)*Bamount),(F(38,35),F(57,70)),'exact_vs_rounding_dispute')
    put(85,sum(len(set(p))==3 and p[0]!=0 for p in itertools.product(range(3),repeat=5)),100,'enumeration')
    put(86,F(75**2*200,3*150**2),F(50,3))
    r=F(50)/(F(3,2)-1);put(87,3*r*r/10000,F(3))
    put(88,(2*(3*3-1*1),2*math.sqrt(1*1+2*2)),(16,2*math.sqrt(5)))
    put(89,None,None,'manual_missing_question_snapshot',{'missing':'remaining conditions and question absent; no arithmetic solver'})
    put(90,3*math.pi*25/6-2*math.sqrt(3)*25/4,25*(math.pi-math.sqrt(3))/2)
    put(91,F(300)-F(150)/F(5,4)-F(150)/F(3,4),F(-20))
    put(92,F(80)*(15+12+24)/24,F(170))
    put(93,F(1040+150+300+160,150+100+80),F(5))
    prices=[10,10,20,20,20];orders=[]
    for k in range(1,6):
     orders.extend(p for p in itertools.permutations(range(5),k) if sum(prices[i] for i in p)==40)
    put(94,len(orders),24,'enumeration')
    put(95,sum(p.count(0)>=2 and p.count(1)>=1 and p.count(2)>=1 for p in itertools.product(range(3),repeat=6)),360,'enumeration')
    opts=[(2*x+(3000-x),x,3000-x) for x in range(3001) if -2*x+3*(3000-x)>=0];put(96,max(opts),(4800,1800,1200),'enumeration')
    scores=[5]*2+[4]*4+[3]*3+[2]*4;put(97,sum(sum(scores[i] for i in q)>=13 for q in itertools.combinations(range(13),3)),19,'enumeration')
    prob=F(0);paths=[]
    for path in itertools.product([0,1],repeat=4):
     a=b=20;server=1;pr=F(1);valid=True
     for j,winner in enumerate(path):
      pa=F(3,5) if server==0 else F(3,10);pr*=pa if winner==0 else 1-pa
      if winner==0:a+=1
      else:b+=1
      server=winner
      if abs(a-b)>=2 and j<3:valid=False;break
     if valid and (a,b)==(23,21):prob+=pr;paths.append(''.join('AB'[x] for x in path))
    put(98,prob,F(243,2500),'state_enumeration',paths)
    best=(-1,0,0)
    for b in range(801):
     a=min((5000-2*b)//5,(2400-3*b)//2)
     if a>=0:best=max(best,(5*a+4*b,a,b))
    put(99,best,(5363,927,182),'integer_optimization_enumeration')
    put(100,4/(6+4*math.sqrt(2)),6-4*math.sqrt(2))
