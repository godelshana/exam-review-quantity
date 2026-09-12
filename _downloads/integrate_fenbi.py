# -*- coding: utf-8 -*-
"""整合粉笔数据：题干匹配映射到主库题号 + 下载题目图片 + 生成粉笔版markdown"""
import json, os, re, urllib.parse, difflib, sys, time
import urllib.request, ssl

BASE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.join(BASE, "fb")
IMGDIR = os.path.normpath(os.path.join(BASE, "..", "真题库", "图片", "fenbi"))
sys.path.insert(0, BASE)

HEADER_RE = re.compile(r'\d{4}年国家公务员录用考试|《行测》题?|（[^）]*回忆[^）]*）|考生回忆版|---估分')
def norm(s):
    s = HEADER_RE.sub('', s or '')
    return re.sub(r'[^\u4e00-\u9fa50-9A-Za-z0-9]', '', s)[:40]

VISUAL_MAP = {
    ("2023", "副省级", 67): "C", ("2023", "副省级", 71): "A",
    ("2023", "地市级", 69): "A",
    ("2023", "行政执法类", 62): "C", ("2023", "行政执法类", 66): "D", ("2023", "行政执法类", 70): "A",
    ("2024", "行政执法类", 64): "C",
    ("2025", "副省级", 79): "D",
    ("2025", "地市级", 66): "B", ("2025", "地市级", 74): "D",
    ("2025", "行政执法类", 70): "B", ("2025", "行政执法类", 75): "C",
    ("2026", "副省级", 71): "B", ("2026", "副省级", 72): "C",
}
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
        letter = chr(ord('A') + int(choice)) if choice is not None and str(choice).isdigit() and 0 <= int(choice) <= 3 else None
        qs.append({'num': i+1, 'mod': mod, 'choice': choice, 'answer': letter,
                   'stem': q.get('content') or '', 'material': q.get('material'),
                   'options': (q.get('accessories') or [{}])[0].get('options') or [],
                   'type': q.get('type'), 'fenbi_id': q['id']})
    papers[tag] = {'paperId': d['paperId'], 'exerciseId': d['exerciseId'],
                   'chapters': d['chapters'], 'questions': qs}

# ---------- 下载图片（静态资源，无需登录） ----------
os.makedirs(IMGDIR, exist_ok=True)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def dl_img(url, fname):
    if url.startswith('//'): url = 'https:' + url
    out = os.path.join(IMGDIR, fname)
    if os.path.exists(out) and os.path.getsize(out) > 100: return fname
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.fenbi.com/'})
        data = urllib.request.urlopen(req, timeout=25, context=CTX).read()
        open(out, 'wb').write(data)
        return fname
    except Exception as e:
        print('  img fail:', url[:60], str(e)[:40])
        return None

def rewrite_images(html, tag, qnum, counter):
    """把题目HTML中的图片下载到本地并替换为相对引用"""
    def rep(m):
        src = m.group(1)
        ext = '.png'
        counter[0] += 1
        fname = f'{tag}_{qnum:03d}_{counter[0]}{ext}'
        ok = dl_img(src, fname)
        if ok:
            return f'<img src="../../图片/fenbi/{fname}"/>'
        return m.group(0)
    return re.sub(r'<img[^>]*?src="([^"]+)"[^>]*/?>', rep, html or '')

# ---------- 题干匹配映射到主库 ----------
fenbi_answers = {}   # "year|level" -> {my_num: {"ans":letter, "fenbi_num":n, "fenbi_id":id}}
mlog = {"matched": 0, "unmatched": []}

for tag, pp in papers.items():
    m = re.match(r'(\d{4})(副省级|地市级|行政执法类)', tag)
    if not m: continue
    y, lv = m.group(1), m.group(2)
    fn = None
    for cand in [f'parsed/xg_xc_{y}_{lv}.json', f'parsed/aipta_xc_{y}_{lv}.json', f'parsed/sl_xc_{y}_{lv}.json']:
        p = os.path.join(BASE, cand)
        if os.path.exists(p): fn = p; break
    if not fn:
        print('无主库来源:', tag); continue
    dd = json.load(open(fn, encoding='utf-8'))
    amap = {}
    used = set()
    for modname, blocks in dd['sections'].items():
        for b in blocks:
            k = norm(b.get('stem', ''))
            if len(k) < 12: continue
            best, bestscore = None, 0
            for fq in pp['questions']:
                if fq['fenbi_id'] in used or fq['mod'] != modname: continue
                fk = norm(fq['stem'])
                if len(fk) < 12: continue
                if fk[:26] == k[:26]:
                    best, bestscore = fq, 1.0; break
                sc = difflib.SequenceMatcher(None, k, fk).ratio()
                if sc > bestscore: best, bestscore = fq, sc
            if best and bestscore > 0.75:
                used.add(best['fenbi_id'])
                if best['answer']:
                    # 选项内容映射：粉笔答案内容 -> 我库选项字母
                    my_letter = None
                    fb_content = ''
                    if best['options'] and best['choice'] is not None and int(best['choice']) < len(best['options']):
                        fb_content = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', str(best['options'][int(best['choice'])])))
                    if fb_content:
                        for j in range(4):
                            mo = (b.get('opts') or {}).get(chr(ord('A') + j))
                            if mo is None: continue
                            mo_n = re.sub(r'\s+', '', str(mo))
                            if mo_n and (mo_n == fb_content or mo_n in fb_content or fb_content in mo_n):
                                my_letter = chr(ord('A') + j); break
                    my_letter2 = VISUAL_MAP.get((y, lv, b['num']))
                    amap[str(b['num'])] = {'ans': my_letter or my_letter2 or best['answer'],
                                           'fenbi_letter': best['answer'],
                                           'mapped': bool(my_letter or my_letter2),
                                       'visual': bool(my_letter2),
                                           'fenbi_num': best['num'], 'fenbi_id': best['fenbi_id']}
                    mlog['matched'] += 1
            else:
                mlog['unmatched'].append(f'{tag} {modname} Q{b["num"]}: {k[:24]}')
    fenbi_answers[f'{y}|{lv}'] = amap

