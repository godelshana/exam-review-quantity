"""Offline, fail-closed quantity datasets. Only writes datasets/.

python 教学/速刷/build_datasets.py --import-local  # explicit snapshot refresh
python 教学/速刷/build_datasets.py                 # snapshots only; no raw repo needed
python 教学/速刷/build_datasets.py --check         # read-only deterministic check
"""
from __future__ import annotations
import argparse
import ast
import copy
import hashlib
import itertools
import json
import math
from functools import lru_cache
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'datasets'
ROOT = HERE.parent.parent
VERSION = '2026-09-11.v1'
YEARS = (2024, 2025, 2026)
PAPERS = {'副省': '副省级', '地市': '地市级', '执法': '行政执法类', '合卷': '合卷'}


def dumps(x):
    return json.dumps(x, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def digest(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def write(p, text):
    # No implicit directories outside the explicitly permitted output folder.
    if p.parent.resolve() != DATA.resolve():
        raise ValueError('output outside datasets')
    with p.open('w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def source_hash(q):
    return digest({k: q.get(k) for k in ('uid','year','exam','paper','number','moduleIndex',
                                       's','o','sourceAnswer','source','sourceQuestionUid',
                                       'sourceYear','originYear','sourceLabel')})


def import_local():
    """Copy ONLY structured quantity questions and minimal provenance, never PDFs."""
    base = ROOT / '真题库/按模块/01_数量关系'
    qt = (base / '题目汇编.md').read_text(encoding='utf-8')
    xt = (base / '答案与解析.md').read_text(encoding='utf-8')
    explanations = {}
    xp = r'^\*\*(\d{4})·([^·]+)·(\d+)（答案：([^）]+)）\*\*\n([\s\S]*?)(?=^\*\*\d{4}·|^## |\Z)'
    for m in re.finditer(xp, xt, re.M):
        explanations[(int(m[1]), m[2], int(m[3]))] = (m[4], m[5].strip())
    fb = read_json(ROOT / '_downloads/fenbi_answers.json')
    ai = read_json(ROOT / '_downloads/ai_answers.json')
    prior = read_json(ROOT / '教学/审查/2011-2023数量关系逐题审查清单.json')
    prior_map = {r['id']: {'review': r['review'], 'auditNotes': r['auditNotes'],
                          'kind': 'reused_structure_only_not_math'} for r in prior['items']}
    records = []
    pat = r'^\*\*(\d+)\.\*\* ([\s\S]*?)`\[(\d{4})·([^·]+)·(\d+)\]`\s*\n([\s\S]*?)(?=^\*\*\d+\.\*\*|^## |\Z)'
    counts = Counter()
    for m in re.finditer(pat, qt, re.M):
        year, paper, number = int(m[3]), PAPERS[m[4]], int(m[5])
        key = (year, m[4], number)
        ans, explanation = explanations.get(key, ('待核', ''))
        options = re.findall(r'^- [A-D]\.\s*(.*)$', m[6], re.M)
        aligned = fb.get(f'{year}|{paper}', {}).get(str(number))
        if year >= 2023:
            ans = aligned['ans'] if aligned and aligned.get('mapped') else '待核'
        counts[(year, paper)] += 1
        r = dict(uid=f'real:{year}:{paper}:{number}', year=year, exam='国考',
                 paper=paper, number=number, moduleIndex=counts[(year, paper)],
                 s=m[2].strip(), o=options, sourceAnswer=ans,
                 sourceExplanation=explanation,
                 source={'path': '真题库/按模块/01_数量关系/题目汇编.md',
                         'locator': f'{year}·{m[4]}·{number}',
                         'answerAuthority': '高教逐题解析' if year <= 2022 else '粉笔内容对齐答案（非官方公布答案）',
                         'alignedAnswer': aligned,
                         'aiAnswer': ai.get(f'{year}|{paper}|数量关系', {}).get(str(number)),
                         'priorStructuralReview': prior_map.get(f'{year}-{m[4]}-{number}'),
                         'imageReferences': re.findall(r'!\[[^\]]*\]\(([^)]+)\)', m[2]+m[6]),
                         'imagePolicy': '本数据快照未带图；依赖图片的一律不计分'})
        records.append(r)
    if len(records) != 400 or sum(q['year'] in YEARS for q in records) != 105:
        raise ValueError('unexpected local coverage: review parser/input before importing')
    glm_prior = read_json(HERE / '精选GLM题库审计.json')
    # Keep the prior audit as evidence of structural review, not a math certificate.
    gp = {r['id']: r for r in glm_prior['records']}
    glm = []
    for letter in 'ABCDE':
        filename = f'gen_{letter}_output.json'
        for i, q in enumerate(read_json(HERE / 'gen' / filename)):
            oldid = f'glm:{letter}:{i}'
            matching = [r for r in gp.values() if r.get('source', {}).get('file') == filename
                        and r.get('source', {}).get('index0') == i]
            glm.append(dict(uid=oldid, year=None, exam='GLM模拟', paper=letter,
                            number=i, moduleIndex=i+1, s=q['s'], o=[str(x) for x in q['o']],
                            sourceAnswer='ABCD'[q['a']] if q['a'] in range(4) else '待核',
                            sourceExplanation=q.get('e', ''), original=q,
                            source={'path': f'教学/速刷/gen/{filename}', 'index': i,
                                    'answerAuthority': 'GLM生成答案，非可信参考答案',
                                    'normalization': '选项数字仅转为等值字符串，原类型保留在original；不修题面/答案',
                                    'priorStructuralReview': ({'id':matching[0]['id'], 'assessment':matching[0]['assessment'], 'familyId':matching[0]['familyId']} if matching else None),
                                    'priorReviewKind': 'structure_only_not_independent_math',
                                    'imageReferences': []}))
    if len(glm) != 545:
        raise ValueError('GLM coverage changed')
    paths = [base/'题目汇编.md', base/'答案与解析.md', ROOT/'_downloads/fenbi_answers.json',
             ROOT/'_downloads/ai_answers.json'] + [HERE/'gen'/f'gen_{c}_output.json' for c in 'ABCDE']
    source_manifest = [{'path': p.relative_to(ROOT).as_posix(),
                        'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    authored = []
    for name in ('手写模拟题_100.js', '原创复合24.js'):
        text = (HERE/name).read_text(encoding='utf-8')
        qs = json.JSONDecoder().raw_decode(text[text.index('=')+1:].lstrip())[0]
        authored.extend({k:q.get(k) for k in ('uid','s','h','familyId')} for q in qs)
    if len(authored)!=124: raise ValueError('authored inventory changed')
    snapshot = {'schemaVersion': 1, 'authoredScreeningInputs': authored, 'sourceFiles': source_manifest,
                'policy': {'validationYears': list(YEARS),
                           'supersedes': '旧审查2021—2023保留验证结论已过时，禁止继承',
                           'independentAuditScope': '仅certificates.json中绑定原题且复算通过者'},
                'guangdong': [{'exam': '广东省考', 'year': y, 'expectedSlots': None,
                               'availableQuestions': 0, 'status': 'missing_source',
                               'validationStatus': 'V3',
                               'reason': '本地真题库无广东题面、卷别目录或可靠答案；题量未知，不能生成虚构槽位',
                               'searchedRoots': ['真题库', '教学/速刷/gen'],
                               'required': ['真实试卷及卷别清单', '数量关系逐题题面与选项', '可靠答案及原图']}
                              for y in YEARS],
                'real': records, 'glm': glm}
    write(DATA/'sources.json', dumps(snapshot))


# Small exact-arithmetic language: no eval, attributes, subscripts or executable input.
@lru_cache(maxsize=10000)
def expression_tree(expr):
    return ast.parse(expr,mode='eval')


def calc(expr, env=None):
    env = env or {}
    def visit(n):
        if isinstance(n, ast.Expression): return visit(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, bool): return F(n.value)
        if isinstance(n, ast.Name) and n.id in env: return F(env[n.id])
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -visit(n.operand) if isinstance(n.op, ast.USub) else visit(n.operand)
        if isinstance(n, ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            ops={ast.Add:lambda:a+b, ast.Sub:lambda:a-b, ast.Mult:lambda:a*b,
                 ast.Div:lambda:a/b, ast.FloorDiv:lambda:F(a//b), ast.Mod:lambda:a%b,
                 ast.Pow:lambda:a**int(b) if b.denominator==1 and abs(b)<=20 else fail('unsafe power')}
            if type(n.op) in ops:return ops[type(n.op)]()
        if isinstance(n, ast.Compare):
            vals=[visit(n.left)]+[visit(x) for x in n.comparators]
            ops={ast.Eq:lambda a,b:a==b, ast.NotEq:lambda a,b:a!=b,
                 ast.Lt:lambda a,b:a<b, ast.LtE:lambda a,b:a<=b,
                 ast.Gt:lambda a,b:a>b, ast.GtE:lambda a,b:a>=b}
            return all(ops[type(op)](vals[i],vals[i+1]) for i,op in enumerate(n.ops))
        if isinstance(n, ast.BoolOp) and isinstance(n.op,(ast.And,ast.Or)):
            v=[bool(visit(x)) for x in n.values]
            return all(v) if isinstance(n.op,ast.And) else any(v)
        if isinstance(n, ast.Call) and isinstance(n.func,ast.Name) and not n.keywords:
            args=[visit(x) for x in n.args]
            if n.func.id=='C' and len(args)==2:
                if any(x.denominator!=1 or x<0 or x>10000 for x in args):raise ValueError('invalid combination arguments')
                return F(math.comb(*[int(x) for x in args]))
            if n.func.id=='ceil' and len(args)==1:return F(math.ceil(args[0]))
            if n.func.id=='floor' and len(args)==1:return F(math.floor(args[0]))
            if n.func.id=='min':return min(args)
            if n.func.id=='max':return max(args)
        raise ValueError(f'forbidden expression: {expr}')
    return visit(expression_tree(expr))


def fail(message): raise ValueError(message)


def exact_options(q, c):
    # A question-specific text-to-value mapping is explicit for units/ratios/ranges.
    # It must match each full option string; no inferred answer letter is accepted.
    if 'optionMap' in c:
        if list(c['optionMap']) != q['o']:
            # JSON sort order is not option order; use exact set keys instead.
            if set(c['optionMap']) != set(q['o']): raise ValueError('option map mismatch')
        return [calc(c['optionMap'][x]) for x in q['o']]
    values=[]
    for text in q['o']:
        text=text.strip()
        if text.endswith('%'): values.append(F(text[:-1])/100)
        else:
            try: values.append(F(text))
            except ValueError: values.append(calc(text))
    return values


def solve(q, c):
    if c['sourceHash'] != source_hash(q):raise ValueError(f"stale math certificate: {q['uid']}")
    fast = calc(c['fast'])
    normal = c['normal']
    witness = []
    if 'expression' in normal:
        slow = calc(normal['expression'])
        checks = {x: bool(calc(x, {'answer': slow})) for x in normal['checks']}
        if not checks or not all(checks.values()):raise ValueError('normal invariant failed')
        witness = checks
    else:
        domains = normal['domains']
        size = math.prod(hi-lo+1 for lo,hi in domains.values())
        if size>2000000:raise ValueError('unbounded audit search')
        names = list(domains)
        solutions=[]
        for values in itertools.product(*(range(a,b+1) for a,b in domains.values())):
            env=dict(zip(names,values))
            if all(calc(x,env) for x in normal['where']):
                solutions.append(calc(normal['value'],env))
                if len(witness)<12:witness.append(env)
        if not solutions:raise ValueError('no feasible solution')
        mode=normal.get('aggregate','unique')
        if mode=='unique':
            if len(set(solutions))!=1:raise ValueError('nonunique computed result')
            slow=solutions[0]
        elif mode=='min':slow=min(solutions)
        elif mode=='max':slow=max(solutions)
        elif mode=='count':slow=F(len(solutions))
        else:raise ValueError('invalid aggregate')
    vals = exact_options(q,c)
    if len(vals)!=4 or len(set(vals))!=4:raise ValueError('duplicate/missing options')
    matches=[i for i,v in enumerate(vals) if v==fast]
    if fast!=slow or len(matches)!=1:raise ValueError('two-path or unique-option failure')
    return {'status':'passed', 'kind':'source-independent-exact-recalculation',
            'reviewerIndependence':'同一作者从题干重建两路径；不是第二审查者的独立审计',
            'sourceHash':c['sourceHash'], 'certificateHash':digest(c),
            'fastResult':str(fast),'normalResult':str(slow),
            'matchedOption':matches[0], 'optionValues':[str(v) for v in vals],
            'witness':witness,'fastExpression':c['fast'],'normalModel':normal,
            'boundsJustification':c.get('boundsJustification','闭式计算后回代题干约束，无搜索截断'),
            'sourceAgreement':q['sourceAnswer']=='ABCD'[matches[0]]}


@lru_cache(maxsize=10000)
def normalize(s, numbers=False):
    s=re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)
    s=re.sub(r'\s+|[，。；：？！、,.;:?!（）()\[\]`]', '', s)
    if numbers:s=re.sub(r'\d+(?:\.\d+)?', '#', s)
    return s


def structural_tags(s):
    """Specific relationship systems, NOT blanket topic labels like 'geometry'."""
    tags=[]
    if all(t in s for t in ['乙','丙','丁','并入']):tags.append('four_departments_partial_transfer_merge')
    if all(t in s for t in ['答对','答错']) and re.search(r'大于0|不低于1',s):
        tags.append('unit_random_walk_strictly_positive_prefix')
    if all(t in s for t in ['圆锥','圆柱','分钟']) and re.search(r'液面|水深|注水',s):
        tags.append('inverted_cone_cylinder_constant_flow')
    if '课程' in s and re.search(r'连续|连学',s) and '不相邻' in s:
        tags.append('two_course_blocks_nonadjacent_rest')
    if all(t in s for t in ['甲车间','乙车间','生产','A','B','每天']):
        tags.append('two_workshops_two_components_allocation')
    if re.search(r'前3|前三|一季度',s) and re.search(r'前6|上半年|接下来三',s) and re.search(r'等差|每个月.*比上个月',s):
        tags.append('arithmetic_monthly_partial_sums_forecast')
    return tags


def leakage_check(q, validation):
    hits=[]
    closest={'uid':None,'similarity':0}
    tags=set(structural_tags(q['s']))
    for v in validation:
        if not v.get('s'):continue
        reason=[];risk='low'
        if normalize(q['s'])==normalize(v['s']):reason.append('exact_stem');risk='high'
        score=SequenceMatcher(None,normalize(q['s'],True),normalize(v['s'],True),autojunk=False).ratio()
        if score>closest['similarity']:closest={'uid':v['uid'],'similarity':round(score,4)}
        if score>=0.72:reason.append('number_normalized_near_duplicate');risk='high'
        elif score>=0.52 and risk!='high':reason.append('near_template_requires_manual_review');risk='medium'
        common=tags & set(structural_tags(v['s']))
        if common:reason+=['same_relationship_system:'+x for x in sorted(common)];risk='high'
        if q['familyId']==v['familyId'] and not q['familyId'].startswith('unclassified:'):
            reason.append('same_specific_family');risk='high'
        # Score-rank extremization under a total/mean constraint is related but the
        # held-out question constrains only the >=90 subset: not an exact clone.
        if re.search(r'最低.*(?:排|名)|名次最低|排名最低',q['s']) and re.search(r'名次|排名',v['s']) and '互不相同' in v['s']:
            if risk=='low':risk='medium'
            reason.append('related_rank_extremum_different_mean_scope')
        if reason:hits.append({'uid':v['uid'],'risk':risk,'reasons':reason,'similarity':round(score,4)})
    risk='high' if any(x['risk']=='high' for x in hits) else ('medium' if hits else 'low')
    return {'risk':risk,'matches':hits,'closestMatch':closest,
            'templateFingerprint':digest(normalize(q['s'],True)),
            'structuralTags':sorted(tags),'thresholds':{'high':0.72,'medium':0.52},
            'checkedAgainst':'全部已收录2024—2026国考105槽位，含V3可读题干',
            'externalCoverage':'风险仅针对本地题面；广东缺资料，未知范围不承诺零风险',
            'semanticLimit':'全文数字归一化+明确关系系统标签；非完整语义同构证明'}


def family_for(q, certs):
    if q['uid'] in certs:return certs[q['uid']]['familyId']
    s=q['s']
    # Validation family guards apply even when the source cannot be scored.
    guards=[('profit.discount_equal_daily', ['降价','利润','相同']),
            ('travel.equal_distance_harmonic', ['往返','平均速度']),
            ('work.two_rates_percent', ['效率','提升','车间']),
            ('probability.two_named_choose_three', ['随机选3人','30倍']),
            ('sets.two_set_surplus', ['两个项目','都不']),
            ('allocation.majority_seven_two_fixed', ['7人','老张','小王']),
            ('calendar.two_month_fixed_days', ['接访群众','9月']),
            ('geometry.cone_cylinder_equal_base_height', ['圆柱','圆锥','底','高'])]
    for family,terms in guards:
        if all(t in s for t in terms):return family
    return 'unclassified:'+digest(normalize(s,True))[:16]


def is_reserved(q):
    if any(str(q.get(k)) in {'2024','2025','2026'} for k in ('year','sourceYear','originYear')):return True
    origin=' '.join(str(q.get(k,'')) for k in ('uid','sourceQuestionUid','sourceLabel'))
    origin+=' '+str(q.get('source',{}).get('locator',''))
    return bool(re.search(r'(?<![0-9])202[456](?![0-9])',origin))


def make_record(q, certs):
    r={k:copy.deepcopy(q[k]) for k in ('uid','year','exam','paper','number','moduleIndex','s','o')}
    validation=is_reserved(q)
    r.update(sourceType='glm' if q['exam']=='GLM模拟' else 'real', dataset='validation' if validation else 'train', a=None,
             h='待审',t='待审',e='',tr='',level=None,source=q['source'],
             sourceAnswer=q['sourceAnswer'],sourceExplanation=q['sourceExplanation'],
             answerStatus='unknown',imageStatus='complete',explanationStatus='P0',
             validationStatus='V3' if validation else 'not_applicable',
             fastMethod='none',fastValue='low',skipDecision='skip',
             familyId=family_for(q,certs),leakageRisk='medium',
             fastPath='未完成逐题数学复算，不提供未经证明的快法。',
             normalPath='请核对原题与可靠解析；本题不进入自动计分。',
             fastBoundary='未通过复算/资料不全时不能据此计分。',
             mathAudit={'status':'not_attempted','kind':'structure_only_not_math'},
             admission='quarantine',quarantineReasons=[],scorable=False,usable=False)
    if validation and r['s']:
        r['sourceQuestionUid']='heldout:'+str(r['year'])+':text:'+digest(normalize(r['s']))[:20]
    reasons=r['quarantineReasons']
    if not r['s']:reasons.append('missing_stem')
    if len(r['o'])!=4 or any(not x.strip() for x in r['o']):reasons.append('missing_options')
    if len(set(normalize(x) for x in r['o']))!=len(r['o']):reasons.append('duplicate_options')
    if re.search(r'如下图|如图|下图|如下表|下表|所需时间如下|原图|!\[',r['s']):
        r['imageStatus']='missing';reasons.append('required_image_or_table_not_bundled')
    elif q['source'].get('imageReferences'):
        r['imageStatus']='uncertain';reasons.append('source_visual_reference_not_reviewed')
    if any('国家公务员录用考试' in x or '估分' in x for x in r['o']):reasons.append('option_footer_contamination')
    prior_ai=q['source'].get('aiAnswer')
    if prior_ai and ('矛盾' in prior_ai or prior_ai.startswith('?')):
        reasons.append('prior_ai_unresolved_flag:'+prior_ai)
    if re.search(r'为的|量的[，。]|浓度为[，。]|售价为的',r['s']):
        reasons.append('suspected_missing_formula')
    if '国家公务员录用考试' in r['s'] or '估分' in r['s']:
        reasons.append('stem_footer_contamination')
    source_answer=q['sourceAnswer']
    if source_answer in ('A','B','C','D'):r['answerStatus']='source_only'
    else:reasons.append('unconfirmed_source_answer')
    # Explicitly preserve known competing views, even if generated source files hide the marker.
    if ((q['year']==2026 and '7人' in q['s'] and '分组' in q['s'])
        or (q['year']==2023 and q['paper']=='副省级' and q['number']==63)
        or (q['year']==2025 and q['paper']=='地市级' and q['number']==66)):
        r['answerStatus']='disputed';reasons.append('known_source_dispute')
    if prior_ai in ('A','B','C','D') and source_answer in ('A','B','C','D') and prior_ai!=source_answer:
        r['answerStatus']='disputed';reasons.append('fenbi_ai_answer_conflict')
    if q['uid']=='glm:D:30' and '切成125等份' in q['s']:
        reasons.append('nonunique_equal_volume_partition')
        r['answerStatus']='unknown'
        r['mathAudit']={'status':'failed','kind':'condition_completeness_counterexample',
                        'sourceHash':source_hash(q),
                        'counterexamples':[
                            {'partition':'5×5×5全等小正方体','pieces':5**3,
                             'pieceVolume':str(F(5)**3/125),'unpainted':(5-2)**3},
                            {'partition':'沿一方向切125片，每片5×5×(5/125)',
                             'pieces':125,'pieceVolume':str(F(5)*5*F(5,125)),
                             'unpainted':0}],
                        'reason':'两种分割均为125等份但无涂色块分别27和0；题干未限定全等小正方体，不唯一。',
                        'reviewBasis':'独立复审指出条件缺失，生成器复核等体积反例；不补写源题条件。'}
        r['normalPath']=r['mathAudit']['reason']
    c=certs.get(q['uid'])
    if c and r['mathAudit']['status']=='failed':
        raise ValueError('known incomplete source must not have a passing certificate: '+q['uid'])
    if c:
        try: audit=solve(q,c)
        except ValueError as err: raise ValueError(f"{q['uid']}: {err}") from err
        # Changed certificate or arithmetic error is a BUILD ERROR, never silent downgrade.
        r['mathAudit']=audit
        r.update({k:c[k] for k in ('h','t','tr','level','fastMethod','fastValue','skipDecision',
                                  'fastPath','normalPath','fastBoundary')})
        # knowledge/elimination 是题解升级新增字段；旧证书没有时不得阻断构建。
        for k in ('knowledge','elimination'):
            if isinstance(c.get(k),str) and c[k].strip(): r[k]=c[k]
        r['e']=c['fastPath']
        r['explanationStatus']='P2'
        if not audit['sourceAgreement']:
            if q['exam']=='GLM模拟':reasons.append('glm_generated_answer_mismatch')
            else:
                r['answerStatus']='disputed';reasons.append('independent_source_disagreement')
        elif r['answerStatus']!='disputed':r['answerStatus']='confirmed'
        if not reasons:
            r.update(a=audit['matchedOption'],admission='accepted',usable=True,scorable=True)
            if validation:r['validationStatus']='V1'
    else:
        reasons.append('no_independent_math_certificate')
        if validation and not any(x!='no_independent_math_certificate' for x in reasons):
            r['validationStatus']='V3'
            r['normalPath']='题面与来源答案可读，但未独立复算；当前V3不可练，只供人工核对。'
    if r['answerStatus']=='disputed':
        r['validationStatus']='V3' if validation else 'not_applicable'
        r['disputeViews']={'sourceAnswer':source_answer,'priorAiAnswer':prior_ai,
                           'independentAnswerIndex':r['mathAudit'].get('matchedOption'),
                           'independentAnswerLetter':('ABCD'[r['mathAudit']['matchedOption']] if c else None),
                           'independentReasoning':r['normalPath'] if c else '未独立复算，不补写另一方推理',
                           'sourceReasoning':q['sourceExplanation'] or '来源未给推理，不编造解释',
                           'action':'在粉笔APP历年试卷或华图在线核对原题、选项和完整解析'}
    return r


def assemble(snapshot, certs):
    raw=snapshot['real']+snapshot['glm']
    if len({q['uid'] for q in raw})!=len(raw):raise ValueError('duplicate source uid')
    unknown=set(certs)-{q['uid'] for q in raw}
    if unknown:raise ValueError(f'orphan certificates: {unknown}')
    records=[make_record(q,certs) for q in raw]
    val=[r for r in records if r['dataset']=='validation']
    expected={(y,p,i) for y in YEARS for p,n in [('副省级',15),('地市级',10),('行政执法类',10)] for i in range(1,n+1)}
    seen={(r['year'],r['paper'],r['moduleIndex']) for r in val if r['exam']=='国考'}
    if seen-expected:raise ValueError('unexpected validation slot')
    # Missing known national slots are real omissions, not invented question text/answers.
    for y,p,i in sorted(expected-seen):
        number=(61 if y==2024 else 66)+i-1
        q=dict(uid=f'real:{y}:{p}:{number}',year=y,exam='国考',paper=p,number=number,
               moduleIndex=i,s='',o=[],sourceAnswer='待核',sourceExplanation='',
               source={'path':None,'missing':True,'imageReferences':[]})
        r=make_record(q,certs);r['quarantineReasons'].append('missing_validation_slot')
        records.append(r);val.append(r)
    val.sort(key=lambda r:(r['year'],list(PAPERS.values()).index(r['paper']),r['moduleIndex']))
    for r in records:
        if r['dataset']=='train':
            check=leakage_check(r,val)
            r['leakageCheck']=check;r['leakageRisk']=check['risk']
            if check['matches']:
                r['leakageMatches']=[hit['uid'] for hit in check['matches']]
                r['quarantineReasons'].append('validation_family_or_text_leakage')
                r.update(admission='quarantine',usable=False,scorable=False,a=None)
        else:
            r['leakageRisk']='high'
            r['leakageCheck']={'risk':'high','reason':'strictly_reserved_validation_never_train',
                               'matches':[]}
    # One representative per exact/family group among candidate train items.
    representatives={}
    for r in records:
        if r['dataset']=='train' and r['usable']:
            group=r['familyId']
            if group in representatives:
                r['quarantineReasons'].append('duplicate_training_family')
                r['representativeUid']=representatives[group]
                r.update(admission='quarantine',usable=False,scorable=False,a=None)
            else:representatives[group]=r['uid']
    train=[r for r in records if r['dataset']=='train' and r['usable']]
    quarantine=[r for r in records if r['dataset']=='train' and not r['usable']]
    screening=[];authored_overrides={}
    for q in snapshot.get('authoredScreeningInputs',[])+snapshot['glm']:
        item=dict(q);item['familyId']=family_for(item,certs)
        check=leakage_check(item,val)
        row={'uid':q['uid'],'sourceType':'mock' if q['uid'].startswith(('hand100:','challenge:')) else 'glm',
             'stemSha256':digest(q['s']),'familyId':item['familyId'],'leakageRisk':check['risk'],
             'leakageCheck':check,'auditKind':'structural_template_screen_not_independent_math',
             'decision':'keep_existing_math_gate' if check['risk']=='low' else 'quarantine_from_ordinary_training'}
        screening.append(row)
        if row['sourceType']=='mock':
            override={'leakageRisk':check['risk'],'leakageCheck':check}
            if check['risk']!='low':
                override.update(admission='quarantine',usable=False,scorable=False,
                                quarantineReasons=['reserved_validation_template_risk'])
            authored_overrides[q['uid']]=override
    summary={'version':VERSION,'validationYears':list(YEARS),
             'realSourceQuestions':len(snapshot['real']), 'oldRealAuditedInventory':sum(q['year']<=2023 for q in snapshot['real']),
             'glmInventory':len(snapshot['glm']),
             'templateScreening':{'authored':dict(Counter(r['leakageRisk'] for r in screening if r['sourceType']=='mock')),
                                  'glm':dict(Counter(r['leakageRisk'] for r in screening if r['sourceType']=='glm')),
                                  'total':len(screening),'independentMathClaim':False},
             'train':{'total':len(train),'byExam':dict(Counter(r['exam'] for r in train)),
                      'byYear':dict(Counter(str(r['year']) for r in train)),
                      'byLevel':dict(Counter(r['level'] for r in train))},
             'validation':{'expectedNationalSlots':105,'inventorySlots':len(val),
                           'withStem':sum(bool(r['s']) for r in val),
                           'byStatus':dict(Counter(r['validationStatus'] for r in val)),
                           'scorable':sum(r['scorable'] for r in val),
                           'uniqueScorableIdentities':len({r.get('sourceQuestionUid',r['uid']) for r in val if r['scorable']}),
                           'completeScorable':all(r['scorable'] for r in val),
                           'guangdongComplete':False},
             'math':{'attempted':sum(r['mathAudit']['status']!='not_attempted' for r in records),
                     'failed':[r['uid'] for r in records if r['mathAudit']['status']=='failed'],'passedCalculation':sum(r['mathAudit']['status']=='passed' for r in records),
                     'sourceDisagreements':[r['uid'] for r in records if r['mathAudit'].get('sourceAgreement') is False],
                     'notAttempted':sum(r['mathAudit']['status']=='not_attempted' for r in records)},
             'quarantine':{'trainCount':len(quarantine),
                           'byExam':dict(Counter(r['exam'] for r in quarantine)),
                           'reasonCounts':dict(Counter(x for r in records for x in r['quarantineReasons']))},
             'limitations':['独立指从题干复算、不以来源答案为计算输入；非独立第二审查者。',
                            '未复算条目只做逐题结构审查，绝不冒称数学通过。',
                            'V2单列暂定成绩、不进入正式验证指标；未满足usable/资格门禁不练；V3不计分。',
                            '难度与快法时间收益是教学判断，不是考生群体实测。',
                            '广东近三年缺资料，无法证明对未知题零泄漏；low只表示已收录范围未命中，不是对缺失广东题的保证。',
                            '不包含主代理包装的原创124题。']}
    manifest={'version':VERSION,'sourceSnapshotSha256':digest(snapshot),'certificatesSha256':digest(certs),
              'builderSha256':hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
              'validationPolicy':{'years':list(YEARS),'exams':['国考','广东省考'],
                                  'forbidTrain':True,'guangdongExpectedSlots':None},
              'guangdongGaps':snapshot['guangdong'],
              'nationalSlots':[dict(uid=r['uid'],year=r['year'],paper=r['paper'],moduleIndex=r['moduleIndex'],
                                    validationStatus=r['validationStatus'],scorable=r['scorable'],
                                    sourcePresent=bool(r['s']),reasons=r['quarantineReasons']) for r in val],
              'summary':summary}
    return train,val,quarantine,records,summary,manifest,screening,authored_overrides


def outputs(snapshot,certs):
    train,val,quarantine,records,summary,manifest,screening,authored_overrides=assemble(snapshot,certs)
    banks='// Generated offline by build_datasets.py; do not edit.\n'
    for name,data in [('DATASET_TRAIN',train),('DATASET_VALIDATION',val),('DATASET_AUDIT_SUMMARY',summary)]:
        banks+='window.'+name+' = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n'
    return {'banks.js':banks,'manifest.json':dumps(manifest),'audit.json':dumps(records),
            'quarantine.json':dumps(quarantine),'summary.json':dumps(summary),
            'template_screening.json':dumps(screening),
            'authored_policy.json':dumps({'version':VERSION,'auditKind':'structural_screen_only','overrides':authored_overrides}),
            'authored_policy.js':'// Apply by uid AFTER original metadata; no original question bank here.\nwindow.DATASET_AUTHORED_OVERRIDES = '+json.dumps(authored_overrides,ensure_ascii=False,separators=(',',':'))+';\n'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-local',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.check and args.import_local:parser.error('--check is read-only; cannot import')
    if args.import_local:
        import_local();print('Imported 400 real + 545 GLM structured questions.');return
    artifacts=outputs(read_json(DATA/'sources.json'),read_json(DATA/'certificates.json'))
    for name,text in artifacts.items():
        path=DATA/name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8')!=text:raise SystemExit(f'STALE: {name}')
        else:write(path,text)
    print(artifacts['summary.json'])


if __name__=='__main__':main()
