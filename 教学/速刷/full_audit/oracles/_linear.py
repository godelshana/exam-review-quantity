"""Small bounded LP: enumerate vertices using exact Fraction Gaussian elimination.
Only the subset used by national_03 is accepted. No numerical optimizer dependency.
Used here only for feasible pointed polytopes/polyhedra with an attained minimum.
This is not a general solver: infeasibility vs unboundedness is not classified.
"""
from fractions import Fraction as F
from itertools import combinations
from types import SimpleNamespace

def linear_system(rows,rhs,n):
    a=[[F(v) for v in row]+[F(b)] for row,b in zip(rows,rhs)]
    if len(a)!=n: return None
    for col in range(n):
        k=next((k for k in range(col,n) if a[k][col]),None)
        if k is None:return None
        a[col],a[k]=a[k],a[col]
        pivot=a[col][col];a[col]=[v/pivot for v in a[col]]
        for k in range(n):
            if k!=col:
                factor=a[k][col]
                a[k]=[v-factor*w for v,w in zip(a[k],a[col])]
    return [row[-1] for row in a]

def linprog(c,*,A_ub,b_ub,A_eq,b_eq,bounds,method=None):
    n=len(c)
    assert bounds==[(0,None)]*n and len(A_eq)==len(b_eq)
    inequalities=[list(row) for row in A_ub]+[[-int(j==k) for j in range(n)] for k in range(n)]
    limits=list(b_ub)+[0]*n
    best=None;vertices=0
    for active in combinations(range(len(inequalities)),n-len(A_eq)):
        x=linear_system(list(A_eq)+[inequalities[k] for k in active],list(b_eq)+[limits[k] for k in active],n)
        if x is None:continue
        if any(sum(F(v)*z for v,z in zip(row,x))>b for row,b in zip(inequalities,limits)):continue
        vertices+=1;value=sum(F(v)*z for v,z in zip(c,x))
        if best is None or value<best[0]:best=(value,x)
    return SimpleNamespace(success=best is not None,fun=best[0] if best else None,x=best[1] if best else None,vertices=vertices)
