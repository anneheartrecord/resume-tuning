[English](./README_EN.md)

![resume-tuning](./assets/banner.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

我自己投简历的时候最烦两件事。一件是对着模板抠字号想塞进一页，结果一导出还是两页。另一件是想把 X、GitHub 这些做成点一下就能跳的链接，手动搞半天还老是漏掉一个。

resume-tuning 就是来干掉这两件事的。你丢给它一份旧简历，或者干脆只口述几段经历，它问你几个问题，生成几种版式让你挑，最后给你一份排好版、链接能点、刚好一页的 **PDF**。

它是个 Claude Code skill，谁都能用，不挑岗位。技术、产品、设计、运营、还在读书的，都行。

## 它怎么干活

不是一把梭生成完就拉倒，是跟你来回几轮：

1. 先搞清楚你手里有什么。有旧简历就读出来，连里面已经埋好的超链接一起扒下来；只有零散内容就问你要。
2. 问几个个性化的问题：投什么岗、最想突出哪一点、中文还是英文、要不要放作品集或者开源。
3. 把内容按好简历的标准过一遍，该量化的量化，空话删掉，顺手把错别字和 `DevOps`、`Kubernetes` 这种专有名词的大小写也校了。
4. 同一份内容套出 classic、minimal、modern 三种版式的初稿，你看着挑一个。
5. 选中的那版精修到刚好一页，X、GitHub、个人站、项目、博客全做成可点链接，导出 PDF。

缺的数据它不会替你编，会标出来让你自己补。

## 三种版式

| 版式 | 长相 | 谁适合 |
|---|---|---|
| **classic** | 蓝色栏目标题，稳重通用 | 大多数人，技术岗 |
| **minimal** | 衬线、细线分栏、留白多 | 资深、管理、学术，想低调一点 |
| **modern** | 彩色页眉卡片，跳眼 | 产品、设计、市场，想从一堆白底简历里冒出来 |

三套是同一份内容套不同 CSS，随便切，内容不丢。

## 安装

把整个目录丢进你 agent 的 skills 目录，比如 `~/.claude/skills/`：

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git resume-tuning
```

渲染 PDF 用的是 WeasyPrint，第一次跑之前装一下依赖：

```bash
brew install pango gdk-pixbuf libffi
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
```

## 用它

跟你的 AI 助手说一句就行：

- 帮我做一份简历，我口述经历给你
- 把我这份旧简历优化一下，导出 PDF
- 简历帮我转成英文版
- 帮我排个版，我准备发出去

## 目录结构

```
resume-tuning/
├── SKILL.md                       交互流程
├── references/
│   └── resume-standards.md        好简历的判断标准 + 错别字校对清单
├── assets/
│   ├── banner.svg
│   └── templates/                 classic / minimal / modern 三套版式
└── examples/
    └── before-after-example.md    一段经历改写前后对照
```

## 判断标准哪来的

`references/resume-standards.md` 是从一套求职实战里攒出来的：简历本质上是份只活 10 秒的销售文案，一页、一行一句、最亮点前置、用数字说话、别堆技能列表、空话要带论据、埋钩子让面试官来问、实事求是、自我评价写清楚你从哪来现在在哪想去哪。还有一份反复踩坑攒下来的错别字清单。

## License

[MIT](./LICENSE)
