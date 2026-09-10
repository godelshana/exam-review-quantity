"""Import locally available question figures into audited PNG copies; originals are untouched.
Default --check is stdlib-only and checks the committed, content-addressed image copies.
--import-local requires Pillow and Node.js, already used by the local image review tools.
No PDF pages or review contact sheets are ever selected automatically.
"""
from pathlib import Path
import argparse,hashlib,io,json,re
ROOT=Path(__file__).resolve().parent; REPO=ROOT.parents[1]; DATA=ROOT/'full_audit'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--import-local',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();mapping={}
 if a.import_local:
  from PIL import Image
  import subprocess
  paths={im['path'] for q in read(DATA/'intake.json')['provincial'] for im in q.get('images',[])}
  for p in sorted((DATA/'reviews').glob('*.json')):
   for q in read(p):
    paths.update(q.get('displayImages',[]))
    for text in [q.get('correctedStem') or '',*(q.get('correctedOptions') or [])]:
     paths.update(re.findall(r'!\[[^]]*\]\(([^)]+)\)',text))
  for path in sorted(paths):
   path=path.replace('\\','/')
   if path.startswith('../../'):path=path[6:]
   if path.startswith('full_audit/'):path='教学/速刷/'+path
   source=(REPO/path).resolve();assert source.is_relative_to(REPO.resolve()),path
   raw=source.read_bytes();decoded=raw;method='image-decode'
   try:im=Image.open(io.BytesIO(decoded));im.load()
   except Exception:
    decoded=subprocess.run(['node','-e',"process.stdout.write(require('node:zlib').brotliDecompressSync(require('node:fs').readFileSync(0)))"],input=raw,capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(decoded));im.load();method='brotli+image-decode'
   # White backing is essential for black formulas with transparent backgrounds.
   im=im.convert('RGBA');white=Image.new('RGBA',im.size,'white');white.alpha_composite(im);out=io.BytesIO();white.convert('RGB').save(out,format='PNG',compress_level=9);data=out.getvalue()
   dest='真题库/图片/已审计/'+sha(data)[:24]+'.png';target=REPO/dest;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   mapping[path]=dict(path=dest,sourceSha256=sha(raw),sha256=sha(data),width=im.width,height=im.height,decode=method)
  (DATA/'asset_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 else:mapping=read(DATA/'asset_map.json')
 for old,record in mapping.items():
  p=(REPO/record['path']).resolve();assert p.is_relative_to(REPO.resolve());data=p.read_bytes()
  assert data.startswith(b'\x89PNG\r\n\x1a\n') and sha(data)==record['sha256'],old
 print('PASS: original images preserved; content-addressed PNG copies:',len(mapping),'unique:',len({r['path'] for r in mapping.values()}),'Brotli recovered:',sum('brotli' in r['decode'] for r in mapping.values()))
if __name__=='__main__':main()
