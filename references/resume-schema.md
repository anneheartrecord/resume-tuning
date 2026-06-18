# Resume Profile Schema

Profile 是 resume-tuning 的结构化中间数据。它用于导入、JD 定制、内容 lint 和模板填充；最终交付仍是 PDF。

## Top-Level Shape

```json
{
  "schema_version": "1.0",
  "language": "zh",
  "target": {
    "role": "Backend Engineer",
    "industry": "AI tooling",
    "identity": "experienced",
    "privacy_mode": "private"
  },
  "header": {
    "name": "张三",
    "headline": "后端开发工程师",
    "location": "北京",
    "email": "a@example.com",
    "phone": "+86 ...",
    "links": [{"label": "GitHub", "url": "https://github.com/example"}]
  },
  "summary": [{"label": "后端", "text": "用事实证明的一句话"}],
  "sections": [],
  "skills": [],
  "data_needed": []
}
```

## Required Fields

- `schema_version`: string，当前为 `"1.0"`。
- `language`: `"zh"` 或 `"en"`。
- `target.role`: 本次目标岗位。
- `target.identity`: `experienced`、`student`、`academic`、`career_switcher` 之一。
- `target.privacy_mode`: `private`、`public`、`recruiter` 之一。
- `header.name`: 姓名。
- `sections`: section 数组，可为空但会触发 warning。

## Section Shape

`sections[]` 每项：

```json
{
  "type": "experience",
  "title": "工作经历",
  "items": [
    {
      "name": "Acme",
      "role": "Backend Intern",
      "date": "2024.06 - 2024.09",
      "location": "Shanghai",
      "links": [{"label": "Project", "url": "https://example.com"}],
      "bullets": ["负责 ...，带来 [DATA NEEDED: 延迟下降幅度]"]
    }
  ]
}
```

允许的 `type`：

- `experience`
- `project`
- `education`
- `research`
- `publication`
- `award`
- `certificate`
- `open_source`
- `portfolio`
- `custom`

## Skills Shape

`skills[]` 每项：

```json
{"label": "Backend", "items": ["Go", "PostgreSQL", "Redis"]}
```

技能只放用户真实具备的内容。JD 缺口不要写进 skills。

## Data Needed Shape

`data_needed[]` 每项：

```json
{
  "path": "sections[1].items[0].bullets[2]",
  "question": "这个优化让 P99 从多少降到多少？",
  "reason": "结果缺量化，无法形成 STAR"
}
```

## Validation Rules

- 未知 top-level 字段是 error。
- 必填字段缺失是 error。
- email 格式明显错误是 warning。
- public privacy mode 下存在 phone 是 warning。
- `sections` 为空是 warning。
- bullet 含 `[DATA NEEDED` 在 draft 是 warning，在 final 是 error。
- 链接必须是 `http://`、`https://` 或 `mailto:`。
- 不要写空字符串；未知信息直接省略字段或写入 `data_needed`。

