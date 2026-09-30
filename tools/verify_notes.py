# -*- coding: utf-8 -*-
"""正确校验生成 PDF 左侧边注对齐：以 content.json 为基准。

对每个带边注的段落：
  - 在生成 PDF 中找到该段落首行基线 (para_base) 与边注基线 (note_base)
  - 计算 gen_offset = note_base - para_base
  - 与 content.json 中该边注的 stored_offset 比对
若 gen_offset ≈ stored_offset，则标签落在“段首行 + 原书偏移”处 = 正确对齐。
（参考公式由 calib_note.tex 实测：note_base = para_firstline_base + offset）
"""
import sys, io, os, re, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pymupdf as fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, 'latex', 'main.pdf')
CONTENT = os.path.join(ROOT, 'data', 'content.json')


def baseline_of_rect(page, rect):
    """返回覆盖 rect 中心的 span 的基线 y；找不到则返回 rect 底边-2。"""
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2
    best, bestd = None, 1e9
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for ln in b['lines']:
            for s in ln['spans']:
                ox, oy = s.get('origin', (s['bbox'][0], s['bbox'][3]))
                if s['bbox'][0] <= cx <= s['bbox'][2] and s['bbox'][1] <= cy <= s['bbox'][3]:
                    d = (cx - (s['bbox'][0] + s['bbox'][2]) / 2) ** 2
                    if d < bestd:
                        bestd, best = d, oy
    return best if best is not None else (rect.y1 - 2)


def para_text(b):
    return ''.join(x[1] for x in b.get('segs', []) if isinstance(x, (list, tuple)))


def main():
    B = json.load(open(CONTENT, encoding='utf-8'))
    dg = fitz.open(GEN)

    # 收集带边注的段落：(para_frag, [(note_text, stored_offset)])
    paras = []
    for blk in B:
        if blk.get('t') == 'para' and blk.get('notes'):
            frag = para_text(blk)[:14].strip()
            frag = re.sub(r'\s+', '', frag)
            if len(frag) < 4:
                continue
            paras.append((frag, blk['notes']))

    # 为了前后中抽样：按 content.json 顺序，取首/中/尾若干
    n = len(paras)
    picks_idx = set()
    picks_idx |= set(range(0, min(12, n)))                      # 前
    mid = n // 2
    picks_idx |= set(range(mid - 6, mid + 6))                  # 中
    picks_idx |= set(range(max(0, n - 12), n))                 # 尾
    picks = sorted(i for i in picks_idx if 0 <= i < n)

    checked = 0
    maxdiff = 0.0
    fails = []
    for i in picks:
        frag, notes = paras[i]
        # 在生成 PDF 中搜索该段落（逐页）
        found_page = None
        para_rect = None
        for pno in range(dg.page_count):
            rects = dg[pno].search_for(frag)
            if rects:
                found_page, para_rect = pno, rects[0]
                break
        if found_page is None:
            continue
        para_base = baseline_of_rect(dg[found_page], para_rect)
        for ntxt, soff in notes:
            nshort = re.sub(r'\s+', '', ntxt)[:10]
            nrects = dg[found_page].search_for(nshort)
            if not nrects:
                continue
            # 取最靠近段落基线的边注
            nbase = min((baseline_of_rect(dg[found_page], r) for r in nrects),
                        key=lambda y: abs(y - para_base))
            gen_off = round(nbase - para_base, 1)
            soff_r = round(soff, 1)
            diff = abs(gen_off - soff_r)
            maxdiff = max(maxdiff, diff)
            checked += 1
            if diff > 3.0:
                fails.append((found_page, nshort, soff_r, gen_off, diff))
            # 仅前几个打印细节
            if checked <= 40:
                flag = 'OK ' if diff <= 3 else 'DIFF'
                print('P%-4d %-12s stored=%6.1f gen=%6.1f Δ=%5.1f %s'
                      % (found_page, nshort, soff_r, gen_off, diff, flag))

    print('=' * 70)
    print('共校验 %d 条边注；最大偏移差 %.1f bp' % (checked, maxdiff))
    if fails:
        print('偏差 >3bp 的 %d 条（页码, 标签, 存, 实测, 差）:' % len(fails))
        for f in fails[:30]:
            print('  ', f)
    else:
        print('全部边注对齐（Δ≤3bp）。')


if __name__ == '__main__':
    main()
