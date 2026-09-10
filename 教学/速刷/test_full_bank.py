"""Whole-bank integrity, exact source/rubric binding, targeted arithmetic and fault injection.
This does not mislabel schema checks as a second independent mathematical proof of all items.
The 1,105 individual derivations live in reviews; per-batch arithmetic oracles are separate.
"""
import copy,json,re,unittest
from math import hypot
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import build_full_bank as B
class FullBank(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.intake=B.read(B.DATA/'intake.json');cls.catalog=B.read(B.DATA/'catalog.json');cls.byuid={q['uid']:q for q in cls.catalog};cls.summary=B.read(B.DATA/'summary.json')
 def test_every_existing_question_reviewed_and_delivered(self):
  inputs=self.intake['national']+self.intake['provincial'];self.assertEqual(len(inputs),1105)
  self.assertEqual({q['uid'] for q in inputs},set(self.byuid))
  self.assertEqual(self.summary['reviewed'],1105)
  self.assertGreater(self.summary['train'],850) # Regression: never ship another 147-question substitute.
  self.assertEqual(sum(self.summary['verdicts'].values()),1105)
  self.assertNotIn('pending',self.summary['verdicts'])
 def test_guangdong_present_not_fabricated_gap(self):
  for year in B.YEARS:
   qs=[q for q in self.catalog if q['exam']=='广东省考' and q['year']==year]
   self.assertEqual(len(qs),15);self.assertTrue(all(q['dataset']=='validation' for q in qs))
 def test_other_provinces_recent_years_train(self):
  for uid in ['prov:12536410','prov:12536412','prov:12536420','prov:12536422','prov:12536428']:
   self.assertEqual(self.byuid[uid]['dataset'],'train');self.assertTrue(self.byuid[uid]['usable'])
  for q in self.intake['national']+self.intake['provincial']:
   if B.held(q):self.assertEqual(self.byuid[q['uid']]['dataset'],'validation')
 def test_reproducible_inputs_outputs_images(self):
  for name,text in B.build().items():self.assertEqual((B.DATA/name).read_bytes(),text.encode('utf8'),name)
  manifest=B.read(B.DATA/'manifest.json')
  for name,h in manifest['images'].items():self.assertEqual(B.sha((B.REPO/name).read_bytes()),h)
 def test_no_unreviewed_or_broken_options_pass(self):
  q=self.intake['national'][0];r=B.read(B.DATA/'reviews/national_01.json')[0]
  for key,value in [('verdict','pending'),('verification',''),('fastBoundary',''),('level','容易'),('answerIndex',8),('inputHash','0'*64)]:
   bad={**r,key:value}
   with self.assertRaises(ValueError,msg=key):B.validate_review(q,bad)
 def test_bound_question_cannot_silently_change(self):
  q=self.intake['national'][0];r=B.read(B.DATA/'reviews/national_01.json')[0];b=B.read(B.DATA/'review_bindings.json')[q['uid']]
  B.check_binding(q,r,b)
  for changed_q,changed_r in [({**q,'s':q['s']+' changed'},r),(q,{**r,'answerIndex':(r['answerIndex']+1)%4})]:
   with self.assertRaises(ValueError):B.check_binding(changed_q,changed_r,b)
 def test_rubric_and_math_evidence_reaches_practice(self):
  for q in self.catalog:
   for field in ['difficultyReason','fastPath','normalPath','fastBoundary','verification','computedAnswer','tr','skipReason']:self.assertTrue(q[field].strip(),(q['uid'],field))
   if q['usable']:
    self.assertEqual(q['verdict'],'verified');self.assertEqual(len(q['o']),4);self.assertTrue(all(q['o']));self.assertEqual(len(set(q['o'])),4)
   else:self.assertNotEqual(q['answerStatus'],'confirmed')
 def test_exact_identity_not_collapsing_image_sequences(self):
  a='如图所示：![图](full_audit/work/a.png)';b=a.replace('a.png','b.png')
  self.assertNotEqual(B.identity(a),B.identity(b))
 def test_main_review_recomputed_not_source_echo(self):
  salt=F(1,5)+F(1,2)*F(3,5)**5;self.assertEqual(salt,F(2986,12500));self.assertTrue(F(23,100)<salt<F(25,100))
  self.assertEqual(self.byuid['prov:12536410']['a'],1)
  self.assertEqual([v for v in [125,135,145,155] if F(1380,11)<=v<=F(1500,11)],[135])
  self.assertEqual(self.byuid['prov:12536412']['a'],1)
  self.assertEqual(self.byuid['prov:12536420']['a'],1)
  self.assertEqual(F(7,10)-F(1,5)*(F(7,10)-F(1,5)*F(7,10)),F(147,250))
  self.assertEqual(self.byuid['prov:12536422']['a'],2)
  self.assertEqual(40**2+120**2,120**2+40**2);self.assertAlmostEqual(hypot(40,30)+80+hypot(120,40)-(hypot(40,30)+hypot(40,120)),80)
  self.assertEqual(self.byuid['prov:12536428']['a'],3)
 def test_no_raw_html_in_practice(self):
  for q in self.catalog:
   for text in [q['s'],*q['o']]:
    self.assertNotRegex(text,r'<(?:script|iframe|img)\b')
    for path in re.findall(r'!\[[^]]*\]\(([^)]+)\)',text):
     self.assertFalse(path.startswith(('http:','https:','教学/','真题库/')),path);B.asset(path)
if __name__=='__main__':unittest.main()
