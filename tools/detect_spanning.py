# -*- coding: utf-8 -*-
"""检测哪些正文段落跨页：输出 data/at_skip.json（这些段落不加 ActualText 标记）。

为什么要跳过跨页段落：
  把整段包进 /Span<</ActualText ...>> BDC ... EMC 时，若该段跨物理页，
  BDC 与 EMC 会分处两页，部分阅读器（PyMuPDF/poppler）会把整段文本在两页各
  抽一次 → 复制/检索时出现重复；同时内容流出现 EMC 不匹配。
  因此只在“单页内”的段落上启用 ActualText。

用法（须在 latex/main.pdf 为“未加标记”的版本上运行）：
    python tools/build_tex.py          # ACTUALTEXT=0
    (tectonic 编译)
    python tools/detect_spanning.py    # -> data/at_skip.json
    python tools/build_tex.py          # ACTUALTEXT=1（自动读取 skip 列表）
"""
import json, os, re, sys, io, bisect
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'data', 'content.json')
PDF = os.path.join(ROOT, 'latex', 'main.pdf')
OUT = os.path.join(ROOT, 'data', 'at_skip.json')


def norm(s):
    return re.sub(r'\s+', '', s or '')


def para_plain(b):
    return norm(''.join(x[1] for x in b.get('segs', [])))


def main():
    blocks = json.load(open(CONTENT, encoding='utf-8'))
    paras = [b for b in blocks if b['t'] == 'para']

    doc = fitz.open(PDF)
    pages = [norm(p.get_text()) for p in doc]
    doc.close()
    C = ''.join(pages)
    offs = [0]
    for t in pages:
        offs.append(offs[-1] + len(t))

    def page_of(pos):
        return bisect.bisect_right(offs, pos) - 1

    cursor = 0
    skip = []
    matched = 0
    for i, b in enumerate(paras):
        plain = para_plain(b)
        if len(plain) < 8:
            continue  # 极短段落不会跨页，保留标记
        head = plain[:20]
        tail = plain[-20:]
        hs = C.find(head, cursor)
        if hs < 0:
            hs = C.find(head)
        if hs < 0:
            skip.append(i)
            continue
        cursor = hs
        te = C.find(tail, hs)
        if te < 0:
            skip.append(i)
            continue
        end = te + len(tail)
        matched += 1
        if page_of(hs) != page_of(end - 1):
            skip.append(i)

    json.dump(skip, open(OUT, 'w', encoding='utf-8'))
    print('段落总数 %d，已定位 %d，跨页/不可定位（跳过标记） %d -> %s'
          % (len(paras), matched, len(skip), os.path.relpath(OUT, ROOT)))


if __name__ == '__main__':
    main()
