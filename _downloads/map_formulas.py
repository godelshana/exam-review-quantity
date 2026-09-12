# -*- coding: utf-8 -*-
"""未映射的24题：提取粉笔答案选项的公式图，拼图供视觉读取"""
import json, os, re, urllib.request, urllib.parse, ssl
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.join(BASE, "fb")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

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
        qs.append({'num': i+1, 'mod': mod, 'choice': q.get('correctAnswer', {}).get('choice'),
                   'options': (q.get('accessories') or [{}])[0].get('options') or []})
    papers[tag] = qs

fa = json.load(open(os.path.join(BASE, 'fenbi_answers.json'), encoding='utf-8'))
targets = []
for key, amap in fa.items():
    y, lv = key.split('|')
    qs = papers[f'{y}{lv}']
    for num, v in amap.items():
        if v.get('mapped'): continue
        num = int(num)
        q = qs[num-1]
        if q['mod'] != '数量关系' or not q['choice']: continue
        letter_idx = int(q['choice'])
        opt = q['options'][letter_idx] if letter_idx < len(q['options']) else None
        if isinstance(opt, str) and 'src="' in opt:
            src = re.search(r'src="([^"]+)"', opt).group(1)
            targets.append((key, num, chr(ord('A')+letter_idx), src))

print('待读取:', len(targets))
os.makedirs(os.path.join(BASE, 'fb_optimgs'), exist_ok=True)
rows = []
for key, num, letter, src in targets:
    if src.startswith('//'): src = 'https:' + src
    fn = re.sub(r'[^\w]', '_', src[-30:]) + '.png'
    fp = os.path.join(BASE, 'fb_optimgs', fn)
    if not os.path.exists(fp):
        try:
            req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.fenbi.com/'})
            data = urllib.request.urlopen(req, timeout=25, context=CTX).read()
            open(fp, 'wb').write(data)
        except Exception as e:
            print('fail', key, num, letter, str(e)[:40]); continue
    try:
        imrgba = Image.open(fp).convert('RGBA')
        im = Image.new('RGB', imrgba.size, 'white')
        im.paste(imrgba, mask=imrgba.split()[-1])
    except Exception:
        print('bad image file, skip:', key, num); continue
    if im.width > 500:
        im = im.resize((500, int(im.height * 500 / im.width)))
    rows.append((f'{key} Q{num} 粉笔答案={letter}', im))

# 拼图：每5题一张
W = 620
sheet, cur, cur_h = [], [], 0
for label, im in rows:
    h = im.height + 44
    if cur_h + h > 1350 and cur:
        sheet.append(cur); cur, cur_h = [], 0
    cur.append((label, im)); cur_h += h
if cur: sheet.append(cur)
for si, group in enumerate(sheet):
    th = sum(im.height + 44 for _, im in group) + 10
    canvas = Image.new('RGB', (W, th), 'white')
    draw = ImageDraw.Draw(canvas)
    yy = 5
    for label, im in group:
        draw.text((8, yy), label, fill='red'); yy += 28
        canvas.paste(im, (8, yy)); yy += im.height + 14
    canvas.save(os.path.join(BASE, f'fbopt_{si}.png'))
    print(f'fbopt_{si}.png', canvas.size, len(group))
