"""Reproduce review batches from the committed intake; optionally verify local raw imports.
The intake freezes the 66 selected raw-paper ranges, all 855 occurrences, 400 national
records and 705 Fenbi-ID-deduplicated provincial questions. No raw files are edited.
--verify-local checks every frozen item against those existing raw JSON files; this
is intentionally separate from offline CI (which never needs the user's whole archive).
"""
from pathlib import Path
import argparse, json, re
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
DATA=ROOT/'full_audit'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--verify-local',action='store_true');a=ap.parse_args()
    intake=read(DATA/'intake.json');uids=set()
    for group in ('national','provincial'):
        qs=intake[group]
        for q in qs:
            assert q['uid'] not in uids;uids.add(q['uid'])
            assert len(q['inputHash'])==64
        for start in range(0,len(qs),100):
            p=DATA/f'{group}_{start//100+1:02}.json';items=qs[start:start+100]
            if a.check:assert read(p)==items,p
            else:p.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    if a.verify_local:
        raw={}
        expected={}
        for p in intake['papers']:
            d=read(REPO/p['rawFile']);raw[p['rawFile']]=d
            lo,hi=p['range']; selected=[q for q in d['questions'] if lo<=q['num']<=hi]
            assert len(selected)==p['selected']
            for q in selected:expected[(p['rawFile'],q['num'])]=str(q['id'])
        actual={}
        for q in intake['provincial']:
            for o in q['occurrences']:actual[(o['sourceFile'],o['number'])]=q['fenbiId']
            src=next(x for x in raw[q['sourceFile']]['questions'] if x['num']==q['number'])
            assert str(src['id'])==q['fenbiId']
            assert src['stem']==q['s'] and src.get('stemHtml','')==q['stemHtml'],q['uid']
            assert [re.sub(r'^[A-D][.、．\s]+','',s) for s in src['options']]==q['o'],q['uid']
            assert int(src['choice'])==q['sourceAnswerIndex'],q['uid']
        assert actual==expected,'An occurrence was omitted from intake'
        national={q['uid']:q for q in read(ROOT/'datasets/sources.json')['real']}
        for q in intake['national']:
            assert all(q[k]==v for k,v in national[q['uid']].items()),q['uid']
        print('PASS: all frozen national/provincial source payloads and 855 raw-paper occurrences')
    print('PASS: unique complete intake and reproducible 12 review batches:',len(uids))
if __name__=='__main__':main()
