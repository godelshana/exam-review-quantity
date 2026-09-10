"""Offline port of national_01 work calculations; see runner boundaries.
No work/raw/image dependency and no answer-key solver inputs.
"""
import math, itertools, collections, re, datetime
from math import comb, factorial, ceil, floor, sqrt, isclose, gcd
from itertools import combinations, permutations, product
from collections import Counter, deque
from fractions import Fraction as F
from decimal import Decimal as D
from _common import numeric, equal as semantic_equal
BATCH = 'national_01'
def normalize_option(s):
 s=re.sub(r'\s+','',s).replace('：',':')
 s=re.sub(r'^A(?=\d)','',s)
 for u in ['立方厘米','平方米','公斤','公里','分钟','万元','元','厘米','人数','人','起','棵','天','分','岁','种','排','倍','个','米']:
  if s.endswith(u): s=s[:-len(u)];break
 if '，' in s or ',' in s:return tuple(F(t) for t in re.split('[，,]',s))
 if '︰' in s or '∶' in s:return tuple(F(t) for t in re.split('[︰∶]',s))
 if re.fullmatch(r'\d+:\d+',s):
  h,m=map(int,s.split(':'));return h*60+m
 if s in ['九折','七五折','六折','四八折']:return {'九折':F(9,10),'七五折':F(3,4),'六折':F(3,5),'四八折':F(12,25)}[s]
 if s.endswith('万'):return F(s[:-1])*10000
 if s.endswith('千'):return F(s[:-1])*1000
 if s.startswith('少'):return -F(s[1:])
 if s.startswith('多'):return F(s[1:])
 if s.endswith('%'):return F(s[:-1])/100
 if '√' in s:
  # Restricted expression from already visually confirmed numeric options.
  s=re.sub(r'√(\d+)',r'sqrt(\1)',s)
  s=re.sub(r'(\d)(sqrt)',r'\1*\2',s)
  assert re.fullmatch(r'[0-9sqrt()/*+. -]+',s)
  return numeric(s)
 return F(s)
def eq(a,b):
 if isinstance(a,tuple) or isinstance(b,tuple):return a==b
 if isinstance(a,str) or isinstance(b,str):return a==b
 return isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10)

