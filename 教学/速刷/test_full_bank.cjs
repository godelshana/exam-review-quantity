const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const C=require('./core.js');const w={};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'full_audit/banks.js'),'utf8'),{window:w});
const train=w.FULL_REAL_TRAIN.map(C.normalize),validation=w.FULL_REAL_VALIDATION.map(C.normalize),all=[...train,...validation];
assert(train.length>850);assert(train.every(C.trainEligible));assert(validation.every(C.isValidation));
for(const y of [2024,2025,2026]){assert.equal(validation.filter(q=>q.year===y&&q.exam==='广东省考').length,15);for(const exam of ['安徽省考','湖北省考','河南省考','四川省考']){const q={...train[0],uid:'prov:test',sourceQuestionUid:'prov:synthetic',sourceLabel:'',provenance:{},year:y,exam,province:exam.slice(0,2),occurrences:[]};assert(!C.isValidation(q));assert(C.trainEligible(q));}}
for(const y of [2024,2025,2026]){const reprint={...train[0],year:2018,exam:'安徽省考',occurrences:[{exam:'广东省考',year:y}]};assert(C.isValidation(reprint));assert(!C.trainEligible(reprint));}
const suppressed=train.filter(q=>!C.sample([q,...validation],{size:1}).questions.some(x=>x.uid===q.uid));
assert.equal(suppressed.length,0,'No silent withholding of reviewed training questions; any exact-text derivative needs explicit provenance and treatment');
let seed=7890;const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2**32;};const visited=new Set();
for(let i=0;i<1000;i++){
 const sampled=C.sample(all,{size:5,rng}).questions;assert.equal(sampled.length,5);assert(sampled.every(C.trainEligible));assert.equal(new Set(sampled.map(q=>q.s.replace(/\s/g,''))).size,5);
 sampled.forEach(q=>visited.add(q.uid));
 if(i%10===0){const mixed=C.sample(all,{mode:'transfer',size:5,rng}).questions;assert.equal(mixed.filter(C.isValidation).length,2);}
}
for(const level of C.levels){const qs=train.filter(q=>q.level===level);assert(qs.length>=5,level);assert.equal(C.sample(qs,{size:5}).questions.length,5);}
for(const province of ['国考','安徽','广东','湖北','河南','四川'])assert(train.some(q=>q.province===province||(q.occurrences||[]).some(o=>o.province===province)),province);
for(const q of all.filter(q=>q.usable))for(let i=0;i<4;i++){const m=C.shuffled(q,rng);assert.equal(m.opts[m.answer],q.o[q.a]);assert.equal(m.map[m.answer],q.a);}
const v=validation.find(q=>q.validationStatus==='V1'),identity=C.validationIdentity(v);
assert(!C.sample(all,{mode:'validation',size:1000,exposures:[identity]}).questions.some(q=>C.validationIdentity(q)===identity));
assert(C.sample(all,{mode:'validation-review',exposures:[identity]}).questions.every(q=>C.validationIdentity(q)===identity));
const seq={...train[0],uid:'sequence:test',sourceQuestionUid:'sequence:test',s:'1，2，3，4，（ ）',topic:'数字推理',h:'数字推理'};
assert.equal(C.sample([seq,{...seq,uid:'reserved:sequence',dataset:'validation',s:'2，3，4，5，（ ）',validationStatus:'V1'}]).questions.length,1,'different numerical sequences remain trainable');
console.log(JSON.stringify({passed:true,train:train.length,validationSlots:validation.length,validationScorable:validation.filter(C.validationEligible).length,trainVisitedAcross1000Rounds:visited.size,levels:Object.fromEntries(C.levels.map(l=>[l,train.filter(q=>q.level===l).length]))}));

assert(!C.isValidation({uid:'prov:regression',year:2022,exam:'广东省考',sourceQuestionUid:'real-shared:adf2024bcf'}),'hash substrings are not exam years');

const legacy={...validation[0],sourceQuestionUid:'legacy:first-test-identity'},newId=C.validationIdentity(validation[0]);
const migrated=C.migrateValidationExposures(['legacy:first-test-identity'],[],[legacy],validation);
assert(migrated.includes(newId)&&migrated.includes('legacy:first-test-identity'));
assert(C.migrateValidationExposures([],[{uid:legacy.uid,q:legacy,dataset:'validation'}],[],validation).includes(newId));
assert(!C.sample(all,{mode:'validation',size:1000,exposures:migrated}).questions.some(q=>C.validationIdentity(q)===newId));
