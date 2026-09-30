# -*- coding: utf-8 -*-
"""原版资料来源路径（单一入口，便于切换新版）。

约定：把官方资料放在 `source/` 目录下，文件名用“出版日期_书名”表示版本，例如
    20231221_专利审查指南2023.pdf
    20231221_专利审查指南2023.bookmark
    20231221_专利审查指南2023.doc

脚本从这里取路径；换新版时只需替换 `source/` 里的文件（或设置环境变量
`GUIDE_SOURCE_DIR` 指向另一个目录），无需改任何脚本。
"""
import os
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.environ.get('GUIDE_SOURCE_DIR', os.path.join(ROOT, 'source'))


def _one(pattern, exclude=()):
    xs = sorted(glob.glob(os.path.join(SOURCE_DIR, pattern)))
    xs = [x for x in xs if not any(e in os.path.basename(x) for e in exclude)]
    return xs[-1] if xs else None


# 官方原书 PDF（权威数据源）。source/ 里还可能有“修改决定”之类的其它 PDF，
# 其文件名含“决定”，需排除，故按日期取最新、并排除决定/通知类文件。
PDF = _one('*.pdf', exclude=('决定', '通知', '公告'))
BOOKMARK = _one('*.bookmark')  # 官方书签（页码 -> 结构）
DOC = _one('*.doc')            # 官方 DOC（备查）


def require(path, what):
    if not path:
        raise FileNotFoundError(
            '在 %s 里找不到%s文件；请把官方资料放入该目录，或设置 GUIDE_SOURCE_DIR。'
            % (SOURCE_DIR, what))
    return path
