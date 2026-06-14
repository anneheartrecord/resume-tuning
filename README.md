[English](./README_EN.md)

# resume-tuning

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

一个面向技术人员的 skill，用来诊断和优化简历。

## 这个 skill 解决什么问题

面试官看一份简历平均只花 10 秒。简历不是个人信息登记表，而是一份只有 10 秒生命的销售文案。这个 skill 把「什么是好简历」拆成可执行的标准，逐条扫你的简历，然后给反馈。

它专门面向技术岗（工程师、AI / 云原生 / 后端 / 全栈等），默认带这些偏好：GitHub / 开源作品接近刚需、技能用项目经历证明、专有名词大小写要规范、量化用技术指标。

## 它会做什么

- **错别字 + 一致性校对**：专有名词大小写、分隔符、多字漏字、同一份内两种写法、数字格式。
- **结构与内容诊断**：是否一页、最亮点是否前置、时间线是否最新、每段经历是否量化（STAR）、自我评价是否带论据、技能是否用项目证明、有没有埋钩子、措辞是否夸大。
- **分档反馈**：必须改 / 强烈建议改 / 可选，每条都给理由，默认用文本说，不擅自改你的文件。

## 工作流程

```
简历 ──► Step 0 读判断标准（references/resume-standards.md）
       │
       ▼
       Step 1 拿到简历本体
       │
       ▼
       Step 2 拆模块 + 确认最想突出的优势
       │
       ▼
       Step 3 错别字 / 一致性校对
       │
       ▼
       Step 4 按好简历标准逐条优化
       │
       ▼
       Step 5 分档文本反馈（必改 / 建议改 / 可选）
```

## 安装

把整个目录放到你的 AI agent 的 skills 目录下（例如 `~/.claude/skills/`）：

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git resume-tuning
```

## 使用

对你的 AI 助手说：

- 「看下我的简历，有哪些可以优化」
- 「帮我把 XX 这段经历加进简历」
- 「这版简历还有什么问题 / 帮我校对一下错别字」

## 文件结构

```
resume-tuning/
├── SKILL.md                          # 流程定义
├── references/
│   └── resume-standards.md           # 好简历标准 + 坏简历问题 + 校对清单
└── examples/
    └── before-after-example.md       # 一段经历改写前后对照
```

## 判断标准来自哪里

`references/resume-standards.md` 提炼自一套求职实战心得：简历的本质（10 秒销售文案）、9 条核心标准（一页、一行一句、最亮点前置、量化 STAR、不堆技能列表、要论据、埋钩子、实事求是、个人总结写过去 / 现在 / 未来），以及一份反复踩坑总结出来的错别字校对清单。

## License

[MIT](./LICENSE)
