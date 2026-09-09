"""粗粒度教学结构抽样映射；不把100个细标题假称100个模型。"""
import json, sys
from pathlib import Path
from build_hand100_review import G
ROOT=Path(__file__).resolve().parent

def build():
    mapping={}
    for i,line in enumerate(G.strip().splitlines(),1):
        ids,name,_=line.split('|')
        for n in map(int,ids.split(',')):
            uid=f'hand100:v2:{n:03}'
            if uid in mapping:raise ValueError('重复结构归组 '+uid)
            mapping[uid]='model:'+name
    if len(mapping)!=100:raise ValueError('百题结构归组未全覆盖')
    # 复合补充与百题中已有的粗模型共享抽样家族；不是数学严格同构的宣称。
    anchors={1:2,2:74,3:80,4:56,5:8,6:21,7:84,8:85,9:17,11:63,12:41,13:41,14:43,15:91,16:68,17:24,18:73,19:3,21:75,22:86,23:74,24:25}
    for n,anchor in anchors.items():mapping[f'challenge:{n:03}']=mapping[f'hand100:v2:{anchor:03}']
    mapping['challenge:010']='model:整除末位与条件相邻排列'
    mapping['challenge:020']='model:混合再蒸发的分段溶质守恒'
    return mapping

def main():
    data=build();content=('// 作者粗粒度结构归并，用于避免五题内同模型扎堆；不是模型互异性证明。\nwindow.TRAINING_FAMILIES = '+json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+';\n').encode('utf-8')
    out=ROOT/'training_families.js'
    if '--check' in sys.argv:
        if not out.is_file() or out.read_bytes()!=content:raise SystemExit('教学结构抽样映射需重新生成')
    else:out.write_bytes(content)
    print('Training families:',len(data),'questions;',len(set(data.values())),'coarse groups')
if __name__=='__main__':main()
