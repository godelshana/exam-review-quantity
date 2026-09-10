"""Offline mathematical oracle support (stdlib only; never writes data/reviews).

Frozen problem parameters are not answer keys. A SHA-256 binds each manually
ported solver to the submitted stem/options; changed problems fail closed until
re-parameterized. Schema checks are reported separately from computation.
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path


def fingerprint(q):
    payload = {'uid': q['uid'], 's': q['s'], 'o': q['o']}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def serial(value):
    if isinstance(value, (Fraction, Path)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def numeric(text):
    """Restricted arithmetic parser, without eval or executable input."""
    if not isinstance(text, str):
        return text
    s = re.sub(r'\s+', '', text).replace('−', '-').replace('×', '*').replace('÷', '/')
    if not s or '![' in s:
        return None
    s = re.sub(r'(?<![A-Za-z])√(\d+)', r'sqrt(\1)', s)
    s = re.sub(r'(\d|\))(?=sqrt|\()', r'\1*', s)
    try:
        tree = ast.parse(s, mode='eval')
    except (SyntaxError, ValueError):
        return None
    def walk(n):
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return Fraction(str(n.value))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            return walk(n.operand) * (-1 if isinstance(n.op, ast.USub) else 1)
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add): return a+b
            if isinstance(n.op, ast.Sub): return a-b
            if isinstance(n.op, ast.Mult): return a*b
            if isinstance(n.op, ast.Div): return a/b
            if isinstance(n.op, ast.Pow) and abs(b) <= 12: return a**b
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'sqrt' and len(n.args) == 1 and not n.keywords:
            return math.sqrt(walk(n.args[0]))
        raise ValueError('unsupported numeric expression')
    try: return walk(tree.body)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError): return None


def equal(a, b):
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    if isinstance(a, str) and isinstance(b, str):
        norm = lambda x: re.sub(r'\s+', '', x).replace('：', ':').replace('～', '~').replace('＞', '>')
        if norm(a) == norm(b): return True
        aa, bb = numeric(a), numeric(b)
        return aa is not None and bb is not None and equal(aa, bb)
    if isinstance(a, str):
        a = numeric(a)
        if a is None: return False
    if isinstance(b, str):
        b = numeric(b)
        if b is None: return False
    if type(a) is bool or type(b) is bool: return type(a) is type(b) and a == b
    if isinstance(a, Fraction) and isinstance(b, (Fraction, int)): return a == b
    try: return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)
    except (TypeError, ValueError): return a == b


def option_match(value, text):
    if equal(value, text): return True
    s = re.sub(r'\s+', '', str(text)).replace('：', ':').replace('～', '~').replace('∶', ':')
    # Exact same semantic statement, or numeric quantities with units.
    unit = r'(?:立方厘米|平方厘米|平方米|千米/小时|海里/小时|万元|厘米|公斤|公里|千米|分钟|小时|万元|人数|个人|名|元|人|起|棵|天|分|岁|种|排|倍|个|米|件|台|年|吨|袋|箱|盆|页|本)'
    s = re.sub(unit, '', s)
    # Compare computed quantities with explicit numeric/range OPTION CONTENT,
    # never an index copied from the source. Percent endpoints use fractions.
    val = numeric(value) if isinstance(value,str) else value
    token = r'([+-]?\d+(?:\.\d+)?)(%?)'
    def endpoint(number,percent):
        return Fraction(number)/(100 if percent else 1)
    if isinstance(val,(int,float,Fraction)) and type(val) is not bool:
        m=re.fullmatch(r'(?:在)?'+token+r'(?:到|至|~|-|—|–)'+token+r'(?:之间|范围内)?',s)
        if m:
            lo=endpoint(m[1],m[2]);hi=endpoint(m[3],m[4])
            return lo<=val<=hi
        m=re.fullmatch(r'高于'+token+r'但低于'+token,s)
        if m:return endpoint(m[1],m[2])<val<endpoint(m[3],m[4])
        prefixes={'低于':lambda a,b:a<b,'高于':lambda a,b:a>b,
            '不到':lambda a,b:a<b,'超过':lambda a,b:a>b,
            '不高于':lambda a,b:a<=b,'不低于':lambda a,b:a>=b,
            '小于':lambda a,b:a<b,'大于':lambda a,b:a>b,'正好为':lambda a,b:equal(a,b)}
        for prefix,op in prefixes.items():
            m=re.fullmatch(re.escape(prefix)+token,s)
            if m:return op(val,endpoint(m[1],m[2]))
    if s.endswith('%'):
        n = numeric(s[:-1]); return n is not None and equal(value, n/100)
    if s.startswith(('多', '少')):
        n = numeric(s[1:]); return n is not None and equal(value, -n if s[0] == '少' else n)
    if ':' in s and s.count(':') == 1:
        a,b = s.split(':'); aa,bb = numeric(a), numeric(b)
        if aa is not None and bb not in (None,0) and equal(value,aa/bb): return True
    s = s.replace('之间', '').replace('范围内', '').removeprefix('在')
    scale = 10000 if '万' in s else 1
    s = s.replace('万', '')
    val = numeric(value) if isinstance(value,str) else value
    if isinstance(val,(int,float,Fraction)):
        if '~' in s:
            left,right=s.split('~',1); lo,hi=numeric(left),numeric(right)
            if lo is not None and hi is not None: return lo*scale <= val <= hi*scale
        for prefix,op in [('不到',lambda a,b:a<b),('超过',lambda a,b:a>b),('小于',lambda a,b:a<b),('大于',lambda a,b:a>b)]:
            if s.startswith(prefix):
                n=numeric(s[len(prefix):]); return n is not None and op(val,n*scale)
    n=numeric(s)
    return n is not None and equal(value,n*scale)


def semantic_text(text):
    """Asset relocation is not a math change; other effective text changes are."""
    return re.sub(r'\s+','',re.sub(r'!\[[^\]]*\]\([^)]*\)','',text))


class Context:
    def __init__(self, batch, audit_dir, snapshots, compare_reviews=True):
        self.batch=batch; self.audit_dir=Path(audit_dir); self.snapshots=snapshots
        shard=self.audit_dir/(batch+'.json')
        if shard.is_file(): self.inputs=json.loads(shard.read_text('utf-8-sig'))
        else:
            intake=json.loads((self.audit_dir/'intake.json').read_text('utf-8-sig'))
            group=intake['national' if batch.startswith('national') else 'provincial']
            if isinstance(group,dict): group=list(group.values())
            lookup={q['uid']:q for q in group}
            self.inputs=[lookup[s['uid']] for s in snapshots]
        if len(self.inputs)!=len(snapshots): raise AssertionError(f'{batch}: shard/snapshot length changed')
        for i,(q,s) in enumerate(zip(self.inputs,snapshots)):
            if q['uid']!=s['uid'] or fingerprint(q)!=s['inputFingerprint']:
                raise AssertionError(f'{batch}[{i}] problem changed: re-parameterize solver; no stale-answer pass')
        # Prefer submitted content; only repaired/OCR-missing fields use the audited
        # frozen effective snapshot. No answer or source metadata enters problems.
        self.problems=[{'uid':q['uid'],
            's':q['s'] if semantic_text(q['s'])==semantic_text(s['stem']) else s['stem'],
            'o':q['o'] if list(map(semantic_text,q['o']))==list(map(semantic_text,s['options'])) else s['options']}
            for q,s in zip(self.inputs,snapshots)]
        self.reviews=None; self.schema_rows=0; self.cases=[]; self.errors=[]
        path=self.audit_dir/'reviews'/(batch+'.json')
        if compare_reviews and not path.is_file():
            raise AssertionError(f'{batch}: review missing; use --no-review explicitly for computation-only execution')
        if compare_reviews:
            self.reviews=json.loads(path.read_text('utf-8-sig'))
            if len(self.reviews)!=len(self.inputs): raise AssertionError('review coverage length mismatch')
            for q,r,snap in zip(self.inputs,self.reviews,snapshots):
                assert q['uid']==r['uid'], 'review uid/order mismatch'
                assert r['verdict'] in {'verified','disputed','invalid','off_module'}
                # Extra displayImages/inputHash/etc are intentionally accepted.
                assert r.get('answerIndex') is None or (type(r['answerIndex']) is int and 0<=r['answerIndex']<4)
                assert len(r.get('correctedOptions') or q['o'])==4 or r['verdict'] in {'invalid','off_module'}
                effective_stem=r.get('correctedStem') or q['s']
                effective_options=r.get('correctedOptions') or q['o']
                if (semantic_text(effective_stem)!=semantic_text(snap['stem']) or
                    list(map(semantic_text,effective_options))!=list(map(semantic_text,snap['options']))):
                    raise AssertionError(f"{q['uid']}: effective review stem/options changed; update the mathematical model, not just its hash")
                self.schema_rows+=1

    def add(self, i, value=None, *, evidence=None, candidates=None, mode='computation', boundary=None, compare=True, property_only=False, alias_of=None):
        assert i not in {c['index'] for c in self.cases}, (self.batch,i,'duplicate oracle case')
        snap=self.snapshots[i]
        # A case can perform true arithmetic while remaining conditional on a manual diagram/model.
        assumptions=[]
        if snap.get('hasImages'): assumptions.append('manual_image_or_formula_transcription')
        if snap.get('patternAssumption'): assumptions.append('finite_prefix_pattern_assumption_not_uniqueness_proof')
        if boundary: assumptions.append(boundary)
        matches=[]
        if value is not None and not property_only and mode not in {'manual_only','snapshot_only'}:
            if candidates is not None:
                matches=[j for j,c in enumerate(candidates) if equal(value,c)]
            else:
                matches=[j for j,o in enumerate(snap['options']) if option_match(value,o)]
        record=dict(index=i,uid=snap['uid'],mode=mode,computed=serial(value),evidence=serial(evidence),assumptions=assumptions,
                    manualBoundary=snap.get('boundary',''),propertyOnly=property_only and mode not in {'manual_only','snapshot_only'},optionMatches=matches,
                    uniqueOptionMatched=len(matches)==1,reviewAnswerChecked=False)
        if alias_of is not None: record['aliasOf']=alias_of
        if len(matches)>1:
            record['matchingBoundary']='multiple semantic/numeric matches: not claimed as unique option verification'
        if not matches and value is not None and not property_only:
            record['matchingBoundary']='quantity/property computed; semantic option mapping not implemented (not an answer check)'
        if compare and len(matches)==1 and self.reviews is not None:
            expected=self.reviews[i]['answerIndex']; record['reviewAnswerChecked']=True
            if matches[0]!=expected:
                record['reviewMismatch']={'review':expected,'oracle':matches[0]}
                self.errors.append({'uid':snap['uid'],'type':'mathematical_option_mismatch','computed':serial(value),'matches':matches,'reviewAnswerIndex':expected,'reviewVerdict':self.reviews[i]['verdict']})
        self.cases.append(record)
        return record

    def finish(self):
        modes={m:sum(c['mode']==m for c in self.cases) for m in sorted({c['mode'] for c in self.cases})}
        computed=[c for c in self.cases if c['mode'] not in {'manual_only','snapshot_only','alias_reuse'}]
        return dict(batch=self.batch,inputRows=len(self.inputs),schemaRows=self.schema_rows,caseRows=len(self.cases),
            computationRows=len(computed),aliasReuseRows=modes.get('alias_reuse',0),manualOnlyRows=modes.get('manual_only',0)+modes.get('snapshot_only',0),
            conditionalComputationRows=sum(bool(c['assumptions']) for c in computed),propertyOnlyRows=sum(c['propertyOnly'] for c in computed),
            aliasPropertyRows=sum(c['propertyOnly'] for c in self.cases if c['mode']=='alias_reuse'),
            manualImageComputationRows=sum('manual_image_or_formula_transcription' in c['assumptions'] for c in computed),
            patternAssumptionRows=sum('finite_prefix_pattern_assumption_not_uniqueness_proof' in c['assumptions'] for c in computed),
            freshReviewAnswersChecked=sum(c['reviewAnswerChecked'] for c in computed),
            uniqueOptionMatches=sum(c['uniqueOptionMatched'] for c in self.cases),reviewAnswersChecked=sum(c['reviewAnswerChecked'] for c in self.cases),
            uncoveredRows=len(self.inputs)-len(self.cases),uncoveredUids=[q['uid'] for i,q in enumerate(self.inputs) if i not in {c['index'] for c in self.cases}],
            modeCounts=modes,errors=self.errors,cases=sorted(self.cases,key=lambda c:c['index']))
