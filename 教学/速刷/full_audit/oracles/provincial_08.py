"""Five provincial_08 computations from submitted problem parameters.

Salt: direct mass accounting checked against affine closed form.
Clock: exact candidate-time substitution AND interval derivation.
Fold: exact quadratic feasible interval, conditional on transcribed rectangle.
Probability: state recursion checked against all eight win/loss histories.
Pool: full visibility-graph simple-path enumeration. Assumes no crossing pool
interior and Euclidean land travel; polygon shortest paths bend only at vertices.
No source key, proof result, display asset, or review answer is a solver input.
"""
from fractions import Fraction as F
from itertools import product, permutations
from math import sqrt, isclose, isqrt
import re
BATCH='provincial_08'

def run(ctx):
    # Row0: grams of salt, total fluid fixed at100 grams.
    mass=F(70);history=[mass]
    for _ in range(5):
        mass=mass*(1-F(40,100))+40*F(20,100)
        history.append(mass)
    concentration=mass/100
    closed=F(20,100)+(F(70,100)-F(20,100))*(1-F(40,100))**5
    assert concentration==closed
    ctx.add(0,concentration,evidence={'saltMasses':history,'closedForm':closed},boundary='well-mixed fluid, constant100g; two exact derivations')

    # Row1: finish10:m has 6m=300+m/2. Start8:m meets |5.5m-240|<=30.
    end=10*60+F(10*30,F(11,2))
    start_bounds=[8*60+F(8*30+x,F(11,2)) for x in (-30,30)]
    duration_bounds=(end-start_bounds[1],end-start_bounds[0])
    durations=[];valid=[]
    for text in ctx.problems[1]['o']:
        match=re.fullmatch(r'(\d+)小时(\d+)分钟',text)
        assert match,('unsupported duration option',text)
        duration=60*int(match[1])+int(match[2]);durations.append(duration)
        minute=end-duration-8*60
        delta=abs(6*minute-(8*30+minute/2))%360
        good=0<=minute<60 and min(delta,360-delta)<=30
        assert good==(duration_bounds[0]<=duration<=duration_bounds[1])
        valid.append(good)
    assert sum(valid)==1
    ctx.add(1,True,candidates=valid,evidence={'finishMinutes':end,'durationInterval':duration_bounds,'optionDurations':durations,'valid':valid},boundary='8点多/10点多 interpreted as the respective clock hours')

    # Row2: fold A(0,0) onto E(x,5). Bisector2xu+10v=x²+25.
    # Intersects AB iff x²<=25; intersects AD iff x²-26x+25<=0.
    length,width=13,5
    discriminant=(2*length)**2-4*width**2
    root=isqrt(discriminant);assert root*root==discriminant
    left,right=F(2*length-root,2),F(2*length+root,2)
    lower=max(F(0),left);upper=min(F(length),F(width),right)
    assert lower<=upper
    for x in (lower,upper):
        intersection_ab=(x*x+width*width)/(2*width)
        intersection_ad=(x*x+width*width)/(2*x)
        assert 0<=intersection_ab<=width and 0<=intersection_ad<=length
    ctx.add(2,upper-lower,evidence={'quadraticRoots':[left,right],'intersectionInterval':[lower,upper],'bisector':'2xu+2wv=x²+w²'},boundary='diagram transcribed as A(0,0),B(0,5),D(13,0),E(x,5); quadratic sign gives the entire interval, not a sampled grid')

    # Row3: entire probability space, no assumed source interval.
    p=F(7,10);states=[p]
    for _ in range(2):p=p*F(1,2)+(1-p)*F(7,10);states.append(p)
    histories={}
    for wins in product((False,True),repeat=3):
        probability=F(1)
        for j,win in enumerate(wins):
            chance=F(7,10) if j==0 or not wins[j-1] else F(1,2)
            probability*=chance if win else 1-chance
        histories[wins]=probability
    assert sum(histories.values())==1
    enumerated=sum(prob for wins,prob in histories.items() if wins[-1])
    assert p==enumerated
    ctx.add(3,p,evidence={'stateProbabilities':states,'allHistories':histories,'enumeratedThirdWin':enumerated},boundary='no draws; previous winner alone determines next-game probability')

    # Row4: reject a segment iff some interior point lies in open square(0,80)^2.
    # Open t-interval intersections are exact Fractions, including boundary grazing.
    vertices={'A':(0,80),'B':(80,80),'C':(80,0),'D':(0,0),'E':(40,110),'F':(120,-40)}
    def visible(a,b):
        lo,hi=F(0),F(1)
        for x,y in zip(vertices[a],vertices[b]):
            delta=y-x
            if not delta:
                if not 0<x<80:return True
                continue
            t1,t2=F(-x,delta),F(80-x,delta)
            lo=max(lo,min(t1,t2));hi=min(hi,max(t1,t2))
        return lo>=hi
    def squared(a,b):return sum((x-y)**2 for x,y in zip(vertices[a],vertices[b]))
    edges={(a,b):sqrt(squared(a,b)) for a in vertices for b in vertices if a!=b and visible(a,b)}
    paths=[]
    for n in range(5):
        for mid in permutations('ABCD',n):
            route=('E',)+mid+('F',);legs=list(zip(route,route[1:]))
            if all(leg in edges for leg in legs):paths.append((sum(edges[leg] for leg in legs),route))
    shortest=min(paths);through_d=min(p for p in paths if 'D' in p[1])
    difference=through_d[0]-shortest[0]
    # Independent exact cancellation checks: E-A=E-B; D-F=B-F; extra edge A-D.
    assert squared('E','A')==squared('E','B') and squared('D','F')==squared('B','F')
    exact_extra=isqrt(squared('A','D'));assert exact_extra**2==squared('A','D')
    assert isclose(difference,exact_extra,rel_tol=1e-12,abs_tol=1e-12)
    ctx.add(4,exact_extra,evidence={'vertices':vertices,'legalSimplePaths':len(paths),'shortest':shortest,'shortestViaD':through_d,'numericalDifference':difference,'exactCancellationExtra':exact_extra},boundary='manual diagram coordinates; Euclidean polygon-obstacle visibility theorem; no crossing pool interior')
