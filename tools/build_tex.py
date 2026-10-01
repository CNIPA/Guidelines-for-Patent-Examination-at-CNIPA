# -*- coding: utf-8 -*-
"""data/content.json → latex/main.tex + latex/content/partN.tex + idx.tex

版式忠实复刻原书；所有参数见 guide.cls。
"""
import json, os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textdiff import diff_segs   # noqa: E402

LAT = os.path.join(ROOT, 'latex')
CONTENT = os.environ.get('CONTENT_JSON') or os.path.join(ROOT, 'data', 'content.json')

PART_NUM_CN = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六'}


def esc(t):
    t = t.replace('\\', r'\textbackslash{}')
    for ch, rep in [('%', r'\%'), ('&', r'\&'), ('#', r'\#'), ('_', r'\_'),
                    ('$', r'\$'), ('{', r'\{'), ('}', r'\}'),
                    ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')]:
        t = t.replace(ch, rep)
    return t


def fix_text(t):
    """把行尾多余空格去掉；标题中的 CJK 间 ASCII 空格保留。"""
    return t


def segs_to_tex(segs):
    """[(style,text)] → LaTeX 片段"""
    out = []
    for st, t in segs:
        t = esc(t)
        if not t:
            continue
        if st == '' or st == 'sub' and not out:
            out.append(t)
        elif st == 'add':
            out.append('\\added{%s}' % t)
        elif st == 'del':
            out.append('\\deleted{%s}' % t)
        elif st == 'kai':
            out.append('{\\kaiti %s}' % t)
        elif st == 'hei':
            out.append('{\\heiti %s}' % t)
        elif st == 'bf':
            out.append('\\textbf{%s}' % t)
        elif st == 'it':
            out.append('\\textit{%s}' % t)
        elif st == 'sub':
            out.append('\\textsubscript{%s}' % t)
        elif st == 'itsub':
            out.append('\\textsubscript{\\textit{%s}}' % t)
        elif st == 'bfsub':
            out.append('\\textsubscript{\\textbf{%s}}' % t)
        else:
            out.append(t)
    s = ''.join(out)
    return s.strip()


def notes_tex(notes):
    """[(text, offset)] → 前缀命令串
    偏移作安全钳制：避免将来重新抽取时出现过大负偏移把边注顶进页眉。"""
    s = ''
    for txt, off in notes:
        off = max(-11.5, min(off, 120.0))
        o = ('[%sbp]' % round(off, 1)) if abs(off) > 0.5 else ''
        s += '\\guidenote%s{%s}' % (o, esc(txt))
    return s


def para_tex(b, actual=False):
    ind = b['indent']
    if ind < 5:
        ind = 0.0
    body = segs_to_tex(b['segs'])
    if not body:
        return ''
    pre = notes_tex(b.get('notes', []))
    if actual:
        plain = ''.join(t for _, t in b['segs']).strip()
        if plain:
            # UTF-16BE hex（不含 BOM；BOM 由 \guideATbegin 的 <FEFF...> 提供）
            hexs = plain.encode('utf-16-be').hex().upper()
            body = '\\guideATbegin{%s}%s\\guideATend' % (hexs, body)
    # 必须以空行（或 \par）结束段落，否则相邻段会被 TeX 并成一段
    if abs(ind - 23.4) < 0.6:
        return '%s%s\n\n' % (pre, body)
    return '{\\setlength{\\parindent}{%sbp}%s%s\\par}\n\n' % (round(ind, 1), pre, body)


def heading_level(text):
    """由编号判断标题级别: 1=章 2=节 3=小节 4=子小节 5=条"""
    t = text.strip()
    if re.match(r'^第[一二三四五六七八九十]+章', t):
        return 1
    m = re.match(r'^(\d+(?:\.\d+)*)(\.?)(\s|$)', t)
    if not m:
        return None
    ndots = m.group(1).count('.')
    if m.group(2) == '.' and ndots == 0:
        return 2
    return 2 + ndots


def split_heading(text):
    """'4.1.3.2 申请人是外国人…' → ('4.1.3.2', '申请人是外国人…')"""
    m = re.match(r'^(第[一二三四五六七八九十]+章|\d+(?:\.\d+)*\.?)\s*(.*)$', text.strip())
    if not m:
        return '', text.strip()
    return m.group(1), m.group(2)


# ---- 索引：位置串（Ⅰ.Ⅰ－6.2.1.2）→ 正文标题锚点的自动映射 ----
_ROMAN_UNI = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ'
_ROMAN_MAP = {c: i + 1 for i, c in enumerate(_ROMAN_UNI)}


def roman_to_int(s):
    if len(s) == 1 and s in _ROMAN_MAP:
        return _ROMAN_MAP[s]
    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    n = prev = 0
    for ch in reversed(s):
        v = vals.get(ch, 0)
        if v < prev:
            n -= v
        else:
            n += v
            prev = v
    return n


# 位置串：<部分罗马>.<章罗马>－<节号>（节号可省，如 Ⅴ.Ⅴ 表示整章）；
# 单独的罗马数字表示“整个第X部分”（如 Ⅳ）。罗马字符也可能是 ASCII I/V/X。
_ROM = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫIVX'
_DASH = '－-'   # 原数据里节号前的连字符有全角－与半角-两种
_POS_ONE = (r'(?:[' + _ROM + r']+\.\s*[' + _ROM + r']+(?:[' + _DASH + r'][0-9.]+)?'
            r'|(?<![' + _ROM + r'.])[' + _ROM + r']+(?![' + _ROM + r'.]))')
_POS_RE = re.compile(
    r'([' + _ROM + r']+)\.\s*([' + _ROM + r']+)(?:[' + _DASH + r']([0-9.]+))?'   # 部分.章[－节]
    r'|(?<![' + _ROM + r'.])([' + _ROM + r']+)(?![' + _ROM + r'.])')  # 单个罗马数字＝整个部分
# 词条末尾的“位置串序列”：位置串之间用；分隔，允许末尾多出一个分隔符（原数据瑕疵）。
_TAIL_RE = re.compile(r'\s*(' + _POS_ONE + r'(?:\s*[；;]\s*' + _POS_ONE + r')*)'
                      r'\s*[；;]?\s*$')


def linkify_index(text, existing):
    """把索引正文里的位置串替换为指向对应标题的 \\hyperlink；－ 显示为 -。
    existing 为已生成锚点名集合（gpos.<部分>.<章>[.<节>] 或 gpos.p<部分>），
    只在存在时才加链接。"""
    out, last = [], 0
    for m in _POS_RE.finditer(text):
        out.append(esc(text[last:m.start()]))
        if m.group(4):
            dest = 'gpos.p%d' % roman_to_int(m.group(4))
        else:
            pr = roman_to_int(m.group(1))
            cr = roman_to_int(m.group(2))
            sec = (m.group(3) or '').rstrip('.')
            dest = 'gpos.%d.%d' % (pr, cr) + ('.' + sec if sec else '')
        disp = m.group(0).replace('－', '-')
        out.append('\\hyperlink{%s}{%s}' % (dest, disp) if dest in existing else disp)
        last = m.end()
    out.append(esc(text[last:]))
    return ''.join(out)


def main():
    blocks = json.load(open(CONTENT, encoding='utf-8'))
    os.makedirs(os.path.join(LAT, 'content'), exist_ok=True)
    # 复制不带折行换行（实验）：默认关闭，ACTUALTEXT=1 时启用（见 README）
    actual = os.environ.get('ACTUALTEXT', '0') in ('1', 'true', 'True')
    revision = os.environ.get('REVISION', '') in ('1', 'true', 'True')
    # 跨页段落不能加标记（否则 BDC/EMC 分处两页会致复制重复），由
    # tools/detect_spanning.py 预先生成跳过列表。
    at_skip = set()
    skip_path = os.path.join(ROOT, 'data', 'at_skip.json')
    if actual and os.path.exists(skip_path):
        try:
            at_skip = set(json.load(open(skip_path, encoding='utf-8')))
        except Exception:
            at_skip = set()
    para_index = 0

    # 按 part 分组
    parts = []
    cur = None
    idx_blocks = []
    for b in blocks:
        if b['t'] == 'part':
            cur = {'info': b, 'blocks': []}
            parts.append(cur)
        elif b['t'] == 'other':
            pass  # 索引单独处理（收集到 idx_blocks）
        elif b['t'] in ('idxentry', 'indextitle'):
            idx_blocks.append(b)
        elif cur is not None:
            cur['blocks'].append(b)

    partfiles = []
    existing_dests = set()   # 所有 gpos.* 锚点（索引位置串据此决定是否加链接）
    for p in parts:
        num = p['info']['num']
        chap_num = 0
        head_idx = 0
        existing_dests.add('gpos.p%d' % num)
        cn = PART_NUM_CN[num]
        fn = 'content/part%d.tex' % num
        partfiles.append((num, cn, p['info'], fn))
        with open(os.path.join(LAT, fn), 'w', encoding='utf-8') as f:
            w = f.write
            w('%% ====== 第%s部分 %s ======\n' % (cn, p['info']['title']))
            w('\\cleardoublepage\\setguidefootmark{%d}{第%s部分}\\resetchapters\n' % (num, cn))
            # ---- 部分封面（物理居中于整页：版心中心 310.75 与页面中心 260.82 差 49.93bp，左移之）----
            lines = p['info']['cover_lines']
            w('\\thispagestyle{plainempty}\\hypertarget{gpos.p%d}{}\\begingroup\\centering\\guidecenterpage\n' % num)
            w('\\dadati\\fontsize{29.04bp}{43bp}\\selectfont\n')
            w('\\vspace*{%dbp}\n' % max(120, 285 - int(len(lines) * 43 / 2)))
            for ln in lines:
                w('%s\\par\n' % esc(ln))
            w('\\phantomsection\n')
            w('\\addcontentsline{toc}{part}{%s\\quad %s}\n'
              % (esc(p['info']['cn']), esc(p['info']['title'])))
            w('\\endgroup\\clearpage\n')
            # ---- 分目录：先读上一遍已生成的完整 .ptc，再开写本遍 ----
            #   （\startparttoc 会立即截断 .ptc；原写法在正文写条目之前就截断，
            #     导致 printparttoc 永远读不到章/节条目。故将开写移到分目录页之后、
            #     正文之前，并让 part 条目也在此处补写。）
            w('\\cleardoublepage\\pagestyle{tocpage}\n')
            w('\\guideoutline[1]{分目录}{parttoc%d}\n' % num)
            w('\\gdef\\guidetabcontent{%s}\n'
              % ''.join('\\hbox{%s}' % ch for ch in p['info']['cn']))
            w('{\\centering\\guidecenterpage\\heiti\\fontsize{14.04bp}{21bp}\\selectfont 目\\quad 录\\par}\n')
            w('\\vspace{6bp}\n')
            w('\\printparttoc{p%d}\n' % num)
            w('\\clearpage\\pagestyle{main}\n')
            w('\\startparttoc{p%d}\n' % num)
            # ---- 正文 ----
            # 计算“连续标题成组”的防孤行预留高度（见 guide.cls 的 \guide@needspace）
            blks = p['blocks']
            is_head = [b['t'] == 'heading' for b in blks]
            need = ['0bp'] * len(blks)
            i = 0
            while i < len(blks):
                if is_head[i]:
                    j = i
                    while j < len(blks) and is_head[j]:
                        j += 1
                    run = j - i
                    # 首个标题预留：组内标题 + 段间空白 + 3 行正文
                    nd = 12.0 + run * 15.6 + (run - 1) * 12.0 + 3 * 15.6
                    need[i] = '%.1fbp' % nd
                    i = j
                else:
                    i += 1
            for bi, b in enumerate(blks):
                t = b['t']
                if t == 'chaptertitle':
                    # 章标题（编号与文字分开传入，正文/目录各自补空白）
                    ch_num, ch_title = split_heading(b['text'])
                    chap_num += 1
                    dest = 'gpos.%d.%d' % (num, chap_num)
                    existing_dests.add(dest)
                    w('\\guidechapter{%s}{%s}{%s}{%s}{0bp}\n'
                      % (dest, esc(ch_num), esc(ch_title), notes_tex(b.get('notes', []))))
                elif t == 'chapter':
                    pass  # 章结构由 chaptertitle 驱动
                elif t == 'heading':
                    lvl = heading_level(b['text'])
                    if lvl is None:
                        lvl = 2
                    hn, ht = split_heading(b['text'])
                    head_idx += 1
                    if hn:
                        dest = 'gpos.%d.%d.%s' % (num, chap_num, hn.rstrip('.'))
                    else:
                        dest = 'gpos.%d.%d.h%d' % (num, chap_num, head_idx)
                    existing_dests.add(dest)
                    nts = notes_tex(b.get('notes', []))
                    nd = need[bi]
                    macro = {2: 'guidesection', 3: 'guidesubsection',
                             4: 'guidesubsubsection', 5: 'guideparagraph'}.get(lvl, 'guidesection')
                    levelname = {2: 'section', 3: 'subsection',
                                 4: 'subsubsection', 5: 'paragraph'}.get(lvl, 'section')
                    rev = b.get('rev')
                    if rev == 'del':
                        if revision:
                            w('\\guiderevold{%s}\n' % esc((hn + ' ' + ht).strip()))
                        continue
                    if revision and rev in ('renumber', 'retitle'):
                        # 只标出真正改动的地方（如仅序号变化），不整体重标标题
                        mix = segs_to_tex(diff_segs(b.get('old_text', ''), (hn + ' ' + ht).strip()))
                        w('\\phantomsection\\hypertarget{%s}{}\n' % dest)
                        w('\\addcontentsline{toc}{%s}{%s %s}\n' % (levelname, esc(hn), esc(ht)))
                        w('\\ptcwrite{%s}{%s}{%s}{%s}\n' % (levelname, dest, esc(hn), esc(ht)))
                        w('\\guiderevheadmix{%s}\n' % mix)
                        continue
                    if revision and rev == 'add':
                        w('\\phantomsection\\hypertarget{%s}{}\n' % dest)
                        w('\\addcontentsline{toc}{%s}{%s %s}\n' % (levelname, esc(hn), esc(ht)))
                        w('\\ptcwrite{%s}{%s}{%s}{%s}\n' % (levelname, dest, esc(hn), esc(ht)))
                        w('\\guiderevnew{%s}\n' % esc((hn + ' ' + ht).strip()))
                        continue
                    w('\\%s{%s}{%s}{%s}{%s}{%s}\n' % (macro, dest, esc(hn), esc(ht), nts, nd))
                elif t == 'para':
                    wrap = actual and (para_index not in at_skip)
                    w(para_tex(b, wrap))
                    para_index += 1
                elif t == 'formula':
                    w('\\guideformula{%s}\n' % b['tex'])
                elif t == 'image':
                    w('\\guidefigure{figures/%s}{%s}{%s}\n'
                      % (b['file'], b['wpt'], b['hpt']))
            w('\\stopparttoc\n')

    # ---- 索引 ----
    with open(os.path.join(LAT, 'content', 'idx.tex'), 'w', encoding='utf-8') as f:
        w = f.write
        w('%% ====== 其他（索引）======\n')
        w('\\startparttoc{idx}\n')
        w('\\cleardoublepage\\thispagestyle{plainempty}\\begingroup\\centering\\guidecenterpage\n')
        w('\\dadati\\fontsize{29.04bp}{43bp}\\selectfont\\vspace*{262bp}其\\quad 他\\par\n')
        w('\\phantomsection\n')
        w('\\addcontentsline{toc}{part}{其他}\n')
        w('\\ptcwrite{part}{}{其他}{索引}\n')
        w('\\endgroup\n')
        w('\\cleardoublepage\\pagestyle{idxpage}\n')
        w('\\markboth{索引}{其他}\n')
        for b in idx_blocks:
            if b['t'] == 'indextitle':
                w('\\guideoutline[0]{索引}{idx}\n')
                w('{\\centering\\guidecenterpage\\heiti\\fontsize{14.04bp}{27bp}\\selectfont %s\\par}\n' % esc(b['text']))
                continue
            t = b['text'].strip()
            if re.fullmatch(r'[A-Z]', t):
                w('\\guideoutline[1]{%s}{idxletter%s}\n' % (esc(t), t))
                w('\\par\\vspace{8bp}{\\leftskip=-74.3bp\\parindent=0bp\\textbf{%s}\\par}\n' % esc(t))
                continue
            # 以“末尾位置串序列”为界拆分：前为词条、后为位置串。
            # 不依赖词条里是否有空格（词条可能含引号等带来的抽取空格）。
            m = _TAIL_RE.search(t)
            if m and m.start() > 0:
                term = re.sub(r'\s+', '', t[:m.start()])
                rest = m.group(1).strip().rstrip('；;')
                w('\\guideidxentry{%s}{%s}\n'
                  % (esc(term), linkify_index(rest, existing_dests)))
            else:
                # 索引开头的说明性文字：普通段落（首行缩进），不套用词条的悬挂缩进
                body = linkify_index(t, existing_dests)
                w('{\\leftskip=-99.3bp\\parindent=18.8bp'
                  '\\baselineskip=19bp %s\\par}\n' % body)
        w('\\stopparttoc\n')

    # ---- main.tex ----
    # 修订开关：环境变量 REVISION=1 时生成带修订标记版（\revisiontrue）
    with open(os.path.join(LAT, 'main.tex'), 'w', encoding='utf-8') as f:
        w = f.write
        w('% !TeX program = tectonic\n')
        w('% 非官方 LaTeX 版《专利审查指南》——由 tools/build_tex.py 自动生成正文\n')
        w('\\documentclass{guide}\n')
        if actual:
            w('% ===== 复制不带折行换行（实验）：启用 ActualText 标记 =====\n')
            w('\\guideactualtrue\n')
        if revision:
            w('% ===== 修订标记版：新增=绿色 / 删除=红色删除线（参照 EPO showing modifications）=====\n')
            w('\\revisiontrue\n')
        w('\\begin{document}\n')
        w('\\input{frontcover}\n')
        # 总目录（无灰底标签，用 tocmain 页式）
        w('\\cleardoublepage\\pagestyle{tocmain}\\setcounter{page}{1}\n')
        w('{\\centering\\guidecenterpage\\heiti\\fontsize{14.04bp}{21bp}\\selectfont '
          '总\\quad 目\\quad 录\\par}\n')
        w('\\guideoutline[0]{总目录}{toc}\n')
        w('\\vspace{18bp}\n')
        w('\\setcounter{tocdepth}{1}\\makeatletter\\@starttoc{toc}\\makeatother\n')
        # 各部分
        for num, cn, info, fn in partfiles:
            w('\\input{%s}\n' % fn)
        w('\\input{content/idx.tex}\n')
        w('\\end{document}\n')

    # ---- 封面 ----
    with open(os.path.join(LAT, 'frontcover.tex'), 'w', encoding='utf-8') as f:
        w = f.write
        w('% 封面（原书实测位置）\n')
        w('\\thispagestyle{plainempty}\n')
        w('\\guideoutline[0]{封面}{cover}\n')
        w('\\begingroup\\centering\\guidecenterpage\n')
        w('\\vspace*{146bp}\n')
        w('{\\songti\\bfseries\\fontsize{36bp}{54bp}\\selectfont 专利审查指南\\par}\n')
        w('\\vspace{73bp}\n')
        w('{\\textbf{\\fontsize{21.96bp}{33bp}\\selectfont 2023}\\par}\n')
        note = os.environ.get('GUIDE_EDITION_NOTE', '')
        if note:
            w('\\vspace{6bp}\n')
            w('{\\songti\\fontsize{12bp}{18bp}\\selectfont %s\\par}\n' % esc(note))
        w('\\vspace{16bp}\n')
        w('{\\songti\\fontsize{10.56bp}{18bp}\\selectfont 国家知识产权局\\quad 制\\quad 定\\par}\n')
        w('\\endgroup\\clearpage\n')

    print('generated: main.tex, frontcover.tex,',
          ', '.join(fn for _, _, _, fn in partfiles), ', content/idx.tex')


if __name__ == '__main__':
    main()
