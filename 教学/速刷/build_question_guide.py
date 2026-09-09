"""将正式候选题库导出为学习者可读的Markdown题册。只读数据，不生成新题。"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent

def main():
    qs=[]
    for fn,var in [('手写模拟题_100.js','HAND_LADDER_100'),('原创复合24.js','CHALLENGE_Q')]:
        text=(ROOT/fn).read_text(encoding='utf-8-sig');qs+=json.loads(re.search(r'window\.'+var+r'\s*=\s*(\[.*\]);\s*$',text,re.S).group(1))
    lines=['# 原创数量关系天梯 · 题册与题解','','> AI逐题编写的模拟题，不是国考真题或人工教师署名。难度是建模成本预估，非考生用时实测。每批审计状态以 `release_manifest.json` 和独立审计报告为准。','','建议先在页面盲做5题，再回到题册复盘。题目下面的折叠块含答案，避免提前阅读。','']
    for level in ['入门','熟练','深化','综合']:
        group=[q for q in qs if q['level']==level];lines.extend([f'## {level}（{len(group)}题）',''])
        for q in group:
            lines.extend([f"### {q['uid']} · {q['h']}",'',q['s'],''])
            lines.extend(f'- {"ABCD"[i]}. {v}' for i,v in enumerate(q['o']))
            lines.extend(['','<details><summary>做完再看：最短思路与易错点</summary>','',f"**答案：{'ABCD'[q['a']]}（{q['o'][q['a']]}）**",'',q['e'],'',f"**易错：**{q['tr']}",'','</details>',''])
    (ROOT/'原创天梯题册.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print('Markdown guide:',len(qs),'questions')
if __name__=='__main__':main()
