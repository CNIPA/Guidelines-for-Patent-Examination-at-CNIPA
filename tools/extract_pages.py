# -*- coding: utf-8 -*-
"""把《专利审查指南》PDF 解析成结构化 JSON（data/pages.json）。

每个页面记录：
  - 尺寸、页码标签（页脚数字）、页眉左右文本
  - 所有 span（含坐标、字体、字号、粗斜体标志）
  - 图片、矢量线条（用于识别表格框线/页眉横线）
用法: python tools/extract_pages.py [pdf路径] [输出json路径]
"""
import sys, os, json, io
import pymupdf as fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
PDF = sys.argv[1] if len(sys.argv) > 1 else paths.require(paths.PDF, 'PDF')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data/pages.json'


def fixfont(name):
    """PDF 里的中文字体名常是 GBK 被当作 latin1 读出来的乱码，还原它。"""
    if not name:
        return name
    # 去掉 ABCDEE+ 子集前缀
    base = name.split('+')[-1]
    try:
        return base.encode('latin1').decode('gbk')
    except Exception:
        return base


def main():
    doc = fitz.open(PDF)
    os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
    pages = []

    for pno in range(doc.page_count):
        page = doc[pno]
        data = page.get_text('dict')
        spans = []
        for b in data['blocks']:
            if b['type'] != 0:
                continue
            for line in b['lines']:
                for s in line['spans']:
                    txt = s['text']
                    if not txt.strip():
                        continue
                    spans.append({
                        'x0': round(s['bbox'][0], 2),
                        'y0': round(s['bbox'][1], 2),
                        'x1': round(s['bbox'][2], 2),
                        'y1': round(s['bbox'][3], 2),
                        'font': fixfont(s['font']),
                        'size': round(s['size'], 2),
                        'flags': s['flags'],
                        'dir': [round(v, 3) for v in line.get('dir', (1, 0))],
                        'text': txt,
                    })
        spans.sort(key=lambda s: (round(s['y0'], 1), s['x0']))

        imgs = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                info = doc.extract_image(xref)
                bbox = page.get_image_bbox(img)
                imgs.append({
                    'xref': xref,
                    'ext': info.get('ext'),
                    'w': info.get('width'),
                    'h': info.get('height'),
                    'bbox': [round(v, 2) for v in bbox] if bbox else None,
                })
            except Exception as e:
                imgs.append({'xref': xref, 'error': str(e)})

        lines = []
        for g in page.get_drawings():
            for it in g['items']:
                r = g['rect']
                lines.append({
                    'kind': it[0],
                    'rect': [round(v, 2) for v in r],
                    'color': g.get('color'),
                    'width': g.get('width'),
                })

        pages.append({
            'index': pno,
            'width': round(page.rect.width, 2),
            'height': round(page.rect.height, 2),
            'spans': spans,
            'images': imgs,
            'drawings': lines,
        })

    # 只记录“相对项目根目录”的可移植路径，避免把本机用户名/绝对路径写进数据
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        src = os.path.relpath(os.path.abspath(PDF), root).replace(os.sep, '/')
        if src.startswith('..'):
            src = os.path.basename(PDF)
    except ValueError:
        src = os.path.basename(PDF)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'source': src, 'pages': pages}, f, ensure_ascii=False)

    print('pages:', len(pages), '->', OUT)
    n_spans = sum(len(p['spans']) for p in pages)
    n_img = sum(len(p['images']) for p in pages)
    print('spans:', n_spans, 'images:', n_img)


if __name__ == '__main__':
    main()
