# Tailor to JD

按目标 JD 定制简历时，只改写和前置用户真实具备的能力。目标是让真实亮点用招聘方语言被看见，不是提高分数而堆砌关键词。

## Required Reading

- `references/ats-and-jd.md`
- `references/resume-schema.md`
- `references/resume-writing.md`

## Procedure

1. **读取 JD。**
   - 如果用户给 URL，能访问就抓取正文；不能访问就让用户粘贴 JD。
   - 抽取 required skills、nice-to-have、职责、资历、行业域、seniority。

2. **生成关键词事实报告。**
   - 优先让 agent 抽好关键词，再运行：
     `python3 scripts/jd_match.py <profile.json> --keywords "Kubernetes,Go,Redis"`
   - 只有 JD 原文时可运行：
     `python3 scripts/jd_match.py <profile.json> --jd jd.txt`
   - PDF 定稿后再用 `scripts/ats_check.py` 检查最终文本层覆盖率。

3. **三档处理。**
   - ✅ 已覆盖：简历已有明确证据，不动或轻微前置。
   - 🟡 有但没突出：用户真实具备，但措辞没用 JD 词、埋太深或没放在显眼位置。允许改写 surface。
   - 🔴 真没有：不要写进简历。列为缺口，追问是否有被漏写的真实经历。

4. **改写顺序。**
   - Summary 第一条先对齐目标岗位最强证据。
   - Skills 内部排序把 JD required 且真实具备的词放前面。
   - Experience / Projects 的首 bullet 优先写 JD 最关心的职责。
   - 删除与本 JD 无关、挤占重点篇幅的弱 bullet。

5. **保持真实性。**
   - 参与不能写成主导。
   - 使用过不能写成精通。
   - 没有数字就用 `[DATA NEEDED: ...]` 追问，不能编造。
   - 模糊同义词需保守处理；K8s/Kubernetes 可视作别名，React/Preact 不能互相替代。

## Output Summary

给用户反馈时说明：

- surface 了哪些 🟡 关键词。
- 哪些 required 仍是 🔴 真实缺口。
- 哪些 bullet 被前置、改写或删除。
- ATS 检查的覆盖率只是事实信号，不代表可以伪造能力。
