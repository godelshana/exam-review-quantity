# -*- coding: utf-8 -*-
"""AI vs 粉笔答案严格对账：选项内容映射，区分真争议与选项顺序差异"""
import json, os, re, urllib.parse, difflib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import build_xingce_registry

FB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fb")

def norm(s):
    return re.sub(r'[\s（）()、，。,:：;；．."\'"“”]', '', s or '')

papers = {}
for f in sorted(os.listdir(FB)):
    if not f.startswith('paper_') or not f.endswith('.json'): continue
    tag = urllib.parse.unquote(f.replace('paper_', '').replace('.json', ''))
    d = json.load(open(os.path.join(FB, f), encoding='utf-8'))
    ch = d['chapters']; counts = [c['count'] for c in ch]
    qs = []
    for i, q in enumerate(d['questions']):
        mod, acc = None, 0
        for j, c in enumerate(ch):
            acc += c['count']
            if i < acc: mod = c['name']; break
        choice = q.get('correctAnswer', {}).get('choice')
        opts = (q.get('accessories') or [{}])[0].get('options')
        opts = [re.sub(r'<[^>]+>', '', o or '') if isinstance(o, str) else None for o in (opts or [])]
        stem = re.sub(r'<[^>]+>', '', str(q.get('content') or ''))
        qs.append({'num': i+1, 'mod': mod, 'choice': choice, 'stem': stem, 'opts': opts, 'fenbi_id': q['id']})
    papers[tag] = qs

registry = build_xingce_registry()
ai = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_answers.json"), encoding='utf-8'))

result = {"agree": [], "dispute": [], "image_opt": [], "unmatched": []}
for key, answers in ai.items():
    if '|' not in key or not isinstance(answers, dict): continue
    y, lv, mod = key.split('|')
    if mod != '数量关系': continue
    tag = f'{y}{lv}'
    if tag not in papers: continue
    pap = registry.get((int(y), lv))
    if not pap or not pap['sections']: continue
    for b in pap['sections'].get('数量关系', []):
        mnum = b['num']
        val = answers.get(str(mnum))
        if val is None: continue
        ai_letter = None if str(val).startswith('?') else (val[-1] if str(val).endswith('图') else val)
        my_opts = b.get('opts') or {}
        k = norm(b.get('stem', ''))
        best = None
        for fq in papers[tag]:
            if fq['mod'] != '数量关系': continue
            fk = norm(fq['stem'])
            if (fk[:28] == k[:28] and len(fk) > 10) or difflib.SequenceMatcher(None, k, fk).ratio() > 0.82:
                best = fq; break
        if best is None or not best['choice']:
            result["unmatched"].append(f'{tag} Q{mnum}')
            continue
        fl = chr(ord('A') + int(best['choice']))
        fb_opt_content = best['opts'][int(best['choice'])] if best['opts'] and int(best['choice']) < len(best['opts']) else None
        if ai_letter is None:
            # AI未答（图形/矛盾）：粉笔答案可直接采用
            result["image_opt"].append(f'{tag} Q{mnum}: AI未答, 粉笔={fl} 内容={fb_opt_content}')
            continue
        my_content = my_opts.get(ai_letter)
        # 内容一致?
        same = False
        if my_content and fb_opt_content:
            same = norm(my_content) == norm(fb_opt_content) or norm(my_content) in norm(fb_opt_content) or norm(fb_opt_content) in norm(my_content)
        if same:
            result["agree"].append(f'{tag} Q{mnum}: {ai_letter}={fl}（内容一致: {my_content[:20]}）')
        else:
            # 选项内容是否在对方选项中存在（选项顺序不同导致字母不同）
            my_in_fb = None
            if my_content:
                for j, fo in enumerate(best['opts'] or []):
                    if fo and (norm(fo) == norm(my_content) or norm(fo) in norm(my_content) or norm(my_content) in norm(fo)):
                        my_in_fb = chr(ord('A') + j); break
            if my_in_fb and my_in_fb == fl:
                result["agree"].append(f'{tag} Q{mnum}: {ai_letter}/{fl}（选项顺序不同但答案内容一致）')
            elif my_in_fb:
                result["dispute"].append(f'{tag} Q{mnum}: AI选{ai_letter}({my_content[:18]}) 粉笔选{fl}({(fb_opt_content or "")[:18]}) — 真争议')
            else:
                result["image_opt"].append(f'{tag} Q{mnum}: AI={ai_letter}({str(my_content)[:18]}) 粉笔={fl} 内容为公式图或无法比对')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reconcile_result.json")
json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('一致:', len(result['agree']), '| 真争议:', len(result['dispute']), '| AI未答/图片:', len(result['image_opt']), '| 未匹配:', len(result['unmatched']))
print('\n--- 真争议 ---')
for d in result['dispute']: print(' ', d)
print('\n--- AI未答(粉笔补充) ---')
for d in result['image_opt']: print(' ', d)
