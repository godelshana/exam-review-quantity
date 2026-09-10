"""Wait for this exact commit's Pages workflow, then verify deployed asset hashes.
Network is explicitly routed through the user-requested localhost:7890 proxy.
No credentials are read or printed. Public repository API only.
"""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[2]
REPO='godelshana/exam-review-quantity'
BASE='https://godelshana.github.io/exam-review-quantity/'
def get(url):
    r=subprocess.run(['curl.exe','--proxy','http://127.0.0.1:7890','-fsSL','--max-time','40','-H','Cache-Control: no-cache',url],capture_output=True)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf-8',errors='replace'))
    return r.stdout
def main():
    p=argparse.ArgumentParser();p.add_argument('--revision');p.add_argument('--wait',type=int,default=600);p.add_argument('--pages-only',action='store_true');a=p.parse_args()
    revision=a.revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    deadline=time.monotonic()+a.wait;run=None;last=None
    if not a.pages_only:
        while time.monotonic()<deadline:
            runs=json.loads(get(f'https://api.github.com/repos/{REPO}/actions/runs?head_sha={revision}&per_page=10'))['workflow_runs']
            matches=[r for r in runs if r.get('path')=='.github/workflows/pages.yml' and r['head_sha']==revision]
            run=max(matches,key=lambda r:r['id']) if matches else None
            status=(run.get('status'),run.get('conclusion')) if run else ('pending-visibility',None)
            if status!=last:print('Actions:',status,flush=True);last=status
            if run and run['status']=='completed':
                if run['conclusion']!='success':raise RuntimeError(f"Actions failed: {run['html_url']} ({run['conclusion']})")
                break
            time.sleep(15)
        else:raise TimeoutError('Exact-commit Actions did not complete before deadline')
    while time.monotonic()<deadline:
        try:
            version=json.loads(get(BASE+'version.json?rev='+revision))
            if version['revision']!=revision:raise ValueError('Pages still serves another commit: '+version['revision'])
            assets=[]
            for name,expected in version['assets'].items():
                local=subprocess.check_output(['git','show',f'{revision}:{name}'],cwd=ROOT)
                if hashlib.sha256(local).hexdigest()!=expected:raise ValueError('Published manifest not bound to committed source: '+name)
                content=get(BASE+quote(name,safe='/')+'?rev='+revision)
                if hashlib.sha256(content).hexdigest()!=expected:raise ValueError('Live asset mismatch: '+name)
                assets.append(name)
            assert version['validationYears']==[2024,2025,2026]
            print(json.dumps({'passed':True,'revision':revision,'actions':None if not run else {'id':run['id'],'conclusion':run['conclusion'],'url':run['html_url']},'url':BASE,'assetCount':len(assets),'verifiedAssets':assets},ensure_ascii=False,indent=2));return
        except (RuntimeError,ValueError,KeyError) as exc:
            print('Pages pending:',str(exc)[:200],flush=True);time.sleep(15)
    raise TimeoutError('Pages version/asset hashes did not match the committed release')
if __name__=='__main__':main()