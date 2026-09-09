/* UI: no inline legacy questions and no silent fallback to unaudited full banks. */
(()=>{'use strict';
const C=window.DrillCore,$=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const STORE='quantity-ladder-v3';let db={schema:3,attempts:[],level:'入门'},persist=true,pendingBackup=null,backupKey=STORE+'-recovery-'+Date.now(),recoveryNote='';
try{const raw=localStorage.getItem(STORE);if(raw){try{const restored=C.restore(JSON.parse(raw));db=restored.db;if(restored.needsBackup)pendingBackup=raw;}catch{pendingBackup=raw;}}}catch{persist=false;}
function save(){try{
 if(pendingBackup!==null){localStorage.setItem(backupKey,pendingBackup);pendingBackup=null;recoveryNote=' 已隔离异常数据，原始记录另存本地恢复备份。';}
 localStorage.setItem(STORE,JSON.stringify(db));persist=true;
 }catch{persist=false;}
 $('storageStatus').textContent=(persist?' 保存在本浏览器，不自动跨设备同步':' 存储不可用：新记录仅在内存，旧存储未覆盖，请导出')+recoveryNote;
}
const normalized=q=>C.normalize({...q,template:window.TRAINING_FAMILIES?.[q.uid||q.curationId]||q.template});
const banks={authored:[...(window.HAND_LADDER_100||[]),...(window.CHALLENGE_Q||[])].map(normalized),glm:(window.CURATED_GLM_BANK||[]).map(C.normalize),real:(window.REAL_Q||[])};
let deck=[],idx=0,rows=[],state='menu',mapping=null,start=0,timer=null,hinted=false,paused=false,hadPause=false,pauseAt=0,pausedTime=0,insightTime=null,roundSource='',roundStrategy='',answered=false;
const describes={入门:'单模型：先学会把题意变成一个量或一个比。建议目标35秒。',熟练:'条件翻译：基数、单位、正反关系、整数边界。建议目标55秒。',深化:'两步配合：差量与比例、守恒与分段、相似与体积。建议目标75秒。',综合:'复合约束：离散可行性、上界与构造、过程限制。建议目标100秒；不会就先跳。'};
$('level').value=db.level;
function refresh(){
 const source=$('source').value,ladder=$('strategy').value==='ladder';
 $('level').disabled=source!=='authored';
 $('ladderInfo').textContent=source==='authored'?(describes[$('level').value]||'跨阶混合：不计入升阶资格。')+'\n'+(ladder?'天梯只在所选阶出题，达标后建议进入下一阶，不会先排序再随机打乱。':'随机 / 新题 / 薄弱策略仅改变抽样，不伪装成难度升级。'):source==='glm'?'GLM代表题已减少模板冗余、隔离已发现问题，但其余题未完成逐题数学复核。建议作为补充，不计天梯升阶。':'真题资料暂不计分：旧导入缺失图片和逐题解析，部分答案存在争议。请回本地真题库或粉笔/华图核对。';
 $('bankInfo').textContent=source==='authored'?`原创模拟 ${banks.authored.length} 题（百题重写 + 24道复合题），不是国考原题。`:source==='glm'?`545道GLM原库仅保留 ${banks.glm.length} 道结构代表进入可选练习，其余移出日常训练。`:`${banks.real.length} 道历史导入仅保留待核资料入口，不纳入本次质量合格题数。`;
 const count=filtered(false).length;
 $('start').textContent=source==='real'?'查看待核说明':`开始 ${$('length').value} 题`;
 $('start').disabled=(source!=='real'&&!count);
 $('reviewPool').disabled=source==='real';
 $('filterInfo').textContent=source==='real'?'待题面、图片及答案争议处理完毕后再恢复自动评分。':`当前可选 ${count} 题；本阶错题 / 慢题 ${filtered(true).length} 题。${count<+$('length').value?'题量不足时只出实际可用题，不复制凑数。':''}`;
}
function mem(){const m={};for(const r of C.currentAttempts(db.attempts,[...banks.authored,...banks.glm])){const x=m[r.uid]||(m[r.uid]={wrong:0,slow:0});x.wrong+=!r.correct;x.slow+=r.secs>r.limit;}return m;}
function filtered(review){const src=$('source').value;const level=$('level').value;const latest=new Map(C.currentAttempts(db.attempts,banks[src]||[]).map(r=>[r.uid,r]));return (banks[src]||[]).filter(q=>C.eligible(C.normalize(q))&&(src!=='authored'||level==='all'||q.level===level)&&(!review||(latest.has(q.uid)&&(!latest.get(q.uid).correct||latest.get(q.uid).secs>latest.get(q.uid).limit||latest.get(q.uid).hinted))));}
function stopTimer(){clearInterval(timer);timer=null;}
function elapsed(){return Math.max(0,((paused?pauseAt:Date.now())-start-pausedTime)/1000);}
function home(){stopTimer();state='menu';$('menu').hidden=false;$('quiz').hidden=true;$('result').hidden=true;refresh();}
function begin(review=false){
 if($('source').value==='real'){alert('这40道旧导入真题尚未完成缺图、争议和题解修复，暂不提供自动判分。原始真题资料仍保留在项目中。');return;}
 let source=filtered(review);const selected=C.sample(source,{size:+$('length').value,strategy:$('strategy').value,memory:mem()});
 if(!selected.questions.length){alert('当前筛选没有可练题目，请切换阶层或题源。');return;}
 $('samplingNote').textContent=selected.relaxed||selected.topicRelaxed?`当前小题池已放宽抽样：同考点上限放宽${selected.topicRelaxed}次，模板不重复限制放宽${selected.relaxed}次；不会复制题目凑数。`:'';
 deck=selected.questions;idx=0;rows=[];roundSource=$('source').value;roundStrategy=$('strategy').value==='ladder'&&$('level').value==='all'?'random':$('strategy').value;
 $('menu').hidden=true;$('quiz').hidden=false;$('result').hidden=true;state='quiz';show();
}
function show(){
 answered=false;hinted=false;paused=false;hadPause=false;pausedTime=0;insightTime=null;const q=deck[idx];mapping=C.shuffled(q);
 $('qno').textContent=`${idx+1} / ${deck.length}`;$('qsource').textContent=q.sourceLabel||'模拟题';$('progress').value=idx/deck.length;
 $('stem').hidden=false;$('opts').hidden=false;$('stem').textContent=q.s;$('opts').replaceChildren();
 mapping.opts.forEach((text,i)=>{const b=document.createElement('button');b.className='opt';b.textContent=`${'ABCD'[i]}. ${text}`;b.onclick=()=>answer(i);$('opts').appendChild(b);});
 $('hintText').hidden=true;$('feedback').hidden=true;$('next').hidden=true;$('skip').hidden=false;
 for(const id of ['confidence','insight','hint','pause'])$(id).disabled=false;
 $('confidence').value='未标记';$('insight').textContent='思路已定';$('pause').textContent='暂停';
 start=Date.now();stopTimer();tick();timer=setInterval(tick,200);
}
function tick(){if(state!=='quiz')return;const q=deck[idx];const sec=Math.floor(elapsed());$('timer').textContent=`${sec}s / 目标 ${q.timeLimit}s`;$('timer').className='timer'+(sec>q.timeLimit?' slow':'');}
function answer(pick){
 if(state!=='quiz'||answered||paused||pick< -1||pick>3)return;answered=true;stopTimer();
 const q=deck[idx],secs=Math.round(elapsed()*10)/10,correct=pick===mapping.answer;
 const r={uid:q.uid,source:roundSource,label:q.sourceLabel,level:q.level||'未定级',training:roundStrategy,date:new Date().toISOString(),pick,correct,secs,limit:q.timeLimit,hinted,paused:hadPause,confidence:$('confidence').value,insightTime,q:{...q},map:[...mapping.map],options:[...mapping.opts],answer:mapping.answer};
 rows.push(r);db.attempts.push(r);db.attempts=db.attempts.slice(-1500);save();
 document.querySelectorAll('#opts button').forEach((b,i)=>{b.disabled=true;if($('mode').value==='practice'){if(i===r.answer)b.classList.add('right');else if(i===pick)b.classList.add('wrong');}});
 for(const id of ['confidence','insight','hint','pause'])$(id).disabled=true;
 $('feedback').hidden=false;$('feedback').textContent=$('mode').value==='practice'?`${pick<0?'已暂跳（不计答对）':correct?'✓ 答对':'✗ 需复盘'} · 正确选项 ${'ABCD'[r.answer]} · ${secs}s\n${q.h} / ${q.level||'未定级'}\n${C.mappedExplanation(q.e,r.map)}\n易错：${C.mappedExplanation(q.tr||'核对题目要求与边界。',r.map)}`:'已记录选择。本套结束后统一查看题解。';
 $('skip').hidden=true;$('next').hidden=false;$('next').textContent=idx===deck.length-1?'查看本套题解':'下一题（回车）';$('progress').value=(idx+1)/deck.length;
}
function next(){if(!answered||state!=='quiz')return;if(++idx<deck.length)show();else finish();}
function finish(){
 stopTimer();state='result';$('quiz').hidden=true;$('result').hidden=false;if(!rows.length){home();return;}
 const s=C.summary(rows),pct=x=>`${Math.round(x*100)}%`,p=C.promotion(db.attempts,rows[0].level,banks.authored);
 let text=`<h2>本套复盘 · ${s.n}题</h2><div class="stats"><div><strong>${pct(s.accuracy)}</strong><span>整体正确率（含暂跳）</span></div><div><strong>${s.correct}/${s.attempted}</strong><span>已选题答对数</span></div><div><strong>${s.median.toFixed(1)}s</strong><span>作答用时中位数</span></div><div><strong>${s.skips}</strong><span>暂跳，仍需复盘</span></div></div>`;
 text+=`<p class="mini">快速独立答对 ${s.fast}/${s.n}。题源：${esc([...new Set(rows.map(r=>r.label))].join(' + '))}。思路计时仅是自报，不据此声称识别正确。</p>`;
 if(roundStrategy==='ladder'&&roundSource==='authored')text+=`<div class="feedback">本阶最近不同题 ${p.n}道，正确率 ${pct(p.accuracy)}，快速独立答对 ${p.fast}道。${p.ready?'已达升阶建议，可进入下一阶。':'至少10道不同题、80%正确且60%快速独立答对，再建议升阶。'}</div>`;
 const per={};rows.forEach(r=>{const k=r.q.h;per[k]||(per[k]={n:0,c:0});per[k].n++;per[k].c+=r.correct;});text+='<table><thead><tr><th>考点</th><th>答对 / 题量</th></tr></thead><tbody>'+Object.entries(per).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${v.c}/${v.n}</td></tr>`).join('')+'</tbody></table><h2 style="margin-top:24px">逐题题解</h2>';
 rows.forEach((r,n)=>{
  text+=`<details ${!r.correct||r.secs>r.limit?'open':''}><summary>${n+1}. ${r.correct?'✓':'待复盘'} · ${esc(r.q.h)} · 你选${r.pick<0?'暂跳':'ABCD'[r.pick]} / 正解${'ABCD'[r.answer]}</summary><div class="review-body">${esc(r.q.s)}\n${r.options.map((o,i)=>`${'ABCD'[i]}. ${o}`).map(esc).join('\n')}\n\n<strong>最短思路与推导</strong>\n${esc(C.mappedExplanation(r.q.e,r.map))}\n\n<strong>易错点</strong>\n${esc(C.mappedExplanation(r.q.tr,r.map))}\n\n<span class="mini">${esc(r.q.sourceLabel)} · ID ${esc(r.uid)} · ${r.secs}s${r.hinted?' · 已看提示':''}${r.paused?' · 有暂停':''}</span></div></details>`;
 });
 text+='<div class="row"><button id="back" class="primary">回到训练设置</button><button id="again">同阶再来一套</button>'+(p.ready&&roundStrategy==='ladder'&&roundSource==='authored'?'<button id="advance">进入下一阶</button>':'')+'</div>';
 $('result').innerHTML=text;$('back').onclick=home;$('again').onclick=()=>begin(false);
 if($('advance'))$('advance').onclick=()=>{db.level=C.levels[C.levels.indexOf(rows[0].level)+1];$('level').value=db.level;save();home();};
 window.scrollTo({top:0,behavior:'smooth'});
}
$('start').onclick=()=>begin();$('reviewPool').onclick=()=>begin(true);$('skip').onclick=()=>answer(-1);$('next').onclick=next;
$('exit').onclick=()=>{if(confirm('结束本轮？已作答记录和题解会保留，未作答题不计入统计。'))finish();};
$('hint').onclick=()=>{if(answered)return;hinted=true;$('hintText').hidden=false;$('hintText').textContent=deck[idx].hint||`入口：${deck[idx].h}。先用一个总量、差量或约束表示问题，再检查选项。`;$('hint').disabled=true;};
$('insight').onclick=()=>{if(answered||paused)return;insightTime=Math.round(elapsed()*10)/10;$('insight').textContent=`思路用时 ${insightTime}s（自报）`;$('insight').disabled=true;};
$('pause').onclick=()=>{if(answered)return;paused=!paused;if(paused){hadPause=true;pauseAt=Date.now();$('pause').textContent='继续';}else{pausedTime+=Date.now()-pauseAt;$('pause').textContent='暂停';}['opts','stem'].forEach(id=>$(id).hidden=paused);};
$('export').onclick=()=>{const blob=new Blob([JSON.stringify(pendingBackup===null?db:{...db,recoveryOriginal:pendingBackup},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='数量关系练习记录.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
for(const id of ['source','length','mode','strategy','level'])$(id).onchange=()=>{if(id==='level'){db.level=$('level').value;save();}refresh();};
document.addEventListener('keydown',e=>{if(e.repeat||state!=='quiz'||['SELECT','INPUT','TEXTAREA'].includes(document.activeElement.tagName))return;const k=e.key.toLowerCase();if('abcd'.includes(k)&&k.length===1)answer('abcd'.indexOf(k));if(k==='j')answer(-1);if(e.key==='Enter'&&answered){e.preventDefault();next();}});
if(!window.TRAINING_FAMILIES||!window.HAND_LADDER_100||!window.CHALLENGE_Q||!window.CURATED_GLM_BANK){$('loadError').hidden=false;$('loadError').textContent='部分题库资源未加载，请刷新或检查网络。本页不会偷偷回退到有问题的旧题库。';}
save();refresh();
})();
