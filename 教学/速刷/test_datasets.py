"""Data-only regression and fault injection; no network or writes outside datasets/.
Run: python 教学/速刷/test_datasets.py
"""
import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
import build_datasets as b


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=b.read_json(b.DATA/'sources.json')
        cls.certs=b.read_json(b.DATA/'certificates.json')
        cls.raw={q['uid']:q for q in cls.snapshot['real']+cls.snapshot['glm']}
        (cls.train,cls.val,cls.quarantine,cls.audit,cls.summary,cls.manifest,
         cls.screening,cls.overrides)=b.assemble(cls.snapshot,cls.certs)
        cls.rows={q['uid']:q for q in cls.audit}

    def test_inventory_all_questions_not_prior_regex_subset(self):
        self.assertEqual(len(self.snapshot['real']),400)
        self.assertEqual(sum(q['year']<=2023 for q in self.snapshot['real']),295)
        self.assertEqual(len(self.snapshot['glm']),545)
        self.assertEqual(len(self.audit),945)
        self.assertEqual(len(self.rows),945)
        self.assertEqual(len(self.snapshot['authoredScreeningInputs']),124)
        self.assertFalse(any(q['uid'].startswith(('hand100:','challenge:')) for q in self.train+self.val))

    def test_exact_105_reserved_slots(self):
        self.assertEqual(len(self.val),105)
        self.assertEqual(len(self.manifest['nationalSlots']),105)
        counts=Counter((q['year'],q['paper']) for q in self.val)
        for year in b.YEARS:
            for paper,n in [('副省级',15),('地市级',10),('行政执法类',10)]:
                self.assertEqual(counts[year,paper],n)
                self.assertEqual(sorted(q['moduleIndex'] for q in self.val if (q['year'],q['paper'])==(year,paper)),list(range(1,n+1)))
        self.assertTrue(all(q['dataset']=='validation' for q in self.val))
        self.assertFalse(any(b.is_reserved(q) for q in self.train))

    def test_guangdong_unknown_counts_not_fabricated(self):
        gaps=self.manifest['guangdongGaps']
        self.assertEqual([r['year'] for r in gaps],[2024,2025,2026])
        for r in gaps:
            self.assertIsNone(r['expectedSlots'])
            self.assertEqual(r['availableQuestions'],0)
            self.assertEqual(r['validationStatus'],'V3')
            self.assertTrue(r['reason'])
        self.assertFalse(self.summary['validation']['guangdongComplete'])

    def test_all_usable_question_contracts(self):
        self.assertGreaterEqual(sum(q['sourceType']=='real' for q in self.train),20)
        self.assertGreaterEqual(sum(q['sourceType']=='glm' for q in self.train),5)
        fields='s o a h t e tr level uid dataset year exam paper moduleIndex answerStatus imageStatus explanationStatus validationStatus fastMethod fastValue skipDecision familyId leakageRisk fastPath normalPath fastBoundary mathAudit sourceType'.split()
        for q in self.train+[v for v in self.val if v['usable']]:
            with self.subTest(uid=q['uid']):
                self.assertTrue(set(fields)<=q.keys())
                for k in ('s','h','t','e','tr','fastPath','normalPath','fastBoundary'):
                    self.assertIsInstance(q[k],str);self.assertTrue(q[k].strip())
                self.assertEqual(len(q['o']),4)
                self.assertTrue(all(isinstance(x,str) and x.strip() for x in q['o']))
                self.assertEqual(len(set(q['o'])),4)
                self.assertIn(q['a'],range(4))
                self.assertIn(q['level'],['入门','熟练','深化','综合'])
                self.assertEqual(q['answerStatus'],'confirmed')
                self.assertEqual(q['imageStatus'],'complete')
                self.assertEqual(q['explanationStatus'],'P2')
                self.assertEqual(q['mathAudit']['status'],'passed')
                self.assertTrue(q['mathAudit']['sourceAgreement'])
                self.assertFalse(q['quarantineReasons'])
                self.assertNotEqual(q['fastPath'],q['normalPath'])
                self.assertIn(q['sourceType'],['real','glm'])
                if q['dataset']=='train':self.assertEqual(q['leakageRisk'],'low')
                else:self.assertEqual(q['validationStatus'],'V1')

    def test_every_certificate_recomputed_and_no_unearned_passes(self):
        for uid,c in self.certs.items():
            with self.subTest(uid=uid):
                audit=b.solve(self.raw[uid],c)
                self.assertEqual(audit['status'],'passed')
                self.assertEqual(audit['fastResult'],audit['normalResult'])
                self.assertEqual(audit['sourceHash'],b.source_hash(self.raw[uid]))
                self.assertIn(uid,self.rows)
        for uid,r in self.rows.items():
            if uid not in self.certs and uid!='glm:D:30':
                self.assertEqual(r['mathAudit']['status'],'not_attempted')
                self.assertFalse(r['usable'])
                self.assertIsNone(r['a'])
        self.assertEqual(self.summary['math']['attempted'],len(self.certs)+1)
        self.assertEqual(self.summary['math']['notAttempted'],945-len(self.certs)-1)

    def test_equal_volume_is_not_congruent_cubes(self):
        q=self.rows['glm:D:30']
        self.assertNotIn(q['uid'],self.certs)
        self.assertEqual(q['s'],self.raw[q['uid']]['s'])
        self.assertIn('切成125等份',q['s'])
        self.assertNotIn('全等小正方体',q['s'])
        self.assertEqual(q['mathAudit']['status'],'failed')
        examples=q['mathAudit']['counterexamples']
        self.assertEqual({r['pieces'] for r in examples},{125})
        self.assertEqual({r['pieceVolume'] for r in examples},{'1'})
        self.assertEqual({r['unpainted'] for r in examples},{0,27})
        self.assertFalse(q['usable']);self.assertIsNone(q['a'])

    def test_source_mismatch_and_known_disputes_not_scorable(self):
        for uid in self.summary['math']['sourceDisagreements']:
            q=self.rows[uid]
            self.assertFalse(q['scorable']);self.assertFalse(q['usable']);self.assertIsNone(q['a'])
            self.assertEqual(q['answerStatus'],'disputed')
            self.assertIn('disputeViews',q)
            if q['dataset']=='validation':self.assertEqual(q['validationStatus'],'V3')
        for uid in ['real:2023:副省级:63','real:2026:地市级:67','real:2025:地市级:66']:
            q=self.rows[uid]
            self.assertEqual(q['answerStatus'],'disputed');self.assertFalse(q['scorable'])
        self.assertFalse(any(v['validationStatus']=='V2' and v['answerStatus']!='confirmed' for v in self.val))

    def test_quarantine_partition_and_prior_glm_is_not_math(self):
        all_train_candidates=[q for q in self.audit if q['dataset']=='train']
        self.assertEqual(len(all_train_candidates),295+545)
        self.assertEqual({q['uid'] for q in all_train_candidates},
                         {q['uid'] for q in self.train+self.quarantine})
        self.assertFalse({q['uid'] for q in self.train}&{q['uid'] for q in self.quarantine})
        q=self.raw['glm:A:0']
        self.assertEqual(q['source']['priorStructuralReview']['assessment']['independentMathAudit'],'not_performed')
        self.assertEqual(q['source']['priorReviewKind'],'structure_only_not_independent_math')
        self.assertTrue(all(q['quarantineReasons'] and not q['usable'] for q in self.quarantine))

    def test_strict_reservation_provenance_attacks(self):
        base=self.raw['real:2011:合卷:66']
        for year in (2024,2025,2026,'2024','2025','2026'):
            for field in ('year','sourceYear','originYear'):
                q=copy.deepcopy(base);q[field]=year
                self.assertTrue(b.is_reserved(q))
            for field in ('uid','sourceQuestionUid','sourceLabel'):
                q=copy.deepcopy(base);q[field]=f'guangdong:{year}:1'
                self.assertTrue(b.is_reserved(q))
            q=copy.deepcopy(base);q['source']['locator']=f'{year}·广东·1'
            self.assertTrue(b.is_reserved(q))
        for year in range(2011,2024):
            self.assertFalse(b.is_reserved({'year':year,'uid':f'real:{year}:合卷:1'}))

    def test_certificate_bound_to_full_content_and_provenance(self):
        uid='real:2011:合卷:66';original=self.raw[uid];c=self.certs[uid]
        for field,value in [('s',original['s'].replace('50%','40%',1)),('o',['1','2','3','4']),
                            ('sourceAnswer','A'),('year',2026),('exam','广东省考'),
                            ('moduleIndex',99),('paper','地市级'),('sourceQuestionUid','real:2025:x')]:
            q=copy.deepcopy(original);q[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'stale math certificate'):b.solve(q,c)
        q=copy.deepcopy(original);q['source']['locator']='2026·地市·66'
        with self.assertRaisesRegex(ValueError,'stale math certificate'):b.solve(q,c)

    def test_math_faults_not_silently_downgraded(self):
        uid='real:2011:合卷:66';q=self.raw[uid]
        c=copy.deepcopy(self.certs[uid]);c['fast']='49'
        with self.assertRaises(ValueError):b.solve(q,c)
        c=copy.deepcopy(self.certs[uid]);c['normal']['expression']='49'
        with self.assertRaises(ValueError):b.solve(q,c)
        q=copy.deepcopy(q);q['sourceAnswer']='A'
        c=copy.deepcopy(self.certs[uid]);c['sourceHash']=b.source_hash(q)
        result=b.make_record(q,{uid:c})
        self.assertEqual(result['mathAudit']['fastResult'],'48')
        self.assertFalse(result['mathAudit']['sourceAgreement'])
        self.assertFalse(result['usable']);self.assertIsNone(result['a'])

    def test_duplicate_equivalent_options_rejected(self):
        uid='real:2011:合卷:66';q=copy.deepcopy(self.raw[uid]);c=copy.deepcopy(self.certs[uid])
        q['o']=['48','48.0','56','60'];c['sourceHash']=b.source_hash(q)
        with self.assertRaisesRegex(ValueError,'duplicate/missing'):b.solve(q,c)

    def test_arithmetic_language_is_safe_and_exact(self):
        self.assertEqual(b.calc('1/10+2/10'),b.F(3,10))
        self.assertEqual(b.calc('C(8,4)'),70)
        for expr in ["__import__('os').system('echo x')",'x.__class__','[1][0]','2**1000','C(3/2,1)']:
            with self.subTest(expr=expr),self.assertRaises(ValueError):b.calc(expr)

    def test_all_authored_and_glm_screened_including_rejected_glm(self):
        self.assertEqual(len(self.screening),669)
        self.assertEqual(len({r['uid'] for r in self.screening}),669)
        self.assertEqual(len(self.overrides),124)
        for row in self.screening:
            self.assertIn(row['leakageRisk'],['low','medium','high'])
            self.assertEqual(row['auditKind'],'structural_template_screen_not_independent_math')
            self.assertIn('externalCoverage',row['leakageCheck'])
        for uid in ('hand100:v2:026','hand100:v2:064','hand100:v2:091','hand100:v2:100','challenge:015'):
            self.assertEqual(self.overrides[uid]['leakageRisk'],'high')
            self.assertEqual(self.overrides[uid]['admission'],'quarantine')
        self.assertFalse(any(r['leakageRisk']!='low' for r in self.train))

    def test_number_replacement_and_paraphrase_leakage(self):
        v=self.val[0]
        q={'uid':'fake:1','s':v['s'].replace('30','45').replace('20','35'),'familyId':'other'}
        self.assertEqual(b.leakage_check(q,[v])['risk'],'high')
        q={'uid':'fake:2','s':'一道判断竞赛，答对加1，答错减1，每一步分数大于0。','familyId':'other'}
        target=next(v for v in self.val if v['uid']=='real:2025:副省级:72')
        self.assertEqual(b.leakage_check(q,[target])['risk'],'high')

    def test_cross_paper_stable_identity_and_exposure_count(self):
        by_text={}
        for q in self.val:
            if not q['s']:continue
            key=(q['year'],b.normalize(q['s']))
            previous=by_text.setdefault(key,q['sourceQuestionUid'])
            self.assertEqual(previous,q['sourceQuestionUid'])
        n=len({q['sourceQuestionUid'] for q in self.val if q['scorable']})
        self.assertEqual(n,self.summary['validation']['uniqueScorableIdentities'])
        self.assertLess(n,self.summary['validation']['scorable'])

    def test_missing_national_slot_retained_as_empty_v3(self):
        snapshot=copy.deepcopy(self.snapshot)
        uid='real:2024:副省级:65'
        self.assertNotIn(uid,self.certs)
        snapshot['real']=[q for q in snapshot['real'] if q['uid']!=uid]
        val=b.assemble(snapshot,self.certs)[1]
        self.assertEqual(len(val),105)
        q=next(q for q in val if q['uid']==uid)
        self.assertEqual(q['s'],'');self.assertEqual(q['o'],[])
        self.assertEqual(q['validationStatus'],'V3');self.assertIsNone(q['a'])
        self.assertIn('missing_validation_slot',q['quarantineReasons'])

    def test_offline_hermetic_rebuild_without_untracked_raw_library(self):
        # Every temporary write is under the allowed datasets root. Resolve and
        # verify the directory immediately before recursive TemporaryDirectory cleanup.
        temp=tempfile.TemporaryDirectory(prefix='_rebuild_test_',dir=b.DATA)
        root=Path(temp.name).resolve()
        self.assertTrue(root.is_relative_to(b.DATA.resolve()))
        try:
            shutil.copyfile(Path(b.__file__),root/'build_datasets.py')
            (root/'datasets').mkdir()
            for name in ('sources.json','certificates.json'):
                shutil.copyfile(b.DATA/name,root/'datasets'/name)
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
            result=subprocess.run([sys.executable,str(root/'build_datasets.py')],cwd=root,env=env,
                                  capture_output=True,text=True,encoding='utf-8',timeout=120)
            self.assertEqual(result.returncode,0,result.stderr)
            for name in ('banks.js','manifest.json','audit.json','quarantine.json','summary.json',
                         'template_screening.json','authored_policy.json','authored_policy.js'):
                self.assertEqual((root/'datasets'/name).read_bytes(),(b.DATA/name).read_bytes(),name)
        finally:
            if not root.is_relative_to(b.DATA.resolve()):raise RuntimeError('unsafe temp cleanup')
            temp.cleanup()

    def test_generated_artifacts_check_is_read_only(self):
        files=[p for p in b.DATA.iterdir() if p.is_file()]
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        result=subprocess.run([sys.executable,str(Path(b.__file__)),'--check'],
                              env=dict(os.environ,PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1'),capture_output=True,
                              text=True,encoding='utf-8',timeout=120)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        self.assertEqual(before,after)

    @unittest.skipUnless(shutil.which('node'),'Node not installed: JS/core integration not executed')
    def test_javascript_globals_and_current_core_gates(self):
        script=r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context={window:{}};vm.createContext(context);
vm.runInContext(fs.readFileSync('datasets/banks.js','utf8'),context);
vm.runInContext(fs.readFileSync('datasets/authored_policy.js','utf8'),context);
const w=context.window,C=require('./core.js'),t=w.DATASET_TRAIN,v=w.DATASET_VALIDATION;
assert(Array.isArray(t)&&Array.isArray(v));assert.equal(v.length,105);
assert(t.every(C.trainEligible));assert(t.every(q=>!C.isValidation(q)));
assert(v.every(C.isValidation));assert.equal(v.filter(C.validationEligible).length,w.DATASET_AUDIT_SUMMARY.validation.scorable);
assert(v.filter(q=>q.validationStatus==='V3').every(q=>!C.validationEligible(q)));
assert.equal(Object.keys(w.DATASET_AUTHORED_OVERRIDES).length,124);
const bank=[...t,...v];
assert(C.sample(bank,{mode:'train',size:1000}).questions.every(C.trainEligible));
assert(C.sample(bank,{mode:'validation',size:1000}).questions.every(C.validationEligible));
assert.equal(C.sample(bank,{mode:'train',size:1000}).questions.length,t.length);
const first=v.find(C.validationEligible),key=C.validationIdentity(first);
assert(C.sample(bank,{mode:'validation',size:1000,exposures:[key]}).questions.every(q=>C.validationIdentity(q)!==key));
const mixed=C.sample(bank,{mode:'transfer',size:5}).questions;
assert.equal(mixed.length,5);assert.equal(mixed.filter(C.isValidation).length,2);
console.log(JSON.stringify({train:t.length,validationSlots:v.length,scorableSlots:v.filter(C.validationEligible).length,
uniqueValidationIdentities:new Set(v.filter(C.validationEligible).map(C.validationIdentity)).size,authoredOverrides:124}));
"""
        result=subprocess.run(['node','-e',script],cwd=b.HERE,capture_output=True,text=True,encoding='utf-8',timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        print('\nJS/core integration:',result.stdout.strip())


if __name__=='__main__':unittest.main(verbosity=2)
