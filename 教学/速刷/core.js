/* Pure engine. Dataset boundaries are enforced here, not only by UI filters. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.DrillCore=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
'use strict';
const levels=['入门','熟练','深化','综合'];
const limits={入门:35,熟练:55,深化:75,综合:100};
const norm=s=>String(s??'').replace(/\s+/g,'');
function isValidation(q){
 if(!q)return false;
 if(q.dataset==='validation')return true;
 const records=[q,...(Array.isArray(q.occurrences)?q.occurrences:[])];
 if(records.some(o=>[o.year,o.sourceYear,o.originYear].some(y=>[2024,2025,2026].includes(Number(y)))&&(/国考|广东|national|guangdong/i.test([o.exam,o.province,o.sourceExam].filter(Boolean).join(' '))||o.code==='GD')))return true;
 const provenance=[q.uid,q.sourceQuestionUid,q.sourceLabel,typeof q.provenance==='string'?q.provenance:JSON.stringify(q.provenance?{exam:q.provenance.exam,year:q.provenance.year,path:q.provenance.path,locator:q.provenance.locator}:{} )].filter(Boolean).join(' ');
 return /(?:real|national|guangdong|heldout):(?:2024|2025|2026):/i.test(provenance)||(/\b(?:2024|2025|2026)\b/.test(provenance)&&/国考|广东|paper_GD_/.test(provenance));
}
// Numeric sequences cannot all collapse into one family just because digits were removed.
function leakageKey(q){const s=norm(q.s);return q.sourceType==='real'&&((s.match(/[\u4e00-\u9fff]/g)||[]).length<5||/数字推理|数列/.test(q.topic||q.h||''))?'exact:'+s:s.replace(/\d+(\.\d+)?/g,'#');}
function normalize(q){
 const authored=/^(hand100:v2:\d{3}|challenge:\d{3})$/.test(q.uid||'')&&q.sourceType==='mock';
 const defaults=authored?{dataset:'train',answerStatus:'confirmed',imageStatus:'complete',explanationStatus:'P2',mathAudit:'passed',leakageRisk:'low',auditBasis:'release_manifest: independent review + executable math oracle'}:{};
 const x={...defaults,...q};
 return {...x,uid:q.uid||q.curationId,dataset:isValidation(x)?'validation':x.dataset,
  sourceType:q.sourceType||'mock',timeLimit:q.timeLimit||q.targetSeconds||limits[q.level]||60,hint:q.hint||q.signal,
  template:q.template||norm(q.s).replace(/\d+(\.\d+)?/g,'#'),familyId:q.familyId||q.template||q.family||norm(q.s).replace(/\d+(\.\d+)?/g,'#'),
  fastPath:q.fastPath||q.e,normalPath:q.normalPath||q.e,fastBoundary:q.fastBoundary||'以上述题目条件为限；条件变化须重新列式，没有额外可靠的省步法时使用常规推导。',
  fastMethod:q.fastMethod||'normal',fastValue:q.fastValue||'low',skipDecision:q.skipDecision||(q.level==='综合'?'conditional':'do')};
}
function eligible(q){return !!q&&!!q.uid&&typeof q.s==='string'&&q.s.trim().length>0&&Array.isArray(q.o)&&q.o.length===4&&q.o.every(o=>typeof o==='string'&&o.trim())&&new Set(q.o.map(norm)).size===4&&Number.isInteger(q.a)&&q.a>=0&&q.a<4&&q.t!=='跳过';}
function mathPassed(q){return q.mathAudit==='passed'||q.mathAudit?.status==='passed';}
function trainEligible(q){return eligible(q)&&q.usable!==false&&q.admission!=='quarantine'&&q.dataset==='train'&&!isValidation(q)&&q.answerStatus==='confirmed'&&q.imageStatus==='complete'&&q.explanationStatus==='P2'&&mathPassed(q)&&q.leakageRisk==='low'&&!!q.e&&!!q.tr;}
function validationEligible(q){return eligible(q)&&q.usable!==false&&q.admission!=='quarantine'&&isValidation(q)&&['V1','V2'].includes(q.validationStatus)&&q.imageStatus==='complete'&&q.answerStatus==='confirmed'&&!!q.e&&(q.validationStatus!=='V1'||(mathPassed(q)&&q.explanationStatus==='P2'));}
function validationIdentity(q){return q.sourceQuestionUid||norm(q.s);}
function migrateValidationExposures(exposures=[],attempts=[],legacy=[],current=[]){
 const out=new Set(exposures),active=new Map(current.filter(isValidation).map(q=>[q.uid,q]));
 for(const q of legacy){const next=active.get(q.uid);if(next&&out.has(validationIdentity(q)))out.add(validationIdentity(next));}
 for(const r of attempts){const next=active.get(r.uid);if(next&&r.q&&(isValidation(r.q)||r.dataset==='validation'))out.add(validationIdentity(next));}
 return [...out];
}
function seenValidation(attempts=[],exposures=[]){const ids=new Set(exposures);attempts.filter(r=>r&&isValidation(r.q)).forEach(r=>ids.add(validationIdentity(r.q)));return ids;}
function sample(source,{size=5,strategy='random',memory={},rng=Math.random,mode='train',attempts=[],exposures=[]}={}){
 const seen=new Set(),uids=new Set(),validationIds=new Set(),exposed=seenValidation(attempts,exposures);
 const validationStems=new Set(source.filter(isValidation).map(q=>leakageKey(q)));
 let pool=source.filter(q=>{
  const v=isValidation(q),k=norm(q.s);
  if(!['train','transfer','validation','validation-review'].includes(mode))return false;
  if(v){if(mode==='train'||!validationEligible(q))return false;
   if(mode==='validation-review'?!exposed.has(validationIdentity(q)):exposed.has(validationIdentity(q)))return false;
  }else if(!['train','transfer'].includes(mode)||!trainEligible(q)||validationStems.has(leakageKey(q)))return false;
  if(seen.has(k)||uids.has(q.uid)||(v&&validationIds.has(validationIdentity(q))))return false;seen.add(k);uids.add(q.uid);if(v)validationIds.add(validationIdentity(q));return true;
 });
 pool=pool.map(q=>{const m=isValidation(q)?null:memory[q.uid];const w=isValidation(q)?1:strategy==='weak'?1+Math.min(8,(m?.wrong||0)*2+(m?.slow||0)):strategy==='fresh'?(m?0.15:4):1;
  return {q,key:-Math.log(Math.max(1e-12,Math.min(1-1e-12,rng())))/w};}).sort((a,b)=>a.key-b.key).map(x=>x.q);
 const out=[];let relaxed=0,topicRelaxed=0;const count=Math.max(0,Math.min(1000,Math.floor(Number(size)||0)));
 while(out.length<count&&pool.length){
  const chunk=out.slice(Math.floor(out.length/5)*5),families=new Set(chunk.map(q=>q.familyId||q.template)),hooks={};chunk.forEach(q=>hooks[q.h]=(hooks[q.h]||0)+1);
  let candidates=pool.map((q,i)=>({q,i}));
  if(mode==='transfer'){
   const wantValidation=chunk.length>=3||(!chunk.length&&pool.every(isValidation));
   const desired=candidates.filter(({q})=>isValidation(q)===wantValidation);if(desired.length)candidates=desired;
  }
  const usedSources=new Set(chunk.filter(q=>!isValidation(q)).map(q=>q.sourceType));
  const diverse=candidates.filter(({q})=>!families.has(q.familyId||q.template)&&(hooks[q.h]||0)<2);
  let pick;
  if(diverse.length)pick=diverse.find(({q})=>!usedSources.has(q.sourceType))||diverse[0];
  else{pick=candidates.find(({q})=>!families.has(q.familyId||q.template));if(pick)topicRelaxed++;else{pick=candidates[0];relaxed++;}}
  out.push(pool.splice(pick.i,1)[0]);
 }
 return {questions:out,relaxed,topicRelaxed};
}
function shuffled(q,rng=Math.random){const map=[0,1,2,3];for(let i=3;i>0;i--){const j=Math.floor(rng()*(i+1));[map[i],map[j]]=[map[j],map[i]];}return {opts:map.map(i=>q.o[i]),answer:map.indexOf(q.a),map};}
function summary(rows){const n=rows.length,attempted=rows.filter(r=>r.pick>=0).length,correct=rows.filter(r=>r.correct).length;
 const fast=rows.filter(r=>r.correct&&!r.hinted&&!r.paused&&r.confidence!=='猜测'&&r.secs<=r.limit).length;
 const times=rows.map(r=>r.secs).sort((a,b)=>a-b),median=n?(n%2?times[(n-1)/2]:(times[n/2-1]+times[n/2])/2):0;
 return {n,attempted,correct,skips:n-attempted,accuracy:n?correct/n:0,attemptAccuracy:attempted?correct/attempted:0,fast,fastAccuracy:n?fast/n:0,median};}
function contentKey(q){return JSON.stringify([q?.s,q?.o,q?.a,q?.level,q?.e,q?.tr]);}
function currentAttempts(rows,questions){const active=new Map(questions.filter(eligible).map(q=>[q.uid,q]));return rows.filter(r=>active.has(r.uid)&&r.q&&contentKey(r.q)===contentKey(active.get(r.uid)));}
function trainingMemory(rows,questions){const allowed=new Set(questions.filter(trainEligible).map(q=>q.uid)),memory={};
 for(const r of currentAttempts(rows,questions)){if(!allowed.has(r.uid)||isValidation(r)||isValidation(r.q)||r.dataset==='validation')continue;const m=memory[r.uid]||(memory[r.uid]={wrong:0,slow:0});m.wrong+=!r.correct;m.slow+=r.secs>r.limit;}return memory;}
function promotion(rows,level,questions=[]){const active=new Map(questions.filter(trainEligible).map(q=>[q.uid,q])),unique=new Map();
 currentAttempts(rows,questions).filter(r=>r.level===level&&active.has(r.uid)&&!isValidation(r)&&!isValidation(r.q)&&r.dataset!=='validation'&&r.training==='ladder'&&r.mode!=='transfer').forEach(r=>{unique.delete(r.uid);unique.set(r.uid,r);});
 const recent=[...unique.values()].slice(-20),s=summary(recent);return {ready:s.n>=10&&s.accuracy>=.8&&s.fast/s.n>=.6&&level!==levels.at(-1),...s};}
function transferStats(rows,questions){const active=new Map(questions.map(q=>[q.uid,q])),train=[],first=[],repeat=[],provisional=[],seen=new Set();
 for(const r of currentAttempts(rows,questions)){
  const q=active.get(r.uid);
  if(isValidation(q)){
   if(!validationEligible(q))continue;
   const key=validationIdentity(q),isFirst=!seen.has(key)&&r.firstValidation!==false&&r.mode!=='validation-review';seen.add(key);
   if(q.validationStatus==='V2')provisional.push(r);else if(isFirst)first.push(r);else repeat.push(r);
  }else if(trainEligible(q)&&!isValidation(r.q)&&!isValidation(r))train.push(r);
 }
 const t=summary(train),v=summary(first);return {train:t,firstValidation:v,repeatValidation:summary(repeat),provisional:summary(provisional),gap:t.n&&v.n?t.accuracy-v.accuracy:null};
}
function mappedExplanation(text,map){return String(text).replace(/\[\[option:([ABCD])\]\]/g,(_,l)=>'ABCD'[map.indexOf('ABCD'.indexOf(l))]);}
function validAttempt(r){
 if(!r||typeof r!=='object'||typeof r.uid!=='string'||!['authored','glm','real'].includes(r.source)||typeof r.level!=='string')return false;
 if(!Number.isInteger(r.pick)||r.pick< -1||r.pick>3||!Number.isInteger(r.answer)||r.answer<0||r.answer>3||typeof r.correct!=='boolean'||r.correct!==(r.pick===r.answer))return false;
 if(!Number.isFinite(r.secs)||r.secs<0||!Number.isFinite(r.limit)||r.limit<=0||typeof r.hinted!=='boolean'||typeof r.paused!=='boolean')return false;
 if(!r.q||!eligible(r.q)||r.q.uid!==r.uid||!Array.isArray(r.map)||r.map.length!==4||[...r.map].sort().join('')!=='0123')return false;
 if(r.dataset!==undefined&&!['train','validation'].includes(r.dataset))return false;
 if(r.firstValidation!==undefined&&typeof r.firstValidation!=='boolean')return false;
 if(isValidation(r.q)&&r.dataset==='train')return false;
 return Array.isArray(r.options)&&r.options.length===4&&r.options.every((o,i)=>typeof o==='string'&&o===r.q.o[r.map[i]])&&r.answer===r.map.indexOf(r.q.a);
}
function restore(value){
 const blank={schema:3,attempts:[],exposures:[],level:'入门'};
 if(!value||value.schema!==3||!Array.isArray(value.attempts))return {db:blank,needsBackup:!!value};
 const attempts=value.attempts.filter(validAttempt),level=[...levels,'all'].includes(value.level)?value.level:'入门';
 const raw=value.exposures,exposures=Array.isArray(raw)?[...new Set(raw.filter(x=>typeof x==='string'&&x.length>0&&x.length<10000))]:[];
 return {db:{schema:3,attempts,exposures,level},needsBackup:attempts.length!==value.attempts.length||level!==value.level||(raw!==undefined&&(!Array.isArray(raw)||exposures.length!==raw.length))};
}
return {levels,limits,normalize,eligible,isValidation,trainEligible,validationEligible,validationIdentity,migrateValidationExposures,sample,shuffled,summary,promotion,trainingMemory,transferStats,mappedExplanation,contentKey,currentAttempts,validAttempt,restore};
});