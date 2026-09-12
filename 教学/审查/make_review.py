import re,json,pathlib,hashlib
root=pathlib.Path('.')
qtext=(root/'真题库/按模块/01_数量关系/题目汇编.md').read_text(encoding='utf-8')
atext=(root/'真题库/按模块/01_数量关系/答案速查.md').read_text(encoding='utf-8')
xtext=(root/'真题库/按模块/01_数量关系/答案与解析.md').read_text(encoding='utf-8')
# exact question blocks
a=[]
pat=re.compile(r'^\*\*(\d+)\.\*\* (.*?)\s+`\[(\d{4})·([^·]+)·(\d+)\]`\n((?:- [A-D]\. .*\n?)+)',re.M)
for m in pat.finditer(qtext):
 y=int(m.group(3))
 if 2011<=y<=2023:
  opts=[re.sub(r'^- [A-D]\. ','',z) for z in m.group(6).strip().splitlines()]
  a.append({'id':f'{y}-{m.group(4)}-{m.group(5)}','year':y,'paper':m.group(4),'no':int(m.group(5)),'stem':m.group(2).strip(),'options':opts})
# Map answer tables by their ordered year/paper headings. 2015+ reuses numbers
# across papers, so (year, paper, question number) is the key.
qgroups={}
for m in pat.finditer(qtext):
 key=(int(m.group(3)),m.group(4)); qgroups.setdefault(key,[]).append(int(m.group(5)))
answer_groups=[]; current=None
for line in atext.splitlines():
 h=re.match(r'^## (\d{4})年(?:（[^）]*）)?(?: · )?(.*?)(?:（\d+题）)?\s*$',line)
 if h:
  y=int(h.group(1)); tail=h.group(2).strip()
  if '副省级' in tail: paper='副省级'
  elif '地市级' in tail: paper='地市级'
  elif '行政执法类' in tail: paper='行政执法类'
  else: paper='合卷'
  current=(y,paper); answer_groups.append((current,[])); continue
 m=re.match(r'^\|\s*(\d+)\s*\|\s*([^|]+)\|',line)
 if m and current: answer_groups[-1][1].append((int(m.group(1)),m.group(2).strip()))
ans={}
# Within each year, the answer tables and compiled question blocks have the same
# paper order. Position alignment is safer than relying on encoding/punctuation in
# paper names, and also handles repeated question numbers across papers.
for y in sorted({k[0] for k in qgroups}):
 qseq=[]
 for k,qs in qgroups.items():
  if k[0]==y: qseq.extend((k,no) for no in qs)
 aseq=[]
 for k,rows in answer_groups:
  if k[0]==y: aseq.extend(rows)
 for (k,no),(listed_no,val) in zip(qseq,aseq): ans[(y,k[1],no)]=val
# explanation presence and flags
for r in a:
 key=f"**{r['year']}·{r['paper']}·{r['no']}（"
 pos=xtext.find(key)
 block=xtext[pos:xtext.find('\n**',pos+3) if xtext.find('\n**',pos+3)>0 else pos+3000] if pos>=0 else ''
 r['answer']=ans.get((r['year'],r['paper'],r['no']),'—')
 r['answerReliability']=('high_source' if r['year']<=2022 else 'fenbi_aligned')
 if any(s in r['answer'] for s in ['？','—']): r['answerReliability']='unverified'
 if '⚠' in r['answer']: r['answerReliability']='disputed'
 r['explanationPresent']=bool(block and '解析：' in block)
 s=r['stem']
 # topic and fastest strategy, deliberately conservative
 rules=[
  (['速度','行驶','游泳','相遇','船','跑步','骑车','追','路程'],'行程','比例/相遇周期；先找相对速度或总路程，能比例就不设方程'),
  (['工程','完成','工作量','效率','生产','加工','装配'],'工程','设总工作量为效率最小公倍数；优先算单位效率和整体工期'),
  (['利润','成本','售价','折扣','进价','销售','价格','涨价'],'经济利润','统一到成本/售价基准；优先用利润额、折扣后的总额反推'),
  (['抽取','概率','排列','组合','夫妻','座位','选出','随机','相邻','分组'],'排列组合概率','先定样本空间；优先捆绑、插空、分类计数，选项明显时反推'),
  (['浓度','溶液','盐','酒精'],'浓度溶液','用溶质守恒/十字交叉；通常不必设多元方程'),
  (['平均','年龄','平均数'],'平均数年龄','总量=平均×人数；优先加权平均或差额法'),
  (['日期','星期','月份','周期','每隔','循环'],'日期周期','先取周期/模运算；避免逐日模拟'),
  (['面积','体积','半径','直径','几何','正方体','圆','三角形','四面体','长方形'],'几何','先看比例和相似/面积比；图形缺失或空间想象成本高时跳过'),
  (['至少','保证','最多','最少','至少有','至多'],'容斥最值','最不利原则/反面计数；先判断是保证型还是极值型'),
  (['余数','整除','倍数','质数','个位','数字','数列','各位数'],'数性比例','数字特征/整除/代入选项优先，少做完整枚举'),
  (['平均分','分给','老师','人数','甲、乙','甲乙'],'比例分配','设份数或总量，优先整数性与比例消元'),
 ]
 r['topic']='其他综合'; r['fastestStrategy']='约束转化后再决定代入/估算；若信息密集先跳过'
 for keys,t,st in rules:
  if any(k in s for k in keys): r['topic']=t; r['fastestStrategy']=st; break
 # difficulty: strategy cost + source era only as weak prior
 hard=0
 if len(s)>115: hard+=1
 if sum(ch in s for ch in '且并同时若则其中分别')>=3: hard+=1
 if r['topic'] in ['排列组合概率','几何','容斥最值','其他综合']: hard+=1
 if any(k in s for k in ['图','相邻','同时满足','恰好','至少','最多']): hard+=1
 r['difficulty']='基础' if hard<=0 else ('熟练' if hard==1 else ('深化' if hard==2 else '综合'))
 r['review']='题面可读；答案按资料来源标记，需独立复算' if r['answerReliability'] in ['high_source','fenbi_aligned'] else '答案/题面存在待核或争议，禁止直接纳入计分天梯'
 r['auditNotes']=[]
 if '图' in s: r['auditNotes'].append('依赖原图，须核图后确认')
 if r['answerReliability'] in ['unverified','disputed']: r['auditNotes'].append('答案不可静默采用')
 if not r['explanationPresent']: r['auditNotes'].append('模块解析缺失')
