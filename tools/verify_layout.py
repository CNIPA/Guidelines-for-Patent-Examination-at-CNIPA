# -*- coding: utf-8 -*-
"""校验四项版式修复：封面居中 / 右侧标签 / 总目录链接 / 分目录非空。
用法：python tools/verify_layout.py
"""
import fitz, os, glob, io, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
LAT = os.path.join(ROOT, 'latex')
PDF = os.path.join(LAT, 'main.pdf')
ORI = paths.PDF


def cover_cx(doc, page_no, ylo_frac=0.55):
    """封面区域（页面上半部）深色像素的水平中心，纯 Python 像素法。"""
    pg = doc[page_no - 1]
    Z = 3.0
    pm = pg.get_pixmap(matrix=fitz.Matrix(Z, Z))
    W, H, n = pm.width, pm.height, pm.n
    buf = pm.samples
    r1 = int((1.0 - ylo_frac) * H)
    xmin, xmax, cnt, xsum = 10**9, -1, 0, 0
    stride = W * n
    for row in range(0, r1, 2):
        base = row * stride
        for col in range(0, W, 1):
            if buf[base + col * n] < 128:
                if col < xmin: xmin = col
                if col > xmax: xmax = col
                xsum += col; cnt += 1
    if cnt == 0:
        return None
    return (xmin / Z, xmax / Z, xsum / cnt / Z)


def count_right_notes(doc, x_thresh=467.0):
    """统计所有页中落在右侧页边（x0 > 阈值）的文字词数（正文右边界约 466.9）。
    目录页外缘的竖排灰底标签（x≈486..519，y<160）属预期设计，不计入。"""
    total = 0
    pages = []
    for i in range(len(doc)):
        for w in doc[i].get_text("words"):
            if w[0] > x_thresh and not (w[1] < 160 and w[0] > 470):
                total += 1
        if total and i not in pages and len(pages) < 50:
            pages.append(i + 1)
    return total, pages


def total_links(doc):
    n = 0
    for i in range(len(doc)):
        n += len(doc[i].get_links())
    return n


def ptc_stats():
    res = {}
    for f in glob.glob(os.path.join(LAT, 'main.*.ptc')):
        base = os.path.basename(f)
        txt = open(f, encoding='utf-8', errors='replace').read()
        kinds = {}
        for k in ('part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph'):
            kinds[k] = txt.count('\\ptcl{%s}' % k)
        res[base] = (len(txt.splitlines()), kinds, txt.strip() != '')
    return res


def part_toc_pages(doc):
    """分目录页 = 同时含独立的'目''录'二字、且至少有一行是节号(如 1. / 3.1 / 4.4.1)，
    或节号后跟标题。返回命中页码列表。"""
    hits = []
    for i in range(len(doc)):
        lines = [l.strip() for l in doc[i].get_text().splitlines()]
        joined = ''.join(lines)
        has_head = ('目' in joined and '录' in joined)
        sec = any(re.match(r'\d+\.', l) for l in lines)
        if has_head and sec:
            hits.append(i + 1)
    return hits


def main():
    print('=' * 60)
    print('1) 封面物理居中：当前 vs 原书（原书 cx≈267.9，页面中心 260.82）')
    cur = fitz.open(PDF)
    ori = fitz.open(ORI) if os.path.exists(ORI) else None
    for pn, name in [(1, '封面'), (5, '第一部分封面')]:
        c = cover_cx(cur, pn, 0.0)
        oc = cover_cx(ori, pn, 0.0) if ori else None
        cx = c[2] if c else -1
        ox = oc[2] if oc else -1
        if ox > 0:
            flag = 'OK' if abs(cx - ox) < 8 else 'CHECK'
        else:
            flag = 'OK' if abs(cx - 260.82) < 12 else 'CHECK'
        print('   %s (p%d): cx=%.1f  [原书 %.1f]  %s' % (name, pn, cx, ox, flag))

    print('=' * 60)
    print('2) 右侧边注标签（x0>467 的文字词数，应为 0）')
    rn, rpages = count_right_notes(cur)
    print('   右侧页边文字词数 = %d  %s' % (rn, 'OK' if rn == 0 else ('pages=%s' % rpages[:10])))

    print('=' * 60)
    print('3) 总目录可点击链接（Link 注释总数，主目录为"部分+章"两级，应≥35）')
    nl = total_links(cur)
    print('   链接注释总数 = %d  %s' % (nl, 'OK' if nl >= 35 else 'LOW'))

    print('=' * 60)
    print('4) 各部分目录 .ptc 数据（tectonic 成功后会清理 p*.ptc，仅 idx 常驻）')
    st = ptc_stats()
    if not st:
        print('   （无 .ptc 常驻文件——中间文件随编译清理，非空性改由第 5 项以渲染页证明）')
    for k in sorted(st):
        lines, kinds, nonempty = st[k]
        total_ent = sum(kinds.values())
        print('   %s: 行数=%d 条目=%d %s  %s' % (k, lines, total_ent, kinds, 'OK' if nonempty else 'EMPTY'))

    print('=' * 60)
    print('5) 分目录页已渲染条目（含"目录"标题 + 节号行）')
    ht = part_toc_pages(cur)
    print('   分目录渲染页 = %s  (共 %d 页)' % (ht, len(ht)))

    print('=' * 60)
    c1 = cover_cx(cur, 1, 0.0)
    cover_ok = bool(c1 and abs(c1[2] - 260.82) < 12)
    print('VERDICT:',
          'PASS' if (cover_ok and rn == 0 and nl >= 35 and len(ht) > 0)
          else 'NEEDS REVIEW')


if __name__ == '__main__':
    main()
