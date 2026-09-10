"""Offline port of provincial_06 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'provincial_06'

def run(ctx):
    data=ctx.problems
    Q=data
    results={};checks={}
    def v(n,value,expected,kind='exact',extra=None):
        if isinstance(value,float): assert math.isclose(value,expected,rel_tol=1e-8,abs_tol=1e-8),(n,value,expected)
        else: assert value==expected,(n,value,expected)
        manual=kind in {'manual_missing_question_snapshot','verbal_manual_argument_audit'}
        results[n]=value;checks[n]=value
        ctx.add(n-1,value,evidence={'kind':kind,'detail':extra,'regressionQuantity':str(expected)},mode='manual_only' if manual else 'computation',property_only=True,boundary='supplementary quantity/property regression; not necessarily full answer; geometry/pattern and finite-search domain justified manually')
    C=math.comb;fac=math.factorial
    v(1,(F(1,9),F(4,9),1-F(1,9)-F(4,9)),(F(1,9),F(4,9),F(4,9)))
    v(2,(F(9)/F(3,6),F(1)/F(1,5)),(F(18),F(5)))
    # These are explicitly textual items, not numerical computations.
    for n in range(3,8):
     v(n,None,None,'verbal_manual_argument_audit',{'notMath':True})
    pairs=[(x,y) for x in range(1,16) for y in range(1,x) if x*x-y*y==45];v(8,(pairs,sum(x*x+y*y for x,y in pairs)),([(7,2),(9,6)],170),'enumeration')
    v(9,math.ceil(F(150)/(2+1+F(11,4))),27)
    c=F(22-6,2);total=c+(c+2)+(c+6);v(10,max(k for k in range(1,20) if k*(k+1)/2<=total),7)
    materials=[(562,933),(420,860),(502,1000),(980,1015)];v(11,[(F(2*l-3*s,5),F(4*s-l,5)) for s,l in materials],[(F(36),F(263)),(F(92),F(164)),(F(494,5),F(1008,5)),(F(-182),F(581))])
    assign=[p for p in itertools.product(range(4),repeat=5) if len(set(p))==4 and p[0]!=0 and p[3]==2 and p.count(3)==1];fav=[p for p in assign if p[0]==p[1]];v(12,(len(assign),len(fav),F(len(fav),len(assign))),(33,2,F(2,33)),'enumeration',{'doubleGroupCounts':[sum(p.count(g)==2 for p in assign) for g in range(4)],'favorable':fav})
    v(13,(F(28,2)-F(45,5),45-F(3*28,4),math.ceil(F(73,6))-7),(F(5),F(24),6))
    v(14,1-F(8,10)**3,F(61,125));assert 7**3<1000*F(61,125)<8**3
    sets=[p for p in itertools.combinations(range(1,10),4) if math.prod(p)%320==0];v(15,(sets,len(sets)*fac(4)**2),([(2,4,5,8),(4,5,6,8)],1152),'enumeration')
    L=F(32);v(16,(L-F(L,4),F(3,2)*L+4-2*(L-10+4)),(F(24),F(0)))
    v(17,F(15,35)*60,F(180,7))
    v(18,30+20*F(5,2)+10*F(9,2),F(125))
    res=set(n*n%20 for n in range(0,20,2));valid=res&set(range(10,20));v(19,(valid,(10-(next(iter(valid))-10))//2),({16},2))
    S=math.sqrt(27*48);v(20,S-S*3/4,9.)
    def sq(n):return math.isqrt(n)**2==n
    formation=[(N,m) for N in range(201,300) for m in range(4,10) if sq(N//3) and sq(N//m)];v(21,formation,[(245,5)],'enumeration')
    comps=[(a,b,c) for a in range(2,6) for b in range(2,7) for c in range(2,5) if a+b+c==9];v(22,len(comps),9,'enumeration',comps)
    c=F(50-20,8-5);parents=8*c;valid=[(a,int(parents)-a) for a in range(1,int(parents)) if a!=parents-a and a!=c and parents-a!=c];best=max(a*b for a,b in valid);v(23,[p for p in valid if p[0]*p[1]==best],[(39,41),(41,39)],'enumeration')
    meters=[(10*a+b,10*b+a,100*a+b) for a in range(1,10) for b in range(1,10) if 2*(10*b+a)==10*a+b+100*a+b];v(24,meters,[(16,61,106)],'enumeration')
    possible={2*x-1 for x in range(1,10)};v(25,([8 in possible,6 in possible]),[False,False],'parity')
    marks=set(range(3,61,4));cams=set(range(8,61,9));v(26,(len(marks),len(cams),marks&cams,500*len(marks)+800*len(cams)-300*len(marks&cams)),(15,6,{35},12000))
    r=F(36-24,48-36);v(27,36*(1+r),F(72))
    v(28,[N for N in range(1,100) if (2*N)%7==0 and (2*N)%9==0],[63],'enumeration')
    v(29,[n for n in range(4,100) if C(n,4)==10*C(n,3)],[43],'enumeration')
    tri=[(b,c) for b in range(1,100) for c in range(b+1,110) if c*c-b*b==49];v(30,(tri,F(25,56)),([(24,25)],F(25,56)))
    v(31,(38+3*18-6,sum([20,19,18,17,14]),20+19),(86,88,39),'bound_and_construction')
    Y=(F(100)-F(4,5)*88)/(F(4,5)-F(7,10));M=Y+88;month=M/12*F(4,5);year=Y*F(7,10);v(32,(Y,M,min(year+6*month,18*month,2*year)),(F(296),F(384),F(1804,5)))
    v(33,5*3.14/(3*3.14+4),15.7/13.42)
    v(34,math.sqrt(150**2+300**2-100**2),50*math.sqrt(41))
    part=[(a,b,c) for a in range(1,13) for b in range(1,a) for c in range(1,b) if a+b+c==12];v(35,len(part),7,'enumeration',part)
    extra=[5*k//4 for k in range(1,6) if 11*k%4==0];v(36,extra,[5],'enumeration')
    a,b=21,7;v(37,(8*(a+b),F(3*a+b,8*(a+b))),(224,F(5,16)))
    sales=[(x,y,40-2*x-y) for x in range(1,20) for y in range(1,40) if 40-2*x-y>=1 and 8*x+5*y==41];v(38,sales,[(2,5,31)],'enumeration')
    assign=[p for p in itertools.product(range(3),repeat=4) if len(set(p))==3 and (p.count(0)<=1 or (p[0]!=0 and p[1]!=0))];v(39,len(assign),26,'enumeration')
    slots=[[(1,0),(2,0),(3,0),(4,0)],[(1,1),(2,1),(5,0),(6,0)],[(3,1),(4,1),(5,1),(6,1)]];v(40,len(set(p for slot in slots for p in slot)),12,'schedule_construction');assert all(len(set(i for i,side in slot))==4 for slot in slots)
    v(41,(216//24,2**8,2**9),(9,256,512))
    events=sorted({F(i,9) for i in range(12)}|{F(i,7) for i in range(10)});first=None
    for lo,hi in zip(events,events[1:]):
     t=(lo+hi)/2
     if math.floor((2+9*t)%4)==math.floor((7*t)%4):first=(lo,math.floor((7*t)%4));break
    v(42,first,(F(5,9),3),'event_enumeration')
    alloc=[(x,a,b,c) for x in range(19) for a in range(19) for b in range(19) for c in range(19) if (x+a+b,x+a+c,x+b+c)==(18,16,15)];v(43,max(x for x,a,b,c in alloc),13,'enumeration')
    pack=[(6*a+3*b,a,b) for a in range(1,30) for b in range(1,30) if 6*a+3*b==4*a+8*b];v(44,min(pack),(36,5,2),'enumeration')
    x=(F(44)+F(5,4)*200)/(F(6,5)+F(5,4));v(45,(x,2*x-200+44),(F(120),F(84)))
    v(46,F(80,4),F(20))
    s=F(159-18)*F(2,3);b=(s-28)/F(3,2);c=s/2+18;v(47,(b,c,math.ceil(F(3,2)*c)-b),(F(44),F(65),F(54)))
    b_start=F(1)-F(1,3);b_at10=3*(2-b_start);c_time=(b_at10/4)/2;v(48,10-c_time,F(19,2))
    alloc=[(a,b,c) for a in range(4) for b in range(6) for c in range(3) if a+b+c==4 and sum(t>0 for t in [a,b,c])>=2];v(49,len(alloc),10,'enumeration',alloc)
    v(50,F(C(5,2)*C(6,2),C(11,4)),F(5,11))
    t=F(1,2)+1;last=2*(F(2)/t)-1;v(51,last/2,F(5,6))
    p2=F(1,5)/(F(9,4)-1);p=F(2,5);assert p*p==p2;v(52,(F(3,2)*p)**2*(1-p)**2,F(81,625))
    valid=[]
    for winners in itertools.product([0,1],repeat=6):
     pair=(0,1);seq=[];win=[]
     for j in winners:
      seq.append(pair);winner=pair[j];win.append(winner);idle=next(t for t in range(3) if t not in pair);pair=tuple(sorted((winner,idle)))
     if sum(0 in p for p in seq)==3 and seq[2]!=seq[0]:valid.append({'pairs':seq,'winners':win})
    v(53,len(valid),4,'state_enumeration',valid)
    v(54,120*(1-F(1,4)/F(3,2)),F(100))
    a,b=3,2;c=2*a;W=8*a+6*b+4*c;v(55,F(W,c),F(10))
    v(56,F(53)/F(18,5)*F(8,5),F(212,9))
    pts={'D':(0,0),'B':(150,200),'F':(-50,150),'G':(-50,50),'C':(150,0)};seq=['D','B','F','G','C'];v(57,sum(math.dist(pts[a],pts[b]) for a,b in zip(seq,seq[1:])),350+100*math.sqrt(17))
    v(58,5*(8+12+15),175)
    edges={tuple(sorted((i,(i+1)%8))) for i in range(8)}|{(0,4),(1,5),(2,6),(3,7)};v(59,(len(edges),[sum(i in e for e in edges) for i in range(8)]),(12,[3]*8),'graph_construction')
    v(60,(312//(3*48+12))*4,8)
    v(61,3+F(3,4)/(F(4,5)*(F(1,12)+F(1,15))),F(37,4))
    v(62,F(7,9+7),F(7,16))
    v(63,F(5*5,4*3)>2,True,'constructive_ratio_bound')
    v(64,[x for x in [F(46,10),F(51,10),F(56,10),F(61,10)] if (24-5*x)/4>=0],[F(23,5)])
    v(65,20*(10+5)+19*F(20,3),F(1280,3))
    op=lambda x,y:x-F(y,2);v(66,op(op(7,10),4),F(0))
    v(67,F(4*7,8-7),F(28))
    v(68,F(6**3-2*3*4,2*3*4),F(8))
    u,vv=60,20;v(69,(F(420,u)+F(80,vv),F(240,u)+F(140,vv),F(u-vv,2)),(F(11),F(11),F(20)))
    revenue=[((F(2)+F(k,5))*(10-F(k,2)),k) for k in range(21)];v(70,max(revenue),(F(45,2),5),'enumeration')
    v(71,next(t for t in range(10) if 2**t>=51),6)
    combos=list(itertools.combinations(range(4,16),3));v(72,F(sum(any(b-a==1 for a,b in zip(p,p[1:])) for p in combos),len(combos)),F(5,11),'enumeration')
    v(73,[N for N in range(1,100) if 1<=5*N+38-6*(N-1)<5],[40,41,42,43],'enumeration')
    v(74,10*F(5,100)+10*F(75,1000)+20*F(1,10),F(13,4))
    v(75,F(100*2+70*5+50*5,10),F(80))
    v(76,F(1)/(F(2,3)-F(1,4)),F(12,5))
    # Q77 pixel-grid topology independently illustrates all four region counts.
    def regions(a,b,adj=False,N=300):
     labels=[]
     for j in range(N):
      y=(j+.5)*b/N;row=[]
      for i in range(N):
       x=(i+.5)*a/N
       first=(x-a/2)**2+y*y<(a/2)**2
       second=(x-a/2)**2+(y-b)**2<(a/2)**2 if not adj else x*x+(y-b/2)**2<(b/2)**2
       row.append(int(first)+2*int(second))
      labels.append(row)
     seen=set();sizes=[]
     for y in range(N):
      for x in range(N):
       if (x,y) in seen:continue
       q=deque([(x,y)]);seen.add((x,y));label=labels[y][x];size=0
       while q:
        xx,yy=q.popleft();size+=1
        for u,w in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
         if 0<=u<N and 0<=w<N and (u,w) not in seen and labels[w][u]==label:seen.add((u,w));q.append((u,w))
       if size>5:sizes.append(size)
     return len(sizes)
    counts=[regions(a,1) for a in [.75,1,1.5,3]];v(77,counts,[3,4,5,7],'topology_cases_grid_crosscheck',{'adjacent': [regions(a,1,True) for a in [.3,1,3]],'proof':'See review for continuous region classification; grid only cross-checks examples.'})
    T=F(6700,3);v(78,(math.floor(T),F(233,1350)+F(2233,2700)<=1),(2233,True),'linear_program_bound_and_integer_construction')
    a,b=105,70;v(79,(8*(a+b),10*a+5*b,F(8*(a+b),b)),(1400,1400,F(20)))
    v(80,F(3,5)*F(9,5)-1,F(2,25))
    v(81,(1+789)%5,0)
    sol=[(a,b) for a in range(51,60) for b in range(1,50) if a+b>100 and 8*a+10*b==944 and 5*(a+b)==530];v(82,sol,[(58,48)],'enumeration')
    v(83,F(95,100)*F(8,100)+F(5,100)*F(92,100),F(61,500))
    v(84,len([n for n in range(100,1000) if '3' in str(n) and '5' in str(n)]),52,'enumeration')
    x=F(125)/(1+1+4+F(1,4));v(85,x-4,F(16))
    v(86,[(n,20000//(32+8*n)) for n in range(40,51) if 20000%(32+8*n)==0],[(46,50)],'enumeration')
    v(87,C(4,1)*3*fac(3),72)
    v(88,F(2,80)/F(3,100),F(5,6))
    attained=158+16*math.sqrt(34);alternatives=[206,238,attained,158+10*math.sqrt(73)];v(89,[i for i,x in enumerate(alternatives) if x>=attained-1e-9],[2],'attainable_lower_bound_eliminates_other_options')
    wins=[(7,0),(7,1),(7,2),(6,0),(6,1),(6,2),(5,0),(5,1),(4,0),(4,1),(3,0),(2,0)];draws=[(1,3),(5,7)];scores=[0]*8
    for a,b in wins:scores[a]+=2
    for a,b in draws:scores[a]+=1;scores[b]+=1
    assert len({tuple(sorted(e)) for e in wins+draws})==14;v(90,(scores,C(8,2)-len(wins)-len(draws)),(list(range(8)),14),'schedule_construction')
    sol=[(a,28-a,d) for a in range(2,14) for d in range(1,10) if a*(28-a+d)==144 and (28-a)//10==(28-a+d)//10];v(91,sol,[(6,22,2)],'enumeration')
    W=F(15)/(F(1,6)-F(1,8));v(92,(W,F(W,14),math.ceil(F(W,14))),(F(360),F(180,7),26))
    v(93,F(28*35,20),F(49))
    v(94,C(10,5)//2,126)
    v(95,14600*(F(98,73)-1),F(5000))
    v(96,200-F(100*80,64),F(75))
    v(97,(F(35)*F(4,5)-22)/(F(4,5)-F(1,2)),F(20))
    v(98,F(24)/(F(7,5)*F(4,5)-1),F(200))
    sol=[n for n in range(1,240) if F(2400,n)-10-F(2400-10*n,n+30)==2];v(99,sol,[120],'enumeration')
    v(100,sum(k*(k+1)//2 for k in range(1,8)),84)
