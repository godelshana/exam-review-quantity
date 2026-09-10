const assert=require('node:assert/strict'),C=require('./core.js');
const train=i=>C.normalize({uid:`old:${i}`,year:2023,exam:'国考',sourceType:'real',dataset:'train',s:`独立训练题${i}条件`,o:['1','2','3','4'],a:0,t:'模型',h:`h${i%5}`,level:'入门',template:`family:${i}`,e:'独立推导',tr:'边界',answerStatus:'confirmed',imageStatus:'complete',explanationStatus:'P2',mathAudit:'passed',leakageRisk:'low'});
const validation=(i,status='V1')=>({...train(i),uid:`national:2024:${i}`,year:2024,dataset:'validation',s:`验证题情境${i}`,validationStatus:status});
const attempt=(q,extra={})=>({uid:q.uid,source:q.sourceType==='glm'?'glm':'real',dataset:q.dataset,year:q.year,level:q.level,training:'ladder',mode:q.dataset==='validation'?'validation':'train',firstValidation:true,pick:0,answer:0,correct:true,secs:12,limit:35,hinted:false,paused:false,confidence:'确定',map:[0,1,2,3],options:q.o,q,...extra});
const ts=Array.from({length:20},(_,i)=>train(i)),vs=Array.from({length:15},(_,i)=>validation(i)),all=[...ts,...vs];
assert.equal(C.sample(all,{size:50}).questions.length,20);
assert(C.sample(all,{size:50}).questions.every(C.trainEligible));
assert.equal(C.sample(all,{mode:'validation',size:50}).questions.length,15);
const mixed=C.sample(all,{mode:'transfer'}).questions;assert.equal(mixed.filter(C.isValidation).length,2);assert.equal(mixed.filter(C.trainEligible).length,3);
for(const year of [2024,2025,2026])for(const exam of ['国考','广东省考'])for(const sourceType of ['mock','glm','real']){
 const malicious={...train(1),year,exam,sourceType};assert(C.isValidation(malicious));assert.equal(C.sample([malicious]).questions.length,0);assert(!C.trainEligible(malicious));
 const r=attempt(malicious);assert.equal(C.promotion(Array(20).fill(r),'入门',[malicious]).n,0);assert.deepEqual(C.trainingMemory([r],[malicious]),{});
}
for(const changes of [{mathAudit:'pending'},{leakageRisk:'high'},{leakageRisk:'medium'},{answerStatus:'disputed'},{imageStatus:'missing'},{explanationStatus:'P0'},{dataset:undefined},{o:['1','1','2','3']}])assert.equal(C.sample([{...ts[0],...changes}]).questions.length,0);
for(const changes of [{validationStatus:'V3'},{answerStatus:'unknown'},{imageStatus:'uncertain'},{mathAudit:'pending'}])assert.equal(C.sample([{...vs[0],...changes}],{mode:'validation'}).questions.length,0);
const poisoned={...train(1),sourceQuestionUid:'guangdong:2026:1'};assert(C.isValidation(poisoned));assert(!C.trainEligible(poisoned));
const derivative={...train(2),s:vs[0].s.replace('0','999')};assert(!C.sample([...vs,derivative]).questions.length);
// Never consume validation weights, even if they are enormous.
const fixed=()=>.4,a=C.sample(all,{mode:'validation',size:3,rng:fixed}).questions.map(q=>q.uid),b=C.sample(all,{mode:'validation',size:3,rng:fixed,strategy:'weak',memory:Object.fromEntries(vs.map(q=>[q.uid,{wrong:9999,slow:9999}]))}).questions.map(q=>q.uid);assert.deepEqual(a,b);
const rows=ts.slice(0,10).map(q=>attempt(q)),vr=attempt(vs[0]);assert(C.promotion(rows,'入门',all).ready);assert.deepEqual(C.promotion([...rows,...vs.map(q=>attempt(q,{pick:-1,correct:false}))],'入门',all),C.promotion(rows,'入门',all));
assert.deepEqual(C.trainingMemory([...rows,vr],all),C.trainingMemory(rows,all));
assert.equal(C.sample(all,{mode:'validation',attempts:[vr],size:30}).questions.length,14);
assert.equal(C.sample(all,{mode:'validation',exposures:[C.validationIdentity(vs[0])],size:30}).questions.length,14);
assert.equal(C.sample(all,{mode:'validation-review',exposures:[C.validationIdentity(vs[0])]}).questions.length,1);
assert.equal(C.sample(all,{mode:'validation-review'}).questions.length,0);
const stats=C.transferStats([...rows,vr,{...vr,pick:-1,correct:false,firstValidation:false,mode:'validation-review'}],all);assert.equal(stats.train.n,10);assert.equal(stats.firstValidation.n,1);assert.equal(stats.firstValidation.accuracy,1);assert.equal(stats.repeatValidation.n,1);assert.equal(stats.gap,0);
assert.equal(C.transferStats([],all).gap,null);
const v2=validation(99,'V2'),pro=C.transferStats([attempt(v2)],[v2]);assert.equal(pro.provisional.n,1);assert.equal(pro.firstValidation.n,0);assert.equal(pro.gap,null);
const same={...vs[0],uid:'different-paper:2024:99'};assert.equal(C.sample([same],{mode:'validation',attempts:[vr]}).questions.length,0);
assert.equal(C.transferStats([vr,attempt(same)],[vs[0],same]).firstValidation.n,1);
assert(!C.validAttempt({...vr,dataset:'train'}));assert.equal(C.restore({schema:3,attempts:[vr],exposures:[null,'id','id'],level:'入门'}).db.exposures.length,1);
assert(C.restore({schema:3,attempts:[],exposures:'bad',level:'入门'}).needsBackup);
assert.equal(C.sample(all,{mode:'invalid'}).questions.length,0);
console.log('PASS: dataset fail-closed gates, national/Guangdong 2024–2026 provenance attacks, math/answer/image faults, holdout exposure/first/repeat/V2, transfer, promotion and weights isolation');
for(const q of [ts[0],vs[0]]){assert(!C.trainEligible({...q,usable:false}));assert(!C.validationEligible({...q,usable:false}));assert.equal(C.sample([{...q,admission:'quarantine'}],{mode:q.dataset==='validation'?'validation':'train'}).questions.length,0);}

const canonical={...vs[0],sourceQuestionUid:'heldout:2024:shared'};const reprinted={...canonical,uid:'other:2024:1',s:canonical.s+'。'};assert.equal(C.sample([canonical,reprinted],{mode:'validation',size:5}).questions.length,1);
