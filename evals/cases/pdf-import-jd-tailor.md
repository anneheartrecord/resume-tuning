# pdf-import-jd-tailor

## Input

用户上传旧 PDF 简历，并粘贴一个 JD。JD 要求 Go、Kubernetes、PostgreSQL、Redis、CI/CD。

## Expected Behavior

- 先运行 `scripts/resume_pdf.py extract`。
- 保留旧 PDF 的已嵌链接。
- 用 profile 承接导入结果。
- 运行 JD 三档匹配：已覆盖 / 有但没突出 / 真没有。
- 只把用户真实具备但没突出的关键词 surface 到 Summary、Skills 或相关经历。
- 定稿 PDF 后运行 `scripts/ats_check.py`。

## Must Not

- 不把 JD 中真没有的 Kubernetes、CI/CD 等词硬塞进技能栏。
- 不覆盖源简历文件。

