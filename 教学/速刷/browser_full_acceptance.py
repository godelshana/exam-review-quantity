"""Full real-bank browser integration on a disposable localhost origin only."""
import argparse,json
from pathlib import Path
from urllib.parse import urlparse
from browser_acceptance import bridge,evaluate,LAYOUT
ROOT=Path(__file__).resolve().parent
CODE=r"""(async()=>{
 const $=id=>document.getElementById(id),assert=(x,m)=>{if(!x)throw Error(m)},set=(id,v)=>{$(id).value=v;$(id).dispatchEvent(new Event('change'))},records=()=>JSON.parse(localStorage.getItem('quantity-ladder-v3')).attempts;
 const C=DrillCore,all=[...FULL_REAL_TRAIN,...FULL_REAL_VALIDATION],find=()=>all.find(q=>q.uid===$('stem').dataset.uid),checks=[];
 set('source','train');set('bankScope','real');set('level','all');set('mode','practice');set('length','5');set('topicFilter','all');
 for(const province of ['四川','广东','湖北']){
  set('provinceFilter',province);const count=Number($('filterInfo').textContent.match(/当前可选 (\d+)/)[1]);if(province==='湖北')assert(count>50,'cross-province reprints not lost');
  const before=records().length;$('start').click();
  for(let n=0;n<5;n++){const q=find();assert(q&&C.trainEligible(q),'real training question');assert(q.province===province||(q.occurrences||[]).some(o=>o.province===province),'province filter');if(province==='广东')assert(q.year<2024,'Guangdong holdout exclusion');document.querySelectorAll('#opts button')[q.a].click();$('next').click();}
  assert(records().length===before+5&&records().slice(-5).every(r=>r.correct),'five real answers and round-trip');$('back').click();checks.push(province+' five-question round');
 }
 function openCatalog(uid){
  set('provinceFilter','all');set('level','all');$('catalogPanel').open=true;$('catalogPanel').dispatchEvent(new Event('toggle'));set('catalogType','train');
  let b=null;for(let n=0;n<100;n++){b=[...document.querySelectorAll('.catalog-practice')].find(b=>b.dataset.uid===uid);if(b||$('catalogNext').disabled)break;$('catalogNext').click();}
  assert(b,'specific reviewed question exists in actual catalog: '+uid);return b;
 }
 const before=records().length;openCatalog('prov:12536410').click();assert(find().year===2024&&find().province==='四川','recent Sichuan actually trainable');assert($('qno').textContent==='1 / 1','single selection uses one question');document.querySelectorAll('#opts button')[find().a].click();$('next').click();assert(records().length===before+1&&records().at(-1).training==='random','single-question practice excluded from promotion');$('back').click();checks.push('2024 Sichuan direct practice and single-question scoring');
 openCatalog('real:2016:地市级:65').click();assert(document.querySelectorAll('#opts img').length===4,'all graphical options render as images');document.querySelectorAll('#opts button')[find().a].click();$('next').click();assert(document.querySelectorAll('#result .review-body img').length>=4,'graph options also render in review');assert(document.documentElement.scrollWidth<=innerWidth,'image review has no horizontal overflow');$('back').click();checks.push('graphical options in practice and result');
 set('provinceFilter','all');set('catalogType','study');$('catalogPanel').open=true;$('catalogPanel').dispatchEvent(new Event('toggle'));assert($('catalogCount').textContent.startsWith(FULL_REAL_STUDY.length+' 题'),'every disputed/defective training item accessible');assert($('catalogItems').textContent.includes('不强行评分'),'disputes not silent grading');assert(!$('catalogItems').querySelector('.catalog-practice'),'disputes cannot masquerade as verified questions');checks.push('non-scoring dispute studies');
 const paths=[...new Set(all.concat(FULL_REAL_STUDY).flatMap(q=>[q.s,...q.o,q.fastPath,q.normalPath,q.verification]).flatMap(s=>[...String(s||'').matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)].map(m=>m[1])))];
 const bad=[];let cursor=0;await Promise.all(Array.from({length:12},async()=>{while(cursor<paths.length){const path=paths[cursor++];try{const img=new Image();img.loading='eager';img.style.cssText='position:fixed;left:0;top:0;width:1px;height:1px;opacity:0';const response=await fetch(path,{cache:'reload'});if(!response.ok)throw Error('HTTP '+response.status);const blobURL=URL.createObjectURL(await response.blob());img.src=blobURL;document.body.appendChild(img);try{await Promise.race([img.decode(),new Promise((_,reject)=>setTimeout(()=>reject(Error('decode timeout')),5000))]);if(!img.naturalWidth||!img.naturalHeight)bad.push(path);}finally{img.remove();URL.revokeObjectURL(blobURL);}}catch{bad.push(path);}}}));assert(bad.length===0,'all published formulas/figures decode: '+bad.join(','));checks.push(paths.length+' distinct image references decoded');
 $('catalogPanel').open=false;set('catalogType','train');set('level','入门');set('provinceFilter','all');
 return JSON.stringify({passed:true,checks,imageCount:paths.length,brokenImages:bad,summary:FULL_REAL_SUMMARY,layout:{width:innerWidth,scrollWidth:document.documentElement.scrollWidth}});
})()"""
def main():
 p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8876/教学/速刷/刷题页面.html');a=p.parse_args()
 if urlparse(a.url).hostname not in ['localhost','127.0.0.1']:raise SystemExit('Disposable local origin required')
 bridge('navigate',{'url':a.url+'?full-bank-acceptance'})
 bridge('cdp',{'method':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
 bridge('cdp',{'method':'Page.bringToFront','params':{}})
 result=evaluate(CODE);assert result['passed'],result
 layout=evaluate(LAYOUT);assert layout['scrollWidth']<=390 and not layout['smallControls'],layout
 missing=evaluate("""(async()=>{const before=localStorage.getItem('quantity-ladder-v3');delete window.FULL_REAL_TRAIN;(0,eval)(await(await fetch('app.js')).text());return JSON.stringify({blocked:document.getElementById('start').disabled,error:!document.getElementById('loadError').hidden,unchanged:localStorage.getItem('quantity-ladder-v3')===before});})()""");assert all(missing.values()),missing
 bridge('navigate',{'url':a.url+'?full-bank-tested'})
 result['missingRealBank']=missing;result['layout']=layout
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
