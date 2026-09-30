# -*- coding: utf-8 -*-
"""分析《专利审查指南》PDF 的版面参数：页边距、行距、字号、字体、页眉页脚。"""
import sys, io, collections
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
PDF = sys.argv[1] if len(sys.argv) > 1 else paths.require(paths.PDF, 'PDF')
doc = fitz.open(PDF)


def fixfont(name):
    try:
        return name.encode('latin1').decode('gbk')
    except Exception:
        return name


print('pages:', doc.page_count, 'size(pt):', doc[0].rect.width, doc[0].rect.height)
print('size(mm): %.2f x %.2f' % (doc[0].rect.width / 72 * 25.4, doc[0].rect.height / 72 * 25.4))

size_hist = collections.Counter()      # (font, size) -> count
left_hist = collections.Counter()      # round(x0) -> count (正文宋体)
line_gap = collections.Counter()       # 行间距
top_hist = collections.Counter()
bot_hist = collections.Counter()

pages_sample = range(0, doc.page_count)
for pno in pages_sample:
    page = doc[pno]
    H = page.rect.height
    data = page.get_text('dict')
    prev_y = None
    for b in data['blocks']:
        if b['type'] != 0:
            continue
        for line in b['lines']:
            for s in line['spans']:
                txt = s['text'].strip()
                if not txt:
                    continue
                f = fixfont(s['font'])
                sz = round(s['size'], 2)
                size_hist[(f, sz)] += 1
                x0, y0, x1, y1 = s['bbox']
                if y0 < 80:
                    top_hist[(round(y0), f, sz)] += 1
                if y1 > H - 80:
                    bot_hist[(round(y0), f, sz)] += 1
                if f == '宋体' and abs(sz - 10.56) < 0.3:
                    left_hist[round(x0)] += 1
            # 行距
            ys = [s['bbox'][1] for s in line['spans']]
            if ys:
                y = min(ys)
                if prev_y is not None:
                    d = round(y - prev_y, 1)
                    if 0 < d < 40:
                        line_gap[d] += 1
                prev_y = y

print('\n== (字体, 字号) 频次 ==')
for k, v in size_hist.most_common(25):
    print('  %-18s %6.2f  %7d' % (k[0], k[1], v))

print('\n== 正文(宋体10.56) 左边界 x0 频次 top20 ==')
for k, v in left_hist.most_common(20):
    print('  x0=%-6s %d' % (k, v))

print('\n== 行距(基线间距) top20 ==')
for k, v in line_gap.most_common(20):
    print('  %-6s %d' % (k, v))

print('\n== 页眉区(y<80) top15 ==')
for k, v in top_hist.most_common(15):
    print('  y=%-5s %-14s %-6s %d' % (k[0], k[1], k[2], v))

print('\n== 页脚区(y>H-80) top15 ==')
for k, v in bot_hist.most_common(15):
    print('  y=%-5s %-14s %-6s %d' % (k[0], k[1], k[2], v))
