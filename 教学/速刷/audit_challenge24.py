"""从约束重算24题：不用题库a/e反求答案。枚举、精确分数或动态规划与讲解交叉验证。"""
import json, math, re
from pathlib import Path
from fractions import Fraction as F
from itertools import product, combinations
ROOT=Path(__file__).resolve().parent

def load():
    t=(ROOT/'原创复合24.js').read_text(encoding='utf-8')
    return json.loads(t.split('window.CHALLENGE_Q = ',1)[1].rstrip(';\n'))

def solve(c):
    k=c['kind']
    if k=='transfer': return F(c['total']*c['before'][0],sum(c['before']))-F(c['total']*c['after'][0],sum(c['after']))
    if k=='resource': return max(n for n in range(500) if sum(max(0,n*r-s)*p for r,s,p in zip(c['need'],c['stock'],c['price']))<=c['budget'])
    if k=='production':
        d=c['days']; (aa,ab),(ba,bb)=c['rates']; ra,rb=c['need']
        return max(min((aa*x+ba*y)//ra,(ab*(d-x)+bb*(d-y))//rb) for x,y in product(range(d+1),repeat=2))
    if k=='return':
        l,a,b=c['length'],c['fast'],c['slow']; t=F(l*2+a*F(c['rest']),a+b)
        assert t>F(l,a)+F(c['rest'])
        return l-b*t
    if k=='ring': return (F(1,c['opposite'])+F(1,c['same']))/(F(1,c['opposite'])-F(1,c['same']))
    if k=='age': return (c['threshold']-c['sum'])//c['people']+1
    if k=='rank':
        # 选其余9个不同分数的背包：最大化高于固定分数的人数。
        n,t,f=c['n']-1,c['total']-c['fixed'],c['fixed']; dp=[{} for _ in range(n+1)];dp[0][0]=0
        for v in range(101):
            if v==f: continue
            for cnt in range(n,0,-1):
                for total,num in list(dp[cnt-1].items()):
                    if total+v<=t: dp[cnt][total+v]=max(dp[cnt].get(total+v,-1),num+(v>f))
        return dp[n][t]+1
    if k=='groups':
        best=0
        for seq in combinations(range(c['minimum'],c['total']),c['groups']-1):
            last=c['total']-sum(seq)
            if last>seq[-1] and last<=c['ratio']*seq[0]: best=max(best,last)
        return best
    if k=='calendar':
        start=(c['start']+c['days'])%7
        days=[d for d in range(1,c['nextDays']+1) if (start+d-1)%7==c['weekday']]
        return days[c['occurrence']-1]
    if k=='courses':
        days=c['days']; a,b=c['lengths']; total=good=0
        for x in range(days-a+1):
            for y in range(days-b+1):
                A=set(range(x,x+a)); B=set(range(y,y+b))
                if A&B:continue
                rest=set(range(days))-A-B; total+=1
                good+=all(d+1 not in rest for d in rest)
        return F(good,total)
    if k=='prefix':
        good=0
        for seq in product([-1,1],repeat=c['n']):
            sums=[sum(seq[:i]) for i in range(1,len(seq)+1)]
            good+=sums[-1]==c['end'] and all(s>0 if c['strict'] else s>=0 for s in sums)
        return good
    if k=='conditional':
        p,q=F(c['p']),F(c['q']); return (p*(1-q)+(1-p)*q)/(1-(1-p)*(1-q))
    if k=='balls':
        allpairs=list(combinations(range(c['red']+c['blue']),c['draw']))
        valid=[pair for pair in allpairs if any(i<c['red'] for i in pair)]
        return F(sum(all(i<c['red'] for i in pair) for pair in valid),len(valid))
    if k=='border': return F(c['area']-4*c['width']**2,c['width'])
    if k=='vessel':
        # 底面积赋为1。小锥半径比=高度比，体积另算。
        H=F(c['coneHeight']); h=F(c['initialHeight']); small=h*(h/H)**2/3
        flow=small/c['initialTime']; full=H/3; vol=full+c['target']-H
        return vol/flow
    if k=='cut':
        a,b,d=c['sides']; return 2*(a*b+a*d+b*d)+2*(c['pieces']-1)*b*d
    if k=='arithmetic':
        b=c['block']; d=F(c['nextBlock']-c['firstBlock'],b*b); first=F(c['firstBlock'],b)-F(b-1,2)*d
        return sum(first+i*d for i in range(c['months']))
    if k=='profit':
        candidates=[(price,(price-c['cost'])*(c['sales']+(c['price']-price)//c['step']*c['growth'])) for price in range(c['cost'],c['price']+1,c['step'])]
        best=max(v for _,v in candidates); prices=[p for p,v in candidates if v==best]; assert len(prices)==1; return prices[0]
    if k=='shipping':
        heavy=F(c['weight']-c['count']*c['light'],c['heavy']-c['light']); assert heavy.denominator==1
        return sum(num*(c['base']+max(0,weight-c['included'])*c['extra']) for num,weight in [(heavy,c['heavy']),(c['count']-heavy,c['light'])])
    if k=='evap': return ((c['mass']-c['water'])*F(c['target'])-c['mass']*F(c['low']))/(F(c['high'])-F(c['low']))
    if k=='replacement':
        salt=F(c['salt'])
        for _ in range(c['times']):salt-=salt*c['remove']/c['mass']
        return salt/F(c['target'])-c['mass']
    if k=='leaders':
        n=c['n'];a,b=c['fixed']; count=0
        for group in combinations(range(n),c['size']):
            A=set(group);B=set(range(n))-A
            if (a in A)==(b in A): continue
            count+=len(A-{a,b})*len(B-{a,b})
        return count
    if k=='boats':
        p=c['people'];a,b=c['seats'];pa,pb=c['prices']; return min(i*pa+j*pb for i in range(p+1) for j in range(p+1) if a*i+b*j>=p)
    if k=='digit_probability':
        from itertools import permutations
        samples=[p for p in permutations(c['digits']) if int(''.join(map(str,p)))%c['divisor']==0]
        a,b=c['adjacent']
        return F(sum(abs(p.index(a)-p.index(b))==1 for p in samples),len(samples))
    if k=='transport': return sum(c['large']*a+c['small']*b==c['mass'] for a in range(1,c['mass']+1) for b in range(1,c['mass']+1))
    raise ValueError(k)

def audit():
    qs=load();rows=[]
    assert len(qs)==24
    for q in qs:
        expected=solve(q['check']); vals=list(map(F,q['o'])); match=[i for i,v in enumerate(vals) if v==expected]
        assert len(set(vals))==4 and match==[q['a']], (q['uid'],expected,q['o'],q['a'])
        rows.append(f"| {q['uid']} | {q['h']} | {expected} | 独立约束复算通过 |")
    (ROOT/'原创复合24审计.md').write_text('# 原创复合24题：数学复算记录\n\n非国考真题；逐题编写，`check`是题面条件的结构化转录，不是参考答案。\n审计不读取解析算答案；由枚举/分数/动态规划独立计算，并检查四选项唯一性。\n程序不能自动证明题面转录无歧义，仍需教学审阅；本批由编写者逐题核读，不宣称专家审定。\n\n| ID | 结构 | 复算结果 | 状态 |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n',encoding='utf-8',newline='\n')
    print('challenge24: 24/24 exact mathematical checks passed')
if __name__=='__main__':audit()
