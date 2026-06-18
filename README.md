[English](./README_EN.md)

![resume-tuning](./assets/banner.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

| Backend · classic | Product · modern | Research · minimal |
|---|---|---|
| ![Backend platform engineer resume demo](./assets/demos/backend-classic.png) | ![AI product manager resume demo](./assets/demos/product-modern.png) | ![Applied ML research resume demo](./assets/demos/research-minimal.png) |
| Growth · modern | Operations · classic | New grad · minimal |
| ![增长营销负责人简历样张](./assets/demos/growth-modern.png) | ![运营策略经理简历样张](./assets/demos/operations-classic.png) | ![New grad data analyst resume demo](./assets/demos/newgrad-minimal.png) |

> 合成候选人示意样张，非真实简历；覆盖技术、产品、研究、增长、运营、学生 6 类场景。排版参考 [tw93/Kami](https://github.com/tw93/Kami)，样张可用 `python3 scripts/generate_demo_resumes.py` 重新生成。

resume-tuning 是一个交互式简历生成 skill。给它一份旧简历，或者只口述几段经历，跟你来回几轮，交付一份**链接能点、刚好一页的 PDF**——classic / minimal / modern 三种版式随便切，不挑岗位。

内容会按好简历的标准过一遍：该量化的量化、空话删掉、最亮点前置、错别字校掉；缺的数据不替你编，标出来让你补。

给一段目标 JD，它会对照标出缺的关键词、把你真有但没突出的经历用招聘方的语言改写到显眼处，并在定稿前做一遍 ATS 可读性自检（文本层、标准章节、联系方式、关键词覆盖率）。它只 surface 你真有的，**绝不替你堆砌虚假关键词**——背调和面试一问就穿帮。

内部流程现在用结构化 profile 做中间层：先把旧 PDF / 图片 / 文本转成可校验 JSON，再做 JD 三档匹配、内容 lint、多版式预览和最终 PDF 渲染。这样同一份内容可以稳定切版式，也能为不同 JD 生成诚实 variant。

改写前 → 改写后：

> 负责服务端开发，提升了系统性能。
> → 主导核心交易接口优化，多级缓存 + 异步解耦，P99 从 800ms 降到 120ms，QPS 提升 5 倍。

## 用它

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git ~/.claude/skills/resume-tuning
brew install pango gdk-pixbuf libffi
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
# 可选：装 rapidfuzz 让 ATS 自检支持关键词词形模糊匹配（不装则降级精确匹配）
# ~/.venv/bin/pip install rapidfuzz
bash resume-tuning/scripts/ensure-fonts.sh   # 做中文简历前跑一次，自动拉 OFL 字体
```

然后跟 AI 助手说「帮我做份简历」「把这份旧简历优化导出 PDF」「转成英文版」就行。
凡是标了 `[DATA NEEDED]` 的地方，补真实数字再定稿——别让它编，面试一问就穿帮。

## 工具链

```bash
python3 scripts/resume_pdf.py extract old.pdf
python3 scripts/resume_profile.py validate examples/profile-example.json
python3 scripts/jd_match.py examples/profile-example.json --jd examples/jd-sample.txt
python3 scripts/resume_lint.py examples/profile-example.json --mode draft
python3 scripts/ats_check.py final.pdf --name "候选人" --keywords "Go,Kubernetes,Redis"
```

模板说明在 [`assets/templates/templates.json`](./assets/templates/templates.json)。`preview` 会把每个版式的适用场景、ATS 稳健度、PDF/PNG 路径和链接检查一起打印出来。

## 测试

```bash
python3 scripts/tests/test_skill_structure.py
python3 scripts/tests/test_resume_profile.py
python3 scripts/tests/test_jd_match.py
python3 scripts/tests/test_resume_lint.py
python3 scripts/tests/test_eval_cases.py
python3 scripts/tests/test_ats_check.py
python3 scripts/tests/test_render.py
```

## references

任务流程在 [`references/intake.md`](./references/intake.md)、[`tailor-to-jd.md`](./references/tailor-to-jd.md)、[`render-and-deliver.md`](./references/render-and-deliver.md)、[`review-only.md`](./references/review-only.md)。结构化 profile 见 [`resume-schema.md`](./references/resume-schema.md)。判断标准在 [`resume-standards.md`](./references/resume-standards.md)、[`resume-writing.md`](./references/resume-writing.md) 和 [`ats-and-jd.md`](./references/ats-and-jd.md)。

## License

[MIT](./LICENSE)
