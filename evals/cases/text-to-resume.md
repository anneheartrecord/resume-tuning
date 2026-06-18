# text-to-resume

## Input

用户只口述经历：

- 目标岗位：后端开发工程师
- 经历：做过一个 Go + Redis 的任务调度系统，主要负责接口、任务状态流转、失败重试
- 教育：计算机本科
- 链接：GitHub 和个人博客

## Expected Behavior

- 先追问目标行业、语言、最想突出的优势和缺失量化数据。
- 生成 profile draft，而不是直接写 HTML。
- 把任务调度经历拆成项目经历，按 STAR 改写。
- 缺数字处标 `[DATA NEEDED: ...]`。
- 最终需要生成 2-3 个版式预览，用户选择后再渲染 PDF。

## Must Not

- 不编造 QPS、延迟、用户数、公司或职位。
- 不把 GitHub 链接写成不可点击纯文本。

