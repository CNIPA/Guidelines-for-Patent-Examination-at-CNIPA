# -*- coding: utf-8 -*-
"""把《国家知识产权局关于修改〈专利审查指南〉的决定》(局令第84号) 解析为结构化条目.

思路: 决定正文是单栏排版, 正文左边界 x0≈79.4, 段落首行缩进到 x0≈111.4.
逐个"物理行"重建成"段落", 再按 顶层(一、二、…)/子项(（一）（二）…) 归类.

输入: source/20251113_国家知识产权局关于修改专利审查指南的决定.pdf
输出: data/decision_items.json
"""
import fitz, json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', '20251113_国家知识产权局关于修改专利审查指南的决定.pdf')
OUT = os.path.join(ROOT, 'data', 'decision_items.json')

CN = '一二三四五六七八九十'
CJK = r'\u3400-\u4dbf\u4e00-\u9fff\u3000-\u303f\uff00-\uffef'
INDENT_X = 100.0     # 段落首行 x0 阈值


def pages_text():
    d = fitz.open(SRC)
    out = []
    for i in range(d.page_count):
        out.append(d[i].get_text('dict'))
    d.close()
    return out


def despace(s):
    s = re.sub(r'\s+', ' ', s)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'(?<=[' + CJK + r']) +', '', s)
        s = re.sub(r' +(?=[' + CJK + r'])', '', s)
    return s.strip()


def is_annex_page(dic):
    """附件对照表页: 第一行内容为“附件”，或出现跨两栏(左右 x 各有一列)。"""
    for b in dic.get('blocks', []):
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans']).strip()
            if t == '附件' and l['bbox'][1] < 150:
                return True
    return False


def paragraph_lines(dic):
    """返回该页的正文物理行 (y, x0, font, text)，已剔除页码。"""
    rows = []
    for b in dic.get('blocks', []):
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans'])
            if not t.strip():
                continue
            x0, y0 = l['bbox'][0], l['bbox'][1]
            if y0 > 740:                     # 页码
                continue
            font = l['spans'][0]['font'] if l['spans'] else ''
            rows.append((y0, x0, font, t))
    rows.sort(key=lambda r: r[0])
    return rows


def build_paragraphs():
    paras = []          # [(font0, text)]
    cur = None
    for dic in pages_text():
        if is_annex_page(dic):
            break
        for y0, x0, font, t in paragraph_lines(dic):
            if x0 >= INDENT_X:
                if cur:
                    paras.append(cur)
                cur = [font, t]
            else:
                if cur is None:
                    cur = [font, t]
                else:
                    cur[1] += t
    if cur:
        paras.append(cur)
    return [(f, despace(txt)) for f, txt in paras]


def main():
    paras = build_paragraphs()

    items = []
    cur_item = None
    cur_sub = None
    for font, txt in paras:
        if not txt:
            continue
        m = re.match(r'^([一二三四五六七八九十]+)、\s*(.*)$', txt)
        if m:
            cur_item = {'idx': m.group(1), 'title': m.group(2), 'subs': []}
            items.append(cur_item)
            cur_sub = None
            continue
        if cur_item is None:
            continue
        m = re.match(r'^（([' + CN + r']+)）(.*)$', txt)
        if m:
            cur_sub = {'marker': m.group(1), 'instr': m.group(2), 'content': []}
            cur_item['subs'].append(cur_sub)
            continue
        if cur_sub is None:
            # 顶层条目下的直属段落（无子项）
            cur_sub = {'marker': '', 'instr': txt, 'content': []}
            cur_item['subs'].append(cur_sub)
        else:
            if re.match(r'^本节其他内容无修改。?$', txt) or txt.startswith('本决定自') \
                    or txt.startswith('附件'):
                continue
            cur_sub['content'].append(txt)

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=1)

    print('items:', len(items), '->', OUT)
    for it in items:
        print('\n### %s、%s' % (it['idx'], it['title']))
        for s in it['subs']:
            print('   [%s] instr: %s' % (s['marker'], s['instr'][:80]))
            print('        content paras: %d  chars=%d' %
                  (len(s['content']), sum(len(x) for x in s['content'])))
    print('\ntotal content chars:',
          sum(len(x) for it in items for s in it['subs'] for x in s['content']))
    print('total paras:', sum(len(it['subs']) for it in items))


if __name__ == '__main__':
    main()
