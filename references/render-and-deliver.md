# Render and Deliver

把同一份 profile 内容填入 2-3 个模板，生成预览，让用户选择版式，再渲染最终 PDF。

## Required Reading

- `references/resume-schema.md`
- `references/resume-writing.md`
- `references/ats-and-jd.md`（有 JD 或需要 ATS 自检时）

## Template Selection

模板在 `assets/templates/`，模板说明在 `assets/templates/templates.json`。

- classic：稳重、蓝色栏目、通用岗位，默认优先。
- minimal：衬线极简、留白更多，适合资深、学术、管理、非技术岗。
- modern：彩色页眉、视觉更强，适合产品、设计、市场、增长或想更醒目的场景。

## Procedure

1. **填充模板。**
   - 默认只改 `<body>` 内容，CSS 不动。
   - 邮箱、GitHub、个人站、作品集、开源、博客、社交账号都用 `<a href>`。
   - 标准章节标题优先用 ATS 友好的中英文标题。

2. **生成预览。**
   - 把同一份内容填入 2-3 个版式。
   - 运行 `python3 scripts/resume_pdf.py preview <classic.html> <minimal.html> <modern.html>`。
   - 把 PDF/PNG、页数、scale、links、warnings 和模板适用说明一起给用户看。

3. **用户选版式后精修。**
   - 保持内容一致，只根据版式空间删减弱项或调整 section 顺序。
   - 默认优先一页；若超过一页，先确认是否有必要完整保留。需要压缩时先删弱经历和弱 bullet，再考虑 dense class；不要无限缩字号。

4. **渲染定稿。**
   - 运行 `python3 scripts/resume_pdf.py render <final.html> <final.pdf>`。
   - 检查页数、scale、links、placeholder leak。
   - 中文简历必须用 `qlmanage -t -s 1200 -o <dir> <final.pdf>` 转 PNG 后肉眼确认 glyph。

5. **ATS 自检。**
   - 有 JD：`python3 scripts/ats_check.py <final.pdf> --name "<姓名>" --keywords "..."`
   - 无 JD：也至少检查文本层、章节、email、页数取舍、阅读顺序。
   - hard failure 必须修复后再交付。

6. **交付。**
   - 输出到用户指定目录；私密内容不要放进仓库。
   - 不覆盖旧简历，除非用户明确要求。
   - 不代发邮件、不发布公开链接，除非用户确认。

## Final Checklist

- 页数已确认：默认推荐 1 页；超过 1 页时说明原因和取舍。
- 没有 `{{...}}`、`[DATA NEEDED]`、`__CJK_*__` 泄漏。
- email 和关键链接可点。
- ATS 至少识别出 2 个标准 section。
- 中文 glyph 已用 PNG 肉眼看过。
- 简短交付说明包含版式、改动、待补数据和 JD 缺口。
