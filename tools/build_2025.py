# -*- coding: utf-8 -*-
"""基于 2025 年修改（局令第84号）构建两个 PDF：

  1. 新版（干净版）：latex/main.pdf
  2. 修订对照版：latex/main_rev.pdf（新增=绿色 / 删除=红色删除线，参照 EPO）

流程：
  tools/parse_decision.py    : source/…决定.pdf -> data/decision_items.json
  tools/apply_revisions.py   : content.json + revisions_2025.json -> content_2026.json
  tools/build_tex.py         : content_2026.json -> latex/*.tex
  tectonic                   : 编译

用法：
  python tools/build_2025.py            # 跑全流程
  python tools/build_2025.py --no-parse # 跳过决定解析（decision_items.json 已存在）
"""
import os, sys, io, subprocess, argparse, shutil, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAT = os.path.join(ROOT, 'latex')
CONTENT_2026 = os.path.join(ROOT, 'data', 'content_2026.json')
TECTONIC = 'tectonic'


def run(cmd, cwd=None, env=None):
    print('$ ' + ' '.join(cmd))
    e = dict(os.environ) if env is None else env
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd or ROOT, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = r.stdout.decode('utf-8', 'replace')
    for line in out.splitlines():
        if 'Fontconfig' in line or line.startswith('note: Skipped'):
            continue
        print('   ' + line)
    if r.returncode != 0:
        print('!! 命令失败 (exit %d)' % r.returncode)
        raise SystemExit(1)
    print('   (%.1fs)' % (time.time() - t0))


def gen_and_compile(revision, note, out_pdf):
    env = {**os.environ,
           'CONTENT_JSON': CONTENT_2026,
           'REVISION': '1' if revision else '0',
           'GUIDE_EDITION_NOTE': note,
           'ACTUALTEXT': '0'}
    run([sys.executable, 'tools/build_tex.py'], env=env)
    run([TECTONIC, '-X', 'compile', 'main.tex', '--outdir', '.'], cwd=LAT, env=env)
    src = os.path.join(LAT, 'main.pdf')
    if out_pdf != 'main.pdf':
        shutil.copy(src, os.path.join(LAT, out_pdf))
    print('-> latex/%s' % out_pdf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-parse', action='store_true', help='跳过 parse_decision')
    args = ap.parse_args()

    if not args.no_parse:
        run([sys.executable, 'tools/parse_decision.py'])
    run([sys.executable, 'tools/apply_revisions.py'])

    print('\n===== 1/2 修订对照版 =====')
    gen_and_compile(True, '（2025年修改·修订对照版）', 'main_rev.pdf')
    print('\n===== 2/2 新版（干净版，最后编译，保证 main.pdf 为干净版）=====')
    gen_and_compile(False, '（2025年修改）', 'main.pdf')

    print('\n完成：')
    print('  新版      latex/main.pdf')
    print('  修订对照版 latex/main_rev.pdf')


if __name__ == '__main__':
    main()
