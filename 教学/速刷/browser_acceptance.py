"""Repeatable real-Chrome acceptance via the user's existing WebBridge daemon.
Runs only on a disposable localhost origin; never clears browser storage.
Windows sends UTF-8 request bodies as unique files, not inline shell JSON.
"""
import argparse, json, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SESSION='quantity-full-bank'
def bridge(action,args):
    with tempfile.NamedTemporaryFile('w',suffix='.json',encoding='utf-8',delete=False) as f:
        json.dump({'action':action,'args':args,'session':SESSION},f,ensure_ascii=False); name=f.name
    try:
        r=subprocess.run(['curl.exe','--max-time','120','-sS','-X','POST','http://127.0.0.1:10086/command','-H','Content-Type: application/json','--data-binary','@'+name],capture_output=True,check=True)
        data=json.loads(r.stdout.decode('utf-8'))
        if not data.get('ok'):raise RuntimeError(data)
        return data['data']
    finally:Path(name).unlink(missing_ok=True)
def evaluate(js):
    data=bridge('evaluate',{'code':js})
    value=data.get('value',data)
    if isinstance(value,str):
        try:return json.loads(value)
        except json.JSONDecodeError:pass
    return value
LAYOUT="""(()=>{const visible=[...document.querySelectorAll('button,select,summary')].filter(e=>e.getClientRects().length);return JSON.stringify({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,smallControls:visible.filter(e=>e.getBoundingClientRect().height<44).map(e=>({id:e.id,text:e.textContent.slice(0,30),h:e.getBoundingClientRect().height})),bankInfo:document.getElementById('bankInfo').textContent,loadErrorHidden:document.getElementById('loadError').hidden});})()"""
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8874/教学/速刷/刷题页面.html');a=p.parse_args()
    from urllib.parse import urlparse
    if urlparse(a.url).hostname not in ['127.0.0.1','localhost']:raise SystemExit('Use a disposable local origin, never live learner storage')
    results={}
    for width,height in [(1920,1080),(390,844)]:
        bridge('navigate',{'url':a.url+'?acceptance='+str(width)})
        bridge('cdp',{'method':'Network.enable','params':{}})
        bridge('cdp',{'method':'Network.setCacheDisabled','params':{'cacheDisabled':True}})
        bridge('cdp',{'method':'Emulation.setDeviceMetricsOverride','params':{'width':width,'height':height,'deviceScaleFactor':1,'mobile':width==390}})
        result=evaluate((ROOT/'browser_smoke.js').read_text(encoding='utf-8'))
        if not result['pass'] or result['skipped']:raise AssertionError(result)
        layout=evaluate(LAYOUT)
        assert layout['scrollWidth']<=width and not layout['smallControls'] and layout['loadErrorHidden'],layout
        results[str(width)]={'smoke':result,'layout':layout}
    # Clock jump simulates a hard deadline without waiting several minutes.
    results['deadline']=evaluate("""(async()=>{const $=id=>document.getElementById(id),set=(id,v)=>{$(id).value=v;$(id).dispatchEvent(new Event('change'))};set('source','transfer');$('start').click();const n=JSON.parse(localStorage.getItem('quantity-ladder-v3')).attempts.length;const now=Date.now;Date.now=()=>now()+3600000;try{await new Promise(r=>setTimeout(r,450));const rows=JSON.parse(localStorage.getItem('quantity-ladder-v3')).attempts;return JSON.stringify({finished:!$('result').hidden,added:rows.length-n,timedOut:rows.at(-1).timedOut,skip:rows.at(-1).pick});}finally{Date.now=now;}})()""")
    assert results['deadline']=={'finished':True,'added':1,'timedOut':True,'skip':-1},results['deadline']
    bridge('navigate',{'url':a.url+'?acceptance=reload'})
    results['reload']=evaluate("""(()=>{const x=JSON.parse(localStorage.getItem('quantity-ladder-v3')),C=DrillCore;const pool=FULL_REAL_VALIDATION.map(C.normalize);const out=C.sample(pool,{mode:'validation',size:1000,attempts:x.attempts,exposures:x.exposures});return JSON.stringify({persistedExposures:x.exposures.length,noExposedReentry:out.questions.every(q=>!x.exposures.includes(C.validationIdentity(q))),restoredAttempts:C.restore(x).db.attempts.length===x.attempts.length});})()""")
    assert results['reload']['persistedExposures']>0 and results['reload']['noExposedReentry'] and results['reload']['restoredAttempts']
    # Missing mandatory policy must not quietly restore the previous broad training pool.
    results['missingPolicy']=evaluate("""(async()=>{const before=localStorage.getItem('quantity-ladder-v3');delete window.DATASET_AUTHORED_OVERRIDES;const code=await (await fetch('app.js')).text();(0,eval)(code);return JSON.stringify({blocked:document.getElementById('start').disabled,errorVisible:!document.getElementById('loadError').hidden,storageUnchanged:localStorage.getItem('quantity-ladder-v3')===before});})()""")
    assert all(results['missingPolicy'].values()),results['missingPolicy']
    bridge('navigate',{'url':a.url+'?acceptance=complete'})
    print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()