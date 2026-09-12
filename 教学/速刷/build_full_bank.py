"""Build the complete audited real-question bank, offline and reproducibly.
Every intake UID requires a substantive individual review. Unreviewed != defective.
Only national/Guangdong 2024–2026 (and exact reprints) are reserved for tests.
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import argparse, hashlib, json, re
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
DATA = ROOT / 'full_audit'
YEARS = (2024, 2025, 2026)
LEVELS = ('入门', '熟练', '深化', '综合')
ASSET_MAP = {}
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b): return hashlib.sha256(b).hexdigest()
def object_sha(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8'))
def check_binding(q,r,b):
    if b.get('sourceSha256')!=object_sha(q) or b.get('reviewSha256')!=object_sha(r):raise ValueError(q['uid']+': question/review changed after individual audit; re-review required')
def dump(x): return json.dumps(x, ensure_ascii=False, indent=2) + '\n'
def held(q):
    return any(int(o.get('year') or 0) in YEARS and (o.get('exam')=='国考' or o.get('code')=='GD' or '广东' in o.get('exam','')) for o in [q, *q.get('occurrences',[])])
def identity(s):
    without=re.sub(r'!\[[^]]*\]\([^)]+\)', '', s)
    if len(re.findall(r'[\u4e00-\u9fff]',without))>=20:s=without
    return re.sub(r'[\s，。；：、,.!?！？;:（）()·—-]', '', s)
def asset(path):
    path=path.replace('\\','/')
    if path.startswith('../../'): path=path[6:]
    if path.startswith('full_audit/'): path='教学/速刷/'+path
    path=ASSET_MAP.get(path,{}).get('path',path)
    p=(REPO/path).resolve()
    if not p.is_relative_to(REPO.resolve()) or not p.is_file(): raise ValueError('Missing/unsafe image: '+path)
    return p.relative_to(REPO).as_posix()
def localize(text):
    return re.sub(r'!\[([^]]*)\]\(([^)]+)\)',lambda m:markdown(m[2],m[1]),text)
def markdown(path, alt='原卷题图'):
    path=asset(path)
    rel=path[len('教学/速刷/'):] if path.startswith('教学/速刷/') else '../../'+path
    return f'![{alt}]({rel})'
class StemParser(HTMLParser):
    def __init__(self,images):
        super().__init__();self.out=[];self.images={i['url'].replace('https:','').replace('http:',''):i['path'] for i in images}; self.refs=[]
    def handle_data(self,data):self.out.append(data)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('br','p'):self.out.append('\n')
        if tag=='img':
            url=a.get('src','').replace('https:','').replace('http:','')
            if url not in self.images: raise ValueError('Unresolved source image: '+url)
            path=self.images[url]; self.refs.append(path);self.out.append(markdown(path,'公式' if a.get('flag')=='tex' or 'formulas?' in url else '原卷题图'))
    def handle_endtag(self,tag):
        if tag in ('p','div'):self.out.append('\n')
def validate_review(q,r):
    if r.get('verdict') not in ('verified','disputed','invalid','off_module'):raise ValueError(q['uid']+': no actual verdict')
    for k in ('topic','level','difficultyReason','fastPath','normalPath','fastBoundary','fastMethod','skipReason','trap','familyId','computedAnswer','verification','knowledge','elimination'):
        if not isinstance(r.get(k),str) or not r[k].strip():raise ValueError(q['uid']+': empty '+k)
    if len(r['knowledge'])<16 or len(r['elimination'])<12:raise ValueError(q['uid']+': knowledge/elimination too thin to teach')
    if r['level'] not in LEVELS or r['fastValue'] not in ('high','medium','low') or r['skipDecision'] not in ('do','conditional','skip'):raise ValueError(q['uid']+': invalid rubric')
    if len(r['verification'])<8:raise ValueError(q['uid']+': no substantive verification')
    if r.get('inputHash') and r['inputHash']!=q['inputHash']:raise ValueError(q['uid']+': stale review binding')
    if r['verdict']=='verified' and (type(r.get('answerIndex')) is not int or not 0<=r['answerIndex']<4):raise ValueError(q['uid']+': no unique answer')
def build():
    global ASSET_MAP
    ASSET_MAP=read(DATA/'asset_map.json')
    intake=read(DATA/'intake.json'); questions=intake['national']+intake['provincial']; reviews={}; files={}
    for name in [*(f'national_{i:02}.json' for i in range(1,5)),*(f'provincial_{i:02}.json' for i in range(1,9))]:
        p=DATA/'reviews'/name
        if not p.is_file():raise ValueError('Review batch not complete: '+name)
        files['full_audit/reviews/'+name]=sha(p.read_bytes())
        for r in read(p):
            if r['uid'] in reviews:raise ValueError('Duplicate review '+r['uid'])
            reviews[r['uid']]=r
    assert len(questions)==len({q['uid'] for q in questions})
    if set(reviews)!={q['uid'] for q in questions}:raise ValueError('Incomplete review coverage: '+str(set(q['uid'] for q in questions)-set(reviews)))
    bindings=read(DATA/'review_bindings.json')
    if set(bindings)!={q['uid'] for q in questions}:raise ValueError('Incomplete source/review bindings')
    result=[]
    for q in questions:
        r=reviews[q['uid']];validate_review(q,r);check_binding(q,r,bindings[q['uid']])
        stem=localize(r.get('correctedStem') or q['s']); opts=[localize(o) for o in (r.get('correctedOptions') or q['o'])]; used=[]
        if q.get('stemHtml'):
            parser=StemParser(q.get('images',[]));parser.feed(q['stemHtml'])
            if not r.get('correctedStem'):stem=''.join(parser.out).strip()
            else:
                # Transcribed formulas already sit in the corrected text. Retain actual diagrams only.
                for im in q.get('images',[]):
                    if 'formulas?' not in im['url'] and im['path'] not in used:
                        mark=markdown(im['path']);used.append(im['path'])
                        if mark not in stem:stem+='\n'+mark
        already={asset(p) for text in [stem,*opts] for p in re.findall(r'!\[[^]]*\]\(([^)]+)\)',text)}
        for path in r.get('displayImages',[]):
            if asset(path) not in already:stem+='\n'+markdown(path);already.add(asset(path))
        # Explicit image references in corrections are always local and checked.
        for text in [stem,*opts]:
            for path in re.findall(r'!\[[^]]*\]\(([^)]+)\)',text):asset(path)
        ok=r['verdict']=='verified'
        if ok and (not stem.strip() or len(opts)!=4 or any(not str(x).strip() for x in opts) or len(set(opts))!=4):raise ValueError(q['uid']+': unusable reviewed question/options')
        exam=q.get('exam','国考'); label=f"[{q['year']}·{exam}·{q.get('variant') or q.get('paper','')}·{q.get('number','')}]"
        a=r.get('answerIndex'); provenance=dict(q.get('source',{}));provenance['originalAnswer']=q.get('sourceAnswer');provenance['auditNotes']=r.get('reviewNotes','')
        x=dict(uid=q['uid'],s=stem,o=opts,a=a,year=q['year'],exam=exam,province=q.get('province','国考'),paper=q.get('paper'),number=q.get('number'),occurrences=q.get('occurrences',[]),source='real',sourceType='real',sourceLabel=label,provenance=provenance,dataset='validation' if held(q) else 'train',validationStatus=(('V2' if r.get('sourceAgreement') is False else 'V1') if ok else 'V3') if held(q) else None,answerStatus='confirmed' if ok else r['verdict'],imageStatus='complete' if ok else 'reviewed',explanationStatus='P2',mathAudit='passed' if ok else r['verdict'],leakageRisk='low',usable=ok,verdict=r['verdict'],h=r['topic'],topic=r['topic'],level=r['level'],difficultyReason=r['difficultyReason'],familyId=r['familyId'],t='真题',e=r['fastPath'],tr=r['trap'],hint=(r.get('knowledge') or '').split('。')[0].strip(),timeLimit=dict(zip(LEVELS,(45,65,90,120)))[r['level']],sourceAnswer=q.get('sourceAnswer'),sourceAgreement=r.get('sourceAgreement'),computedAnswer=r['computedAnswer'],verification=r['verification'],knowledge=r.get('knowledge',''),elimination=r.get('elimination',''),reviewNotes=r.get('reviewNotes',''),inputHash=q['inputHash'],reviewHash=sha(json.dumps(r,ensure_ascii=False,sort_keys=True).encode()))
        for k in ('fastPath','normalPath','fastBoundary','fastValue','fastMethod','skipDecision','skipReason','knowledge','elimination'):x[k]=localize(r[k]) if isinstance(r[k],str) else r[k]
        if r.get('practiceAssumption'):x['practiceAssumption']=r['practiceAssumption']
        if r.get('correctedStem'):x['originalStem']=q['s']
        if r.get('correctedOptions'):x['originalOptions']=q['o']
        x['sourceQuestionUid']='real-shared:'+sha(identity(stem).encode())[:24]
        result.append(x)
    # Exact reprints are preserved as occurrences, not repeated first tests.
    reserved={x['sourceQuestionUid'] for x in result if x['dataset']=='validation'}
    for x in result:
        if x['sourceQuestionUid'] in reserved:
            x['dataset']='validation';x['validationStatus']=('V2' if x['sourceAgreement'] is False else 'V1') if x['usable'] else 'V3'
    train=[x for x in result if x['dataset']=='train' and x['usable']]
    validation=[x for x in result if x['dataset']=='validation']
    study=[x for x in result if x['dataset']=='train' and not x['usable'] and x['verdict']!='off_module']
    images=set()
    for x in [*train,*validation,*study]:
        for t in [x['s'],*x['o'],x['e'],x['normalPath'],x['verification']]:
            for path in re.findall(r'!\[[^]]*\]\(([^)]+)\)',t):images.add(asset(path))
    summary=dict(input=intake['summary'],reviewed=len(reviews),verdicts=dict(Counter(x['verdict'] for x in result)),train=len(train),trainUnique=len({x['sourceQuestionUid'] for x in train}),validationSlots=len(validation),validationUsable=sum(x['usable'] for x in validation),validationUnique=len({x['sourceQuestionUid'] for x in validation if x['usable']}),study=len(study),byLevel=dict(Counter(x['level'] for x in train)),byProvince=dict(Counter(x['province'] for x in train)),trainByOccurrenceProvince={p:sum(p in {x['province'],*(o.get('province','') for o in x['occurrences'])} for x in train) for p in ('国考','安徽','广东','湖北','河南','四川')},images=len(images),coverage=[])
    for exam in ('国考','广东省考'):
        for year in YEARS:
            xs=[x for x in validation if x['year']==year and x['exam']==exam]
            summary['coverage'].append(dict(exam=exam,year=year,slots=len(xs),verified=sum(x['validationStatus']=='V1' for x in xs),provisional=sum(x['validationStatus']=='V2' for x in xs),disputed=sum(x['verdict']=='disputed' for x in xs),invalid=sum(x['verdict']=='invalid' for x in xs)))
    files.update({'full_audit/intake.json':sha((DATA/'intake.json').read_bytes()),'build_full_bank.py':sha(Path(__file__).read_bytes()),'full_audit/asset_map.json':sha((DATA/'asset_map.json').read_bytes()),'full_audit/review_bindings.json':sha((DATA/'review_bindings.json').read_bytes())})
    manifest=dict(schema=1,inputs=files,images={p:sha((REPO/p).read_bytes()) for p in sorted(images)},reviewCoverage=len(reviews))
    js='/* Individually audited real questions. Generated by build_full_bank.py. */\n'+''.join(f'window.{name} = '+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';\n' for name,value in [('FULL_REAL_TRAIN',train),('FULL_REAL_VALIDATION',validation),('FULL_REAL_STUDY',study),('FULL_REAL_SUMMARY',summary)])
    return {'banks.js':js,'summary.json':dump(summary),'manifest.json':dump(manifest),'catalog.json':dump(result)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for name,text in build().items():
        p=DATA/name
        if args.check:
            if not p.exists() or p.read_bytes()!=text.encode('utf8'):raise SystemExit('STALE '+str(p))
        else:p.write_text(text,encoding='utf8',newline='\n')
    print('PASS: complete individual coverage, rubric, local images, reproducible full bank' if args.check else 'Complete bank built')
if __name__=='__main__':main()
