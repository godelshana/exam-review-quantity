# -*- coding: utf-8 -*-
"""Validate quantity-drill banks before merging or publishing.

Usage: python 教学/速刷/validate_bank.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors=[]; warnings=[]
def load_js(path, var):
    text=path.read_text(encoding='utf-8')
    m=re.search(rf'window\.{var}\s*=\s*(\[.*\]);\s*$', text, re.S)
    if not m: errors.append(f'{path.name}: 找不到 window.{var} 数组'); return []
    try: return json.loads(m.group(1))
    except Exception as e: errors.append(f'{path.name}: JSON解析失败: {e}'); return []

def check(q, i, source):
    required=['h','t','s','o','a','e']
    for k in required:
        if k not in q: errors.append(f'{source}[{i}] 缺字段 {k}')
    if not isinstance(q.get('s'),str) or not q.get('s','').strip(): errors.append(f'{source}[{i}] 空题干')
    opts=q.get('o')
    if not isinstance(opts,list) or len(opts)!=4: errors.append(f'{source}[{i}] 选项不是4个')
    elif any(not isinstance(x,str) or not x.strip() for x in opts): errors.append(f'{source}[{i}] 存在空选项')
    elif len(set(opts))!=4: errors.append(f'{source}[{i}] 选项重复')
    a=q.get('a')
    if not isinstance(a,int) or not -1<=a<=3: errors.append(f'{source}[{i}] 答案下标非法: {a}')
    if a==-1 and q.get('t')!='跳过': warnings.append(f'{source}[{i}] a=-1但卡型不是跳过')
    if q.get('sourceType')=='real':
        for k in ('year','paper','number'):
            if not q.get(k): errors.append(f'{source}[{i}] 真题缺{ k }')
    if len(q.get('s',''))>180: warnings.append(f'{source}[{i}] 题干偏长')

def main():
    mock=load_js(ROOT/'题库数据.js','BANK')
    hand=load_js(ROOT/'手写模拟题.js','HAND_Q')
    real=load_js(ROOT/'真题数量关系.js','REAL_Q')
    seen=set()
    for name,bank in [('GLM模拟题',mock),('手写模拟题',hand),('真题',real)]:
        for i,q in enumerate(bank):
            check(q,i,name)
            key=(q.get('sourceType','mock'),q.get('year',''),q.get('paper',''),q.get('number',''),q.get('s',''))
            if key in seen: errors.append(f'{name}[{i}] 重复题目/元数据')
            seen.add(key)
    print(f'GLM模拟题: {len(mock)}  手写模拟题: {len(hand)}  真题: {len(real)}')
    print(f'错误: {len(errors)}  警告: {len(warnings)}')
    for x in errors: print('ERROR',x)
    for x in warnings[:50]: print('WARN ',x)
    return 1 if errors else 0
if __name__=='__main__': sys.exit(main())
