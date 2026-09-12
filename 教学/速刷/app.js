/* Five-question UI. Eligibility, validation history and promotion belong to DrillCore. */
(()=>{'use strict';
const C=window.DrillCore,$=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ready=Array.isArray(window.FULL_REAL_TRAIN)&&Array.isArray(window.FULL_REAL_VALIDATION)&&Array.isArray(window.FULL_REAL_STUDY)&&!!window.FULL_REAL_SUMMARY&&!!C&&['normalize','isValidation','trainEligible','validationEligible','trainingMemory','transferStats','validationIdentity','migrateValidationExposures'].every(k=>typeof C[k]==='function')&&Array.isArray(window.DATASET_TRAIN)&&Array.isArray(window.DATASET_VALIDATION)&&Array.isArray(window.HAND_LADDER_100)&&Array.isArray(window.CHALLENGE_Q)&&!!window.TRAINING_FAMILIES&&!!window.AUTHORED_METHODS&&!!window.DATASET_AUTHORED_OVERRIDES&&[...window.HAND_LADDER_100,...window.CHALLENGE_Q].length===124&&[...window.HAND_LADDER_100,...window.CHALLENGE_Q].every(q=>window.AUTHORED_METHODS[q.uid]&&Object.prototype.hasOwnProperty.call(window.DATASET_AUTHORED_OVERRIDES,q.uid)&&['low','medium','high'].includes(window.DATASET_AUTHORED_OVERRIDES[q.uid]?.leakageRisk));
if(!ready){$('loadError').hidden=false;$('loadError').textContent='题库数据缺失或不完整，已停止抽题。请刷新页面；若持续出现，请检查题库文件是否完整。';$('start').disabled=$('reviewPool').disabled=true;return;}
const STORE='quantity-ladder-v3',names={train:'训练天梯',transfer:'迁移混编',validation:'真题首测','validation-review':'测试复盘'};
let db={schema:3,attempts:[],exposures:[],level:'入门'},persist=true,pendingBackup=null,recoveryNote='';
const backupKey=STORE+'-recovery-'+Date.now();
try{const raw=localStorage.getItem(STORE);if(raw){try{const restored=C.restore(JSON.parse(raw));db=restored.db;if(restored.needsBackup)pendingBackup=raw;}catch{pendingBackup=raw;}}}catch{persist=false;}
function save(){try{if(pendingBackup!==null){localStorage.setItem(backupKey,pendingBackup);pendingBackup=null;recoveryNote=' 异常原始数据已另存恢复备份。';}localStorage.setItem(STORE,JSON.stringify(db));persist=true;}catch{persist=false;}
 $('storageStatus').textContent=(persist?'记录保存在本浏览器，不自动跨设备同步。':'存储不可用：记录仅在内存，请导出；验证首测已禁用以免刷新重置曝光。')+recoveryNote;
}
db.exposures=Array.isArray(db.exposures)?db.exposures:[];
const normalized=q=>C.normalize({...q,...(window.AUTHORED_METHODS[q.uid]||{}),...(window.DATASET_AUTHORED_OVERRIDES?.[q.uid]||{}),template:window.TRAINING_FAMILIES[q.uid||q.curationId]||q.template});
const authored=[...window.HAND_LADDER_100,...window.CHALLENGE_Q].map(q=>normalized({...q,source:'authored'}));
const all=[...new Map([...authored,...window.DATASET_TRAIN.filter(q=>q.sourceType==='glm'),...window.FULL_REAL_TRAIN,...window.FULL_REAL_VALIDATION].map(q=>{const n=normalized(q);return [n.uid,n];})).values()];
const authoredIds=new Set(authored.map(q=>q.uid));
// Source/diagram repairs must not turn previously exposed national questions into fresh tests.
db.exposures=C.migrateValidationExposures(db.exposures,db.attempts,window.DATASET_VALIDATION,all);
const labelOf=q=>q.sourceLabel||(q.exam&&q.year?`[${q.year}年${q.exam}·${q.paper||'卷别待核'}·${q.number??q.moduleIndex??'题号待核'}]`:q.source?.locator||({authored:'原创模拟（非真题）',glm:'审计通过GLM模拟',real:'审计通过真题'}[sourceOf(q)]));
const sourceOf=q=>['authored','glm','real'].includes(q.source)?q.source:authoredIds.has(q.uid)?'authored':(q.sourceType==='glm'||String(q.uid||'').startsWith('glm:'))?'glm':'real';

let deck=[],idx=0,rows=[],state='menu',mapping=null,start=0,timer=null,hinted=false,paused=false,hadPause=false,pauseAt=0,pausedTime=0,insightTime=null,roundMode='train',roundStrategy='',roundFeedback='practice',answered=false,firstValidation=false,deadline=0,expiring=false;
const describes={入门:'单模型：把题意变成一个量或一个比。',熟练:'翻译条件：基数、单位、正反关系与整数边界。',深化:'两步配合：差量与比例、守恒与分段。',综合:'复合约束：离散可行性、上界构造与过程限制。'};
const pct=x=>Number.isFinite(x)?`${Math.round(x*100)}%`:'—';
const identity=q=>C.validationIdentity(q);
const seen=q=>db.exposures.includes(identity(q))||db.attempts.some(r=>r.q&&identity(r.q)===identity(q));
const formal=()=>roundMode==='validation'||roundMode==='transfer';
function inView(q,review=false){const mode=$('source').value;
 if(mode==='train'){
  if(!C.trainEligible(q)||!matchesFilters(q))return false;
  if(mode==='train'&&$('level').value!=='all'&&q.level!==$('level').value)return false;
  if(review){const r=C.currentAttempts(db.attempts,all).filter(r=>r.uid===q.uid&&(r.mode==='train'||r.mode==='transfer'||!r.mode)).at(-1);return !!r&&(!r.correct||r.secs>r.limit||r.hinted||r.paused||r.confidence==='猜测');}
  return true;
 }
 if(mode==='transfer'&&!C.isValidation(q))return C.trainEligible(q);
 if(!C.isValidation(q)||q.validationStatus==='V3')return false;
 if(mode==='validation')return q.validationStatus==='V1'&&C.validationEligible(q)&&!seen(q)&&matchesFilters(q);
 if(mode==='transfer')return C.validationEligible(q)&&!seen(q);
 return q.validationStatus===$('validationTier').value&&seen(q)&&C.validationEligible(q);
}
function statsHTML(){const s=C.transferStats(db.attempts,all);const block=(label,v)=>`<div><strong>${v?.n?pct(v.accuracy):'—'}</strong><span>${label} · ${v?.n||0}题<br>快速独立 ${v?.fast||0}/${v?.n||0}</span></div>`;
 return `<h2>训练 → 真题迁移</h2><div class="stats">${block('训练',s.train)}${block('测试首测',s.firstValidation)}${block('重复 / 复盘',s.repeatValidation)}${block('暂定（单列）',s.provisional)}</div><p class="mini">迁移差 = 训练正确率 − 首测正确率：${s.gap==null?'样本不足':`${Math.round(s.gap*100)} 个百分点`}。提示、暂停、猜测不计快速独立。</p>`;
}
function topicGroup(q){return String(q.h||q.topic||'其他').split(/[\/·（：]/)[0];}
function matchesFilters(q){
 const province=$('provinceFilter').value,topic=$('topicFilter').value;
 return (province==='all'||q.province===province||q.exam===province||(q.occurrences||[]).some(o=>o.province===province))&&(topic==='all'||topicGroup(q)===topic);
}
let catalogPage=0;
function renderCatalog(){
 if($('catalogPanel').hidden||!$('catalogPanel').open)return;
 const type=$('catalogType').value,items=(type==='study'?window.FULL_REAL_STUDY:all.filter(q=>C.trainEligible(q))).filter(q=>matchesFilters(q)&&($('level').value==='all'||q.level===$('level').value));
 const pages=Math.max(1,Math.ceil(items.length/12));catalogPage=Math.min(catalogPage,pages-1);
 $('catalogCount').textContent=`${items.length} 题 · 第 ${catalogPage+1} / ${pages} 页`;
 $('catalogItems').innerHTML=items.slice(catalogPage*12,catalogPage*12+12).map(q=>`<details><summary>${esc(labelOf(q))} · ${esc(q.level)} · ${esc(q.h||q.topic)}${q.usable===false?' · 仅研读':''}</summary><div class="review-body">${renderText(q.s)}\n${q.o.map((o,i)=>'ABCD'[i]+'. '+renderText(o)).join('\n')}</div>${q.usable===false?`${q.originalStem?`<details><summary>查看原始题干</summary><div class="review-body">${renderText(q.originalStem)}</div></details>`:''}<p class="warning">${esc(q.verdict==='invalid'?'题面缺损或矛盾':'机构答案存在争议')}。来源标记 ${esc(q.sourceAnswer||'无')}，独立推导 ${esc(q.computedAnswer)}，建议用粉笔或华图核对。</p>`:`<button class="catalog-practice" data-uid="${esc(q.uid)}">单题限时练</button>`}<details><summary>查看题解</summary>${explanation(q,[0,1,2,3])}</details></details>`).join('');
 for(const b of $('catalogItems').querySelectorAll('.catalog-practice'))b.onclick=()=>begin(false,b.dataset.uid);
 $('catalogPrev').disabled=catalogPage===0;$('catalogNext').disabled=catalogPage===pages-1;
}
function refresh(){if(!ready){$('start').disabled=true;$('reviewPool').disabled=true;return;}
 const mode=$('source').value,formal=mode==='validation'||mode==='transfer',training=mode==='train';
 $('trainingFilters').hidden=false;$('catalogPanel').hidden=!training;
 $('level').disabled=!training;$('strategy').disabled=!training;$('mode').disabled=formal;if(formal)$('mode').value='exam';
 $('validationTierLabel').hidden=mode!=='validation-review';$('reviewPool').hidden=!training;
 $('ladderInfo').textContent=training?(describes[$('level').value]||'跨阶混合。')+' 可按地区、考点筛选。':mode==='transfer'?'训练题与未曝光测试题混编，整轮限时、无提示、不可暂停。':formal?'未曝光真题首测：整轮限时、无提示、不可暂停，结束后统一看题解。题目一显示即计入曝光，刷新不重置。':'复盘已曝光的测试题，可提示、可暂停，不计晋级。';
 const candidates=all.filter(q=>inView(q));
 const count=new Set(candidates.map(q=>C.isValidation(q)?'validation:'+identity(q):'train:'+q.uid)).size;
 $('bankInfo').textContent=`${names[mode]} · 练习池 ${window.FULL_REAL_SUMMARY.trainUnique} 道真题 + ${authored.length} 道模拟`;
 $('start').textContent=`开始 ${$('length').value} 题${formal?'首测':''}`;$('start').disabled=!count||(formal&&!persist);
 $('filterInfo').textContent=`可选 ${count} 道题${count<+$('length').value?'（不足题量按实际出）':''}`;
 $('metrics').innerHTML=statsHTML();renderCatalog();
}
function stopTimer(){clearInterval(timer);timer=null;}
function elapsed(){return Math.max(0,((paused?pauseAt:Date.now())-start-pausedTime)/1000);}
function home(){stopTimer();state='menu';$('menu').hidden=false;$('quiz').hidden=true;$('result').hidden=true;refresh();}
function begin(review=false,singleUid=null){if(!ready)return;roundMode=$('source').value;if(formal()&&!persist)return;
 // Always hand the complete bank and complete history to core; UI restrictions only narrow its output.
 const sampleBank=all.map(q=>(!inView(q,review)||(singleUid&&q.uid!==singleUid))?{...q,usable:false}:q);
 const selected=C.sample(sampleBank,{size:singleUid?1:+$('length').value,strategy:roundMode!=='train'?'random':$('strategy').value,memory:C.trainingMemory(db.attempts,all),mode:roundMode,attempts:db.attempts,exposures:db.exposures});
 const roundIdentities=new Set();
 deck=selected.questions.filter(q=>{if(!inView(q,review))return false;if(C.isValidation(q)){const key=identity(q);if(roundIdentities.has(key))return false;roundIdentities.add(key);}return true;}).slice(0,singleUid?1:+$('length').value);
 if(!deck.length){$('filterInfo').textContent='数据层未返回可练题：可能已曝光、未通过审计或资料不足。不会回退到旧题库。';return;}
 $('samplingNote').textContent=`本轮 ${deck.length} 题`;
 idx=0;rows=[];roundStrategy=!singleUid&&roundMode==='train'&&$('level').value!=='all'?$('strategy').value:'random';roundFeedback=formal()?'exam':$('mode').value;
 deadline=formal()?Date.now()+deck.reduce((n,q)=>n+q.timeLimit,0)*1000:0;
 $('menu').hidden=true;$('quiz').hidden=false;$('result').hidden=true;state='quiz';show();
}
function makeRow(pick,extra={}){const q=deck[idx];return {uid:q.uid,dataset:C.isValidation(q)?'validation':'train',exam:q.exam??'',year:q.year??null,validationStatus:q.validationStatus??null,source:sourceOf(q),mode:roundMode,label:labelOf(q),level:q.level||'未定级',training:roundStrategy,firstValidation:C.isValidation(q)?firstValidation:undefined,date:new Date().toISOString(),pick,correct:pick===mapping.answer,secs:Math.round(elapsed()*10)/10,limit:q.timeLimit,hinted,paused:hadPause,confidence:$('confidence').value,insightTime,q:{...q},map:[...mapping.map],options:[...mapping.opts],answer:mapping.answer,...extra};}
function show(){answered=false;hinted=false;paused=false;hadPause=false;pausedTime=0;insightTime=null;firstValidation=false;const q=deck[idx];mapping=sourceOf(q)==='real'?{opts:[...q.o],answer:q.a,map:[0,1,2,3]}:C.shuffled(q);start=Date.now();
 $('qno').textContent=`${idx+1} / ${deck.length}`;$('qsource').textContent=labelOf(q);$('progress').value=idx/deck.length;
 $('stem').hidden=false;$('opts').hidden=false;$('stem').dataset.uid=q.uid;$('stem').innerHTML=(q.practiceAssumption?`<p class="warning">教学作答口径（与原题文字分开）：${esc(q.practiceAssumption)}</p>`:'')+renderText(q.s);$('opts').replaceChildren();
 mapping.opts.forEach((text,i)=>{const b=document.createElement('button');b.className='opt';b.innerHTML=`${'ABCD'[i]}. ${renderText(text)}`;b.onclick=()=>answer(i);$('opts').appendChild(b);});
 for(const id of ['hintText','feedback','next'])$(id).hidden=true;$('skip').hidden=false;
 for(const id of ['confidence','insight','hint','pause'])$(id).disabled=false;
 $('confidence').value='未标记';$('insight').textContent='思路已定';$('pause').textContent='暂停';
 $('hint').disabled=$('pause').disabled=formal();const hintText=q.hint||(q.knowledge||'').split('。')[0];$('hint').hidden=formal()||!hintText;
 // Exposures consume first viewing without inventing an unanswered score.
 if(C.isValidation(q)){firstValidation=roundMode!=='validation-review'&&!seen(q);const key=identity(q);if(!db.exposures.includes(key))db.exposures.push(key);save();if(formal()&&!persist){finish();return;}}
 stopTimer();tick();if(state==='quiz')timer=setInterval(tick,200);
}
function tick(){if(state!=='quiz')return;const q=deck[idx],sec=Math.floor(elapsed());$('timer').textContent=formal()?`全轮剩余 ${Math.max(0,Math.ceil((deadline-Date.now())/1000))}s · 本题 ${sec}s`:`${sec}s / 目标 ${q.timeLimit}s`;$('timer').className='timer'+(sec>q.timeLimit?' slow':'');
 if(deadline&&Date.now()>=deadline&&!expiring){expiring=true;if(!answered)answer(-1,{timedOut:true});finish();expiring=false;}
}
function renderText(value){const text=typeof value==='object'&&value!==null?JSON.stringify(value,null,2):String(value??'');return text.split(/(!\[[^\]]*\]\([^)]+\))/g).map(part=>{const m=part.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);if(!m)return esc(part);const path=m[2].replace(/\\/g,'/');return /^(?:[a-z]+:|\/\/|\/|#)/i.test(path)?esc(part):`<img class="question-image" src="${esc(path)}" alt="${esc(m[1]||'原卷题图')}" loading="lazy">`;}).join('');}
function explanation(q,map){
 const fastTitle=['high','medium'].includes(q.fastValue)?'方法二 · 快解':'方法二 · 精简解法';
 const mapped=t=>renderText(C.mappedExplanation(typeof t==='object'?JSON.stringify(t,null,2):t??'',map));
 return [...(q.practiceAssumption?[['作答口径',q.practiceAssumption]]:[]),
  ...(q.knowledge?[['考点与知识点',q.knowledge]]:[['考点',q.h||q.topic]]),
  ['方法一 · 常规解法',q.normalPath||q.e],
  [fastTitle,q.fastPath||q.e],
  ...(q.elimination?[['方法三 · 排除法与选项分析',q.elimination]]:[]),
  ...(q.fastBoundary?[['快解使用前提',q.fastBoundary]]:[]),
  ...(q.tr||q.traps?[['易错点',q.tr||q.traps]]:[]),
  ...(q.verification?[['换一条路复核',q.verification]]:[])
 ].filter(([,text])=>String(text??'').trim()).map(([label,text])=>`<section class="solution-part"><strong>${esc(label)}</strong><div>${mapped(text)}</div></section>`).join('');
}
function answer(pick,extra={}){if(state!=='quiz'||answered||paused||pick< -1||pick>3)return;
 if(deadline&&Date.now()>=deadline&&!expiring){tick();return;}answered=true;if(!formal())stopTimer();
 const r=makeRow(pick,{status:'answered',...extra});rows.push(r);db.attempts.push(r);save();
 document.querySelectorAll('#opts button').forEach((b,i)=>{b.disabled=true;if(roundFeedback==='practice'){if(i===r.answer)b.classList.add('right');else if(i===pick)b.classList.add('wrong');}});
 for(const id of ['confidence','insight','hint','pause'])$(id).disabled=true;
 $('feedback').hidden=false;$('feedback').innerHTML=roundFeedback==='practice'?`<strong>${pick<0?'已暂跳':r.correct?'答对':'需要复盘'} · 正确选项 ${'ABCD'[r.answer]}</strong>${explanation(r.q,r.map)}`:(formal()?'已记录，整轮结束后统一看题解；计时继续。':'已记录，整轮结束后统一看题解。');
 $('skip').hidden=true;$('next').hidden=false;$('next').textContent=idx===deck.length-1?'查看本套题解':'下一题（回车）';$('progress').value=(idx+1)/deck.length;
}
function next(){if(!answered||state!=='quiz')return;if(deadline&&Date.now()>=deadline){tick();return;}if(++idx<deck.length)show();else finish();}
function finish(){stopTimer();if(state!=='quiz')return;
 state='result';$('quiz').hidden=true;$('result').hidden=false;if(!rows.length){home();return;}
 const s=C.summary(rows),p=C.promotion(db.attempts,rows[0].level,all),canPromote=roundMode==='train'&&roundStrategy==='ladder';
 let text=`<h2>${esc(names[roundMode])} · 本套复盘 ${s.n}题</h2><div class="stats"><div><strong>${pct(s.accuracy)}</strong><span>正确率</span></div><div><strong>${s.correct}/${s.attempted}</strong><span>答对 / 已答</span></div><div><strong>${s.fast}/${s.n}</strong><span>快速独立答对</span></div><div><strong>${s.median.toFixed(1)}s</strong><span>用时中位数</span></div></div>`;
 if(canPromote)text+=`<div class="feedback">本阶最近 ${p.n} 题：正确率 ${pct(p.accuracy)}，快速独立 ${p.fast} 题。${p.ready?'已达到升阶建议。':'达到 10 题、80% 正确、60% 快速独立后建议升阶。'}</div>`;
 text+=statsHTML()+'<h2>逐题完整题解</h2>';
 rows.forEach((r,n)=>{text+=`<details ${!r.correct||r.secs>r.limit?'open':''}><summary>${n+1}. ${r.correct?'✓':'待复盘'} · ${esc(r.q.h)} · 你选${r.pick<0?'暂跳':'ABCD'[r.pick]} / 正解${'ABCD'[r.answer]}</summary><div class="review-body">${renderText(r.q.s)}\n${r.options.map((o,i)=>`${'ABCD'[i]}. ${o}`).map(renderText).join('\n')}${explanation(r.q,r.map)}<p class="mini">${esc(r.label)} · 用时 ${r.secs}s${r.hinted?' · 已提示':''}${r.paused?' · 曾暂停':''}</p></div></details>`;});
 text+='<div class="row"><button id="back" class="primary">回到训练设置</button><button id="again">再来一套</button>'+(roundMode!=='train'?'<button id="validationReview">进入验证复盘</button>':'')+(canPromote&&p.ready?'<button id="advance">进入下一阶</button>':'')+'</div>';
 $('result').innerHTML=text;$('back').onclick=home;$('again').onclick=()=>begin(false);
 if($('validationReview'))$('validationReview').onclick=()=>{$('source').value='validation-review';$('validationTier').value='V1';home();};
 if($('advance'))$('advance').onclick=()=>{db.level=C.levels[C.levels.indexOf(rows[0].level)+1];$('level').value=db.level;save();home();};window.scrollTo({top:0,behavior:'smooth'});
}
for(const [id,values] of [['provinceFilter',['国考','安徽','广东','湖北','河南','四川']],['topicFilter',[...new Set(window.FULL_REAL_TRAIN.map(topicGroup))].sort()]])for(const value of values){const option=document.createElement('option');option.value=value;option.textContent=value;$(id).appendChild(option);}
for(const id of ['provinceFilter','topicFilter'])$(id).onchange=()=>{catalogPage=0;refresh();};
$('catalogPanel').ontoggle=renderCatalog;$('catalogType').onchange=()=>{catalogPage=0;renderCatalog();};
$('catalogPrev').onclick=()=>{catalogPage--;renderCatalog();};$('catalogNext').onclick=()=>{catalogPage++;renderCatalog();};

$('level').value=db.level;
$('start').onclick=()=>begin();$('reviewPool').onclick=()=>begin(true);$('skip').onclick=()=>answer(-1);$('next').onclick=next;
$('exit').onclick=()=>{if(confirm('结束本轮？已显示的测试题保留曝光记录。'))finish();};
$('hint').onclick=()=>{if(answered||paused||formal())return;hinted=true;const h=deck[idx].hint||(deck[idx].knowledge||'').split('。')[0];if(!h)return;$('hintText').hidden=false;$('hintText').textContent=h;$('hint').disabled=true;};
$('insight').onclick=()=>{if(answered||paused)return;insightTime=Math.round(elapsed()*10)/10;$('insight').textContent=`思路用时 ${insightTime}s（自报）`;$('insight').disabled=true;};
$('pause').onclick=()=>{if(answered||formal())return;paused=!paused;if(paused){hadPause=true;pauseAt=Date.now();$('pause').textContent='继续';}else{pausedTime+=Date.now()-pauseAt;$('pause').textContent='暂停';}['opts','stem','hintText'].forEach(id=>{if(id!=='hintText'||hinted)$(id).hidden=paused;});};
$('export').onclick=()=>{const blob=new Blob([JSON.stringify(pendingBackup===null?db:{...db,recoveryOriginal:pendingBackup},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='数量关系练习记录.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
for(const id of ['source','length','mode','strategy','level','validationTier'])$(id).onchange=()=>{if(id==='level'){db.level=$('level').value;save();}refresh();};
document.addEventListener('keydown',e=>{if(e.repeat||state!=='quiz'||['SELECT','INPUT','TEXTAREA'].includes(document.activeElement?.tagName))return;const k=e.key.toLowerCase();if('abcd'.includes(k)&&k.length===1)answer('abcd'.indexOf(k));if(k==='j')answer(-1);if(e.key==='Enter'&&answered){e.preventDefault();next();}});
save();refresh();
})();