json.dump(fenbi_answers, open(os.path.join(BASE, 'fenbi_answers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mlog, open(os.path.join(BASE, 'fenbi_match_log.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('题干匹配成功:', mlog['matched'], '未匹配:', len(mlog['unmatched']))
for u in mlog['unmatched'][:15]: print('  ', u)

# ---------- 生成粉笔版 markdown（含图片下载） ----------
YROOT = os.path.normpath(os.path.join(BASE, '..', '真题库', '按年份'))
LVMAP = {'副省级': '副省级', '地市级': '地市级', '行政执法类': '行政执法类'}

for tag, pp in papers.items():
    m = re.match(r'(\d{4})(副省级|地市级|行政执法类)', tag)
    if not m: continue
    y, lv = m.group(1), m.group(2)
    L = [f'# {y}年国考《行政职业能力测验》粉笔版（{lv}·网友回忆）', '']
    L.append(f'> 来源：粉笔题库（paperId {pp["paperId"]}）｜题目含粉笔官方标注的正确答案（选项后标注 ✅）')
    L.append('> 图形/公式以图片引用保存于 `真题库/图片/fenbi/`；解析请移步粉笔APP对应试卷。')
    L.append('')
    counter = [0]
    # 按章节输出
    qidx = 0
    amap = fenbi_answers.get(f'{y}|{lv}', {})
    by_my_num = {int(k): v for k, v in amap.items()}
    for ch in pp['chapters']:
        L.append(f'## {ch["name"]}（共{ch["count"]}题）')
        L.append('')
        for _ in range(ch['count']):
            q = pp['questions'][qidx]; qidx += 1
            stem_html = rewrite_images(q['stem'] if isinstance(q['stem'], str) else '', tag, q['num'], counter)
            stem_txt = re.sub(r'<img[^>]*?src="([^"]+)"[^>]*/?>', lambda mm: f'![图]({mm.group(1)})', stem_html)
            stem_txt = re.sub(r'</p>\s*<p[^>]*>', '\n\n', stem_txt)
            stem_txt = re.sub(r'<[^>]+>', '', stem_txt)
            L.append(f'**{q["num"]}.** {stem_txt.strip()}')
            L.append('')
            if q['material']:
                mat = q['material'] if isinstance(q['material'], str) else ''
                mat = rewrite_images(mat, tag, q['num'], counter)
                mat = re.sub(r'<img[^>]*?src="([^"]+)"[^>]*/?>', lambda mm: f'![图]({mm.group(1)})', mat)
                mat = re.sub(r'</p>\s*<p[^>]*>', '\n\n', mat)
                mat = re.sub(r'<[^>]+>', '', mat)
                if mat.strip():
                    L.append('> 材料：' + mat.strip()[:4000])
                    L.append('')
            for j, o in enumerate(q['options'] or []):
                letter = chr(ord('A') + j)
                mark = ' ✅' if (q['answer'] == letter) else ''
                if isinstance(o, str) and '<img' in o:
                    ohtml = rewrite_images(o, tag, q['num'], counter)
                    imgs = re.findall(r'<img[^>]*?src="([^"]+)"', ohtml)
                    otxt = re.sub(r'<img[^>]*?src="[^"]*"[^>]*/?>', '', ohtml)
                    otxt = re.sub(r'</?p[^>]*>', ' ', otxt)
                    otxt = re.sub(r'\s+', ' ', otxt).strip()
                    md_imgs = ' '.join(f'![图]({u})' for u in imgs)
                    if otxt:
                        L.append(f'- {letter}. {otxt} {md_imgs}{mark}'.rstrip())
                    else:
                        L.append(f'- {letter}. {md_imgs}{mark}')
                else:
                    L.append(f'- {letter}. {o}{mark}')
            # 我库题号的粉笔答案
            fa = by_my_num.get(q['num'])
            if fa and fa['ans'] == q['answer']:
                pass
            L.append('')
    # 统计图片下载次数需要重下？已有缓存，跳过
    outdir = os.path.join(YROOT, f'{y}年国考')
    os.makedirs(outdir, exist_ok=True)
    write = os.path.join(outdir, f'行测_{LVMAP[lv]}_粉笔版.md')
    open(write, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('生成', write, f'({counter[0]}张图片)')
print('DONE')
