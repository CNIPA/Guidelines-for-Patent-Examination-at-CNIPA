# -*- coding: utf-8 -*-
"""content.json 导航工具: 按 (部分, 章, 节号) 定位标题与其后的段落。"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'data', 'content.json')

CN_NUM = '一二三四五六七八九十'


def btext(b):
    if b['t'] == 'para':
        return ''.join(t for _, t in b['segs'])
    return b.get('text', '')


def load(path=CONTENT):
    return json.load(open(path, encoding='utf-8'))


def chapter_index(text):
    m = re.match(r'^第([一二三四五六七八九十]+)章', text.strip())
    if not m:
        return None
    s = m.group(1)
    if s in CN_NUM:
        return CN_NUM.index(s) + 1
    return None


def heading_number(text):
    m = re.match(r'^(\d+(?:\.\d+)*)\.?(?:\s|$)', text.strip())
    return m.group(1) if m else None


class Guide:
    def __init__(self, blocks):
        self.blocks = blocks
        # 预扫描: 每个 block 所处的 part / chapter
        self.part = [None] * len(blocks)
        self.chap = [None] * len(blocks)
        p = None
        c = None
        for i, b in enumerate(blocks):
            if b['t'] == 'part':
                p = b['num']
                c = None
            elif b['t'] == 'chaptertitle':
                c = chapter_index(b.get('text', ''))
            self.part[i] = p
            self.chap[i] = c

    def find_heading(self, part, chap, number):
        """找 part/chap 内编号为 number 的标题块下标。"""
        for i, b in enumerate(self.blocks):
            if b['t'] != 'heading':
                continue
            if self.part[i] != part or self.chap[i] != chap:
                continue
            if heading_number(b.get('text', '')) == number:
                return i
        return None

    def find_chapter(self, part, chap):
        for i, b in enumerate(self.blocks):
            if b['t'] == 'chaptertitle' and self.part[i] == part and self.chap[i] == chap:
                return i
        return None

    def section_span(self, head_idx):
        """标题 head_idx 之后, 到下一个 heading/chaptertitle/part 之前的块区间 [start, end)。"""
        end = len(self.blocks)
        for j in range(head_idx + 1, len(self.blocks)):
            if self.blocks[j]['t'] in ('heading', 'chaptertitle', 'part'):
                end = j
                break
        return head_idx + 1, end

    def paras(self, head_idx):
        s, e = self.section_span(head_idx)
        return [j for j in range(s, e) if self.blocks[j]['t'] == 'para']

    def describe(self, part, chap, number):
        hi = self.find_heading(part, chap, number)
        if hi is None:
            return None
        return {'head_idx': hi, 'para_idx': self.paras(hi)}
