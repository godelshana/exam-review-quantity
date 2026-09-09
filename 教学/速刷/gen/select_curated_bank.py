# -*- coding: utf-8 -*-
"""Deterministic, non-destructive GLM selection; NOT a mathematical certification.

python 教学/速刷/gen/select_curated_bank.py
python 教学/速刷/gen/select_curated_bank.py --check
python 教学/速刷/gen/select_curated_bank.py --self-test
Only writes 精选GLM题库.js / 精选GLM题库审计.json / 精选GLM题库筛选报告.md.
Uses only Python's standard library. Never executes the source generators.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
VERSION = '2026-09-09-v3'
CORE = ('h', 't', 's', 'o', 'a', 'e', 'tr')
POLICY = {
    'version': VERSION,
    'skip': 'All t=跳过 or a=-1 records are isolated, irrespective of their explanation.',
    'grades': {
        'A': '独立数学复核与教学审阅均完成。本轮不授予任何题 A 级。',
        'B+': '初筛可用：解析同时有方法/关系和具体代入或运算痕迹；非数学认证。',
        'B': '基础候选：解析有可执行公式或关系，但具体示范较弱；非数学认证。',
        'C': '待改进：解析、情境一致性或干扰项存在明确质量风险，暂不精选。',
        'D': '隔离：跳过卡、硬性结构问题、条件不足或误导性教学结论。',
    },
    'quota': {'default': 1},
    'hook_cap': 12,
    'quality_label': '规则筛选待逐题数审',
    'B_only_family_cap': 1,
    'grouping': '完整归一化题干相同，或完整归一化解析相同，跨标签连通归组。后者是教学方法近似组，不声称逻辑严格同构。',
    'normalization': '去空白、NFKC、阿拉伯数值替换；不截断题干，不抹去甲乙关系、运算符或问题所求。',
    'ranking': '先 B+ 后 B，警告较少优先；其后偏好不同的选项间距/数字形态，最后按来源和原下标稳定排序。',
    'option_policy': '检测互异与数值等价、空值、概率域无效干扰项；记录相邻相对间距。间距过大/小只提示，不单独淘汰。干扰项错误路径尚未人工映射。',
    'math_audit': 'not_performed: neither source checker nor schema success proves statement/answer correctness',
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def text(s) -> str:
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(s)))


def signature(s) -> str:
    return re.sub(r'\d+(?:\.\d+)?', '{数}', text(s))


def option_string(v) -> str:
    # Match existing merge.py's lossless display conversion.
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


def number(s):
    """Parse only exact rational literals (no eval, no guessed units/radicals)."""
    s = text(s).replace('−', '-').replace('⁄', '/')
    percent = s.endswith('%')
    s = s[:-1] if percent else s
    if not re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:/[+-]?\d+(?:\.\d+)?)?', s):
        return None
    try:
        parts = s.split('/')
        v = Fraction(parts[0])
        if len(parts) == 2:
            v /= Fraction(parts[1])
        return v / 100 if percent else v
    except (ValueError, ZeroDivisionError):
        return None


def option_metrics(q):
    opts = q.get('o', [])
    vals = [number(option_string(v)) for v in opts]
    known = [v for v in vals if v is not None]
    metric = {
        'numericParsed': len(known),
        'equivalentDuplicate': len(known) != len(set(known)),
        'normalizedNumericValues': [str(v) if v is not None else None for v in vals],
        'nearestRelativeGap': None, 'gapBand': 'not_measured',
        'distractorErrorPathAudit': 'not_performed',
    }
    if len(known) == 4 and len(set(known)) == 4:
        values = sorted(known)
        gap = min(b-a for a, b in zip(values, values[1:]))
        scale = max(abs(values[0]), abs(values[-1]), Fraction(1, 1000000))
        metric['nearestRelativeGap'] = float(gap / scale)
        metric['gapBand'] = 'tight' if gap/scale < Fraction(1, 100) else ('wide' if gap/scale > Fraction(1, 5) else 'middle')
    return metric


def assess(q):
    """Observable screening, deliberately not an answer solver."""
    issues = []
    def add(code, severity, evidence):
        issues.append({'code': code, 'severity': severity, 'evidence': evidence})

    if q.get('t') == '跳过' or q.get('a') == -1:
        add('SKIP_ISOLATION', 'isolate', '策略动作不能代替数学答案；30张原始跳过卡全部隔离，待重写后另审。')
    missing = [k for k in CORE if k not in q]
    if missing:
        add('SCHEMA', 'isolate', '缺字段: '+','.join(missing))
    for k in ('h', 't', 's', 'e'):
        if not isinstance(q.get(k), str) or not q.get(k, '').strip():
            add('SCHEMA', 'isolate', k+' 非非空字符串')
    a = q.get('a')
    if type(a) is not int or not -1 <= a <= 3:
        add('SCHEMA', 'isolate', '答案下标必须为整数 -1..3，不接受 bool')
    opts = q.get('o')
    valid_opts = isinstance(opts, list) and len(opts) == 4
    if not valid_opts or any(type(v) not in (str, int, float) or not text(v) for v in opts):
        add('SCHEMA', 'isolate', '选项必须是4个非空字符串或数值')
    metric = option_metrics(q) if valid_opts else {}
    if valid_opts and (len({text(v) for v in opts}) < 4 or metric['equivalentDuplicate']):
        add('EQUIVALENT_OPTIONS', 'isolate', '选项文字重复，或分数/小数/百分数归一后等价')

    s, e, tr = (str(q.get(k, '')) for k in ('s', 'e', 'tr'))
    unresolved = [v for v in re.findall(r'\{([A-Za-z_]\w*)\}', s+' '+e+' '+tr) if v != 'an']
    if unresolved:
        add('PLACEHOLDER', 'isolate', str(unresolved))
    # Specific confirmed teaching/statement defects. These are not inferred from length.
    if re.search(r'(原价|总数)必被100整除', e):
        add('FALSE_INTEGER_GENERALIZATION', 'isolate', '生成器碰巧取整百不能变成解题定理。70%人数为整数仅约束总人数为10的倍数；总人数10、男性7即反例。50%折后75元的原价150也非整百。')
    if re.search(r'某影厅一排共\d+个座位', s) and '连续奇数' in s and '最中间' in s and not re.search(r'和|起|从|首|第一', s):
        add('MISSING_ANCHOR', 'isolate', '只有座位数量及连续奇数，缺编号总和或起始编号；整体平移2仍满足条件，答案不唯一。解析擅用未给出的编号和。')
    seq = re.search(r'等比数列首项为1、公比为(\d+)，则其第(\d+)项的个位', s)
    if seq and valid_opts and type(a) is int and 0 <= a < 4:
        ratio, nth = map(int, seq.groups())
        expected = pow(ratio, nth-1, 10) if nth >= 1 else None
        if expected is None or number(option_string(opts[a])) != expected:
            add('GEOMETRIC_SEQUENCE_INDEX_ERROR', 'isolate',
                f'定点复核：首项1时第n项=r^(n-1)，不是r^n；题干r={ratio}, n={nth}，个位应为{expected}，源答案为{opts[a]}。仅复核此模式，不推广为全库数审通过。')
    if '每封信独立选邮筒' in e and '信' not in s and '邮筒' not in s:
        add('EXPLANATION_SCENE_MISMATCH', 'improve', '乘客/工序题直接复制信件解析，未说明每个对象对应什么及指数含义。')
    if '底面积为' in s and '深在两步：底面积=边' in e:
        add('UNNECESSARY_MODEL_STEP', 'improve', '题干已给底面积，只需体积/底面积，解析反而要求先平方，削弱最小计算直觉。')
    if re.search(r'答案[是为]?\s*[ABCD]\s*[。.!！]?$', e.strip()) and len(e) < 15:
        add('ANSWER_ONLY', 'improve', '解析只报选项，不能复盘')

    relational = bool(re.search(r'[=＝÷×^²³/]|反比|守恒|补集|勾股|同余|取反|插空|捆绑|中项|整除|C\(|A\(|阶乘|奇偶|周期|循环|排列|排序|!|≡', e))
    specific = bool(re.search(r'\d', e))
    operation = bool(re.search(r'设|减|加|乘|除|相差|和|比|枚举|代入|排除|反|余数|平方|立方|根|相同|独立', e))
    if not relational and not operation:
        add('NO_EXECUTABLE_EXPLANATION', 'improve', '未识别到可执行关系或动作；是保守质量筛选，不等于数学错误。')
    if len(text(e)) < 10:
        add('TOO_LITTLE_EXPLANATION', 'improve', '解释少于10个非空白字符且难以复盘，需补模型；不因题干短而淘汰。')
    if len(text(tr)) < 8:
        add('WEAK_TRAP_NOTE', 'warning', '陷阱提示少于8字符，需补错误路径')
    if not specific:
        add('GENERIC_EXPLANATION', 'warning', '公式/方法可用但没有具体数字示范，只作为基础反射候选')
    if metric.get('gapBand') in ('wide', 'tight'):
        add('OPTION_GAP_'+metric['gapBand'].upper(), 'warning', '相邻选项最小相对间距='+str(metric['nearestRelativeGap'])+'；仅供复核，不以间距直接判定低效。')
    if '概率' in s and '百分' not in s and valid_opts:
        invalid = [option_string(v) for v in opts if number(v) is not None and not 0 <= number(v) <= 1]
        if len(invalid) >= 2:
            add('IMPLAUSIBLE_PROBABILITY_DISTRACTORS', 'improve', '至少两个选项超出[0,1]，排除只需概率定义而非目标方法：'+str(invalid))
    if any(x['severity'] == 'isolate' for x in issues):
        grade, decision = 'D', 'isolated'
    elif any(x['severity'] == 'improve' for x in issues):
        grade, decision = 'C', 'needs_revision'
    else:
        grade, decision = ('B+' if relational and specific else 'B'), 'candidate'
    return {'grade': grade, 'decision': decision, 'issues': issues, 'options': metric,
            'explanationSignals': {'relationship': relational, 'numericExample': specific, 'operation': operation},
            'independentMathAudit': 'not_performed'}


def family_groups(rows):
    parent = list(range(len(rows)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    seen = {}
    for i, row in enumerate(rows):
        q = row['question']
        for kind in ('s', 'e'):
            sig = signature(q.get(kind, ''))
            # Do not connect records by an empty/near-empty explanation.
            if kind == 'e' and len(text(q.get('e', ''))) < 10:
                continue
            key = (kind, sig)
            if key in seen:
                parent[root(i)] = root(seen[key])
            else:
                seen[key] = i
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[root(i)].append(row)
    return list(groups.values())


def select(rows):
    family_audit = []
    for group in family_groups(rows):
        # Content-based family ID; fully reproducible for this input snapshot.
        family_id = 'family:'+digest(canonical(sorted(r['id'] for r in group)))[:16]
        candidates = [r for r in group if r['assessment']['decision'] == 'candidate']
        t = group[0]['question'].get('t')
        cap = POLICY['quota'].get(t, POLICY['quota']['default'])
        if candidates and all(r['assessment']['grade'] == 'B' for r in candidates):
            cap = POLICY['B_only_family_cap']
        selected, chosen_features = [], set()
        while candidates and len(selected) < cap:
            def rank(r):
                a = r['assessment']
                nums = re.findall(r'\d+(?:\.\d+)?', r['question']['s'])
                feature = (a['options'].get('gapBand'), any('.' in n for n in nums),
                           max((len(n.split('.')[0]) for n in nums), default=0))
                return (0 if a['grade'] == 'B+' else 1,
                        sum(x['severity'] == 'warning' for x in a['issues']),
                        feature in chosen_features, r['source']['file'], r['source']['index0'])
            chosen = min(candidates, key=rank)
            candidates.remove(chosen)
            selected.append(chosen)
            nums = re.findall(r'\d+(?:\.\d+)?', chosen['question']['s'])
            chosen_features.add((chosen['assessment']['options'].get('gapBand'), any('.' in n for n in nums),
                                 max((len(n.split('.')[0]) for n in nums), default=0)))
        selected_ids = {r['id'] for r in selected}
        for row in group:
            row['familyId'] = family_id
            a = row['assessment']
            if a['decision'] == 'candidate':
                a['decision'] = 'selected' if row['id'] in selected_ids else 'reserve'
                a['selectionReason'] = ('代表题：在家族配额内保留，非独立数学认证。' if row['id'] in selected_ids else
                    f'同构/方法近似组共{len(group)}题，配额{cap}；转入专项备选，不声称题目错误。')
            else:
                a['selectionReason'] = ' / '.join(x['code'] for x in a['issues'] if x['severity'] != 'warning')
        family_audit.append({'id': family_id, 'rawCount': len(group), 'cap': cap,
                             'members': [r['id'] for r in group], 'selectedIds': sorted(selected_ids),
                             'stemSignatures': sorted({signature(r['question'].get('s', '')) for r in group}),
                             'explanationSignatures': sorted({signature(r['question'].get('e', '')) for r in group})})
    return sorted(family_audit, key=lambda g: g['id'])


def build():
    files = [HERE/f'gen_{letter}_output.json' for letter in 'ABCDE']
    if any(not f.is_file() for f in files):
        raise ValueError('必须提供 A-E 五份原始输出；拒绝把缺失数据当成空库。')
    rows, manifest = [], []
    for path in files:
        blob = path.read_bytes()
        qs = json.loads(blob.decode('utf-8-sig'))
        if not isinstance(qs, list) or any(not isinstance(q, dict) for q in qs):
            raise ValueError(path.name+': expected array of question objects')
        manifest.append({'file': path.name, 'sha256': digest(blob), 'count': len(qs)})
        for i, q in enumerate(qs):
            sha = digest(canonical(q))
            rows.append({'id': f'glm:{path.stem}:{i:03d}:{sha[:12]}',
                         'source': {'file': path.name, 'index0': i, 'number1': i+1, 'questionSha256': sha},
                         'question': q, 'assessment': assess(q)})
    if len(rows) != 545:
        raise ValueError('本规则版本审阅对象固定545题；源规模变化后请更新版本和审计。')
    families = select(rows)
    # Ensure full-stem duplicates cannot survive across different tag families.
    seen = {}
    for row in rows:
        a = row['assessment']
        if a['decision'] != 'selected':
            continue
        key = text(row['question']['s'])
        if key in seen:
            a['decision'] = 'reserve'
            a['selectionReason'] = '完整题干重复，优先代表为 '+seen[key]
        else:
            seen[key] = row['id']
    # Cross-family hook quota: do not let any old h label dominate daily practice.
    hook_audit = []
    hooks = defaultdict(list)
    for row in rows:
        if row['assessment']['decision'] == 'selected':
            hooks[row['question']['h']].append(row)
    for hook, candidates in sorted(hooks.items()):
        ranked = sorted(candidates, key=lambda r: (
            0 if r['assessment']['grade'] == 'B+' else 1,
            sum(i['severity'] == 'warning' for i in r['assessment']['issues']),
            r['source']['file'], r['source']['index0']))
        winners = ranked[:POLICY['hook_cap']]
        for row in ranked[POLICY['hook_cap']:]:
            row['assessment']['decision'] = 'reserve'
            row['assessment']['selectionReason'] = f'考点标签{hook}超过日常精选上限{POLICY["hook_cap"]}题；转专项备选。'
        hook_audit.append({'hook': hook, 'cap': POLICY['hook_cap'],
                           'familyRepresentativesBeforeCap': len(candidates),
                           'selectedIds': [r['id'] for r in winners]})
    selected_ids = {r['id'] for r in rows if r['assessment']['decision'] == 'selected'}
    for f in families:
        f['selectedIds'] = [i for i in f['selectedIds'] if i in selected_ids]
    selected = []
    for row in rows:
        a, q = row['assessment'], row['question']
        if a['decision'] != 'selected':
            continue
        # Preserve question, answer, explanation verbatim; only stringify numeric options.
        out = dict(q)
        out['o'] = [option_string(v) for v in q['o']]
        out.update({'sourceType': 'mock', 'sourceLabel': 'GLM精选模拟（初筛）',
                    'curationId': row['id'], 'curated': True, 'qualityGrade': a['grade'],
                    'quality': POLICY['quality_label'],
                    'curationVersion': VERSION, 'template': row['familyId'],
                    'provenance': row['source'], 'mathAuditStatus': 'not_performed'})
        selected.append(out)
    # Compare authoritative generator output with existing full bank on core fields only.
    bank_path = OUT/'题库数据.js'
    bank_blob = bank_path.read_bytes()
    m = re.search(r'window\.BANK\s*=\s*(\[.*\]);\s*$', bank_blob.decode('utf-8-sig'), re.S)
    if not m:
        raise ValueError('无法读取现有 window.BANK')
    bank = json.loads(m.group(1))
    def core(q):
        result = {k: q.get(k, '') for k in CORE}
        result['o'] = [option_string(v) for v in q.get('o', [])]
        return digest(canonical(result))
    raw_core = Counter(core(r['question']) for r in rows)
    bank_core = Counter(core(q) for q in bank)
    consistency = {'file': bank_path.name, 'sha256': digest(bank_blob), 'count': len(bank),
                   'coreFieldsMatch': raw_core == bank_core,
                   'missingFromBank': sum((raw_core-bank_core).values()),
                   'notInRaw': sum((bank_core-raw_core).values()),
                   'metadataPolicy': '不采用旧 merge.py 按卡型一刀切生成的 canEstimate/canPlugOptions/optionValue；其正确性未审查。'}
    if not consistency['coreFieldsMatch']:
        raise ValueError('现有题库与原始输出的核心内容不一致；请先核对，不静默选择一个版本。')
    status = Counter(r['assessment']['decision'] for r in rows)
    by_type = {}
    for t in sorted({r['question']['t'] for r in rows}):
        subset = [r for r in rows if r['question']['t'] == t]
        by_type[t] = {'raw': len(subset), **dict(Counter(r['assessment']['decision'] for r in subset))}
    stats = {'raw': len(rows), 'selected': len(selected), 'excluded': len(rows)-len(selected),
             'byDecision': dict(status), 'byGrade': dict(Counter(r['assessment']['grade'] for r in rows)),
             'selectedByGrade': dict(Counter(q['qualityGrade'] for q in selected)), 'byType': by_type,
             'rawByHook': dict(Counter(r['question']['h'] for r in rows)),
             'selectedByHook': dict(Counter(q['h'] for q in selected)),
             'methodFamilies': len(families), 'repeatedFamilies': sum(f['rawCount'] > 1 for f in families),
             'ruleHits': dict(Counter(i['code'] for r in rows for i in r['assessment']['issues']))}
    report = {'version': VERSION, 'policy': POLICY, 'inputs': manifest, 'bankConsistency': consistency,
              'scriptSha256': digest(Path(__file__).read_bytes()), 'statistics': stats,
              'selectedIds': sorted(selected_ids), 'excludedIds': [r['id'] for r in rows if r['id'] not in selected_ids],
              'families': families, 'hookQuotas': hook_audit, 'records': rows}
    verify(report, selected)
    js = '// 自动生成，仅初筛，不代表独立数学审计通过。原始题目不改写。\nwindow.CURATED_GLM_BANK = '+json.dumps(selected, ensure_ascii=False, separators=(',', ':'))+';\n'
    return {
        '精选GLM题库.js': js.encode('utf-8'),
        '精选GLM题库审计.json': (json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'),
        '精选GLM题库筛选报告.md': markdown(report).encode('utf-8'),
    }, report


def verify(report, selected):
    rows = report['records']
    ids = {r['id'] for r in rows}
    yes, no = set(report['selectedIds']), set(report['excludedIds'])
    assert len(ids) == len(rows) == 545
    assert yes.isdisjoint(no) and yes | no == ids
    assert len(yes) == len(selected)
    assert sum(report['statistics']['byDecision'].values()) == 545
    assert all(q['t'] != '跳过' and q['a'] != -1 for q in selected)
    assert sum(r['question']['t'] == '跳过' for r in rows) == 30
    assert all(r['assessment']['decision'] == 'isolated' for r in rows if r['question']['t'] == '跳过')
    assert all(q['qualityGrade'] in ('B+', 'B') and q['mathAuditStatus'] == 'not_performed' for q in selected)
    assert all(len(f['selectedIds']) <= 1 for f in report['families'])
    assert all(n <= 12 for n in Counter(q['h'] for q in selected).values())
    assert all(q['quality'] == '规则筛选待逐题数审' for q in selected)
    assert all(not any(k in q for k in ('cost', 'canEstimate', 'canPlugOptions', 'optionValue')) for q in selected)
    source = {r['id']: r['question'] for r in rows}
    for q in selected:
        original = source[q['curationId']]
        assert all(q[k] == original[k] for k in CORE if k != 'o')
        assert q['o'] == [option_string(v) for v in original['o']]


def markdown(report):
    s = report['statistics']
    lines = [
        '# 545道 GLM 题库：系统筛选报告', '', f'规则版本：`{VERSION}`。这是**教学效用初筛，不是独立数学审计证书**。', '',
        '## 筛选结果', '',
        '| 去向 | 数量 | 含义 |', '|---|---:|---|',
        f"| 精选 selected | {s['selected']} | B+/B级代表题，仍待独立数学复核 |",
        f"| 专项备选 reserve | {s['byDecision'].get('reserve',0)} | 降低同构/相同方法密度；不是判为错题 |",
        f"| 待改进 needs_revision | {s['byDecision'].get('needs_revision',0)} | 解析、情境、干扰项等风险 |",
        f"| 隔离 isolated | {s['byDecision'].get('isolated',0)} | 含全部30张跳过卡，以及明确内容/结构问题 |", '',
        f"总计 **545**；本轮不进入精选 **{s['excluded']}**。所有源题完整保留；没有删除或改写原始输出。", '',
        '| 原卡型 | 原始 | 精选 | 专项备选 | 待改进 | 隔离 |', '|---|---:|---:|---:|---:|---:|',
    ]
    for t, v in s['byType'].items():
        lines.append(f"| {t} | {v['raw']} | {v.get('selected',0)} | {v.get('reserve',0)} | {v.get('needs_revision',0)} | {v.get('isolated',0)} |")
    lines += ['', '## 质量等级不是难度等级', '']
    for grade, meaning in POLICY['grades'].items():
        lines.append(f"- **{grade}**：{meaning} 全库 {s['byGrade'].get(grade,0)} 题，精选 {s['selectedByGrade'].get(grade,0)} 题。")
    lines += ['', '所有入选题统一标注 `quality: 规则筛选待逐题数审`。B+/B只是解析完整度的启发式等级，均可能有未发现错误，不是数审已过的等级。入门题也可以有好质量；不沿用“深钩=高质量”。', '',
        '## 规则与教学目的', '',
        '1. **同构/方法近似组**：完整数字归一化题干或解析跨标签连接相近题，不让换考点/卡型标签绕开配额。解析相同也分组，避免仅换“餐厅/选课/景点”逃过筛选。保留运算符、甲乙关系及所求量，不截取前80字。方法组是启发式归类，不是严格语义等价证明。',
        '   - 每个模板/方法近似组最多1道，日常只保留结构代表；每个原考点h最多12道。超过配额的保留原文进专项备选，不补位凑题量。',
        '   - 优先解释有具体代入、警告较少的题，再保留不同数字/选项间距形态。所有落选者均可回查其组内入选代表。',
        f"   - 本次 {s['methodFamilies']} 个方法组，其中 {s['repeatedFamilies']} 组多于1题；不把数量当成已覆盖的国考考点数。",
        '2. **解析质量**：检查可执行关系、具体示范、模板残留与题干/解析情境一致性。短且有效的“圆锥=圆柱/3”可以作为基础题保留；不因短题干或缺某个关键词直接判错。只报答案或没有可执行方法的转待改进。',
        '3. **选项区分度**：用精确分数统一小数/分数/百分数，等价重复选项隔离；概率题若至少两项超出[0,1]则转待改进。记录相邻相对间距但不拿大小直接判质量：大间距可用于估算，小间距也可能是好的精算边界。尚未对每个干扰项的真实错误路径做人工映射，账本明确记为未完成。',
        '4. **跳过合理性**：全部30张隔离，不接受“程序枚举所以45秒必做不完”的推断；不能把 a=-1 当数学正确答案。未来重入需独立解答、检查选项代入/边界/补集等短路，并以个人用时标注取舍。',
        '5. **不混用旧元数据**：旧merge.py把几乎所有非跳过题一律标成可估算/可代入，本次不继承这些未经核实的断言。', '',
        '## 已定位的实质缺陷（不是仅靠字数筛选）', '',
        '- `gen_A_output.json` 下标28–33、72–79（下标从0开始）：解析把“原价/总数必被100整除”当一般方法。反例：男生占70%，全班10人男生7人；50%折后75元原价150元。应先约分检查整数性，不能把生成器的取数习惯当定理。这14题隔离而非静默修文案。',
        '- 同文件下标115、119：座位编号题只给数量和连续奇数，未给编号和/起点，解析却用了165/259。整体平移仍满足题面，不能唯一作答，隔离。',
        '- `gen_B_output.json` 下标40、44：首项为1的等比数列第n项应为r^(n−1)，原答案按r^n取尾数，分别给6/9，题面应为8/1。两题定点复核发现索引错误，隔离。这只是两题的检查，不是全库数学审计。',
        '- `gen_D_output.json` 下标62、63、65：乘客/工艺题直接粘贴“每封信独立选邮筒”，未解释映射，转待改进。',
        '- 同文件下标33、35：已给底面积却在解析强调先算边长平方，增加无效步骤，转待改进。',
        '- 跳过卡中的袜子、租船、单禁点路径等不据题名断言应跳过。本轮只隔离，未修改答案，也不声称已完成这30题逐题解答。', '',
        '## 覆盖变化', '', '| 原标签 | 原始 | 精选 |', '|---|---:|---:|']
    for h, count in s['rawByHook'].items():
        lines.append(f"| {h} | {count} | {s['selectedByHook'].get(h,0)} |")
    lines += ['', '这些是GLM原标签，不是重新审定的难度或考点体系。精选减少机械重复，不自动补齐前缀约束、边界构造、多概念耦合等缺口。', '',
        '## 可审计与集成', '',
        '- `gen/select_curated_bank.py`：规则、确定性排序、自测与重建入口，仅Python标准库。',
        '- `精选GLM题库.js`：`window.CURATED_GLM_BANK`，只含入选题；保留原题干/答案/解析，数值选项只转字符串。',
        '- `精选GLM题库审计.json`：全545题原记录、来源文件、0基下标/1基序号、题目SHA256、质量等级、每条命中规则及证据、最终去向、家族代表；另存输入文件和筛选脚本SHA256。',
        '- 原始5份输出与现有545题BANK的核心字段已作多重集合对齐：一致。此对齐只说明版本相同，不说明答案正确。',
        '- 此脚本不写页面、验证器或其他题库；页面接入、发布由主agent整合。', '',
        '```powershell',
        'python 教学/速刷/gen/select_curated_bank.py --self-test',
        'python 教学/速刷/gen/select_curated_bank.py',
        'python 教学/速刷/gen/select_curated_bank.py --check',
        '```', '',
        '`--check` 不写文件，按字节验证可重现，并验证选中/排除构成完整互斥分区、30张跳过卡零泄漏、配额与原文保真。源文件缺失、题量不是545或BANK核心内容不匹配会失败，不静默漏题。', '',
        '**验证边界**：自测验证筛选程序和回归样例，不是545题数学审计。所有精选题的 `mathAuditStatus` 均为 `not_performed`。', '']
    return '\n'.join(lines)


def self_test():
    q = {'h': '测试', 't': '钩子', 's': '已知总数12，某部分为其一半，问这部分为几？',
         'o': ['3','6','9','12'], 'a': 1, 'e': '设总数12，一半=12÷2=6。', 'tr': '不要把整体当成所求部分。'}
    assert assess(q)['grade'] == 'B+'
    for change in ({'t':'跳过'}, {'a':-1}):
        assert assess(dict(q, **change))['decision'] == 'isolated'
    assert assess(dict(q, o=['0.5','1/2','2','3']))['decision'] == 'isolated'
    assert number('50%') == number('0.5') == number('1/2')
    assert number('1/0') is None and number('2√3') is None
    assert assess(dict(q, o=1))['decision'] == 'isolated'
    assert assess(dict(q, o=None))['decision'] == 'isolated'
    assert assess(dict(q, a=True))['decision'] == 'isolated'
    assert assess(dict(q, e='总数必被100整除'))['decision'] == 'isolated'
    short = dict(q, e='等底等高：圆锥=圆柱×1/3。')
    assert assess(short)['decision'] == 'candidate'
    assert assess(dict(q, e='甲位置定死，其余n−1人全排列(n−1)!。'))['decision'] == 'candidate'
    assert assess(dict(q, e='个位以4为周期循环，44≡0(mod4)，取末位6。'))['decision'] == 'candidate'
    assert signature('甲比乙多1/2') != signature('甲比乙少1/2')
    assert signature('某题'+('长'*90)+'求甲') != signature('某题'+('长'*90)+'求乙')
    missing = dict(q, s='某影厅一排共5个座位，座位号是连续奇数，最中间的座号是几？')
    assert assess(missing)['decision'] == 'isolated'
    rows = []
    for i in range(8):
        question = dict(q, s=f'情境{i}求总数的一半是多少？')
        rows.append({'id': str(i), 'source': {'file': 'test', 'index0': i},
                     'question': question, 'assessment': assess(question)})
    families = select(rows)
    assert len(families) == 1 and len(families[0]['selectedIds']) == 1
    assert sum(r['assessment']['decision'] == 'reserve' for r in rows) == 7
    print('Self-tests passed (screening only, not mathematical audit).')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='no writes; compare all outputs byte for byte')
    parser.add_argument('--self-test', action='store_true', help='run policy regression tests without writes')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    artifacts, report = build()
    if args.check:
        stale = [name for name, data in artifacts.items() if not (OUT/name).is_file() or (OUT/name).read_bytes() != data]
        if stale:
            print('Missing/stale outputs:', ', '.join(stale))
            return 1
        print('Determinism / partition / provenance / skip isolation checks passed.')
    else:
        for name, data in artifacts.items():
            (OUT/name).write_bytes(data)
    # Assert sources are untouched, including original untracked JSON files.
    for item in report['inputs']:
        assert digest((HERE/item['file']).read_bytes()) == item['sha256']
    print(json.dumps(report['statistics'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, AssertionError) as exc:
        print(f'FAILED: {exc}', file=sys.stderr)
        sys.exit(1)
