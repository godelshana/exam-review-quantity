"""发布题库结构门禁。数学门禁另见 audit_hand100 / audit_challenge24，不能以字段检查替代数学审计。"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import json,re,sys
ROOT=Path(__file__).resolve().parent
FILES=[('手写模拟题_100.js','HAND_LADDER_100',True),('原创复合24.js','CHALLENGE_Q',True),('精选GLM题库.js','CURATED_GLM_BANK',False)]
def load_js(path,var):
    t=path.read_text(encoding='utf-8-sig');m=re.search(r'window\.'+var+r'\s*=\s*(\[.*\]);\s*$',t,re.S)
    if not m:raise ValueError(f'{path.name}: 缺少{var}')
    return json.loads(m.group(1))
def numeric(v):
    try:
        v=v.strip();return ('number',Fraction(v[:-1])/100 if v.endswith('%') else Fraction(v))
    except (ValueError,ZeroDivisionError):return ('text',re.sub(r'\s+','',v))
def validate(bundles):
    errors=[];ids=set();stems=set()
    for name,questions,authored in bundles:
        if not questions: errors.append(f'{name}: 空题库')
        local=set()
        for i,q in enumerate(questions):
            uid=q.get('uid') or q.get('curationId');prefix=f'{name} {uid or i}'
            if not uid or uid in ids:errors.append(prefix+': 缺失或重复ID')
            ids.add(uid)
            for key in ['s','h','t','e','tr']:
                if not isinstance(q.get(key),str) or not q[key].strip():errors.append(prefix+': 缺文本 '+key)
            if type(q.get('a')) is not int or not 0<=q['a']<=3 or q.get('t')=='跳过':errors.append(prefix+': 不能将跳过当数学答案')
            # Plain letters can name objects (A组件). Use values or [[option:A]] for actual option references.
            for key in ['e','tr']:
                text=q.get(key,'')
                if re.search(r'(?:答案|正解)[为是：:\s]*[A-D](?![A-Za-z])|(?:选项|排除|选择|故选|选)\s*[A-D](?:项|(?=[，。；\s]|$))',text):
                    errors.append(prefix+': 解析请引用选项内容或[[option:A]]，不能硬编码选项字母 '+key)
            opts=q.get('o')
            if not isinstance(opts,list) or len(opts)!=4 or any(not isinstance(x,str) or not x.strip() for x in opts): errors.append(prefix+': 必须4个文本选项')
            elif len(set(map(numeric,opts)))!=4:errors.append(prefix+': 有重复或数值等价选项')
            stem=re.sub(r'\s+','',q.get('s',''))
            if stem in local:errors.append(prefix+': 题面精确重复')
            if authored and stem in stems:errors.append(prefix+': 原创跨批次重复')
            local.add(stem)
            if authored:
                stems.add(stem)
                if q.get('level') not in ['入门','熟练','深化','综合']:errors.append(prefix+': 缺人工分层')
            if q.get('sourceType')!='mock':errors.append(prefix+': 模拟题来源不合法')
            if not authored and q.get('mathAuditStatus')!='not_performed':errors.append(prefix+': GLM初筛不应伪称数审通过')
    return errors

def main():
    bundles=[(fn,load_js(ROOT/fn,var),auth) for fn,var,auth in FILES]
    errors=validate(bundles)
    for fn,qs,_ in bundles:print(fn,len(qs),dict(Counter(q.get('level','未定级') for q in qs)))
    for error in errors:print('FAIL',error)
    print(f'Schema: {len(errors)} errors. This does NOT certify mathematical correctness.')
    return bool(errors)
if __name__=='__main__':sys.exit(main())
