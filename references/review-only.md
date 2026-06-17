# Review Only

用户只想诊断简历时，不直接改写、渲染或输出 PDF。先给可执行反馈，让用户决定是否进入生成流程。

## Required Reading

- `references/resume-standards.md`
- `references/resume-writing.md`
- `references/ats-and-jd.md`（用户关心 ATS 或提供 JD 时）

## Procedure

1. **读取简历。**
   - PDF 先运行 `scripts/resume_pdf.py extract`。
   - 图片/扫描件走视觉 OCR。
   - 如果只给文本，直接诊断文本。

2. **按三档反馈。**
   - 必须改：事实错误、错别字、超一页、联系方式不可解析、明显夸大、ATS 无法解析。
   - 强烈建议：无量化、bullet 无结果、亮点埋太深、技能墙、结构排序不合身份。
   - 可选优化：版式、措辞、模块取舍、链接补充、进一步 JD 定制。

3. **有 JD 时补充三档匹配。**
   - ✅ 已覆盖。
   - 🟡 有但没突出。
   - 🔴 真没有。

4. **不要擅自生成成品。**
   - 如果用户确认“开始改 / 做成 PDF / 直接出定稿”，再进入 `references/intake.md` 和 `references/render-and-deliver.md`。

## Output Shape

保持短而具体。每条建议包含问题、为什么影响筛选、怎么改。不要写泛泛的“建议优化表达”。