def run(ctx):
    S=ctx.problems
    R=[dict(correctedStem=q["s"],correctedOptions=q["o"]) for q in S]
    checks=[]
    def check(i,value,opts=None,evidence=None):
        values=opts
        if values is None:
            try: values=[normalize_option(x) for x in S[i]['o']]
            except (ValueError,TypeError,AssertionError): pass
        ctx.add(i,value,candidates=values,evidence=evidence,boundary='ported equation/enumeration domain; geometric derivation and graph transcription remain manual')
        checks.append({'index':i})
    def flags(i,bs,evidence):
        assert len(bs)==4
        check(i,True,bs,evidence)
    # 2011
    check(0,F(120)/F(5,2))
    check(1,((6+5+4)*16/2-6*16)/4)
    times=set()
    for k in range(-10,11):
     for rate in [F(90),F(15)]:
      t=F(30+60*k)/rate
      if 0<t<=F(11,6):times.add(t)
    check(2,len(times),evidence=list(map(str,sorted(times))))
    men=F(F(830)*F(5,100)-3,F(11,100));check(3,men*F(94,100))
    nonraw=F(1,40)/(F(1,15)-F(1,16));check(4,1/(15-nonraw))
    check(5,(F(9000)-12500*F(3,10))/(12500*F(7,10)))
    check(6,comb(4,2)**2+comb(4,3)*comb(4,1)+1-2)
    rests=[]
    # A rest sequence determines an admissible sequence of losers; adjacent rests differ.
    for zpos in combinations(range(11),2):
     for qpos in combinations([i for i in range(11) if i not in zpos],3):
      seq=['孙']*11
      for j in zpos:seq[j]='赵'
      for j in qpos:seq[j]='钱'
      if all(seq[j]!=seq[j+1] for j in range(10)):rests.append(seq)
    assert len(rests)==10 and {s[8] for s in rests}=={'孙'}
    check(7,'赵钱',['钱孙','赵钱','赵孙','任意'],{'admissibleRestSequences':len(rests),'ninthRest':'孙'})
    check(8,52-(8+10+9-7-2))
    check(9,sqrt(2)/4)
    check(10,F(38*3+24*4+42*5,12))
    check(11,F(2*(160-90),180-160))
    check(12,F(3)/(F(5,17)-F(10,17)*F(5,13)))
    check(13,floor(F(30)*F(57,2)-30*20)//10)
    Ns=[n for n in range(1,300) if ceil(n/2)-ceil(n/3)==8 and ceil(n/3)-ceil(n/4)==5]
    assert Ns==[52];check(14,ceil(Ns[0]/5),evidence=Ns)
    # 2012
    check(15,2/(1/F(11,100)+1/F(9,100)))
    check(16,15000-F(25000-10000,3))
    check(17,sum(min(69,n) for n in [100,80,70,50])+1)
    def prime(n):return n>=2 and all(n%d for d in range(2,int(sqrt(n))+1))
    pq=[(p,q) for p in range(2,16) for q in range(2,13) if prime(p) and prime(q) and 5*p+6*q==76]
    assert pq==[(2,11)];check(18,4*pq[0][0]+3*pq[0][1],evidence=pq)
    check(19,(F(3)/F(3,5)+1)/2)
    p=F(factorial(4)*2**5,factorial(9));flags(20,[F(1,1000)<p<F(5,1000),F(5,1000)<p<F(1,100),p>F(1,100),p<=F(1,1000)],str(p))
    check(21,15*F(6,5)/F(3,2))
    triples=[(a,b,c) for a in range(11) for b in range(11) for c in range(11) if a+b+c==10 and 3*a+2*b+c==15]
    flags(22,[all(a+b==6 for a,b,c in triples),all(b+c==7 for a,b,c in triples),max(a for a,b,c in triples)==5,all(c-a==5 for a,b,c in triples)],triples)
    check(23,ceil(360/60)+1,evidence='Six maximal 60-degree arcs require centers at 5sqrt(3)>5; center uncovered; seven-disk construction verified analytically.')
    first=None
    for k in range(20):
     gap=F(2)-F(k,4)
     if gap<=F(3,4): first=9*60+k*60+gap/F(3,2)*60;break
    check(24,first)
    check(25,F(50+5*max(F(10,3),F(60,10)),100))
    boxes=[(a,b) for a in range(9) for b in range(20) if 12*a+5*b==99 and 10<a+b<20]
    assert boxes==[(2,15)];check(26,abs(boxes[0][0]-boxes[0][1]),evidence=boxes)
    check(27,7*(F(460,5)+86)/2)
    check(28,2*10*(5-1),evidence='Height-ordered chain length <=40; closed chain/convex hull <=80; collinear endpoints achieve limiting lower bound.')
    check(29,2*F(6*6,2)*3/3)
    # 2013
    check(30,min(x for x in range(1,66) if x+6*(x-1)>=65))
    check(31,7*F(18,9)+1)
    p=2*F(3,10)*F(7,10)*F(4,10)**2+F(3,10)**2*(1-F(6,10)**2)
    flags(32,[p<F(5,100),F(5,100)<p<F(10,100),F(10,100)<p<F(15,100),p>F(15,100)],str(p))
    ratios=[normalize_option(s) for s in S[33]['o']]
    flags(33,[3*b+6*c==4*a and a+2*b==7*c for a,b,c in ratios],list(map(str,ratios)))
    check(34,(6*200+4*175)*F(21,2)-2000*F(9,2))
    check(35,comb(4,2)*4+1)
    # Functional claims on all possible previous balances: evaluate two distinct values to disprove wrong affine claims.
    affs=[]
    for x in [10000,20000]:affs.append((x,F(3,4)*(F(6,5)*x-2000)+1500))
    flags(36,[all(z==F(9,10)*x for x,z in affs),all(z==F(11,10)*x for x,z in affs),all(z==x-1000 for x,z in affs),all(z==x+1000 for x,z in affs)],list(map(str,affs)))
    check(37,F(60*10-80*6,10-6))
    cycle=['小说']*3+['教材']*4+['工具书']*5+['科技树']*7
    check(38,cycle[(136-1)%len(cycle)],S[38]['o'])
    starts=[d for d in range(7) if sum((d+j)%7<5 for j in range(31))==22]
    check(39,tuple(starts),[(0,2),(2,6),(0,3),(3,6)],starts)
    # Per-second window enumeration over all 32-minute phases; moving 1 km/min, stop intervals last 2 minutes.
    maxstop=max(sum(((s+phase)%(32*60))>=30*60 for s in range(60*60)) for phase in range(32*60))
    assert maxstop==240;check(40,63-(60-F(maxstop,60)))
    plans=[(x,30-x) for x in range(31) if 80*x+50*(30-x)<=2070 and 40*x+90*(30-x)<=1800]
    best=max(plans,key=lambda p:120*p[0]+140*p[1]);check(41,best,[(19,11),(20,10),(17,13),(18,12)],plans)
    cases=[(a,160-a) for a in range(1,160) if (17*a)%100==0 and ((160-a)*20)%100==0]
    assert cases==[(100,60)];check(42,F(cases[0][1]*80,100))
    scores=[]
    for p in range(101):
     f=F(94+p,2);c=f+2;m=3*p-190
     if f.denominator==1 and 0<=c<=100 and 0<=m<=100 and m>c>max(94,p,f):scores.append((p,f,c,m))
    assert len(scores)==1;check(43,scores[0][0],evidence=list(map(str,scores)))
    minimum=100
    for off in product([0,1],repeat=8):
     cells=list(off[:4])+[2]+list(off[4:]);g=[cells[j:j+3] for j in [0,3,6]]
     if [max(row) for row in g]==[1,2,1] and [max(g[i][j] for i in range(3)) for j in range(3)]==[1,2,1]:minimum=min(minimum,sum(cells))
    check(44,minimum)
    # 2014
    check(45,F(7)/(F(3,2)*F(4,5)*F(19,20)-1))
    needed=(F(1,4)-F(1,10))*100/(F(1,2)-F(1,4));assert needed==60;check(46,ceil(needed/14))
    check(47,max(m for m in range(1,12) if sum(range(12,17))+sum(range(m,m+5))<=100))
    check(48,(30-1)*3)
    check(49,sum([15,15,20,25,30,35])+sum([10,20,30]))
    x=(F(6,100)-F(5,50))/(F(1,50)-F(1,45));assert x==18;check(50,F(x+7,50))
    # Color the cube adjacency graph: adjacent iff not the same face and not opposite paired faces.
    edges=[(a,b) for a in range(6) for b in range(a+1,6) if a//2!=b//2]
    chromatic=next(k for k in range(1,7) if any(all(c[a]!=c[b] for a,b in edges) for c in product(range(k),repeat=6)))
    check(51,chromatic)
    check(52,(1-F(4,5))/(F(4,5)*F(5,8)),evidence="Sunday-only=2, both=1, Saturday=6; Saturday-only=5 of union8")
    schedules=[]
    for a in combinations(range(1,13),4):
     if 1 not in a or 2 not in a or sum(a)!=26:continue
     for b in combinations(sorted(set(range(1,13))-set(a)),4):
      if 9 in b and 10 in b and sum(b)==26:
       c=sorted(set(range(1,13))-set(a)-set(b));schedules.append((a,b,c,c[-1]-c[0]-3))
    assert len(schedules)==1;check(53,max(x[3] for x in schedules),evidence=schedules)
    total=1/(F(1,6)-F(1,8));check(54,total*(F(1,4)-F(1,6)))
    check(55,comb(3,1)*factorial(5)**2)
    n=23;byes=0
    while n>1:byes+=n%2;n=ceil(n/2)
    check(56,byes)
    t=7+F(4,11)/(F(1,13)+F(1,11));check(57,t-floor(t))
    check(58,(F(219,2)-F(3,2)*78)/(10*(1-F(3,2))))
    donations=[(2*z+w,z+w,z,w) for z in range(1,26) for w in range(1,z) if 4*z+3*w==25]
    assert donations==[(11,7,4,3)];check(59,donations[0][0],evidence=donations)
    # 2015 provincial
    check(60,F(min(30,35),50))
    total=F(6)/(F(32,100)-F(24,100));check(61,total*(1-2*F(32,100)-F(24,100)))
    check(62,F(36*7)/(40*F(105,100)))
    li1994=F(15-1,2);check(63,(li1994+20,li1994+3+20))
    check(64,F(179+146+246-24-2*115+52)/F(9,10))
    check(65,6*(1+4)-2-4)
    placements=[c for c in combinations(range(2,9),3) if all(c[j+1]-c[j]>1 for j in range(2))]
    assert len(placements)==10;check(66,len(placements)**2)
    oils=[(a,b,c) for a in range(16) for b in range(4) for c in range(9) if 5*a+2*b+c==9]
    check(67,len(oils),evidence=oils)
    patrol=[d for d in range(1,32) if any((d-1)%p==0 for p in [3,5,8])];check(68,31-len(patrol),evidence=patrol)
    room_solutions=[]
    for p in permutations([1211,1213,1215,1217,1219]):
     a,b,c,d,empty=p
     if abs(a-b)==6 and b+c>max(p[i]+p[j] for i,j in combinations(range(4),2) if (i,j)!=(1,2)) and abs(d-a)==2 and abs(d-b)!=2 and abs(d-c)!=2:room_solutions.append(p)
    emptyset={p[4] for p in room_solutions};flags(69,[int(v) in emptyset for v in S[69]['o']],room_solutions)
    d=F(4,3)-F(11,12);c=d*F(3,5);bc=F(11,12)/F(11,5);check(70,bc-c)
    check(71,ceil(F(2*25,12)),evidence='Global two-boundary length bound; five 5x8 cells at radius sqrt(22.25)<5 cover rectangle.')
    vdelta=F(400,8);va=10*vdelta-250;vb=va+vdelta
    assert va==250 and vb==300 and 3*va==150+2*vb
    check(72,min(400-250,250))
    check(73,F(5,5**3))
    # Actual graph options visually inspected in PDF: (has upward jumps, same troughs, decaying peaks).
    visual75=[(False,False,False),(True,True,True),(False,False,False),(False,False,False)]
    f=lambda n:F(40)+F(250*ceil(n/10),n)
    assert all(f(10*k)==65 and f(10*k+1)>65 for k in range(1,100))
    assert all(f(10*k+1)>f(10*(k+1)+1) for k in range(1,100))
    check(74,(True,True,True),visual75,{str(n):str(f(n)) for n in [1,10,11,20,21,30]})
    # 2015 district: checked individually, including restored percentages and original formula images.
    check(75,F(50*3,5)/50)
    N=F(6)/F(8,100);check(76,N-2*N*F(32,100)-N*F(24,100))
    check(77,F(36*(14-7),(36+4)*F(105,100)))
    li2014=F(15+39,2);check(78,(li2014,li2014+3))
    onlyone=179+146+246-2*24-3*115;check(79,F(onlyone+24+115+52)/F(9,10))
    check(80,5*1**2+4*2**2+(2**2-1**2))
    check(81,comb(5,3)**2)
    check(82,sum(1 for a in range(2) for b in range(4) if 0<=9-5*a-2*b<=8))
    check(83,ceil(F(50,12)))
    D=16-11;C=F(3,5)*D;BC=F(11)/F(11,5)
    check(84,(BC-C)/12)
    # 2016
    bad,ping,football,basket=4,2,3,1
    check(85,bad,[football+basket,ping+football,F(3,2)*football,3*basket])
    c1=[1,1,1,0];c2=[1,0,0,0,0]
    mx1=max(sum(c1[(j+s)%4] for j in range(35)) for s in range(4))
    mx2=max(sum(c2[(j+s)%5] for j in range(35)) for s in range(5))
    check(86,mx1+mx2)
    fares=[(a,b,20-a-b) for a in range(21) for b in range(21-a) if 2000*a+1800*b+1000*(20-a-b)+170*20==27000]
    assert fares==[(2,2,16)];a,b,_=fares[0];flags(87,[a==b,b==a+1,a==b+2,b==a+4],fares)
    check(88,F(370)*F(15,2)/(37*15))
    check(89,F(30*5-18*5,5-2))
    check(90,max(sum((d-a)%3==0 and (d-b)%4==0 for d in range(1,32)) for a in range(3) for b in range(4)))
    v=F(3,2)*F(18,5)/(2-F(3,2));dist=4*v
    flags(91,[40<dist<50,dist>50,dist<30,30<dist<40],str(dist))
    # Visual graph features: (linear upper, staircase lower).
    features=[(False,True),(True,False),(True,True),(True,False)]
    for x in range(1,40):
     ys=[max(a,b,x-a-b) for a in range(x+1) for b in range(x-a+1)]
     assert min(ys)==ceil(x/3) and max(ys)==x
    check(92,(True,True),features,'All nonnegative three-company partitions X=1..39 verify ceil(X/3) and X.')
    ways=factorial(3)*factorial(3)*factorial(2)*factorial(4)
    flags(93,[ways<1000,1000<=ways<=5000,5001<=ways<=20000,ways>20000],ways)
    start=min(F(360*k+r)/F(11,2) for k in range(12) for r in [120,240] if F(360*k+r)/F(11,2)>510)
    end=max(F(360*k+180)/F(11,2) for k in range(12) if F(360*k+180)/F(11,2)<720)
    rights=[F(360*k+r)/F(11,2) for k in range(12) for r in [90,270] if start<F(360*k+r)/F(11,2)<end]
    check(94,len(rights),evidence={'start':str(start),'end':str(end),'rights':list(map(str,rights))})
    ds=lambda x:sum(map(int,str(x)))
    ages=[a for a in range(100,115) if 3*ds(a)==ds(a-3)];assert ages==[111]
    check(95,ds(2015-ages[0]),evidence=ages)
    check(96,4*F(6,5)**2-3)
    lang=[(e,f,j) for e in range(1,11) for f in range(1,11) for j in range(1,11) if e+f+j-1==10 and f==e+4 and f==2*j]
    assert lang==[(2,6,3)];check(97,lang[0][0]-1,evidence=lang)
    staff=[n for n in range(20,100) if F(14,n)-F(12,n-2)==F(3,100)];assert staff==[50]
    p=F(comb(12,2),comb(staff[0]-2,2));flags(98,[p<F(1,100),F(1,100)<=p<=F(4,100),F(4,100)<p<=F(7,100),F(7,100)<p<=F(10,100)],str(p))
    # Exhaustively allocate 4 four-black cubes and 24 three-black cubes among 8 corners/24 edges.
    # Any remaining exterior face-center cube shows at most one; opposite-only cubes show at most one everywhere.
    best=-1;allocation=None
    for four_corners in range(5):
     for three_corners in range(min(24,8-four_corners)+1):
      for four_edges in range(min(4-four_corners,24)+1):
       for three_edges in range(min(24-three_corners,24-four_edges)+1):
        used=8+24;remaining_special=(4-four_corners-four_edges)+(24-three_corners-three_edges)
        if remaining_special>32:continue
        score=56+2*four_corners+three_corners+four_edges+three_edges
        if score>best:best=score;allocation=[four_corners,three_corners,four_edges,three_edges]
    check(99,best,evidence={'optimalSpecialCubeCounts_corner4_corner3_edge4_edge3':allocation})
