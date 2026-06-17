---
name: resume-tuning
description: 交互式简历生成器，面向所有岗位（技术、产品、设计、运营、市场、学生、学术等）。用户给一份现成简历（PDF、图片、扫描件、Markdown、文本），或只口述零散经历时，用它生成、优化、诊断、按目标 JD 定制、检查 ATS 可读性，并交付一份链接可点、刚好一页的 PDF 简历。当用户说「做简历」「优化简历」「调整简历」「把经历做成简历」「生成 PDF 简历」「简历转英文」「帮我排版简历」「按这个 JD 调简历」「看看能不能过 ATS」「诊断这份简历」时使用。
---

# resume-tuning

最终交付物是**一份单页 PDF 简历**。纯文本、Markdown、JSON profile、HTML 都只是中间产物。

这是交互式 skill：先问清目标岗位、语言、优势、可选模块、JD 和隐私场景，再出 2-3 个版式预览让用户选，最后渲染定稿。不要一把梭。

## Routing

先判断用户要做哪类任务，只读对应 reference，再按需读取公共标准。

| 用户意图 | 必读 reference |
|---|---|
| 从旧 PDF / 图片 / 粘贴文本 / 口述经历生成简历 | `references/intake.md` |
| 按目标 JD 调整简历、检查关键词覆盖 | `references/tailor-to-jd.md` |
| 渲染多版式预览、输出最终 PDF | `references/render-and-deliver.md` |
| 只诊断问题，不直接生成 PDF | `references/review-only.md` |
| 需要结构化中间数据或脚本校验 | `references/resume-schema.md` |

公共标准按任务读取：

- 内容质量：`references/resume-standards.md`
- 写作硬指标：`references/resume-writing.md`
- ATS / JD 规则：`references/ats-and-jd.md`

## Non-Negotiables

- 不编造数字、经历、职位、技能、证书、学校、公司或项目。
- 缺数据标 `[DATA NEEDED: ...]` 并追问；定稿 PDF 不能残留该标记。
- JD 匹配只 surface 用户真实具备的能力；真没有的关键词作为缺口反馈，不能塞进简历。
- 扫描/图片型 PDF 不能依赖文本提取结果，要用视觉 OCR 转写后再结构化。
- 中文简历必须使用内嵌单文件 CJK 字体，并在定稿前转 PNG 肉眼核验字形。
- 真实简历、JD、手机号、邮箱等私密内容不要提交到仓库；输出放用户指定目录。
- 模板 CSS 默认不改；优先只替换 `<body>` 内容。要改模板样式时先确认这是版式优化任务。

## Tooling

- 提取 / 渲染 / 预览：`python3 scripts/resume_pdf.py extract|render|preview ...`
- ATS 检查：`python3 scripts/ats_check.py <final.pdf> --name "<姓名>" --keywords "..."`，或 `--jd jd.txt` 做粗匹配。
- Profile 校验：`python3 scripts/resume_profile.py validate <profile.json>`
- JD 分档：`python3 scripts/jd_match.py <profile.json> --keywords "..."`，或 `--jd jd.txt`
- 内容 lint：`python3 scripts/resume_lint.py <profile.json> --mode draft|final`

## Output Contract

交付时简短说明：

- 选了哪个版式，以及选择理由。
- 内容上改了什么：亮点前置、STAR、量化、技能压缩、JD surface。
- 还有哪些 `[DATA NEEDED]` 或真实技能缺口。
- 定稿检查结果：一页、链接、ATS、中文 glyph、占位符是否通过。
