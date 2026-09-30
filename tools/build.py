# -*- coding: utf-8 -*-
"""一键构建非官方 LaTeX 版《专利审查指南》。

用法：
  python tools/build.py            # 抽取+生成源码+编译 干净版  -> latex/main.pdf
  python tools/build.py --revision # 同上，但生成带修订标记版      -> latex/main_rev.pdf
  python tools/build.py --no-extract   # 跳过 PDF 抽取，仅重生成源码+编译
  python tools/build.py --actualtext   # 附加“复制不带折行换行”实验标记

流程：
  1. tools/build_content.py    : PDF + bookmark -> data/content.json
  2. tools/build_tex.py        : content.json   -> latex/ 下各 .tex
  3. tectonic 编译
  （--actualtext 时多一趟：先不加标记编译，用 detect_spanning.py 找出跨页段落，
    再加标记重编；详见 README 的说明与限制）

修订工作流见 README.md。
"""
import os, sys, io, subprocess, argparse, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAT = os.path.join(ROOT, 'latex')
TOOLS = os.path.join(ROOT, 'tools')
PY = r'C:\Users\clinku\.workbuddy\binaries\python\envs\default\Scripts\python.exe'
TECTONIC = 'tectonic'


def run(cmd, cwd=None, env=None):
    print('$ ' + ' '.join(cmd))
    e = dict(os.environ) if env is None else env
    r = subprocess.run(cmd, cwd=cwd or ROOT, env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = r.stdout.decode('utf-8', 'replace')
    # 仅打印警告/错误，省略海量 Fontconfig 信息
    for line in out.splitlines():
        if 'Fontconfig' in line or line.startswith('note: Skipped'):
            continue
        print('   ' + line)
    if r.returncode != 0:
        print('!! 命令失败 (exit %d)' % r.returncode)
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--revision', action='store_true', help='生成带修订标记版')
    ap.add_argument('--no-extract', action='store_true', help='跳过 PDF 抽取')
    ap.add_argument('--actualtext', action='store_true',
                    help='附加“复制不带折行换行”实验标记（默认关闭）')
    args = ap.parse_args()

    if not args.no_extract:
        run([PY, 'tools/build_content.py'])
    base_env = {**os.environ, 'REVISION': '1' if args.revision else '0'}

    def gen_tex(actual):
        run([PY, 'tools/build_tex.py'], env={**base_env, 'ACTUALTEXT': actual})

    def compile_tex():
        # tectonic 会按需自动重跑若干遍以收敛目录/分目录
        run([TECTONIC, '-X', 'compile', 'main.tex', '--outdir', '.'], cwd=LAT)

    if not args.actualtext:
        gen_tex('0')
        compile_tex()
    else:
        # 第一遍：不加标记编译，探测哪些段落跨页（跨页段落不加标记）
        gen_tex('0')
        compile_tex()
        run([PY, 'tools/detect_spanning.py'])
        # 第二遍：仅对单页段落加 ActualText 标记
        gen_tex('1')
        compile_tex()

    if args.revision:
        shutil.copy(os.path.join(LAT, 'main.pdf'),
                    os.path.join(LAT, 'main_rev.pdf'))
        print('-> latex/main_rev.pdf')
    print('\n完成：latex/%s' % ('main_rev.pdf' if args.revision else 'main.pdf'))


if __name__ == '__main__':
    main()
