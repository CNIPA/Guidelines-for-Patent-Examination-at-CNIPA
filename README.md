# 非官方版《专利审查指南》（2023）

> **📥 下载 PDF**（各版本按公布日打 tag；`dist/` 目录亦保留各版本 PDF）
> - **2025 年修改版（tag [`20251113`](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases/tag/20251113)）**：
>   [不带修订记录（干净版）](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases/download/20251113/Guidelines-for-Patent-Examination-2023_unofficial_no-revision-marks.pdf) ·
>   [带修订记录（对照版）](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases/download/20251113/Guidelines-for-Patent-Examination-2023_unofficial_with-revision-marks.pdf)
> - 2023 原版（tag [`20231221`](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases/tag/20231221)）：
>   [直接下载 PDF](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases/download/20231221/Guidelines-for-Patent-Examination-2023_unofficial.pdf)
> - 全部版本见 [Releases](https://github.com/CNIPA/Guidelines-for-Patent-Examination-at-CNIPA/releases)。
>
> **许可协议**：[CC0 1.0 通用（公共领域贡献）](LICENSE) —— 可自由复制、修改、分发，包括商业用途，无需署名。

把国家知识产权局《专利审查指南》PDF 逆向工程成一个**非官方、可排版、可修订**的 LaTeX 工程。

目标不是像素级复刻官方 PDF，而是：

- **正文左侧的醒目标记（"法 18"、"细则 26" 等）精确对齐到原书对应段落** —— 这是本工程的第一优先级；
- 字体、字号、行距、字间距**与原书大致一致**（宋体 10.56bp、行距 15.6bp、CJK 步进约 11.75bp）；
- 未来官方发布"修改对照表"时，能**快速生成带修订记录的版本 + 排版干净的最新版**。

> 说明：因不追求逐页逐行精确还原（含防孤行标题导致的留白），生成 PDF 的页数与官方 613 页不同（本工程 2023 版约 680 页，叠加 2025 年修改后的新版约 695 页），行尾对齐方式也不同，但内容完整、左侧标记对齐。

---

## 目录结构

```
source/                  官方原始资料（用日期表示版本）
  20231221_专利审查指南2023.pdf       官方原书（权威数据源）
  20231221_专利审查指南2023.bookmark  官方书签（页码 -> 结构）
  20231221_专利审查指南2023.doc       官方 DOC（备查）
  20251113_国家知识产权局关于修改专利审查指南的决定.pdf   局令第84号决定 + 修改对照表附件
data/
  pages.json             由官方 PDF 抽取的逐页 span/矢量/图片（原始中间产物，仅 extract_pages 生成）
  content.json           结构化正文：全部文字、标题层级、左侧边注、索引等（build_tex 的唯一输入，内容真源）
  decision_items.json    由决定 PDF 解析出的结构化修改条目（parse_decision.py 生成）
  revisions_2025.json    2025 年修改的修订覆盖层（引用 decision_items.json 的新文本）
  content_2026.json      应用覆盖层后的“带修订标注”内容（apply_revisions.py 生成）
  at_skip.json           可选：仅 --actualtext 实验模式用（由 detect_spanning 按需生成，平时不存在）
LICENSE                  CC0 1.0（公共领域贡献）
dist/                    各版本编译产物（文件名前缀为“公布日_”，便于用户查看历史版本）
  20231221_专利审查指南2023_非官方版.pdf                    （2023 原版，tag 20231221）
  20251113_专利审查指南2023_非官方版_不带修订记录.pdf        （2025 新版·干净版，tag 20251113）
  20251113_专利审查指南2023_非官方版_带修订记录.pdf          （2025 新版·修订对照版，tag 20251113）
latex/
  guide.cls              文档类：页面几何、字体、页眉页脚、边注、EPO 式修订宏、分目录
  cjkhl.sty              中文可换行背景高亮宏包（dpctex，MIT/LPPL；本工程加了删除线钩子）
  main.tex               主文档（自动生成）
  frontcover.tex         封面（自动生成）
  content/partN.tex      各部分正文（自动生成）
  content/idx.tex        索引（其他）（自动生成）
  figures/               抽取出的 16 张图
  main.pdf               编译产物（干净版；build_2025.py 后为 2025 年修改版）
  main_rev.pdf           编译产物（EPO 式修订对照版）
tools/
  paths.py               原版资料来源路径（source/ 下按扩展名自动识别）
  extract_pages.py        PDF -> pages.json
  build_content.py        pages.json + bookmark -> content.json（含边注挂接）
  parse_decision.py       修改决定 PDF -> decision_items.json（按段落重建 + 条目归类）
  apply_revisions.py      覆盖层 + content.json -> content_2026.json（精确 diff 标注 add/del）
  guidemodel.py           content.json 导航（按 部分/章/节号 定位标题与段落）
  textdiff.py             修订 diff 工具：句子对齐 + 逐字/记号级比较、自适应合并（apply_revisions 与 build_tex 共用）
  build_tex.py            content.json -> latex/*.tex（支持 REVISION / CONTENT_JSON）
  build_2025.py           2025 修改一键构建：干净版 + EPO 式修订对照版
  build.py               原版（2023）一键构建脚本
  verify_notes.py        左侧边注对齐校验（前/中/后多页抽查）
  verify_text.py         文本保真度校验：content.json ↔ main.pdf（证明无丢字/无幻觉）
  verify_layout.py       版式校验：封面居中 / 右侧无标签 / 总目录链接 / 分目录非空
  detect_spanning.py     探测跨页段落（--actualtext 模式用，生成 data/at_skip.json）
```

---

## 一键构建

前置依赖：

- Python 3 + `pymupdf`（`pip install pymupdf`）
- [tectonic](https://tectonic-typesetting.github.io/)（XeLaTeX 引擎，自带包管理）
- 系统中文字体：`SimSun`(宋体)、`SimHei`(黑体)、`KaiTi`(楷体)、`Times New Roman`

> 官方原始资料放在 `source/` 目录，文件名以**出版日期表示版本**（如 `20231221_专利审查指南2023.pdf` /
> `.bookmark` / `.doc`）。脚本通过 `tools/paths.py` 按扩展名自动识别，**换新版只需替换 `source/` 里的文件**，
> 无需改代码；也可用环境变量 `GUIDE_SOURCE_DIR` 指向别的资料目录。
> （`source/` 里同时存放“修改决定”等 PDF 时，`paths.py` 会**排除**文件名含“决定/通知/公告”的 PDF，仍取最新的指南 PDF。）

```bash
# 干净版：抽取 + 生成源码 + 编译 -> latex/main.pdf
python tools/build.py

# 仅重新生成源码并编译（跳过 PDF 抽取，改了 content.json 后用）
python tools/build.py --no-extract

# 修订标记版：新增绿色 / 删除红色删除线 -> latex/main_rev.pdf
python tools/build.py --revision

# 附加“复制不带折行换行”实验标记（见下方“复制文本”一节）
python tools/build.py --actualtext
```

如只想分步执行（首次或换新版时）：

```bash
python tools/extract_pages.py    # 官方 PDF -> data/pages.json
python tools/build_content.py    # pages.json + bookmark -> data/content.json
python tools/build_tex.py        # -> latex/*.tex  (REVISION=1 生成修订标记版)
```

### 2025 年修改（局令第84号）一键构建

```bash
# 解析决定 -> 应用修订覆盖层 -> 编译两个版本
python tools/build_2025.py

#   新版（干净版）  -> latex/main.pdf
#   修订对照版      -> latex/main_rev.pdf

# 已解析过决定、只想重跑覆盖层与编译：
python tools/build_2025.py --no-parse
```

---

## 修订工作流（应对官方“修改决定 / 修改对照表”）

官方只发布修改决定（含对照表附件），不发布修订后 PDF。本工程让你在发生修订时，**先提取数据、再一键生成两个版本**。

### 1. 修订标记规则（`guide.cls`，参照并加强 EPO《… showing modifications》）

样式规则已从欧专局修订对照版提炼并**加强**（背景高亮比单纯变色明显得多），写进 `guide.cls`：

| 语义 | 背景 | 装饰 | 宏 |
|---|---|---|---|
| 新增文字 | 浅绿 `revaddbg` | — | `\added{...}`（内部 `\cjkhl`） |
| 删除文字 | 浅红 `revdelbg` | 删除线 | `\deleted{...}`（内部 `\cjkhlst`） |
| 替换 | 旧浅红 + 新浅绿 | | `\changed{旧}{新}` |
| 标题改号/改名 | 旧标题“幽灵行”= 浅红+删除线 | 旧在前、新在后 | `\guiderevold{...}` + 新标题 |
| 新增标题 | 浅绿高亮标题 | | `\guiderevnew{...}` |

**增删顺序约定**：同一处既有删除又有新增时，**一律“删除在前、新增在后”**（`apply_revisions.py` 的 `_order_del_before_add` 保证，标题的幽灵行也同样）。

效果由 `\ifrevision` 控制：

- **干净版**（`\revisionfalse`，默认）：`\added` 正常显示、`\deleted` 不显示（若整段被删则整段消失）、`\changed` 只显示新文字。目录/书签只含新文本。
- **修订对照版**（`\revisiontrue`）：新增浅绿背景、删除浅红背景+删除线。

> 实现说明：中文**可换行的背景高亮**用 `cjkhl`（`latex/cjkhl.sty`，源自 dpctex / D. Carlisle，MIT/LPPL），它把每个字放进一个 `\colorbox`。删除线不能用 `\CJKsout`（在 `\colorbox` 内不绘制）、也不能用 `ulem`/`soul`（与 `xeCJK` 的 `CJKglue` 冲突，报 `Improper \prevdepth`/`Reconstruction failed`），故在 `cjkhl` 的每字钩子里**手工画一条横线**（`\cjkhlst`）。

### 2. 提取修改数据 → 覆盖层 → 应用（2025 年修改已内置）

```bash
python tools/parse_decision.py    # 决定 PDF -> data/decision_items.json
python tools/apply_revisions.py   # content.json + revisions_2025.json -> content_2026.json
```

- **`parse_decision.py`**：按版面（正文左边界/首行缩进）把决定 PDF 的“物理行”重建成“段落”，再按 `一、二、…`（顶层）与 `（一）（二）…`（子项）归类，输出 `decision_items.json`；同时排除对 `第（一）项` 之类引用的误拆，并把附件“修改对照表”截掉。
- **`revisions_2025.json`**：人工核对的覆盖层，每条操作说明“改哪一节、哪一段、何种操作”，新文本通过 `from` 引用 `decision_items.json`（**不手工转录**，保证与决定一致）。支持的操作：`replace_para` / `append_para` / `insert_after_para` / `insert_before_para` / `insert_section_end` / `insert_chapter_end` / `insert_before_heading` / `delete_para` / `delete_section` / `retitle` / `renumber_headings` / `renumber_items` / `pairreplace`。
- **`apply_revisions.py`**：定位目标段落，对“修改”做**以人为本的标注**（`tools/textdiff.py`）：先按句末标点对齐（标点不会错配），句内再做记号级比较——**例号/列表号/章节号按整体记号**处理（`【例10】→【例12】`、`6.1.3→6.1.4` 标整段，而非只标一个数字），**删除一律在前、新增在后**。目标是让人一眼看出“改前是什么、改后是什么”：**小的增删单独标出**（如新增的两字“品种”、删除的两字“选择”），**整段重写的部分则成块“整段删 + 整段增”**，而不是逐字交错。多数段落由 `textdiff` 自动得到合适粒度；**个别难以自动对齐或需成块显示的段落**在 `revisions_2025.json` 里用 `set_segs` **逐段核定**（如 6.2.2、9 第二段）。列表条目（（1）（2）…）按**条目正文**对齐：插入新条目时旧条目只改序号（与官方《修改对照表》一致）。标题改号/改名只标真正改动处（如仅序号）。输出 `content_2026.json`，`build_tex.py` 据此一次生成干净版与修订版。

### 3. 未来再修订时

1. 把新的决定 PDF 放进 `source/`；
2. 写一份新的 `data/revisions_20XX.json`（可复制 `revisions_2025.json` 改写）；
3. `parse_decision.py` 里改一下目标文件名，`apply_revisions.py` 里改一下覆盖层文件名；
4. `build_2025.py`/`build_tex.py` 设 `CONTENT_JSON` 指向新的 `content_20XX.json`，编译即得两个版本。

样式规则本身无需改动——它已在 `guide.cls` 里参数化。

---

## 左侧标记对齐（核心保证）

`build_content.py` 把每页左侧的"法/细则/条例"边注挂接到其所在段落，并记录**相对该段首行的纵向偏移**；`guide.cls` 的 `\guidenote[偏移]{文字}` 用 `marginnote` 把标记放在"段首行基线 + 偏移"处。经 `tools/verify_notes.py` 对前/中/后多页抽样校验，34 条（含跨页负偏移）全部 `Δ=0.0bp`，即与原书逐条对齐。

`verify_notes.py` 用法：先 `python tools/build_tex.py` 再 `python tools/verify_notes.py`，会打印每条抽样边注的 `stored` 与 `gen` 偏移差。

---

## 文本保真度保证（无幻觉、无错字）

本工程的文字全部来自对官方 PDF **文本层（text layer）的逐字抽取**，过程中**没有任何语言模型参与生成、改写或翻译**——从根本上排除了"幻觉"的可能。

### 文字来源链路（只读不写）

1. `extract_pages.py`：用 PyMuPDF 读取原书 PDF 的 `rawdict`，按页保存 span/矢量/图片（中间产物 `pages.json`）。
2. `build_content.py`：把 `pages.json` 过滤为干净正文（去掉页眉、页码、页位标记 `(X-Y)`、表格/图区），挂接左侧边注，输出结构化 `content.json`。
3. `build_tex.py`：`content.json` 序列化为 LaTeX，**只做字符转义**（`% & # _ { } ~ ^` 等），不增删改任何文字。
4. tectonic / XeLaTeX 编译为 `main.pdf`。

### 如何证明没有丢字 / 错字 / 幻觉

`tools/verify_text.py` 做**反向校验**：把生成 `main.pdf` 的全文文本（**不过滤**页眉/批注，从而免疫抽取噪声、不产生假阴性）逐块与 `content.json` 比对：

- 对 5707 个正文块（长度≥12）：
  - 逐字存在（整块为生成全文的连续子串）：**5554 块（97.32%）**
  - 前 50/30 字存在（near）：**153 块（2.68%）**，逐块定位首个差异点
  - 未能定位（missing）：**0 块**

  153 个 near 块逐块核验，差异性质为：
  - 页眉抽取噪声（原书与生成 PDF 在抽取时都会把"专利审查指南第X部分第Y章"/页码/`(X-Y)` 串入正文流）：**151**
  - 相邻段落边界比对的假阳性（插入片段实为另一条相邻段落正文）：**2**
  - 疑似真实内容差异：**0**

- 防重复抽检：随机抽 8 个长段落，exact 类均恰好出现 1 次，**无重复段落**（生成 PDF 中无段落被错误复制）。

**结论：抽取与编译均未丢字、未改字、无幻觉。** 渲染可见文本即原书文本；仅 PDF 文本层在抽取时会把页眉串入，属抽取噪声而非内容错误。

用法：

```bash
python tools/verify_text.py
```

### 封面 / 目录版式说明

- 封面与各部分封面均为 `\centering` **居中**（与原书一致）；
- 目录的"目 录 / 总 目 录"标题居中，下方章节条目**左对齐并向左探出**（`guide.cls` 中 `leftskip=-99.3bp`），这是原书目录格式；
- 侧边标记（"法 18"、"细则 26" 等）**仅出现在正文页**，目录页本身无标签区。

目录（总目录与各部分分目录）的细化还原：

- **点号（引导线）密度**按原书实测设为每 2.64bp 一个点（原书约 113 点/296bp），不再是稀疏的大间隔点；
- **总目录二级标题**（"第一章 …"）相对一级标题（"第一部分 …"）缩进 23.4bp（原书无缩进，此处按需保留了小缩进）；
- **目录标题居中**：`总目录 / 目录 / 索引` 均按**整张页面**居中（`\guidecenterpage`；若只按版心居中会偏右约 50bp）；
- **各部分分目录**：章号左对齐在页边（x=55.3），章号与章标题之间留约 **1 个字符**；各级标题统一对齐到 **x=102.3bp**；节号相对章号再**右缩进约 1 个字符**（x≈66.3）后左对齐。因最深的节号（如 `5.10.1.1`）宽约 34bp，节号缩进取约 1 字符，才能同时满足「标题对齐」与「章号后 1 字符空白」；分目录**不再重复首行"第X部分 …"**（原书亦无此首行）；
- **页眉（书眉）**：一端为"专利审查指南第X部分第Y章"，另一端**只显示章标题、不重复"第Y章"**（`\markboth{标题}{专利审查指南…}`）；
- **外缘竖排灰底标签**：只在各部分分目录页出现，奇数页贴右缘（x=484.3..519.0）、偶数页贴左缘（x=0..34.8），框 34.8×52.2bp、宋体 10.56bp 逐字竖排（基线步进 10.56bp）；**总目录页不再出现空灰框**。

### 索引（"其他 > 索引"）版式与自动跳转

- **词条与位置串之间**留一个字符宽的空白（`\hspace{1em}`），不再几乎贴在一起；拆分点是**末尾的位置串序列**（用正则从行尾匹配），因此词条里即便因抽取带上空格/引号（如 `避免“ 事后诸葛亮”`）也能正确归为词条、与其它词条对齐；
- **折行的位置串**与**本词条第一行位置串的左端**对齐：悬挂缩进 = 词条实测宽度 + 1em（`guide.cls` 的 `\guideidxentry`，用 `\settowidth` 自动测量），随词条长度自适应，不再用固定值；字母分区标题（A/B/…）**不缩进**（与词条同起于 x=80.3）；
- 位置串里的连字符：原数据里**全角 `－` 与半角 `-` 都有**，统一显示为半角 `-`（更紧凑、减少不必要折行）；原数据个别词条末尾多余的 `；` 会自动去掉；
- 词条/位置的切分与"新词条/续行"判定都按**规则**（行尾位置串序列、行首是否为位置串/单字母、左边界区间），已覆盖引号内空格、位置串前的空格（`Ⅵ. Ⅱ`）、跨行位置串等情况；
- **抽取数据本身在生成 `content.json` 时就已规范化**（`build_content.py` 的 `norm_idx_text`）：罗马数字点号后的空格、`；` 两侧空格、连字符两侧空格、引号内外空格、末尾多余 `；`、全角 `－` 全部清理；可用一组正则审计，现为 0；
- **位置串自动生成跳转链接**：规则为 `<部分罗马>.<章罗马>－<节号>`（如 `Ⅰ.Ⅰ-6.2.1.2` = 第一部分第一章 6.2.1.2 节）；**单独的罗马数字**（如 `Ⅳ`）表示整个第 X 部分，链接到该部分封面；节号可以没有小数点（如 `Ⅴ.Ⅳ-6`）。`build_tex.py` 解析该规则，按 `gpos.<部分>.<章>[.<节>]` / `gpos.p<部分>` **确定性**命名锚点（见 `guide.cls` 的 `\guide@head`），索引位置串据此加 `\hyperlink`，无需手工维护锚点。标题编号的尾点（如 `6.`）在生成锚点时归一化掉，保证与索引里的 `-6` 对得上。锚点放在标题行内，标题跨页时链接仍指向标题所在页。
- 索引开头的**说明文字**与其他词条同等处理：它是一段普通段落（首行缩进、其余行回到左边界），**不套用词条的悬挂缩进**；其中的示例 `Ⅰ.Ⅰ-6.2.1.2` 也会换成半角 `-` 并加链接（索引说明与词条续行已正确合并为一条，不再被误拆）。
- 兼容性：与总目录/分目录用的是同一套标准 PDF 链接，主流阅读器均支持。

### 防“孤行标题”（样式层）

`guide.cls` 的 `\guide@needspace` 会在放置标题前检查当前页剩余高度：若不足以容纳（该标题 + 其后至少 3 行正文）则先换页。`build_tex.py` 进一步识别**连续的标题组**（如"4. / 4.1 / 4.1.1"三连标题），为整组预留高度，组内非首个标题不再重复触发换页。这样标题永远不会单独留在页尾、其后正文跑到下一页。

> 代价：为避免孤行，个别页尾会留白，总页数会略增（这是需要人工确认的取舍）。预留行数在 `tools/build_tex.py` 的 `nd = ... 3 * 15.6` 一处可调。

### PDF 书签（大纲）与目录链接

- 生成与原书一致的**多级书签树**（`guide.cls` 中 `bookmarksdepth=6`）：封面、总目录、各部分、分目录、章、节、小节、子小节、条，并在末尾给出 **`其他 > 索引 > A…Z`**（原书为 21 个存在的字母，本工程一致），共约 1409 条（原书 1408 条，同一结构）。
- 书签由每个标题的 `\addcontentsline` 触发 hyperref 自动生成（层级取标准 `toclevel@part/chapter/section/...`），**不需要手写 `\pdfbookmark`**；封面/总目录/分目录等非标题元素用 `\guideoutline`。
- **各部分分目录的条目、以及索引里的位置串都可点击跳转**：每个标题用确定性锚点 `gpos.*`（写入 `.ptc` 供分目录用，索引侧直接按同一规则生成）。
- 书签/链接需要读取上一遍的 `.out`/`.aux`，因此 **tectonic 会自动重跑几遍**（"可能要编译两次"）。

### 左侧边注与标题的自动绑定（不再依赖分页）

之前边注是挂到"下一个段落"上、并用一个可能很大的负偏移去对齐，一旦该段落跨到页首，标记就会被顶进页眉（如"细则 50"）。

现在改为**按结构挂接**（`tools/build_content.py`）：

- 位于标题行（或标题上方）的边注，直接挂到该**标题块**上，偏移是相对**标题首行**测得的（通常 ≈0）；
- 段落内/段落前的边注仍挂到该**段落**，偏移相对段落首行；同一段落的多个边注按原书行序给出递增偏移；
- `guide.cls` 的标题宏接收第三个参数（边注串），把 `\guidenote` 放在标题行内，于是标记**始终随标题/段落移动**，无需再关心分页；
- **防重叠兜底**：`build_tex.py` 把偏移钳制在 −11.5…+120bp（负偏移不会越过上一行、顶到上一条边注），跨页边注排到同段其它边注之下一行；页首/页尾边注也不再与页眉重叠。

维护时只需增删正文文字：标记跟着它所属的标题/段落走，位置自动正确。

### 复制文本：不带折行换行（实验，默认关闭）

目标：复制一段跨行文字时，不因视觉折行而多出换行符。做法是把每个正文段落包进 PDF 标记内容
`/Span<</ActualText<UTF-16BE…>>> BDC … EMC`，由支持 `ActualText` 的阅读器（如 Adobe Acrobat 等）
在复制时按整段连续文本输出。

- 启用：`python tools/build.py --actualtext`（或 `tools/build_tex.py` 时设 `ACTUALTEXT=1`）。
- 该模式会先编译一版（不加标记）用 `tools/detect_spanning.py` 找出**跨页段落**，只对单页段落加标记。
- **限制**：加标记会轻微改变分页，跨页段落的探测只能"尽力而为"；若某段仍跨页，
  个别阅读器/提取器可能把该段在两页各抽一次。因此该功能**默认关闭**，生成的 `main.pdf` 不含标记、最为稳妥。
- 各提取器行为不一：`ActualText` 对遵循规范的阅读器有效，但 `pdftotext`、`pdfminer` 等按版面重排者仍可能插入换行。


---

## 已知限制

- 页数、行尾对齐、页眉书眉交替规则按"大致一致"实现，不与官方逐页相等；
- 原书部分封面用"方正大黑简体"，本工程以 `SimHei + AutoFakeBold` 近似；
- 图/公式/结构式统一按 300dpi **栅格化区域**抽取（不会把带透明掩码的化学结构式抽成黑块），在版式中**单独占位**（不再与文字重叠），故非可编辑矢量、且相对原书的精确位置略有出入；
  - 例外：**可用 LaTeX 排版的公式**改为 `formula` 块（`{"t":"formula","tex":"..."}`），由 `guide.cls` 的 `\guideformula` 以行间公式呈现。目前第二部分第九章例 1 的圆周率公式 `π=(Σ圆内“点”计数值)/(Σ正方形内“点”计数值)×4` 已如此修正（该处原先被栅格化成图片，且图片还吞掉了紧随其后的一行正文，现一并修复）；
- 原书对短标题（约 2～3 个汉字）采用"字间加空"排版（如"年 费""引 言""新 颖 性"）。本工程在 `build_content.clean_head_text` 中**去掉了标题内部相邻汉字之间的空格**（标题号/章号与标题之间的分隔空格保留），故标题样式与原书略有出入；正文段落不含此类空格，不受影响；
- 修订覆盖层脚本（见上）需自行补充以支撑批量修订；
- **2025 年修改版**：`content_2026.json` 由 `content.json`（2023 原书）+ `revisions_2025.json` 叠加而来；正文与标题的增删改已按决定落实并着色，但**索引中的“位置串”指向的节号未随改号自动更新**（决定未包含索引变更；如涉改号节被索引引用，链接可能指向旧节号），且**页码/页数**与本工程自身的 2023 版不同；
- **修订对照版**对“修改”只标出真正改动的字词（例号/序号整体标记），红/绿成块；对**大段改写**的段落退回「整段删除+整段新增」（`textdiff` 相似度阈值）；`\added`/`\deleted` 仅在该版有背景色；
- "复制不带折行换行"为实验特性（默认关闭）：加标记会轻微影响分页，跨页段落的探测不保证 100%，详见"复制文本"一节。
