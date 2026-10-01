%% guide.cls —— 非官方 LaTeX 版《专利审查指南》文档类
%% 复刻国家知识产权局《专利审查指南 2023》PDF 版面（原书全部长度用 bp 作单位）
%%   页面        521.64bp × 737.16bp （184.02 × 260.05 mm）
%%   版心        左 154.6bp，宽 312.3bp；正文首行基线 101.3bp
%%   正文        宋体 10.56bp，基线间距 15.6bp
%%   章标题      黑体 14.04bp，基线 104.7bp（章首页）
%%   节/小节标题 黑体 10.56bp，段前 +12.0bp，段后 0
%%   页眉        楷体 9bp，基线 51.6bp；页眉横线 y=55.4bp
%%   页脚        基线 684.6bp；中央（部分-章内页码），外侧页码
%%   正文左侧边注列（"法 26 / 细则 50" 楷体标记），左端 x=65.9bp
%% 原书为"左右边距不互换"的双面版式（正文永远在 x=154.6），故强制 evensidemargin=oddsidemargin。
%% 用 XeLaTeX / tectonic 编译；需编译两遍以生成目录。
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{guide}[2026/09/30 v1.3 unofficial CNIPA Guide layout]
\LoadClass[twoside,openany]{book}

\newif\ifrevision            % \revisiontrue → 修订标记版；false → 干净版
\revisionfalse

% ================= 页面几何（原书实测） =================
\RequirePackage[
  paperwidth=521.64bp, paperheight=737.16bp,
  left=154.6bp, textwidth=312.3bp,
  top=85.7bp, headheight=13.6bp, headsep=30.5bp,
  textheight=552bp, footskip=46.9bp,
  marginparwidth=80.1bp, marginparsep=8.6bp,
]{geometry}
% 首行基线 = 版心顶 + topskip = 85.7 + 15.6 = 101.3bp
\setlength{\topskip}{15.6bp}
\raggedbottom                 % 原书各页末行基线不固定 → 不拉平页高

% ================= 字体 =================
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\setmainfont{Times New Roman}
\setCJKmainfont[AutoFakeBold=2.5]{SimSun}
\newCJKfontfamily\songti[AutoFakeBold=2.5]{SimSun}
\newCJKfontfamily\heiti[AutoFakeBold=2.5]{SimHei}
\newCJKfontfamily\kaiti{KaiTi}
\newCJKfontfamily\dadati[AutoFakeBold=3.2]{SimHei}  % 部分封面"方正大黑"替代

% ================= 字号与行距 =================
\newcommand*{\bodyfont}{\fontsize{10.56bp}{15.6bp}\selectfont}
\AtBeginDocument{\bodyfont}
% 原书启用"文档网格/字符网格"：宋体 10.56bp 的字形，实际步进 11.75bp（每行 26 字，
% 行末分散对齐后步进 12.01bp）。这里给 CJK 字符间加 1.19bp 可伸缩胶来复刻。
\xeCJKsetup{CJKglue=\hskip 1.19bp plus 1.6bp minus 0.25bp, CheckSingle=false}
% 带圈数字（①②③…）与少量数学符号（∈）出现在中文段落里，归入 CJK 类让宋体渲染
\xeCJKsetcharclass{"2460}{"2473}{1}
\xeCJKsetcharclass{"2208}{"2208}{1}

% ================= 段落 =================
\setlength{\parindent}{23.4bp}
\setlength{\parskip}{0bp}
\clubpenalty=10000 \widowpenalty=10000
\brokenpenalty=100
\emergencystretch=3em

% ================= 页眉页脚 =================
\RequirePackage{fancyhdr}
\RequirePackage{xcolor}
\newcommand*{\guideheadextend}{99.3bp}
\newcommand*{\guidefootmark}{1-1}   % 页脚中央 (X-Y)
\newcommand*{\guidebookmark}{专利审查指南}
\newcommand*{\guidetabcontent}{}    % 目录页外侧竖排标签（每字一个 \hbox）