# sort and summary
summary={'scope':'2011-2023国考数量关系模块','generated':'2026-09-11','count':len(a),'byYear':{},'byTopic':{},'byStrategy':{},'byDifficulty':{},'answerReliability':{}}
for r in a:
 for key,field in [('byTopic','topic'),('byDifficulty','difficulty'),('answerReliability','answerReliability')]: summary[key][r[field]]=summary[key].get(r[field],0)+1
 summary['byYear'][str(r['year'])]=summary['byYear'].get(str(r['year']),0)+1
 summary['byStrategy'][r['fastestStrategy']]=summary['byStrategy'].get(r['fastestStrategy'],0)+1
out={'meta':{'purpose':'逐题审查清单的第一版结构化底稿；策略与梯度为人工复核前的保守标注，不等同数学证明','sourceFiles':['真题库/按模块/01_数量关系/题目汇编.md','真题库/按模块/01_数量关系/答案速查.md','真题库/按模块/01_数量关系/答案与解析.md'],'rules':{'recentValidationSet':'2021-2023应从训练池剔除，保留作验证集','answer':'2011-2022按高教解析优先；2023按粉笔对齐；争议/待核不计分','strategy':'估算/代入/数字特征优先；常规计算不伪装成秒杀；高成本题标记跳过候选'},'summary':summary},'items':a}
path=root/'教学/审查/2011-2023数量关系逐题审查清单.json'
path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
# markdown report
md=['# 2011—2023 国考数量关系逐题审查报告（结构化底稿）','',f'> 范围：{len(a)}题。此文件不修改任何生成的真题文件，也未提交 Git。','> 说明：答案可靠性沿用项目答案来源优先级；“最快策略/难度”是保守教学标注，后续入天梯前仍须逐题独立复算，尤其是图题、争议题和题面异常题。','', '## 结论与使用边界','', '- 2021—2023建议完整保留为验证集，不进入训练天梯；2023题面与答案应按粉笔版逐题对齐。','- 2011—2020可作为训练真题，但不应把“有解析”当作“题面和答案已数学审计”。','- `unverified`、`disputed`、依赖缺图的题目先隔离；绝不为了题量强行计分。','- “最快策略”服务于选对：估算、代入、数字特征、比例消元优先；没有稳定快法的题标为常规计算或跳过候选。','', '## 统计','', '```json',json.dumps(summary,ensure_ascii=False,indent=2),'```','', '## JSON字段','', '|字段|含义|','|---|---|','|id|年份·卷种·原卷题号|','|answerReliability|high_source / fenbi_aligned / disputed / unverified|','|topic|主考点（粗分类）|','|fastestStrategy|最快可行入口|','|difficulty|基础/熟练/深化/综合|','|review|是否允许进入计分题池的初步建议|','|auditNotes|需要人工核验的风险|','', '## 逐题清单','', '|ID|答案|考点|最快入口|梯度|可靠性|审查备注|','|---|---:|---|---|---|---|---|']
for r in a:
 notes='；'.join(r['auditNotes']) or '待独立复算'
 md.append(f"|{r['id']}|{r['answer']}|{r['topic']}|{r['fastestStrategy'].split('；')[0]}|{r['difficulty']}|{r['answerReliability']}|{notes}|")
(root/'教学/审查/2011-2023数量关系逐题审查报告.md').write_text('\n'.join(md),encoding='utf-8')
print('wrote',len(a))

