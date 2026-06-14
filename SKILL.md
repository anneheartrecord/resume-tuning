---
name: resume-tuning
description: 交互式简历生成器，面向**所有岗位**（技术、产品、设计、运营、市场、学生等）。用户给一份现成简历、或只口述/粘贴一些零散经历，都能交付一份排版好的**单页 PDF 简历**。流程是交互式的：先问清个性化输入，再生成几种版式的初稿让用户挑，最后渲染定稿 PDF。当用户说「做/调整/优化简历」「把这段经历做成简历」「生成一份简历」「简历转成英文」「帮我排版简历」时使用。
version: 3.0.0
metadata:
  trigger: 交互式生成 / 优化任意岗位的 PDF 简历
  audience: 所有人（不限技术岗）
  deliverable: 单页 PDF（不是纯文本，也不是 Markdown）
  style: interactive — 分步个性化输入 + 多版式选择
---

# 交互式简历生成器（resume-tuning）

## Overview

最终产物是**一份排版好的单页 PDF 简历**——纯文本/Markdown 只是中间过程，不是交付物。

面向**所有岗位**，不只技术人员。判断标准在 `references/resume-standards.md`。版式模板在 `assets/templates/`（classic / minimal / modern 三种，同一份内容可套不同版式）。

两种输入都要走到 PDF：
- **A. 已有简历**（PDF/MD/图片）→ 提取内容（含已有超链接）→ 优化 → PDF。
- **B. 只有零散内容**（口述、几段经历、一段自我介绍）→ 结构化 → PDF。

**这是个交互式 skill：不要一把梭生成。** 分步问清用户的个性化输入，先给几种初稿让用户选，再定稿。

## 处理流程（交互式）

### Step 0 · 读标准
读 `references/resume-standards.md`，吃进好简历标准 + 校对清单。

### Step 1 · 收集输入（交互）
- A：读简历；PDF 用 pypdf 提取**文本 + 已有超链接**（`/Annots` 里 `/Subtype=/Link` 的 `/A/URI`），改版/翻译时带过去。
- B：缺什么问什么。
- **用 AskUserQuestion 问清这几个个性化项**（已知的跳过）：
  1. **目标岗位/行业**——决定措辞和重点（技术岗强调项目+量化+GitHub；设计岗强调作品集；运营/市场强调增长数据；学生强调项目+实习+奖项）。
  2. **最想突出的优势**——决定排序，放第一。
  3. **语言**——中文 / 英文。
  4. **可选模块**——开源 / 作品集 / 获奖 / 证书。
- 缺的量化数字用 `[DATA NEEDED: …]` 占位，**绝不编造**。

### Step 2 · 结构化内容
拆模块：抬头/联系方式、自我评价、经历（倒序）、技能/专长、教育，按岗位增删可选模块，按岗位调整重点。

### Step 3 · 优化 + 校对
- 内容按标准：量化(STAR)、带论据、措辞精确、最亮点前置；非技术岗把「技能用项目证明」换成「用成果/作品/数据证明」。
- 校对：错别字、专有名词大小写、分隔符、数字格式统一。

### Step 4 · 出多版式初稿，让用户选（交互核心）
1. 把**同一份内容**分别填进 `assets/templates/` 的 2–3 个版式，各渲染一份**草稿 PDF**。
2. 几版一起给用户看，用 AskUserQuestion 让他选（附一句风格说明：classic=蓝色栏目/通用，minimal=衬线极简/资深，modern=彩色页眉/醒目）。
3. 选定后在该版式上精修。
> 别跳过这步直接定一版——多版式选择是核心体验。

### Step 5 · 渲染定稿 PDF
- 只改模板 `<body>`，CSS 不动。
- **超链接做成可点**：邮箱(mailto:)、GitHub、个人站、作品集、开源、博客、社交账号都用 `<a href>` 包起来。
- 用 WeasyPrint 渲染并校验页数 + 打印嵌入的链接：
  ```bash
  python3 -c "
  from weasyprint import HTML
  from pypdf import PdfReader
  HTML(filename='resume.html').write_pdf('out.pdf')
  r=PdfReader('out.pdf'); print('pages:', len(r.pages))
  print('links:', [(o.get_object().get('/A') or {}).get('/URI') for p in r.pages for o in (p.get('/Annots') or []) if o.get_object().get('/Subtype')=='/Link'])
  "
  ```
  （macOS 上 WeasyPrint 找不到系统库时，给命令加前缀 `DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib"`。）
- **一页硬约束**：`pages!=1` 就收紧（删非必要块 → 压缩弱经历 → `<body class="dense">` → 调小 margin），重渲染到 1 页。
- 核对打印出的链接列表，确认齐全、与源简历一致。

### Step 6 · 交付
- PDF 存到用户的简历目录（私密的放私密目录，不进 git）。
- 简短文本小结：选了哪个版式、改了什么、还有哪些 `[DATA NEEDED]` 要补。
- 默认**不发送 / 不发布**；要发邮件/挂公开链接先确认。

## 渲染环境
```bash
brew install pango gdk-pixbuf libffi          # macOS 系统库
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
```

## 注意
- **终态必须是 PDF**；交互式、多版式可选；面向所有岗位。
- 不编造数字，缺的标 `[DATA NEEDED]`。
- 一页；中英文同模板（改 `lang` + 字体回退，模板含 PingFang 回退）。
- 不覆盖用户其他简历，除非用户明确要求替换。
