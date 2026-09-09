"""发布门禁故障注入；在临时目录操作，不更改真实题库。"""
import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from build_site import REQUIRED, verify_manifest
from validate_bank import validate, load_js, ROOT
from audit_challenge24 import solve

class QualityGates(unittest.TestCase):
    def test_release_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='quantity-gate-') as td:
            root=Path(td)
            manifest={'audited':{}}
            for i,(name,status) in enumerate(REQUIRED.items()):
                (root/name).write_text('reviewed content '+name,encoding='utf-8')
                sha=hashlib.sha256((root/name).read_bytes()).hexdigest()
                record={'sha256':sha,'status':status}
                if status=='math_and_independent_review_passed':
                    report=root/f'review-{i}.md'
                    report.write_text('RELEASE_APPROVED_SHA256: '+sha,encoding='utf-8')
                    record['independentReview']={'file':report.name,'sha256':hashlib.sha256(report.read_bytes()).hexdigest()}
                manifest['audited'][name]=record
            self.assertTrue(verify_manifest(manifest,root))
            with self.assertRaises(ValueError):verify_manifest({'audited':{}},root)
            altered=copy.deepcopy(manifest)
            altered['audited']['精选GLM题库.js']['status']='math_and_independent_review_passed'
            with self.assertRaises(ValueError):verify_manifest(altered,root)
            (root/'手写模拟题_100.js').write_text('one option changed',encoding='utf-8')
            with self.assertRaises(ValueError):verify_manifest(manifest,root)

    def test_review_report_cannot_float(self):
        # The real release is checked in build_site; here prove no content-only gate.
        with self.assertRaises(ValueError):
            verify_manifest({'audited':{name:{'status':status,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name,status in REQUIRED.items()}})

    def test_challenge_oracle_not_answer_echo(self):
        questions=load_js(ROOT/'原创复合24.js','CHALLENGE_Q')
        from fractions import Fraction
        for q in questions:
            expected=solve(q['check'])
            self.assertEqual([i for i,v in enumerate(q['o']) if Fraction(v)==expected],[q['a']])
            wrong=copy.deepcopy(q);wrong['a']=(wrong['a']+1)%4;wrong['e']='胡乱声称答案999999'
            self.assertNotEqual(Fraction(wrong['o'][wrong['a']]),solve(wrong['check']))
        # Each of the 24 models is covered; an answer-index mutation must fail.
        self.assertEqual(len(questions),24)

    def test_schema_equivalent_options_and_skip(self):
        q=load_js(ROOT/'原创复合24.js','CHALLENGE_Q')[0]
        self.assertEqual(validate([('test',[q],True)]),[])
        broken=copy.deepcopy(q);broken['o']=['1/2','50%','2','3']
        self.assertTrue(validate([('test',[broken],True)]))
        broken=copy.deepcopy(q);broken.update(a=-1,t='跳过')
        self.assertTrue(validate([('test',[broken],True)]))
        self.assertTrue(validate([('test',[q,q],True)]))

if __name__=='__main__':unittest.main()
