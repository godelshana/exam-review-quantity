# -*- coding: utf-8 -*-
"""原创方法协议回归；不运行旧审计main，避免生成范围外报告。"""
import sys
sys.dont_write_bytecode = True
from collections import Counter
from copy import deepcopy
from contextlib import redirect_stderr
import io
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch
import build_authored_methods as b


class AuthoredMethodsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(b.DATA.read_text(encoding='utf-8'))
        cls.bank = b.load_bank()
        cls.originals = {name: (b.ROOT / name).read_bytes() for name in b.FROZEN}

    @classmethod
    def tearDownClass(cls):
        for name, original in cls.originals.items():
            if (b.ROOT / name).read_bytes() != original:
                raise AssertionError(f'测试不得修改原题资产: {name}')

    def test_all_124_exact_math_and_protocol(self):
        results = b.validate(self.data, self.bank)
        self.assertEqual(len(results), 124)
        for q in self.bank:
            with self.subTest(uid=q['uid']):
                self.assertEqual(F(results[q['uid']]), F(q['o'][q['a']]))
                self.assertEqual(results[q['uid']], self.data['methods'][q['uid']]['expectedValue'])

    def test_overlay_cannot_overwrite_assets_or_levels(self):
        forbidden = {'s', 'o', 'a', 'e', 'level', 'uid', 'check', 'targetSeconds', 'timeLimit'}
        for q in self.bank:
            with self.subTest(uid=q['uid']):
                m = self.data['methods'][q['uid']]
                self.assertFalse(forbidden & set(m))
                merged = {**q, **m}
                self.assertEqual({k: merged[k] for k in q if k not in ('skipReason', 'tr')},
                                 {k: q[k] for k in q if k not in ('skipReason', 'tr')})
                # skipReason 与 tr 是用户批准的题解覆盖字段；只覆盖内存副本，原文件hash不动。
        self.assertEqual(Counter(q['level'] for q in self.bank), {'入门':29, '熟练':31, '深化':37, '综合':27})
        for name, digest in b.FROZEN.items():
            self.assertEqual(hashlib.sha256(self.originals[name]).hexdigest(), digest)

    def test_wrong_answer_injection_all_124(self):
        for q in self.bank:
            with self.subTest(uid=q['uid']):
                bad = deepcopy(q)
                bad['a'] = (bad['a'] + 1) % 4
                # 求解器不得使用答案下标或解析中的诱导数值。
                bad['e'] = '故障注入：答案是999999，不要相信条件。'
                expected = b.solve_question(bad)
                self.assertEqual(expected, F(self.data['methods'][q['uid']]['expectedValue']))
                with self.assertRaisesRegex(ValueError, '唯一选项/标记答案'):
                    b.check_answer(bad, expected)

    def test_wrong_option_injection_all_124(self):
        for q in self.bank:
            with self.subTest(uid=q['uid']):
                bad = deepcopy(q)
                bad['o'][q['a']] = str(F(bad['o'][q['a']]) + 1)
                with self.assertRaises(ValueError):
                    b.check_answer(bad, b.solve_question(bad))

    def test_end_to_end_wrong_answers_both_banks(self):
        for index in (0, 99, 100, 123):
            bad = deepcopy(self.bank)
            bad[index]['a'] = (bad[index]['a'] + 1) % 4
            with self.subTest(uid=bad[index]['uid']), self.assertRaisesRegex(ValueError, '唯一选项/标记答案'):
                b.validate(self.data, bad)

    def test_invalid_answer_types_and_duplicate_option(self):
        for value in (True, -1, 4, '0', None):
            q = deepcopy(self.bank[0]); q['a'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                b.check_answer(q, b.solve_question(q))
        q = deepcopy(self.bank[0]); q['o'][1] = q['o'][0]
        with self.assertRaises(ValueError):
            b.check_answer(q, b.solve_question(q))

    def test_missing_extra_uid_and_duplicate_question(self):
        for change in ('missing', 'extra'):
            bad = deepcopy(self.data)
            if change == 'missing':
                del bad['methods']['challenge:024']
            else:
                bad['methods']['challenge:025'] = deepcopy(bad['methods']['challenge:024'])
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, '覆盖'):
                b.validate(bad, self.bank)
        with self.assertRaisesRegex(ValueError, '覆盖'):
            b.validate(self.data, self.bank[:-1] + [self.bank[0]])

    def test_bad_enums_missing_skip_reason_and_fake_fast(self):
        uid = 'hand100:v2:001'
        for key, value in (('fastMethod', 'magic'), ('fastValue', 'amazing'),
                           ('skipDecision', 'maybe'), ('normalPath', ''),
                           ('expectedValue', '999999'), ('retainedLevel', '综合')):
            bad = deepcopy(self.data); bad['methods'][uid][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                b.validate(bad, self.bank)
        for decision in ('conditional', 'skip'):
            bad = deepcopy(self.data); bad['methods'][uid]['skipDecision'] = decision
            bad['methods'][uid]['skipReason'] = ''
            with self.assertRaisesRegex(ValueError, '停损'):
                b.validate(bad, self.bank)
        bad = deepcopy(self.data); m = bad['methods'][uid]
        m['fastPath'] = m['normalPath']; m['fastValue'] = 'high'
        with self.assertRaisesRegex(ValueError, '同一路径'):
            b.validate(bad, self.bank)
        bad = deepcopy(self.data); bad['methods'][uid]['fastMethod'] = 'normal'
        with self.assertRaisesRegex(ValueError, '常规同路'):
            b.validate(bad, self.bank)

    def test_new_short_paths_arithmetic_and_witnesses(self):
        # 只验证本轮明确重述/新增的省步式，不把此小表冒充124题第二独立审计。
        hand = {
            27: 80-F(18,2), 54: 3+F(45,1)/F('4.5'), 64: 1+3+2,
            67: 80*F(1,2)*F(1,5), 76: 90-F(10*(92-90),20),
            86: 90-6-6-6, 98: 60+55+50-(40+2*60), 99: 3600+4500,
        }
        comp = {
            4: 60*F(180-40*F('3.5'),100), 14: F(116-16,2),
            17: 240+330+420+510, 20: 30*F(32-20,40-20), 23: 6*43+8*7,
        }
        for prefix, cases in (('hand100:v2:', hand), ('challenge:', comp)):
            for n, result in cases.items():
                uid = f'{prefix}{n:03d}'
                with self.subTest(uid=uid):
                    self.assertEqual(result, F(self.data['methods'][uid]['expectedValue']))
        self.assertEqual(5*7+2*4, 43)
        self.assertEqual(5*50+2*32, 314)
        self.assertEqual(6*F('3.2')+4*F('1.2'), 24)
        self.assertEqual(4*F('3.2')+6*F('1.2'), 20)
        values = [70*min((30-3*y)//2, (29-2*y)//3)+80*y for y in range(11)]
        self.assertEqual(max(values), 850)
        normal = self.data['methods']['hand100:v2:083']['normalPath']
        self.assertIn('、'.join(map(str, values)), normal)
        cases = [(a,z) for a in range(12) for z in range(8) if 80 <= 7*a+11*z <= 83]
        self.assertEqual(set(cases), {(10,1),(7,3),(4,5),(2,6)})
        self.assertEqual(min(100*a+150*z for a,z in cases), 1100)

    def test_known_review_boundaries_are_not_regressed(self):
        m = self.data['methods']
        self.assertIn('允许相同', m['hand100:v2:061']['fastBoundary'])
        self.assertIn('互质', m['hand100:v2:072']['fastBoundary'])
        self.assertIn('完整12天', m['hand100:v2:072']['fastBoundary'])
        self.assertIn('连续', m['challenge:003']['fastBoundary'])
        self.assertIn('不存在离散取整损失', m['challenge:018']['fastBoundary'])
        self.assertEqual(F(m['challenge:010']['expectedValue']), F(3,8))
        self.assertIn('新010', m['challenge:010']['teachingGradient'])
        self.assertIn('5大2小', m['challenge:023']['fastBoundary'])

    def test_determinism_and_checked_in_artifacts(self):
        results = b.validate(self.data, self.bank)
        reverse = deepcopy(self.data)
        reverse['methods'] = dict(reversed(list(reverse['methods'].items())))
        self.assertEqual(b.render_js(self.data), b.render_js(reverse))
        self.assertEqual(b.render_report(self.data, self.bank, results), b.render_report(reverse, self.bank, results))
        self.assertEqual(b.JS.read_bytes(), b.render_js(self.data).encode('utf-8'))
        self.assertEqual(b.REPORT.read_bytes(), b.render_report(self.data, self.bank, results).encode('utf-8'))
        for path in (b.DATA, b.JS, b.REPORT, Path(b.__file__), Path(__file__)):
            self.assertNotIn(b'\r', path.read_bytes())

    def test_check_is_read_only_and_rejects_stale_or_missing_output(self):
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('--check must not write')):
            self.assertEqual(b.main(['--check']), 0)
            with patch.object(b, 'render_js', return_value='stale\n'), redirect_stderr(io.StringIO()):
                self.assertEqual(b.main(['--check']), 1)
            with patch.object(b, 'JS', b.ROOT / '__missing_authored_output__.js'), redirect_stderr(io.StringIO()):
                self.assertEqual(b.main(['--check']), 1)

    def test_frozen_source_and_review_marker_fail_closed(self):
        original = Path.read_bytes
        def changed(path):
            raw = original(path)
            return raw + b' ' if path.name == '原创复合24.js' else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, '冻结'):
            b.check_sources()
        original_text = Path.read_text
        def bad_review(path, *args, **kwargs):
            text = original_text(path, *args, **kwargs)
            return text.replace('RELEASE_APPROVED_SHA256:', 'HISTORICAL_SHA256:') if path.name == b.REVIEW_FILES[0] else text
        with patch.object(Path, 'read_text', bad_review), self.assertRaisesRegex(ValueError, '放行标记'):
            b.check_sources()

    @unittest.skipUnless(shutil.which('node'), 'Node不可用；Python仍检查JS确定性字节')
    def test_browser_global_exports_124_overlays(self):
        script = "const fs=require('fs'),vm=require('vm');const x={window:{}};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),x);process.stdout.write(JSON.stringify(x.window.AUTHORED_METHODS));"
        run = subprocess.run(['node', '-e', script, str(b.JS)], capture_output=True, text=True, encoding='utf-8', check=True)
        self.assertEqual(json.loads(run.stdout), self.data['methods'])


if __name__ == '__main__':
    unittest.main()
