const assert=require('node:assert/strict');const C=require('./core.js');
let seed=20260909;const rng=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
const bank=Array.from({length:100},(_,i)=>({dataset:"train",answerStatus:"confirmed",imageStatus:"complete",explanationStatus:"P2",mathAudit:"passed",leakageRisk:"low",e:"derive",tr:"trap",uid:`t:${i}`,s:`题目${i}`,o:['1','2','3','4'],a:i%4,t:'模型',h:`h${i%6}`,level:C.levels[i%4],template:`f${i%10}`}));
const out=C.sample(bank,{size:30,rng}).questions;
assert.equal(out.length,30);assert.equal(new Set(out.map(q=>q.uid)).size,30);
for(let i=0;i<30;i+=5){const chunk=out.slice(i,i+5);assert.equal(new Set(chunk.map(q=>q.template)).size,5);}
assert.equal(C.sample([{...bank[0],a:-1,t:'跳过'}]).questions.length,0);
assert.equal(C.sample([bank[0],{...bank[0],uid:'duplicate'}]).questions.length,1);
assert.equal(C.sample(bank.slice(0,2),{size:5}).questions.length,2);
assert.equal(C.summary([]).accuracy,0);
const rows=Array.from({length:10},(_,i)=>({dataset:"train",answerStatus:"confirmed",imageStatus:"complete",explanationStatus:"P2",mathAudit:"passed",leakageRisk:"low",e:"derive",tr:"trap",uid:`t:${i}`,level:'入门',source:'authored',training:'ladder',pick:i<8?0:-1,correct:i<8,secs:20,limit:35,hinted:false,paused:false,confidence:'确定'}));
const active=rows.map(r=>C.normalize({...bank[0],uid:r.uid,s:r.uid,level:r.level}));rows.forEach((r,i)=>r.q={...active[i]});
assert.equal(C.summary(rows).accuracy,.8);assert.equal(C.summary(rows).skips,2);assert.equal(C.summary(rows).attemptAccuracy,1);assert.equal(C.promotion(rows,'入门',active).ready,true);
assert.equal(C.promotion(rows.map(r=>({...r,uid:'same'})),'入门',active).ready,false);
assert.equal(C.promotion(rows.map(r=>({...r,hinted:true})),'入门',active).ready,false);
assert.equal(C.promotion(rows.map(r=>({...r,source:'glm'})),'入门',active).ready,true); // Individually audited GLM is allowed.
assert.equal(C.summary(rows.map(r=>({...r,pick:-1,correct:false}))).accuracy,0);
for(const q of bank){const m=C.shuffled(q,rng);assert.equal(m.opts[m.answer],q.o[q.a]);assert.equal(C.mappedExplanation(`故选[[option:${'ABCD'[q.a]}]]`,m.map),`故选${'ABCD'[m.answer]}`);}
// Higher weight must actually increase sampling probability; not sort using random comparator.
let unseen=0;for(let i=0;i<1000;i++){const selected=C.sample(bank.slice(0,2),{size:1,strategy:'fresh',memory:{'t:0':{wrong:0}},rng}).questions[0];unseen+=selected.uid==='t:1';}assert(unseen>850,unseen);
console.log('PASS: sampling, diversity, insufficient pool, skip denominator, promotion, confidence, answer mapping, weights');

assert.equal(C.normalize({...bank[0],signal:'先看差量',targetSeconds:42}).hint,'先看差量');
assert.equal(C.normalize({...bank[0],targetSeconds:42}).timeLimit,42);
assert.equal(C.sample([bank[0],{...bank[0],s:'同ID不同题干'}]).questions.length,1);
// Repeating an old UID must move its latest attempt into the recent window.
const history=Array.from({length:25},(_,i)=>({...rows[0],uid:`history:${i}`,correct:true,pick:0}));
history.forEach(r=>r.q={...active[0],uid:r.uid,s:r.uid});const historyBank=history.map(r=>r.q);
const recent=C.promotion([...history,{...history[0],correct:false,pick:-1}],'入门',historyBank);
assert.equal(recent.n,20);assert.equal(recent.correct,19);
console.log('PASS: metadata aliases, UID deduplication, actual latest-20 ordering');

assert.equal(C.promotion(rows,'入门',[]).ready,false);
assert.equal(C.promotion(rows,'入门',active.map(q=>({...q,e:'新版解法'}))).ready,false);
assert.equal(C.promotion(rows.map(r=>({...r,uid:'removed:'+r.uid})),'入门',active).ready,false);
assert.equal(C.mappedExplanation('应选A产品，而不是B产品',[3,2,1,0]),'应选A产品，而不是B产品');
assert.equal(C.mappedExplanation('答案：[[option:A]]；排除[[option:B]]项',[3,2,1,0]),'答案：D；排除C项');
const valid={...rows[0],answer:0,pick:0,map:[0,1,2,3],options:active[0].o};
assert(C.validAttempt(valid));
assert.equal(C.restore({schema:3,attempts:[null,valid],level:'深化'}).db.attempts.length,1);
assert.equal(C.restore({schema:3,attempts:[null,valid],level:'深化'}).needsBackup,true);
assert.equal(C.restore({schema:2,attempts:[valid]}).needsBackup,true);
assert.equal(C.restore({schema:3,attempts:[valid],level:'all'}).db.level,'all');
assert(!C.validAttempt({...valid,secs:Infinity}));
assert(!C.validAttempt({...valid,correct:false}));
assert(!C.validAttempt({...valid,map:[0,0,2,3]}));
assert.equal(C.sample(bank.slice(0,5).map((q,i)=>({...q,h:'same',template:String(i)})),{size:5,rng}).topicRelaxed,3);
console.log('PASS: withdrawn/revised history excluded, structured options, corrupted history, topic fallback');

const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');const context={window:{}};
for(const file of ['手写模拟题_100.js','原创复合24.js','training_families.js'])vm.runInNewContext(fs.readFileSync(path.join(__dirname,file),'utf8'),context);
const actual=[...context.window.HAND_LADDER_100,...context.window.CHALLENGE_Q].map(q=>C.normalize({...q,template:context.window.TRAINING_FAMILIES[q.uid]}));
assert.equal(actual.length,124);assert.equal(Object.keys(context.window.TRAINING_FAMILIES).length,124);
assert(actual.every(q=>q.template.startsWith('model:')));
for(const level of C.levels){const pool=actual.filter(q=>q.level===level);for(let i=0;i<100;i++){const set=C.sample(pool,{size:5,rng});assert.equal(set.questions.length,5);assert.equal(new Set(set.questions.map(q=>q.template)).size,5);}}
console.log('PASS: actual authored bank, all four levels, 400 five-question coarse-model diversity samples');
