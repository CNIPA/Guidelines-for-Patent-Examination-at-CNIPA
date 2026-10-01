# -*- coding: utf-8 -*-
"""把 data/revisions_2025.json 覆盖层应用到 data/content.json, 生成
data/content_2026.json —— 一份"带修订标注"的结构化内容。

标注约定（与 EPO「showing modifications」一致）:
  * seg 样式 'add' = 新增（渲染为绿色）
  * seg 样式 'del' = 删除（渲染为红色删除线）
  * 块级字段 rev = 'add' | 'del' | 'edit' | 'renumber' | 'retitle'
      - 新增/删除的整段: 全段 seg 分别为 'add'/'del'
      - 修改的段落: segs 由 old/new 的字符级 diff 生成
      - 标题改号 renumber: old_num / old_title（渲染时作旧标题幽灵行）
      - 标题改名 retitle: old_text
build_tex.py 在干净版里忽略所有 'del' 标注、正文取新文本；在修订版里按
'add'→绿色、'del'→红色删除线渲染。

用法: python tools/apply_revisions.py
"""
import json, os, re, sys, io, difflib, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guidemodel as gm
from textdiff import diff_segs, merge_segs

CONTENT = os.path.join(ROOT, 'data', 'content.json')
REVS = os.path.join(ROOT, 'data', 'revisions_2025.json')
DECISION = os.path.join(ROOT, 'data', 'decision_items.json')
OUT = os.path.join(ROOT, 'data', 'content_2026.json')

CN = '一二三四五六七八九十'
MARKER_RE = re.compile(r'^(（[0-9ivxIVX一二三四五六七八九十]+）|【例\s*[0-9]+】|[0-9]+\.)')


# ------------------------------------------------------------------ 工具
def btext(b):
    return ''.join(t for _, t in b['segs']) if b['t'] == 'para' else b.get('text', '')


def norm_quote(s):
    return s.replace('‘', '“').replace('’', '”')




def split_by_newline(segs):
    """把带 '\\n' 的 seg 序列拆成多段（用于一次替换成多段的情形）。"""
    paras = [[]]
    for st, t in segs:
        if '\n' not in t:
            paras[-1].append([st, t])
        else:
            parts = t.split('\n')
            for k, p in enumerate(parts):
                if k > 0:
                    paras.append([])
                if p:
                    paras[-1].append([st, p])
    return [merge_segs(p) for p in paras if p]


def is_struct_heading(t):
    t = t.strip()
    if not re.match(r'^\d+(\.\d+)*', t):
        return False
    if len(t) > 60 or re.search(r'[。，；：]', t) or '其特征在于' in t:
        return False
    return True


def _num_with_dot(num):
    """一级（章内小节）标题号后要带点，如 “6.”；二级及以后不带，如 “6.1”“6.1.2”。"""
    if not num:
        return num
    return num if '.' in num else num + '.'


def make_heading(text):
    m = re.match(r'^(\d+(?:\.\d+)*)\.?\s*(.*)$', text.strip())
    num, title = m.group(1), m.group(2).strip()
    return {'t': 'heading', 'text': '%s %s' % (_num_with_dot(num), title), 'notes': [],
            'page_idx': 0, 'rev': 'add'}


def make_para(text, rev='add', indent=None):
    t = text.strip()
    if indent is None:
        indent = 17.5 if re.match(r'^（|^【例|^[①-⑨]', t) else 23.4
    style = 'add' if rev == 'add' else ('del' if rev == 'del' else '')
    return {'t': 'para', 'segs': [[style, t]], 'indent': indent, 'notes': [],
            'page_idx': 0, 'rev': rev}


