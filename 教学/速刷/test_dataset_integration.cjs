const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict'),C=require('./core.js');
const ctx={window:{}};
for(const name of ['手写模拟题_100.js','原创复合24.js','training_families.js','authored_methods.js','datasets/banks.js','datasets/authored_policy.js'])vm.runInNewContext(fs.readFileSync(path.join(__dirname,name),'utf8'),ctx);
const w=ctx.window,original=[...w.HAND_LADDER_100,...w.CHALLENGE_Q],all=[...original,...w.DATASET_TRAIN,...w.DATASET_VALIDATION].map(q=>C.normalize({...q,...w.AUTHORED_METHODS[q.uid],...w.DATASET_AUTHORED_OVERRIDES[q.uid],template:w.TRAINING_FAMILIES[q.uid]||q.template}));
assert.equal(original.length,124);assert.equal(Object.keys(w.DATASET_AUTHORED_OVERRIDES).length,124);assert.equal(w.DATASET_VALIDATION.length,105);
for(const year of [2024,2025,2026])assert.equal(w.DATASET_VALIDATION.filter(q=>q.year===year).length,35);
assert(w.DATASET_TRAIN.every(C.trainEligible));assert(w.DATASET_VALIDATION.every(C.isValidation));
const train=all.filter(C.trainEligible),validation=all.filter(C.validationEligible),withheld=original.filter(q=>w.DATASET_AUTHORED_OVERRIDES[q.uid].leakageRisk!=='low');
assert(withheld.length>0,'reserved structurally matching authored questions must be excluded');
for(const q of withheld)assert(!train.some(t=>t.uid===q.uid));
let seed=20260911;const rng=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
for(let i=0;i<200;i++){
 const out=C.sample(all,{rng,size:5});assert.equal(out.questions.length,5);assert(out.questions.every(C.trainEligible));
 const t=C.sample(all,{rng,size:5,mode:'transfer'});assert.equal(t.questions.filter(C.isValidation).length,2);
 assert.equal(t.questions.filter(C.trainEligible).length,3);assert(t.questions.every(q=>q.validationStatus!=='V3'));
 const v=C.sample(all,{rng,size:5,mode:'validation'});assert.equal(v.questions.length,5);assert(v.questions.every(C.validationEligible));
}
for(const level of C.levels){const eligible=all.map(q=>!C.isValidation(q)&&q.level!==level?{...q,mathAudit:'not_this_level'}:q);for(let i=0;i<100;i++){const out=C.sample(eligible,{rng});assert.equal(out.questions.length,5);assert(out.questions.every(q=>q.level===level));}}
// Public build must not silently restore legacy unreviewed banks, or omit isolation policies.
const html=fs.readFileSync(path.join(__dirname,'刷题页面.html'),'utf8');
for(const asset of ['datasets/banks.js','datasets/authored_policy.js','authored_methods.js'])assert(html.includes(`src="${asset}"`));
for(const legacy of ['真题数量关系.js','精选GLM题库.js','题库数据.js'])assert(!html.includes(`src="${legacy}"`));
console.log(JSON.stringify({passed:true,train:train.length,authoredActive:124-withheld.length,authoredWithheld:withheld.length,otherTrain:w.DATASET_TRAIN.length,validationScorable:validation.length,validationSlots:105,samplingRounds:1000}));