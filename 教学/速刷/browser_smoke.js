/* Inject AFTER app initialization in a disposable local tab. This script never launches a browser.
 * For a non-local disposable origin explicitly set window.__ALLOW_DRILL_SMOKE__ = true.
 * Do not run on a learner's live storage. It adds attempts/exposures, never clears them.
 */
(()=>{'use strict';
const assert=(v,m)=>{if(!v)throw Error('browser_smoke: '+m);},$=id=>document.getElementById(id);
assert(['localhost','127.0.0.1','[::1]'].includes(location.hostname)||window.__ALLOW_DRILL_SMOKE__===true,'use a disposable origin');
const C=window.DrillCore,stored=()=>JSON.parse(localStorage.getItem('quantity-ladder-v3')),records=()=>stored().attempts;
const set=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new Event('change',{bubbles:true}));};
const checks=[],skipped=[];
const raw=[...window.HAND_LADDER_100,...window.CHALLENGE_Q,...window.DATASET_TRAIN.filter(q=>q.sourceType==='glm'),...window.FULL_REAL_TRAIN,...window.FULL_REAL_VALIDATION];
const all=[...new Map(raw.map(q=>{const n=C.normalize({...q,...window.AUTHORED_METHODS[q.uid],...window.DATASET_AUTHORED_OVERRIDES?.[q.uid],template:window.TRAINING_FAMILIES[q.uid]||q.template});return[n.uid,n];})).values()];
const question=()=>all.find(q=>q.uid===$('stem').dataset.uid);
const finishSkips=()=>{let guard=0;while(!$('quiz').hidden&&guard++<35){if(!$('skip').hidden)$('skip').click();if(!$('next').hidden)$('next').click();}assert(guard<35,'round terminates');};
const exit=()=>{const old=window.confirm;try{window.confirm=()=>true;$('exit').click();}finally{window.confirm=old;}if(!$('result').hidden)$('back').click();};
assert($('loadError').hidden,'required assets loaded');assert([...window.HAND_LADDER_100,...window.CHALLENGE_Q].every(q=>Object.prototype.hasOwnProperty.call(window.DATASET_AUTHORED_OVERRIDES||{},q.uid)),'authored isolation policy covers every UID');assert(all.filter(q=>['medium','high'].includes(q.leakageRisk)&&/^(hand100:|challenge:)/.test(q.uid)).every(q=>!C.trainEligible(q)),'medium/high-risk authored questions excluded');assert($('length').value==='5','default five questions');
set('source','train');set('level','入门');set('mode','exam');const baseline=records().length;$('start').click();assert(!$('quiz').hidden,'training starts');
for(let i=0;i<5;i++){$('skip').click();$('skip').click();assert(!$('next').hidden,'next appears');assert(!$('feedback').textContent.includes('正确选项'),'exam hides answer');$('next').click();}
assert(records().length===baseline+5,'duplicate submit blocked');assert($('result').querySelectorAll('.review-body').length===5,'five complete reviews');assert($('result').innerText.includes('0%'),'all skips score zero');
assert($('result').querySelectorAll('.solution-part').length>=30,'complete explanation sections per question');
for(const body of $('result').querySelectorAll('.review-body')){const parts=body.querySelectorAll('.solution-part');const rating=[...parts].find(p=>p.querySelector('strong')?.textContent.includes('快法评级：')),decision=[...parts].find(p=>p.querySelector('strong')?.textContent.includes('取舍'));assert(rating&&decision,'fast-value rating and decision visible');assert(!/^(do|conditional|skip)$/.test(decision.querySelector('div').textContent.trim()),'decision translated into Chinese');if(rating.textContent.includes('快法评级：低'))assert(!rating.querySelector('strong').textContent.includes('最快'),'low-rated path not advertised as fastest');}
const firstTrain=records().slice(baseline);assert(firstTrain.every(r=>r.dataset==='train'&&!C.isValidation(r.q)&&r.mode==='train'),'no validation leak in training');assert(firstTrain.every(r=>C.validAttempt(r)),'new attempts restore-compatible');
checks.push('five questions, dedup submit, no leakage, full explanations');$('back').click();
set('mode','practice');set('level','综合');$('start').click();const before=records().length;$('pause').click();document.querySelector('#opts button').click();assert(records().length===before,'paused answer blocked');$('pause').click();$('hint').click();assert(!$('hintText').hidden,'training hint available');
const q=question();assert(q,'find displayed question');const opts=[...document.querySelectorAll('#opts button')],good=q.sourceType==='real'?q.a:opts.findIndex(b=>b.textContent.slice(3)===q.o[q.a]);const bad=(good+1)%4;opts[bad].click();const r=records().at(-1);assert(r.pick===bad&&!r.correct&&r.hinted&&r.paused,'actual pick / hint / pause flags');finishSkips();assert($('result').querySelector('summary').textContent.includes('你选'+'ABCD'[bad]),'actual wrong option in review');$('back').click();checks.push('hint, pause, wrong-pick mapping');
set('level','all');set('strategy','ladder');$('start').click();const mixedStart=records().length;finishSkips();assert(records().slice(mixedStart).every(r=>r.training==='random'),'cross-level excluded from promotion');$('back').click();
set('source','validation');assert($('mode').disabled&&$('mode').value==='exam','formal validation forces delayed feedback');
if(!$('start').disabled){
 const n=records().length,exp=stored().exposures.length;const stats=JSON.stringify(C.transferStats(records(),all));$('start').click();const v=question();assert(v&&v.validationStatus==='V1','formal V1 only');const key=C.validationIdentity(v);
 assert(stored().exposures.includes(key)&&stored().exposures.length===exp+1,'show persists exposure');assert(records().length===n,'unanswered exposure not a score');assert(JSON.stringify(C.transferStats(records(),all))===stats,'exposure leaves metrics unchanged');
 assert($('hint').disabled&&$('pause').disabled,'formal hint / pause disabled');$('hint').onclick();$('pause').onclick();assert($('hintText').hidden&&!$('stem').hidden,'handlers also block formal assistance');assert($('feedback').hidden,'no answer preview');
 const restored=C.restore(stored()).db;assert(restored.exposures.includes(key),'exposure survives restore');
 assert(!C.sample(all,{size:1000,mode:'validation',attempts:restored.attempts,exposures:restored.exposures}).questions.some(q=>C.validationIdentity(q)===key),'cross-paper identity cannot re-enter first test');
 $('skip').click();assert(records().at(-1).firstValidation===true,'first-validation flag before show');assert(records().at(-1).dataset==='validation','validation metadata');const firstStats=JSON.stringify(C.transferStats(records(),all).firstValidation);exit();
 set('source','validation-review');set('validationTier','V1');set('mode','practice');$('start').click();assert(!$('quiz').hidden,'seen-only review available');assert(!$('hint').disabled&&!$('pause').disabled,'review assistance allowed');$('hint').click();$('skip').click();assert(records().at(-1).firstValidation===false,'review not first');assert(JSON.stringify(C.transferStats(records(),all).firstValidation)===firstStats,'review does not backfill first score');exit();checks.push('V1 first exposure / restore / no preview / review contamination');
 // Exiting another unattempted first item must preserve exposure but add no score.
 set('source','validation');if(!$('start').disabled){const count=records().length;$('start').click();const key2=C.validationIdentity(question());exit();assert(records().length===count&&stored().exposures.includes(key2),'exit preserves unscored exposure');}
}else skipped.push('No unseen eligible V1: first-test interaction requires available V1 or isolated fixture');
set('source','transfer');if(!$('start').disabled){const n=records().length;$('start').click();assert($('hint').disabled&&$('pause').disabled,'transfer timed');finishSkips();const added=records().slice(n);assert(added.every(r=>r.mode==='transfer'),'per-attempt transfer mode');assert(added.filter(r=>r.dataset==='validation').every(r=>['V1','V2'].includes(r.validationStatus)),'V3 excluded');assert(added.every(r=>r.source===(/^(hand100:|challenge:)/.test(r.uid)?'authored':r.q.sourceType==='glm'?'glm':'real')),'source assigned per question');assert(JSON.stringify(C.trainingMemory(records().filter(r=>r.dataset!=='validation'),all))===JSON.stringify(C.trainingMemory(records(),all)),'validation cannot weight training memory');$('back').click();checks.push('mixed transfer / per-question provenance / V3 isolation');}
assert($('coverage').textContent.includes('2024年广东')&&$('coverage').textContent.includes('2026年广东'),'Guangdong years visible even if missing');assert($('metrics').textContent.includes('已曝光未答'),'unanswered exposure count');
assert(C.restore(stored()).db.attempts.length===records().length,'schema3 round-trip preserves new attempts');
for(const summary of document.querySelectorAll('summary')){const rect=summary.getBoundingClientRect();if(rect.width&&rect.height)assert(rect.height>=44,'visible summary touch target >=44px');}
checks.push('Chinese decisions / fast-value rating / summary touch targets');
const oldSchema={...stored()};delete oldSchema.exposures;assert(Array.isArray(C.restore(oldSchema).db.exposures),'old schema3 without exposures compatible');
set('source','train');set('level','入门');set('mode','practice');set('strategy','ladder');
return JSON.stringify({pass:true,checks,skipped,attemptsAdded:records().length-baseline,viewport:{width:innerWidth,height:innerHeight,horizontalOverflow:document.documentElement.scrollWidth>innerWidth}});
})();