# ------------------------------------------------------------------ 主体
class Applier:
    def __init__(self, blocks, items):
        self.b = blocks
        self.items = items
        self.log = []
        self.warn = []

    # --- 导航（每次重新扫描，容忍前面的插删） ---
    def _scan(self):
        part = [None] * len(self.b)
        chap = [None] * len(self.b)
        p = c = None
        for i, b in enumerate(self.b):
            if b['t'] == 'part':
                p, c = b['num'], None
            elif b['t'] == 'chaptertitle':
                c = gm.chapter_index(b.get('text', ''))
            part[i], chap[i] = p, c
        return part, chap

    def find_heading(self, part, chap, number):
        pa, ca = self._scan()
        for i, b in enumerate(self.b):
            if b['t'] == 'heading' and pa[i] == part and ca[i] == chap \
                    and gm.heading_number(b.get('text', '')) == number:
                return i
        return None

    def find_heading_by_title(self, part, chap, anchor):
        pa, ca = self._scan()
        for i, b in enumerate(self.b):
            if b['t'] == 'heading' and pa[i] == part and ca[i] == chap \
                    and anchor in b.get('text', ''):
                return i
        return None

    def paras(self, head):
        out = []
        for j in range(head + 1, len(self.b)):
            if self.b[j]['t'] in ('heading', 'chaptertitle', 'part'):
                break
            if self.b[j]['t'] == 'para':
                out.append(j)
        return out

    def section_end(self, head):
        for j in range(head + 1, len(self.b)):
            if self.b[j]['t'] in ('heading', 'chaptertitle', 'part'):
                return j
        return len(self.b)

    def section_subtree_end(self, part, chap, section):
        """section 及其所有子标题（如 6.3 → 6.3.1/6.3.2）之后的插入位置。
        仅用 section_end 会停在第一个子标题之前，导致 6.3.3 插到 6.3.1 前面。"""
        h = self.find_heading(part, chap, section)
        prefix = section + '.'
        j = h + 1
        while j < len(self.b):
            bj = self.b[j]
            if bj['t'] in ('chaptertitle', 'part'):
                break
            if bj['t'] == 'heading':
                num = gm.heading_number(bj.get('text', ''))
                if not (num and num.startswith(prefix)):
                    break
            j += 1
        return j

    def chapter_end(self, part, chap):
        pa, ca = self._scan()
        last = None
        for i, b in enumerate(self.b):
            if pa[i] == part and ca[i] == chap:
                last = i
        return (last + 1) if last is not None else len(self.b)

    def content(self, ref):
        for it in self.items:
            if it['idx'] == ref['item']:
                for s in it['subs']:
                    if s['marker'] == ref.get('sub', ''):
                        return [x.strip() for x in s['content'] if x.strip()]
        raise KeyError('decision item not found: %r' % (ref,))

    def instr(self, ref):
        for it in self.items:
            if it['idx'] == ref['item']:
                for s in it['subs']:
                    if s['marker'] == ref.get('sub', ''):
                        return s['instr']
        raise KeyError(ref)

    # --- 操作 ---
    def _add_blocks(self, at, texts, headings_ok=False):
        new = []
        for t in texts:
            if headings_ok and is_struct_heading(t):
                new.append(make_heading(t))
            else:
                new.append(make_para(t, rev='add'))
        self.b[at:at] = new
        return len(new)

    def replace_para(self, part, chap, section, para, n, ref):
        h = self.find_heading(part, chap, section)
        if h is None:
            self.warn.append('replace: section %s not found (p%s c%s)' % (section, part, chap))
            return
        ps = self.paras(h)
        tgt = ps[para:para + n]
        news = [norm_quote(x) for x in self.content(ref)]
        if not tgt:
            self.warn.append('replace: no target para %s#%d' % (section, para))
            return
        old_items = [btext(self.b[j]) for j in tgt]
        is_item = lambda s: bool(re.match(r'^\s*（\d+）', s))
        if all(is_item(x) for x in old_items) and all(is_item(x) for x in news):
            # 列表条目（（1）（2）…）按“条目正文”对齐：插入新条目时，旧条目改号只标序号，
            # 与官方《修改对照表》做法一致（新增(4)、原(4)改号为(5)）。
            blocks = self._align_items(old_items, news)
            self.b[tgt[0]:tgt[-1] + 1] = blocks
            self.log.append('replace_para p%s.c%s %s para%d 列表条目对齐 (%d->%d)' %
                            (part, chap, section, para, len(old_items), len(news)))
            return
        # 保留列表前缀（（N）/【例N】），使 diff 聚焦正文
        old0 = btext(self.b[tgt[0]])
        marker = MARKER_RE.match(old0)
        mtext = marker.group(1) if marker else ''
        if mtext and news and not MARKER_RE.match(news[0]):
            news = [mtext + news[0]] + news[1:]
        # 与“全部新段落拼接”做一次 diff（而非只与第一段），使新旧在跨段处正确对齐，
        # 再按 '\n' 拆回多段；逐字精确、标点不错配。
        old_concat = '\n'.join(btext(self.b[j]) for j in tgt)
        combined = '\n'.join(news)
        sm = difflib.SequenceMatcher(None, old_concat, combined, autojunk=False)
        matched = sum(bl.size for bl in sm.get_matching_blocks())
        sim = 2.0 * matched / (len(old_concat) + len(combined) or 1)
        if sim < 0.40:
            # 大段改写：逐字 diff 会非常碎，改为“整段删除 + 整段新增”成块显示，
            # 更接近官方《修改对照表》的观感（小改动仍走下面的精确 diff）。
            blocks = []
            for j in tgt:
                bb = dict(self.b[j])
                bb['segs'] = [['del', btext(bb)]]
                bb['rev'] = 'del'
                blocks.append(bb)
            for x in news:
                blocks.append(make_para(x))
            self.b[tgt[0]:tgt[-1] + 1] = blocks
            self.log.append('replace_para p%s.c%s %s para%d n=%d 大改(整段删+增) sim=%.2f' %
                            (part, chap, section, para, n, sim))
            return
        paras = split_by_newline(diff_segs(old_concat, combined))
        blocks = []
        for p in paras:
            bb = dict(self.b[tgt[0]])
            bb['segs'] = p
            bb['rev'] = 'edit'
            blocks.append(bb)
        self.b[tgt[0]:tgt[-1] + 1] = blocks
        self.log.append('replace_para p%s.c%s %s para%d n=%d (%d->%d, %d 段) sim=%.2f' %
                        (part, chap, section, para, n, n, len(news), len(blocks), sim))

    def _align_items(self, old_items, new_items):
        """按条目正文对齐两组列表条目，输出处理过的块列表。"""
        om = [re.match(r'^\s*(（\d+）)(.*)$', x, re.S) for x in old_items]
        nm = [re.match(r'^\s*(（\d+）)(.*)$', x, re.S) for x in new_items]
        ob = [m.group(2) for m in om]
        nb = [m.group(2) for m in nm]
        sm = difflib.SequenceMatcher(None, ob, nb, autojunk=False)
        blocks = []

        def mkpara(segs, rev):
            return {'t': 'para', 'segs': segs, 'indent': 17.5, 'notes': [],
                    'page_idx': 0, 'rev': rev}

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    oi, ni = i1 + k, j1 + k
                    mo, mn = om[oi].group(1), nm[ni].group(1)
                    if mo == mn:
                        blocks.append(mkpara([['', mo + ob[oi]]], 'edit'))
                    else:   # 仅是序号变化：只标序号
                        blocks.append(mkpara([['del', mo], ['add', mn], ['', ob[oi]]], 'edit'))
            elif tag == 'delete':
                for k in range(i1, i2):
                    blocks.append(mkpara([['del', old_items[k]]], 'del'))
            elif tag == 'insert':
                for k in range(j1, j2):
                    blocks.append(mkpara([['add', new_items[k]]], 'add'))
            else:   # replace
                if (i2 - i1) == (j2 - j1):
                    for k in range(i2 - i1):
                        blocks.append(mkpara(diff_segs(old_items[i1 + k], new_items[j1 + k]), 'edit'))
                else:
                    for k in range(i1, i2):
                        blocks.append(mkpara([['del', old_items[k]]], 'del'))
                    for k in range(j1, j2):
                        blocks.append(mkpara([['add', new_items[k]]], 'add'))
        return blocks

    def set_segs(self, part, chap, section, para, segs):
        """直接写入某一段的标注 seg（用于个别难以自动对齐、需要人工核定的段落）。"""
        h = self.find_heading(part, chap, section)
        ps = self.paras(h)
        j = ps[para]
        bb = dict(self.b[j])
        bb['segs'] = [[s, t] for s, t in segs]
        bb['rev'] = 'edit'
        self.b[j] = bb
        self.log.append('set_segs p%s.c%s %s para%d' % (part, chap, section, para))

    def append_para(self, part, chap, section, para, ref):
        h = self.find_heading(part, chap, section)
        ps = self.paras(h)
        j = ps[para]
        add = ''.join(self.content(ref))
        bb = dict(self.b[j])
        bb['segs'] = [list(s) for s in bb['segs']]
        bb['segs'].extend(diff_segs('', add))
        bb['rev'] = 'edit'
        self.b[j] = bb
        self.log.append('append_para p%s.c%s %s para%d' % (part, chap, section, para))

    def insert_after_para(self, part, chap, section, para, ref):
        h = self.find_heading(part, chap, section)
        ps = self.paras(h)
        at = ps[para] + 1
        k = self._add_blocks(at, self.content(ref))
        self.log.append('insert_after_para p%s.c%s %s para%d (+%d)' % (part, chap, section, para, k))

    def insert_before_para(self, part, chap, section, para, ref):
        h = self.find_heading(part, chap, section)
        ps = self.paras(h)
        at = ps[para]
        k = self._add_blocks(at, self.content(ref))
        self.log.append('insert_before_para p%s.c%s %s para%d (+%d)' % (part, chap, section, para, k))

    def insert_section_end(self, part, chap, section, ref):
        at = self.section_subtree_end(part, chap, section)
        k = self._add_blocks(at, self.content(ref), headings_ok=True)
        self.log.append('insert_section_end p%s.c%s %s (+%d)' % (part, chap, section, k))

    def insert_chapter_end(self, part, chap, ref):
        at = self.chapter_end(part, chap)
        k = self._add_blocks(at, self.content(ref), headings_ok=True)
        self.log.append('insert_chapter_end p%s.c%s (+%d)' % (part, chap, k))

    def insert_before_heading(self, part, chap, anchor, ref):
        h = self.find_heading_by_title(part, chap, anchor)
        if h is None:
            self.warn.append('insert_before_heading: anchor %r not found' % anchor)
            return
        k = self._add_blocks(h, self.content(ref), headings_ok=True)
        self.log.append('insert_before_heading p%s.c%s %r (+%d)' % (part, chap, anchor, k))

    def delete_para(self, part, chap, section, find):
        h = self.find_heading(part, chap, section)
        for j in self.paras(h):
            if find in btext(self.b[j]):
                bb = dict(self.b[j])
                bb['segs'] = [['del', btext(bb)]]
                bb['rev'] = 'del'
                self.b[j] = bb
                self.log.append('delete_para p%s.c%s %s %r' % (part, chap, section, find[:16]))
                return
        self.warn.append('delete_para not found: %s %r' % (section, find[:20]))

    def delete_section(self, part, chap, section):
        h = self.find_heading(part, chap, section)
        if h is None:
            self.warn.append('delete_section not found: %s' % section)
            return
        e = self.section_end(h)
        for j in range(h, e):
            bb = dict(self.b[j])
            if bb['t'] == 'para':
                bb['segs'] = [['del', btext(bb)]]
            elif 'text' in bb:
                bb['old_text'] = bb['text']
            bb['rev'] = 'del'
            self.b[j] = bb
        self.log.append('delete_section p%s.c%s %s (%d blocks)' % (part, chap, section, e - h))

    def retitle(self, part, chap, section, title):
        h = self.find_heading(part, chap, section)
        bb = dict(self.b[h])
        bb['old_text'] = bb['text']
        num = gm.heading_number(bb['text'])
        bb['text'] = ('%s %s' % (_num_with_dot(num), title)) if num else title
        bb['rev'] = 'retitle'
        self.b[h] = bb
        self.log.append('retitle p%s.c%s %s' % (part, chap, section))

    def renumber_headings(self, part, chap, mp):
        pa, ca = self._scan()
        cnt = 0
        for i, b in enumerate(self.b):
            if b['t'] != 'heading' or pa[i] != part or ca[i] != chap:
                continue
            num = gm.heading_number(b.get('text', ''))
            if num in mp:
                bb = dict(b)
                title = re.sub(r'^\s*\d+(?:\.\d+)*\.?\s*', '', bb['text']).strip()
                bb['old_text'] = bb['text']
                bb['text'] = '%s %s' % (mp[num], title)
                bb['rev'] = 'renumber'
                self.b[i] = bb
                cnt += 1
        self.log.append('renumber_headings p%s.c%s %s (%d)' % (part, chap, mp, cnt))

    def renumber_items(self, part, chap, section, mp):
        h = self.find_heading(part, chap, section)
        cnt = 0
        for j in self.paras(h):
            old = btext(self.b[j])
            m = MARKER_RE.match(old)
            if not m:
                continue
            tok = m.group(1)
            if tok not in mp:
                continue
            new = mp[tok] + old[m.end():]
            bb = dict(self.b[j])
            bb['segs'] = diff_segs(old, new)
            bb['rev'] = 'edit'
            self.b[j] = bb
            cnt += 1
        self.log.append('renumber_items p%s.c%s %s (%d)' % (part, chap, section, cnt))

    def pairreplace(self, part, chap, section, ref):
        instr = self.instr(ref)
        pairs = re.findall(r'“([^”]*)”\s*修改为\s*“([^”]*)”', instr)
        h = self.find_heading(part, chap, section)
        ps = self.paras(h)
        for old, new in pairs:
            new = norm_quote(new)
            done = False
            for j in ps:
                t = btext(self.b[j])
                nt = norm_quote(t)
                no = norm_quote(old)
                i = nt.find(no)
                if i < 0:
                    continue
                newtext = t[:i] + new + t[i + len(no):]
                bb = dict(self.b[j])
                bb['segs'] = diff_segs(t, newtext)
                bb['rev'] = 'edit'
                self.b[j] = bb
                done = True
                break
            if not done:
                self.warn.append('pairreplace not found in %s: %r' % (section, old[:24]))
        self.log.append('pairreplace p%s.c%s %s (%d pairs)' % (part, chap, section, len(pairs)))


def main():
    blocks = gm.load(CONTENT)
    items = json.load(open(DECISION, encoding='utf-8'))
    ov = json.load(open(REVS, encoding='utf-8'))
    ap = Applier(blocks, items)
    for op in ov['ops']:
        kind = op['op']
        fn = getattr(ap, kind)
        kw = {k: v for k, v in op.items() if k != 'op'}
        if 'chapter' in kw:
            kw['chap'] = kw.pop('chapter')
        if 'from' in kw:
            kw['ref'] = kw.pop('from')
        if 'map' in kw:
            kw['mp'] = kw.pop('map')
        fn(**kw)
    json.dump(ap.b, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('ops applied:', len(ov['ops']))
    for line in ap.log:
        print('  ', line)
    if ap.warn:
        print('WARNINGS:')
        for w in ap.warn:
            print('  !!', w)
    st = collections.Counter(b.get('rev') for b in ap.b if b.get('rev'))
    print('annotated blocks:', dict(st))
    print('-> ', OUT)


if __name__ == '__main__':
    main()
