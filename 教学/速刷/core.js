/* Pure training engine: reusable in browser and Node regression tests. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.DrillCore=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
'use strict';
const levels=['入门','熟练','深化','综合'];
const limits={入门:35,熟练:55,深化:75,综合:100};
const norm=s=>String(s).replace(/\s+/g,'');
function normalize(q){return {...q,uid:q.uid||q.curationId,sourceType:q.sourceType||'mock',timeLimit:q.timeLimit||q.targetSeconds||limits[q.level]||60,hint:q.hint||q.signal,template:q.template||norm(q.s).replace(/\d+(\.\d+)?/g,'#')};}
function eligible(q){return !!q.uid&&typeof q.s==='string'&&Array.isArray(q.o)&&q.o.length===4&&Number.isInteger(q.a)&&q.a>=0&&q.a<4&&q.t!=='跳过';}
function sample(source,{size=5,strategy='random',memory={},rng=Math.random}={}){
  const seen=new Set(),uids=new Set();let pool=source.filter(q=>{const k=norm(q.s);if(seen.has(k)||uids.has(q.uid)||!eligible(q))return false;seen.add(k);uids.add(q.uid);return true;});
  pool=pool.map(q=>{const m=memory[q.uid];const w=strategy==='weak'?1+Math.min(8,(m?.wrong||0)*2+(m?.slow||0)):strategy==='fresh'?(m?0.15:4):1;
    return {q,key:-Math.log(Math.max(1e-12,Math.min(1-1e-12,rng())))/w};}).sort((a,b)=>a.key-b.key).map(x=>x.q);
  const out=[];let relaxed=0,topicRelaxed=0;
  while(out.length<Math.min(size,source.length)&&pool.length){
    const chunk=out.slice(Math.floor(out.length/5)*5);const templates=new Set(chunk.map(q=>q.template));
    const hooks={};chunk.forEach(q=>hooks[q.h]=(hooks[q.h]||0)+1);
    let i=pool.findIndex(q=>!templates.has(q.template)&&(hooks[q.h]||0)<2);
    if(i<0){i=pool.findIndex(q=>!templates.has(q.template));if(i>=0)topicRelaxed++;}
    if(i<0){i=0;relaxed++;}out.push(pool.splice(i,1)[0]);
  }
  return {questions:out,relaxed,topicRelaxed};
}
function shuffled(q,rng=Math.random){const map=[0,1,2,3];for(let i=3;i>0;i--){const j=Math.floor(rng()*(i+1));[map[i],map[j]]=[map[j],map[i]];}return {opts:map.map(i=>q.o[i]),answer:map.indexOf(q.a),map};}
function summary(rows){const n=rows.length,attempted=rows.filter(r=>r.pick>=0).length,correct=rows.filter(r=>r.correct).length;
  const fast=rows.filter(r=>r.correct&&!r.hinted&&!r.paused&&r.confidence!=='猜测'&&r.secs<=r.limit).length;
  const times=rows.map(r=>r.secs).sort((a,b)=>a-b);const median=n?(n%2?times[(n-1)/2]:(times[n/2-1]+times[n/2])/2):0;
  return {n,attempted,correct,skips:n-attempted,accuracy:n?correct/n:0,attemptAccuracy:attempted?correct/attempted:0,fast,median};}
function contentKey(q){return JSON.stringify([q?.s,q?.o,q?.a,q?.level,q?.e,q?.tr]);}
function currentAttempts(rows,questions){const active=new Map(questions.filter(eligible).map(q=>[q.uid,q]));return rows.filter(r=>active.has(r.uid)&&r.q&&contentKey(r.q)===contentKey(active.get(r.uid)));}
function promotion(rows,level,questions=[]){const unique=new Map();currentAttempts(rows,questions).filter(r=>r.level===level&&r.source==='authored'&&r.training==='ladder').forEach(r=>{unique.delete(r.uid);unique.set(r.uid,r);});
  const recent=[...unique.values()].slice(-20);const s=summary(recent);return {ready:s.n>=10&&s.accuracy>=.8&&s.fast/s.n>=.6&&level!==levels.at(-1),...s};}
// Only structured option references are remapped; A产品 / B机器 are object names.
function mappedExplanation(text,map){return String(text).replace(/\[\[option:([ABCD])\]\]/g,(_,l)=>'ABCD'[map.indexOf('ABCD'.indexOf(l))]);}
function validAttempt(r){
 if(!r||typeof r!=='object'||typeof r.uid!=='string'||!['authored','glm','real'].includes(r.source)||typeof r.level!=='string')return false;
 if(!Number.isInteger(r.pick)||r.pick< -1||r.pick>3||!Number.isInteger(r.answer)||r.answer<0||r.answer>3||typeof r.correct!=='boolean'||r.correct!==(r.pick===r.answer))return false;
 if(!Number.isFinite(r.secs)||r.secs<0||!Number.isFinite(r.limit)||r.limit<=0||typeof r.hinted!=='boolean'||typeof r.paused!=='boolean')return false;
 if(!r.q||!eligible(r.q)||r.q.uid!==r.uid||!Array.isArray(r.map)||r.map.length!==4||[...r.map].sort().join('')!=='0123')return false;
 return Array.isArray(r.options)&&r.options.length===4&&r.options.every((o,i)=>typeof o==='string'&&o===r.q.o[r.map[i]])&&r.answer===r.map.indexOf(r.q.a);
}
function restore(value){
 const blank={schema:3,attempts:[],level:'入门'};
 if(!value||value.schema!==3||!Array.isArray(value.attempts))return {db:blank,needsBackup:!!value};
 const attempts=value.attempts.filter(validAttempt),level=[...levels,'all'].includes(value.level)?value.level:'入门';
 return {db:{schema:3,attempts,level},needsBackup:attempts.length!==value.attempts.length||level!==value.level};
}
return {levels,limits,normalize,eligible,sample,shuffled,summary,promotion,mappedExplanation,contentKey,currentAttempts,validAttempt,restore};
});
