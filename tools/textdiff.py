# -*- coding: utf-8 -*-
"""文本 diff 工具（apply_revisions.py 与 build_tex.py 共用）。

粒度策略（兼顾“精确”与“完整记号”）：
  1. 先按句末标点（。；！？换行）对齐——保证标点不会被错配（如新增句末的“。”）；
  2. 同一句内做“记号级”比较：逐字精确，但例号/列表号/章节号作为整体
     （【例10】→【例12】、6.1.3→6.1.4 标整个记号，而不是只标一个数字）；
  3. 输出统一“删除在前、新增在后”。
"""
import re
import difflib

_SENT_END = '。；！？\n'
_TOKEN_RE = re.compile(r'【例\s*\d+】|（[0-9A-Za-z一二三四五六七八九十ivxIVX]+）|\d+(?:\.\d+)*')


def merge_segs(segs):
    out = []
    for st, t in segs:
        if not t:
            continue
        if out and out[-1][0] == st:
            out[-1][1] += t
        else:
            out.append([st, t])
    return out


def _split_sent(t):
    out, buf = [], ''
    for ch in t:
        buf += ch
        if ch in _SENT_END:
            out.append(buf)
            buf = ''
    if buf:
        out.append(buf)
    return out


def _tokenize(t):
    out, i = [], 0
    while i < len(t):
        m = _TOKEN_RE.match(t, i)
        if m:
            out.append(m.group(0))
            i = m.end()
        else:
            out.append(t[i])
            i += 1
    return out


def _token_diff(old, new):
    ot, nt = _tokenize(old), _tokenize(new)
    sm = difflib.SequenceMatcher(None, ot, nt, autojunk=False)
    segs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            segs.append(['', ''.join(ot[i1:i2])])
        elif tag == 'delete':
            segs.append(['del', ''.join(ot[i1:i2])])
        elif tag == 'insert':
            segs.append(['add', ''.join(nt[j1:j2])])
        else:
            segs.append(['del', ''.join(ot[i1:i2])])
            segs.append(['add', ''.join(nt[j1:j2])])
    return segs


def _order_del_before_add(segs):
    out, i = [], 0
    while i < len(segs):
        if segs[i][0] in ('add', 'del'):
            j = i
            dels, adds = [], []
            while j < len(segs) and segs[j][0] in ('add', 'del'):
                (dels if segs[j][0] == 'del' else adds).append(segs[j][1])
                j += 1
            if dels:
                out.append(['del', ''.join(dels)])
            if adds:
                out.append(['add', ''.join(adds)])
            i = j
        else:
            out.append(segs[i])
            i += 1
    return merge_segs(out)


def _coalesce(segs, max_eq=1):
    """把被“极短相同片段”割裂的改动合并成“整词删除 + 整词新增”。
    例如 同样的→相同或者实质相同的：中间相同的“同”被并入两侧，显示为
    删除“同样的” + 新增“相同或者实质相同的”，比逐字交错更易读。"""
    out, i, n = [], 0, len(segs)
    while i < n:
        if segs[i][0] == '':
            out.append(segs[i])
            i += 1
            continue
        old, new = [], []
        while i < n:
            st, t = segs[i]
            if st == 'del':
                old.append(t)
                i += 1
            elif st == 'add':
                new.append(t)
                i += 1
            else:
                j, eq = i, ''
                while j < n and segs[j][0] == '':
                    eq += segs[j][1]
                    j += 1
                if j < n and len(eq) <= max_eq:
                    old.append(eq)
                    new.append(eq)
                    i = j
                else:
                    break
        if old:
            out.append(['del', ''.join(old)])
        if new:
            out.append(['add', ''.join(new)])
    return merge_segs(out)


def diff_segs(old, new, max_eq=None):
    """精确 diff（句子对齐 + 逐字，例号/列表号/章节号整体）。
    max_eq=None 时自动判定合并力度：改动较碎（块数>10，通常为整段改写）才适度合并，
    其余保持逐字精确。"""
    old = old.rstrip()
    new = new.rstrip()
    osen, nsen = _split_sent(old), _split_sent(new)
    sm = difflib.SequenceMatcher(None, osen, nsen, autojunk=False)
    segs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            segs.extend([['', s] for s in osen[i1:i2]])
        elif tag == 'delete':
            segs.extend([['del', s] for s in osen[i1:i2]])
        elif tag == 'insert':
            segs.extend([['add', s] for s in nsen[j1:j2]])
        else:
            segs.extend(_token_diff(''.join(osen[i1:i2]), ''.join(nsen[j1:j2])))
    segs = _order_del_before_add(merge_segs(segs))
    # 忽略纯空白的增删（上一版抽取残留的空格，不可见，不作为修改）
    segs = [s for s in segs if s[0] == '' or s[1].strip() != '']
    segs = merge_segs(segs)
    if max_eq is None:
        runs, prev = 0, ''
        for st, t in segs:
            if st in ('add', 'del'):
                if st != prev:
                    runs += 1
                prev = st
            else:
                prev = ''
        max_eq = 2 if runs <= 10 else 6
    return _coalesce(segs, max_eq)
