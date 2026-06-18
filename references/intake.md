# Intake Workflow

把旧简历、图片、粘贴文本或口述经历转成可优化的结构化 profile，再进入写作和渲染。

## Required Reading

- `references/resume-schema.md`
- `references/resume-standards.md`
- `references/resume-writing.md`

有目标 JD 时再读 `references/tailor-to-jd.md`。

## Procedure

1. **识别来源类型。**
   - PDF：先运行 `python3 scripts/resume_pdf.py extract <path>`。
   - 图片 / 扫描件 / `IMAGE_BASED` PDF：用视觉 OCR 逐字转写，不使用空文本层。
   - 粘贴文本 / 口述：直接结构化，缺字段再问。

2. **保留来源事实。**
   - 保留姓名、联系方式、链接、公司、职位、时间、项目名和原始职责边界。
   - 源简历写“实习生 / 参与 / 协助”时不能擅自拔高成“工程师 / 主导”。
   - 已嵌入链接必须进入 profile 的 `links` 或条目 `links`，最终 PDF 要可点。

3. **问清个性化项。**
   - 目标岗位 / 行业。
   - 最想突出的优势。
   - 输出语言：中文或英文。
   - 身份类型：experienced、student、academic、career_switcher。
   - 可选模块：开源、作品集、获奖、校园经历、证书、论文、研究成果。
   - 隐私场景：private、public、recruiter。公开分享默认提醒隐藏手机号。
   - 是否有目标 JD。

4. **生成 profile。**
   - 使用 `references/resume-schema.md` 的结构。
   - 内容少也先形成 profile，不直接填 HTML。
   - 缺结果数字时写入 `data_needed`，并在对应 bullet 放 `[DATA NEEDED: ...]`。

5. **按身份排序。**
   - 社招 / 有工作经历：Summary → Experience → Projects / Skills → Education。
   - 学生 / 应届：Summary → Education → Projects → Internship / Experience → Skills。
   - 学术 / 研究：Summary → Education → Research / Publications → Projects → Skills。
   - 非技术岗：成果、作品、营收、增长、转化、作品集优先于工具名。

6. **校验 profile。**
   - 运行 `python3 scripts/resume_profile.py validate <profile.json>`。
   - 有 hard error 先修结构；有 warning 列给用户或进入下一轮追问。

## Edge Cases

- **没有清晰 section：** 先按 Summary / Experience or Projects / Education / Skills 粗分，不强造经历。
- **技能墙很长：** 按方向压成 3-5 行，避免“熟悉 / 了解 / 掌握”流水账。
- **多个目标方向：** 先问用户本次投哪个岗位，不做一份试图覆盖所有岗位的简历。
- **真实信息过少：** 可以产出草稿，但必须显眼标出待补数据，不能靠空话撑满一页。

