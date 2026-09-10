"""Explicitly seal completed individual reviews to the exact source payloads.
This is provenance bookkeeping, NOT a substitute for mathematical review/oracles.
Never run automatically on changed inputs in CI. Re-audit a changed question first.
"""
import argparse
import build_full_bank as B
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seal-reviewed-inputs',action='store_true',required=True);ap.parse_args()
 intake=B.read(B.DATA/'intake.json');questions={q['uid']:q for q in intake['national']+intake['provincial']};bindings={}
 for p in sorted((B.DATA/'reviews').glob('*.json')):
  for r in B.read(p):
   q=questions[r['uid']];B.validate_review(q,r)
   if r['uid'] in bindings:raise ValueError('duplicate review')
   bindings[r['uid']]=dict(batch=p.name,sourceSha256=B.object_sha(q),reviewSha256=B.object_sha(r))
 if set(bindings)!=set(questions):raise ValueError('Cannot seal an incomplete audit')
 (B.DATA/'review_bindings.json').write_text(B.dump(bindings),encoding='utf8',newline='\n')
 print('Sealed reviewed source/overlay pairs:',len(bindings),'; mathematical review remains in reviews and oracles, not this checksum')
if __name__=='__main__':main()