\fancypagestyle{main}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0.5bp}%
  \fancyheadoffset[L]{\guideheadextend}%
  \fancyhead[LO,RE]{\kaiti\fontsize{9bp}{11bp}\selectfont\leftmark}%
  \fancyhead[LE,RO]{\kaiti\fontsize{9bp}{11bp}\selectfont\rightmark}%
  \fancyfoot[RO]{\songti\bodyfont\thepage}%
  \fancyfoot[LE]{\songti\bodyfont\hspace*{-99.3bp}\thepage}%
  \fancyfoot[C]{\songti\bodyfont（\guidefootmark）}%
}
\fancypagestyle{idxpage}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0.5bp}%
  \fancyheadoffset[L]{\guideheadextend}%
  \fancyhead[LO,RE]{\kaiti\fontsize{9bp}{11bp}\selectfont\leftmark}%
  \fancyhead[LE,RO]{\kaiti\fontsize{9bp}{11bp}\selectfont\rightmark}%
  \fancyfoot[RO]{\songti\bodyfont\thepage}%
  \fancyfoot[LE]{\songti\bodyfont\hspace*{-99.3bp}\thepage}%
}
\fancypagestyle{plainempty}{\fancyhf{}\renewcommand{\headrulewidth}{0bp}}
% 总目录页：无灰底标签，仅页脚页码（原书总目录无标签区）
\fancypagestyle{tocmain}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0bp}%
  \fancyfoot[RO]{\songti\bodyfont\thepage}%
  \fancyfoot[LE]{\songti\bodyfont\hspace*{-99.3bp}\thepage}%
}
\fancypagestyle{tocpage}{%
  \fancyhf{}%
  \fancyheadoffset{0bp}%
  \renewcommand{\headrulewidth}{0bp}%
  \fancyhead[RO]{\guidetabRO}%
  \fancyhead[LE]{\guidetabLE}%
  \fancyfoot[RO]{\songti\bodyfont\thepage}%
  \fancyfoot[LE]{\songti\bodyfont\hspace*{-99.3bp}\thepage}%
}

% 目录页外缘竖排灰底标签（奇数页在右、偶数页在左）
%   原书实测：灰底框 34.8bp × 52.2bp；奇数页 x=484.3..519.0，偶数页 x=0..34.8；
%   框内文字宋体 10.56bp，逐字竖排（基线步进 10.56bp），水平居中、上下各留约 5bp。
\definecolor{tabgray}{RGB}{168,169,173}
\setlength{\fboxsep}{0bp}
\newcommand*{\guidetabbox}{%
  {\colorbox{tabgray}{\vbox to 52.2bp{\vfil
    \hbox to 34.74bp{\hfil
      \vtop{\songti\bodyfont\baselineskip=10.56bp\lineskiplimit=-1000bp
        \guidetabcontent}\hfil}\vfil}}}}
\newcommand*{\guidetabRO}{\raisebox{-90.8bp}[0bp][0bp]{\rlap{\hspace*{17.4bp}\guidetabbox}}}
\newcommand*{\guidetabLE}{\raisebox{-90.8bp}[0bp][0bp]{\llap{\guidetabbox\hspace*{119.8bp}}}}

% 目录/封面标题在“整张页面”上居中（版心居中会偏右约 50bp）
\newcommand*{\guidecenterpage}{\leftskip=-49.93bp plus 1fil\rightskip=49.93bp plus 1fil}

