# -*- coding: utf-8 -*-
"""只读冻结原创题，验证逐题协议并确定性生成 JS/Markdown；--check 不写文件。"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
import audit_hand100 as hand
import audit_challenge24 as challenge

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'authored_methods.json'
JS = ROOT / 'authored_methods.js'
REPORT = ROOT / '原创逐题方法审计.md'
FAST_METHODS = frozenset({
    'normal', 'difference', 'ratio', 'assignment', 'complement', 'bundling',
    'symmetry', 'cycle', 'invariant', 'boundary', 'enumeration', 'modular',
    'conservation', 'recurrence', 'equation',
})
FAST_VALUES = frozenset({'high', 'medium', 'low'})
SKIP_DECISIONS = frozenset({'do', 'conditional', 'skip'})
FROZEN = {
    '手写模拟题_100.js': '351b721ec0c208105bccc898a49d2557690cc74527241f84cfbb8cbed2301d96',
    '原创复合24.js': '03f41fb8bef06c079d24d57fb2745cceb547757aa13c353451f1a3a8ac795a9e',
}
REVIEW_FILES = ('手写百题v2独立审计.md', '原创复合24独立审计.md')
REQUIRED = {
    'fastPath', 'normalPath', 'fastBoundary', 'fastMethod', 'fastValue',
    'skipDecision', 'skipReason', 'teachingGradient', 'retainedLevel',
    'expectedValue', 'sourceSha256', 'knowledge', 'elimination', 'tr',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_bank():
    return hand.read_bank() + challenge.load()


def source_name(q):
    return '手写模拟题_100.js' if q['uid'].startswith('hand100:') else '原创复合24.js'


def check_sources():
    for name, report in zip(FROZEN, REVIEW_FILES):
        raw = (ROOT / name).read_bytes()
        if b'\r' in raw or sha(raw) != FROZEN[name]:
            raise ValueError(f'{name}: 冻结字节/hash不匹配，必须重新审题，不自动更新hash')
        markers = re.findall(r'^RELEASE_APPROVED_SHA256: ([0-9a-f]{64})$',
                             (ROOT / report).read_text(encoding='utf-8'), re.M)
        if markers != [FROZEN[name]]:
            raise ValueError(f'{report}: 独立报告的唯一放行标记不匹配')


def solve_question(q):
    """先从条件复算，后读答案；不把解析或选项代入求解器。"""
    uid = q['uid']
    if uid.startswith('hand100:v2:'):
        n = int(uid.rsplit(':', 1)[1])
        locks = json.loads(hand.LOCK.read_text(encoding='utf-8'))
        lock = locks[uid]
        if lock['stemSha256'] != hand.digest(q['s']) or lock['conditions'] != hand.CASES[n].conditions:
            raise ValueError(f'{uid}: 人工题面条件锁不匹配')
        result = Fraction(hand.CASES[n].solve())
    elif uid.startswith('challenge:'):
        result = Fraction(challenge.solve(q['check']))
    else:
        raise ValueError(f'{uid}: 非原创题')
    return result


def check_answer(q, expected):
    uid = q['uid']
    values = [Fraction(v) for v in q['o']]
    answer = q.get('a')
    if (len(values) != 4 or len(set(values)) != 4 or type(answer) is not int
            or not 0 <= answer < 4 or [i for i, v in enumerate(values) if v == expected] != [answer]):
        raise ValueError(f'{uid}: 独立复算 {expected} 与唯一选项/标记答案不一致')


def validate(data, bank=None, verify_sources=True):
    if verify_sources:
        check_sources()
    if data.get('schemaVersion') != 1 or data.get('sources') != FROZEN:
        raise ValueError('schemaVersion/sources 不匹配')
    bank = load_bank() if bank is None else bank
    ids = [q['uid'] for q in bank]
    wanted = {f'hand100:v2:{i:03d}' for i in range(1, 101)} | {f'challenge:{i:03d}' for i in range(1, 25)}
    overlays = data.get('methods', {})
    if len(ids) != 124 or len(set(ids)) != 124 or set(ids) != wanted or set(overlays) != wanted:
        raise ValueError('必须完整且唯一覆盖100v2+24，禁止遗漏/额外UID')
    results = {}
    for q in bank:
        uid = q['uid']; m = overlays[uid]
        if set(m) != REQUIRED:
            raise ValueError(f'{uid}: 协议字段缺失/越权字段: {set(m) ^ REQUIRED}')
        for key in REQUIRED:
            if not isinstance(m[key], str) or (key != 'skipReason' and not m[key].strip()):
                raise ValueError(f'{uid}: {key} 必须为非空文本')
        if m['fastMethod'] not in FAST_METHODS or m['fastValue'] not in FAST_VALUES or m['skipDecision'] not in SKIP_DECISIONS:
            raise ValueError(f'{uid}: 枚举值非法')
        if m['skipDecision'] != 'do' and not m['skipReason'].strip():
            raise ValueError(f'{uid}: conditional/skip 必须说明具体停损条件')
        if m['fastMethod'] == 'normal' and m['fastValue'] != 'low':
            raise ValueError(f'{uid}: 常规同路不能冒称高收益')
        if m['fastPath'] == m['normalPath'] and m['fastValue'] != 'low':
            raise ValueError(f'{uid}: 同一路径必须标low')
        if m['fastValue'] == 'low' and '两路' not in m['fastBoundary']:
            raise ValueError(f'{uid}: low须说明两路关系及收益边界')
        if m['retainedLevel'] != q['level'] or m['sourceSha256'] != FROZEN[source_name(q)]:
            raise ValueError(f'{uid}: 不得改层级或沿用其他版本')
        for key in ('fastPath', 'normalPath', 'fastBoundary', 'teachingGradient',
                    'knowledge', 'elimination', 'tr'):
            if len(m[key]) < 16 or any(s in m[key] for s in ('TODO', '待补', '套公式即可', '秒杀所有')):
                raise ValueError(f'{uid}: {key}缺乏逐题内容')
        expected = solve_question(q)
        check_answer(q, expected)
        if Fraction(m['expectedValue']) != expected:
            raise ValueError(f'{uid}: overlay预期值不符独立复算')
        results[uid] = str(expected)
    return results


def render_js(data):
    return '// Generated by build_authored_methods.py; edit authored_methods.json, not frozen banks.\nwindow.AUTHORED_METHODS = ' + json.dumps(data['methods'], ensure_ascii=False, sort_keys=True, indent=2) + ';\n'


def render_report(data, bank, results):
    methods = data['methods']; values = Counter(m['fastValue'] for m in methods.values())
    skips = Counter(m['skipDecision'] for m in methods.values())
    levels = Counter(q['level'] for q in bank)
    lines = ['# 原创124题逐题教学方法协议审计', '',
        '> 本文件由 build_authored_methods.py 确定性生成。审计对象是教学 overlay，不是重写原题。',
        '> 这是基于冻结题面、已有独立审计与现有异实现求解器的教学判断；不是新增独立审计员放行，也不是考生群体实测。', '',
        '## 可执行交付与集成边界', '',
        '- 数据源：`authored_methods.json`；浏览器产物：`authored_methods.js`，导出 `window.AUTHORED_METHODS={uid:overlay}`。',
        '- 主集成方应在 core 归一化前按 UID 合并 overlay；本任务不修改 core、UI 或 HTML 加载顺序。',
        '- overlay 不含 s/o/a/e/tr/level 等资产字段；retainedLevel 仅记录原等级，不参与改级。',
        '- `python -X utf8 教学/速刷/build_authored_methods.py`：逐题复算并生成 JS/本报告。',
        '- `python -X utf8 教学/速刷/build_authored_methods.py --check`：只读检查数学、覆盖、冻结hash、报告放行标记及产物逐字节一致性。',
        '- `python -X utf8 -m unittest discover -s 教学/速刷 -p test_authored_methods.py -v`：覆盖124题与错答案故障注入。',
        '- fastMethod enum：' + ', '.join(sorted(FAST_METHODS)) + '。',
        '- fastValue：high=有明确结构省步；medium=减少中间量/分类但仍需推导；low=两路相同或等价短算，不能宣传秒杀。收益是审题判断，不是计时实验。',
        '- skipDecision：do=首轮优先做；conditional=识别所列结构再做，否则首轮暂跳；skip=首轮性价比低，留二轮。跳过不是数学答案，专项练习仍需完成。',
        '- teachingGradient：逐题先备能力→本题新增负担/迁移；保留既有四级，不把层级当实测难度。',
        '- 数学证明边界：程序复用 audit_hand100.CASES 与 audit_challenge24.solve，以精确分数、枚举、DP核答案；自然语言两路解法仍须逐题阅读，程序不声称自动证明中文推导。',
        '- 百题题面绑定现有条件锁；24题check转录的可信边界由整文件冻结hash和独立报告绑定。不导入生成器、不重写审计报告、不更新原题hash。', '',
        '## 冻结输入与逐题结论', '',
        '| 输入 | 原始LF SHA-256（保持原样） |', '|---|---|']
    lines += [f'| {name} | `{digest}` |' for name, digest in FROZEN.items()]
    lines += ['', '依据：`手写百题v2独立审计.md`第9节与`原创复合24独立审计.md`第10节最终结论；旧快照建议不当作现存阻断。',
        f'数学唯一选项复算：{len(results)}/124；fastValue分布：{dict(sorted(values.items()))}；首轮决策：{dict(sorted(skips.items()))}。',
        '原等级分布：' + '、'.join(f'{k}{levels[k]}' for k in ('入门', '熟练', '深化', '综合')) + '；本轮无等级变更。', '',
        '重点诚实性回归：百题061允许份数相同；072乘工作占比仅在互质完整共同周期使用；复合010为新版整除条件排列概率；复合003/018离散约束本例未造成连续最优取整后的额外损失；复合023下界必须附5大2小可达见证。', '']
    for q in bank:
        uid = q['uid']; m = methods[uid]
        lines += [f'## {uid} · {q["h"]} · 保留{q["level"]}', '',
            f'- 原题：{q["s"]}',
            f'- 复算值：`{results[uid]}`；唯一选项 {chr(65 + q["a"])}。',
            f'- 知识点：{m["knowledge"]}',
            f'- 快路径（{m["fastMethod"]} / {m["fastValue"]}）：{m["fastPath"]}',
            f'- 常规路径：{m["normalPath"]}', f'- 排除法与选项分析：{m["elimination"]}',
            f'- 快法边界与收益：{m["fastBoundary"]}',
            f'- 易错点（覆盖题面原文）：{m["tr"]}',
            f'- 首轮决策：**{m["skipDecision"]}**' + (f'；{m["skipReason"]}' if m['skipReason'] else '；按上述识别关系直接求解。'),
            f'- 教学梯度：{m["teachingGradient"]}', '']
    return '\n'.join(lines).rstrip() + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        data = json.loads(DATA.read_text(encoding='utf-8'))
        bank = load_bank(); results = validate(data, bank)
        outputs = {JS: render_js(data), REPORT: render_report(data, bank, results)}
        for path, text in outputs.items():
            raw = text.encode('utf-8')
            if args.check:
                if not path.exists() or path.read_bytes() != raw:
                    raise ValueError(f'{path.name}: 产物缺失或过期，请运行生成命令')
            else:
                path.write_bytes(raw)
        print(f'authored methods: {len(results)}/124 exact checks passed; ' + ('artifacts current (read-only)' if args.check else 'JS + report generated'))
        return 0
    except (ValueError, KeyError, TypeError, OSError, AssertionError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