% ================= 标题（自写，不用 titlesec，便于精确控制基线） =================
%   章：\guidechapter{编号}{标题}
%   节/小节/…：\guidesection{编号}{标题} 等
%   编号（"第一章"/"4.4.1"）与标题分开传入：正文按原书在两者间留一个全角空白；
%   分目录则把编号放进固定列宽，使各级标题左端对齐（见 \guidetoc@line）。
\newcommand*{\cnum}[1]{\ifcase#1\or 一\or 二\or 三\or 四\or 五\or 六\or 七\or 八\or 九\or 十\or 十一\or 十二\or 十三\or 十四\or 十五\fi}
\newcounter{gchapter}
\newcounter{gsection}
\newcommand*{\resetchapters}{\setcounter{gchapter}{0}}
% 编号 + 空白 + 标题（编号为空时只输出标题）；空白取半个全角（比 \quad 略小）
\newcommand*{\guide@nt}[2]{\ifx\relax#1\relax #2\else #1\hspace{0.5em}#2\fi}
% 书签/纯文本用：编号与标题间用普通空格（避免 \quad 进入 PDF 字符串）
\newcommand*{\guide@ntplain}[2]{\ifx\relax#1\relax #2\else #1 #2\fi}

% 段前额外空白：#1=额外距离。页中直接加胶（不破坏 \prevdepth，故自然行距保留）；
% 页首（\prevdepth=-1000pt）没有"上一行"，需用 \null 作锚让空白不被页面断裂丢弃，
% 此时 \topskip 已把基线定在 101.3bp，故要扣掉行盒高度 \ht。
% 恒用 \null 作锚（保证空白跨页不断被丢弃），其后 \nointerlineskip 去掉自然行间胶，
% 于是"页首(\topskip=15.6)"与"页中(\prevdepth+行间胶=15.6)"两种情形统一：
%   基线 = 自然下一行基线 + #1
\newcommand*{\guide@skip}[2]{% #1=额外距离 #2=行盒高度
  \null\vskip \dimexpr #1 - #2\relax\nointerlineskip}
% 避免“孤行标题”：若当前页剩余高度不足以容纳（标题 + 段后空白 + 2 行正文），
% 则先换页，让标题与其后正文一起出现在新页顶部。
\newcommand*{\guide@needspace}[1]{%
  \ifdim\pagegoal<\maxdimen
    \ifdim\dimexpr\pagegoal-\pagetotal<\dimexpr#1\relax
      \newpage
    \fi
  \fi}
% 标题通用：#1=段前额外 #2=字体选择 #3=锚点名 #4=文字 #5=段后空白 #6=预留高度
% #6 由 build_tex 计算：连续标题成组时，为“整组标题 + 2 行正文”预留；
% 组内非首个标题传 0（不重复触发换页）。锚点放进标题行内，随标题行换页。
\newcommand*{\guide@head}[6]{%
  \par
  \setbox\@tempboxa\hbox{#2 中}%
  \guide@needspace{#6}%
  \guide@skip{#1}{\ht\@tempboxa}%
  \noindent{\phantomsection\hypertarget{#3}{}\hbadness=10000 #2#4\par}%
  \nobreak\vskip #5\relax}

% 公开版：给非标题元素（封面/总目录/分目录/其他）加书签
\newcommand*{\guideoutline}[3][]{\par\phantomsection\pdfbookmark[#1]{#2}{#3}}

% 索引词条：#1=词条 #2=位置串（已含 \hyperlink）。
% 首行“词条 + 1 个字符 + 位置串”，折行后与“本词条位置串的左端”对齐，
% 悬挂缩进 = 词条实测宽度 + 1em，随词条长度自适应（不再用固定 63bp）。
\newcommand*{\guideidxentry}[2]{%
  \par
  \begingroup
    \bodyfont
    \settowidth{\@tempdima}{#1}%
    \leftskip=-74.3bp\parindent=\z@
    \hangindent=\dimexpr\@tempdima+1em\relax\hangafter=1
    \baselineskip=19bp #1\hspace{1em}#2\par
  \endgroup}

% 各标题宏：#1=锚点名（gpos.部分.章[.节]，由 build_tex 生成）
%             #2=编号  #3=标题  #4=标题行左栏边注串（\guidenote...，可空）
%             #5=预留高度（防孤行标题，见 \guide@needspace；组内非首个为 0bp）
% 每个标题都写一条 \addcontentsline：主目录只渲染到 part/chapter（tocdepth=1），
% 其余层级仅用于生成 PDF 书签与跳转锚点。
\newcommand*{\guidechapter}[5]{%
  \clearpage
  \stepcounter{gchapter}%
  \gdef\guidebookmark{专利审查指南\currentpartlabel #2}%
  \markboth{#3}{\guidebookmark}%
  \ifnum\value{gchapter}=1\relax\setcounter{partfirstpage}{\value{page}}\fi
  \guide@head{3.4bp}{\heiti\fontsize{14.04bp}{27.24bp}\selectfont}{#1}{#4\guide@nt{#2}{#3}}{8.2bp}{#5}%
  \ptcwrite{chapter}{#1}{#2}{#3}%
  \addcontentsline{toc}{chapter}{\guide@nt{#2}{#3}}}
\newcommand*{\guidesection}[5]{%
  \guide@head{12.0bp}{\heiti\bodyfont}{#1}{#4\guide@nt{#2}{#3}}{0bp}{#5}%
  \ptcwrite{section}{#1}{#2}{#3}%
  \addcontentsline{toc}{section}{\guide@nt{#2}{#3}}}
\newcommand*{\guidesubsection}[5]{%
  \guide@head{12.0bp}{\heiti\bodyfont}{#1}{#4\guide@nt{#2}{#3}}{0bp}{#5}%
  \ptcwrite{subsection}{#1}{#2}{#3}%
  \addcontentsline{toc}{subsection}{\guide@nt{#2}{#3}}}
\newcommand*{\guidesubsubsection}[5]{%
  \guide@head{12.0bp}{\heiti\bodyfont}{#1}{#4\guide@nt{#2}{#3}}{0bp}{#5}%
  \ptcwrite{subsubsection}{#1}{#2}{#3}%
  \addcontentsline{toc}{subsubsection}{\guide@nt{#2}{#3}}}
\newcommand*{\guideparagraph}[5]{%
  \guide@head{12.0bp}{\heiti\bodyfont}{#1}{#4\guide@nt{#2}{#3}}{0bp}{#5}%
  \ptcwrite{paragraph}{#1}{#2}{#3}%
  \addcontentsline{toc}{paragraph}{\guide@nt{#2}{#3}}}

% 部分/章管理
\newcounter{guidepartnum}
\newcounter{partfirstpage}[guidepartnum]
\newcommand*{\guidewithinpart}{\the\numexpr\value{page}-\value{partfirstpage}+1\relax}
\newcommand*{\currentpartlabel}{第一部分}
\newcommand*{\setguidefootmark}[2]{% #1=部分序号 #2=第X部分
  \setcounter{guidepartnum}{#1}%
  \gdef\currentpartlabel{#2}%
  \gdef\guidefootmark{\arabic{guidepartnum}-\guidewithinpart}}

% ================= 左侧边注 =================
% 原书所有边注（"法18 / 细则26"）一律落在左侧列（x≈65.9bp）。
% marginnote 的左右判定由 \@mn@margintest 依据"记录到的绝对页码奇偶"延迟决定，
% 与调用处按页码奇偶切换 \reversemarginpar/\normalmarginpar 会相互打架，
% 导致少量页顶锚定的批注误落右侧。这里强制 \@mn@margintest 的判定恒为"左侧"，
% 并取消按页码奇偶的 reversemargin 切换，使全部边注确定性居左。
\RequirePackage{marginnote}
\let\guide@mn@margintest\@mn@margintest
\renewcommand*{\@mn@margintest}{\guide@mn@margintest\@tempswafalse}
\newcommand*{\guidenote}[2][0bp]{%
  \normalmarginpar
  \marginnote{\raggedright\kaiti\bodyfont #2}[#1]}

% ================= 部分（分章）目录：自写读写机制 =================
\newwrite\ptc@out
\newcommand*{\startparttoc}[1]{\immediate\openout\ptc@out=\jobname.#1.ptc\relax}
\newcommand*{\stopparttoc}{\immediate\closeout\ptc@out}
\newcommand*{\ptcwrite}[4]{\immediate\write\ptc@out{\string\ptcl{#1}{#2}{#3}{#4}{\thepage}}}
% 目录行通用版式：#1=编号列文字(可空) #2=正文 #3=页码 #4=是否黑体 #5=跳转锚点(可空)
%                 #6=编号相对行首的缩进（章 0bp，节≈1 字符）
% 标题列统一对齐到 55.3 + \guidetoc@lcol；章号的编号格被冠以 1 字符空白。
\newcommand*{\guidetoc@lcol}{47bp}   % 标题列（相对行首，行首=55.3）
\newcommand*{\guidetoc@sind}{11bp}   % 节号相对章号的缩进（约 1 字符）
\newcommand*{\guidetoc@line}[6]{%
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=\z@\hangindent=\guidetoc@lcol\hangafter=1\interlinepenalty\@M
   \bodyfont
   \ifx\\#4\\\else\heiti\fi
   \ifx\\#1\\\else
     \hspace*{#6}\makebox[\dimexpr\guidetoc@lcol-#6\relax][l]{#1}%
   \fi
   \ifx\\#5\\#2\else\hyperlink{#5}{#2}\fi
   \nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#3}\par}}
\newcommand*{\ptcl@part}[4]{\par\addvspace{10.8bp}\guidetoc@line{}{#2\quad #3}{#4}{b}{}{0bp}}
\newcommand*{\ptcl@chapter}[4]{\par\addvspace{0bp}\guidetoc@line{#2}{#3}{#4}{b}{#1}{0bp}}
\newcommand*{\ptcl@section}[4]{\guidetoc@line{#2}{#3}{#4}{}{#1}{\guidetoc@sind}}
\newcommand*{\ptcl@subsection}[4]{\guidetoc@line{#2}{#3}{#4}{}{#1}{\guidetoc@sind}}
\newcommand*{\ptcl@subsubsection}[4]{\guidetoc@line{#2}{#3}{#4}{}{#1}{\guidetoc@sind}}
\newcommand*{\ptcl@paragraph}[4]{\guidetoc@line{#2}{#3}{#4}{}{#1}{\guidetoc@sind}}
\newcommand*{\printparttoc}[1]{%
  \begingroup
  \def\ptcl##1##2##3##4##5{\csname ptcl@##1\endcsname{##2}{##3}{##4}{##5}}%
  \InputIfFileExists{\jobname.#1.ptc}{}{}%
  \endgroup}

% ================= 总目录（book 类 \l@ 系列重定义） =================
\makeatletter
% 说明：主目录 tocdepth=1，仅渲染 part+chapter 两级；各\"部分目录\"由自定义
% .ptc 机制（见 \ptcl@ 系列）负责，不使用此处命令。
% 注意：嵌套一层宏时源文件须写 ##1（两个 #）。若误写成 ####1，展开后会在
% .toc 中残留非法记号 ##，导致 hyperref 回读时报
% "Parameters must be numbered consecutively."。
\renewcommand*{\l@part}[2]{%
  \addpenalty\@secpenalty\addvspace{10.8bp}%
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=\z@\interlinepenalty\@M\bodyfont\heiti
   \hangindent=63bp\hangafter=1
   #1\nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#2}\par}}
\renewcommand*{\l@chapter}[2]{%
  \ifnum\c@tocdepth>\z@
  \addpenalty\@secpenalty\addvspace{0bp}%
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=23.4bp\interlinepenalty\@M\bodyfont
   \hangindent=23.4bp\hangafter=1
   \def\numberline##1{\hb@xt@23.4bp{##1\hfil}}%
   #1\nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#2}\par}\fi}
\renewcommand*{\l@section}[2]{%
  \ifnum\c@tocdepth>\@ne
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=\z@\hangindent=63bp\hangafter=1\interlinepenalty\@M\bodyfont
   \def\numberline##1{\hb@xt@63bp{##1.\hfil}}%
   #1\nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#2}\par}\fi}
\renewcommand*{\l@subsection}[2]{%
  \ifnum\c@tocdepth>2\relax
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=\z@\hangindent=63bp\hangafter=1\interlinepenalty\@M\bodyfont
   \def\numberline##1{\hb@xt@63bp{##1\hfil}}%
   #1\nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#2}\par}\fi}
\renewcommand*{\l@subsubsection}[2]{%
  \ifnum\c@tocdepth>3\relax
  {\leftskip=-99.3bp\rightskip=\@tocrmarg\parfillskip=-\@tocrmarg
   \parindent=\z@\hangindent=63bp\hangafter=1\interlinepenalty\@M\bodyfont
   \def\numberline##1{\hb@xt@63bp{##1\hfil}}%
   #1\nobreak\leaders\hbox to 2.64bp{\hss.\hss}\hfill\nobreak\hbox{#2}\par}\fi}
\makeatother

% ================= 修订标记（参照 EPO《Guidelines ... showing modifications》，并加强） =================
%   规则：新增 = 绿色背景高亮；删除 = 红色背景高亮 + 删除线。
%   背景高亮用 cjkhl（可自动换行）；删除线在 \colorbox 内不被 \CJKsout 支持，故改为逐字手绘横线。
%   由 \revisiontrue/false 控制：干净版只显示新文本，修订版按背景色显示增删。
\RequirePackage{xeCJKfntef}
\RequirePackage{cjkhl}
\definecolor{revaddbg}{RGB}{198,240,198}   % 新增：浅绿背景
\definecolor{revdelbg}{RGB}{255,200,200}   % 删除：浅红背景
\newcommand*{\added}[1]{\ifrevision\cjkhl{revaddbg}{#1}\else#1\fi}
\newcommand*{\deleted}[1]{\ifrevision\cjkhlst{revdelbg}{#1}\fi}
\newcommand*{\changed}[2]{\deleted{#1}\added{#2}}
% 标题改号/改名的“旧标题幽灵行”（仅修订版显示）——删除在前
\newcommand*{\guiderevold}[1]{%
  \ifrevision\par\vspace{6bp}\noindent{\heiti\bodyfont\cjkhlst{revdelbg}{#1}\par}\nobreak\fi}
% 新增标题（修订版显示为绿色高亮标题；干净版不出现——由 build_tex 直接输出普通标题）——新增在后
\newcommand*{\guiderevnew}[1]{%
  \ifrevision\par\vspace{6bp}\noindent{\heiti\bodyfont\cjkhl{revaddbg}{#1}\par}\nobreak\fi}
% 标题改号/改名的“混合行”：只标出真正改动的部分（旧红删除+新绿高亮），其余照常
\newcommand*{\guiderevheadmix}[1]{%
  \ifrevision\par\vspace{6bp}\noindent{\heiti\bodyfont #1\par}\nobreak\fi}

% ================= 插图 =================
\RequirePackage{graphicx}
\RequirePackage{amsmath}   % \text（公式内中文/词条）
% 图/结构式：#1=文件 #2=宽(bp) #3=高(bp)
% 放在单独一行并占据实际高度，避免与上下文字重叠（原先是零高度 raisebox）。
\newcommand*{\guidefigure}[3]{%
  \par\noindent\hspace*{21bp}%
  \includegraphics[width=#2bp]{#1}\par}
% 行间公式：#1 = 纯 LaTeX 数学（content.json 的 formula 块），居中显示
\newcommand*{\guideformula}[1]{%
  \par\vspace{6bp}\noindent\[#1\]\par\vspace{6bp}}

% ================= 超链接（总目录/分目录可点击跳转） =================
% hidelinks：链接不显示颜色/边框，复刻原书无可见链接样式的观感；
% bookmarks=false：不生成 PDF 书签大纲（本工程章为自写编号，避免脏书签）；
% 目录条目的跳转由 hyperref 接管 \contentsline 自动注入锚点实现。
\RequirePackage[hidelinks, pdfencoding=unicode, bookmarks=true,
  bookmarksopen=true, bookmarksnumbered=false, bookmarksdepth=6]{hyperref}

% ================= 复制 PDF 文本时去掉折行换行（实验，见 README） =================
%   原理：将每个正文段落包进 PDF 标记内容
%       /Span<</ActualText<UTF-16BE 十六进制串>>> BDC ... EMC
%   支持 ActualText 的阅读器（Adobe Acrobat、Chromium/PDFium 等）复制时按整段
%   连续文本输出，不会在视觉折行处插入换行符；不支持的阅读器忽略之，文本不变。
%   参数 #1 为大写 UTF-16BE 十六进制串（BOM FEFF 由宏补上）。
%   注意：若段落跨越物理页，BDC/EMC 会分处两页，个别严格解析器会提示 EMC 不匹配，
%   但正文不会丢失（构建默认开启，可用 ACTUALTEXT=0 关闭）。
\newif\ifguideactual
\guideactualfalse   % 默认关闭；由 build_tex.py 在需要时置 \guideactualtrue
\newcommand*{\guideATbegin}[1]{%
  \ifguideactual\special{pdf:content /Span<</ActualText<FEFF#1>>> BDC}\fi}
\newcommand*{\guideATend}{%
  \ifguideactual\special{pdf:content EMC}\fi}

% 原书正文永远在 x=154.6bp（左右边距不互换）
\AtBeginDocument{%
  \setlength{\evensidemargin}{\oddsidemargin}%
  \pagestyle{main}}




\endinput
