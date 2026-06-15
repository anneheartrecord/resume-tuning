[English](./README_EN.md)

![resume-tuning](./assets/banner.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

| classic | modern | minimal |
|---|---|---|
| ![Sam Altman](./assets/demos/altman-classic.png) | ![Jony Ive](./assets/demos/ive-modern.png) | ![Andrew Ng](./assets/demos/ng-minimal.png) |

> 公开人物公开资料编的示意样张（非本人真迹），各套一种版式。排版参考 [tw93/Kami](https://github.com/tw93/Kami)。

resume-tuning 是一个交互式简历生成 skill。给它一份旧简历，或者只口述几段经历，跟你来回几轮，交付一份**链接能点、刚好一页的 PDF**——classic / minimal / modern 三种版式随便切，不挑岗位。

内容会按好简历的标准过一遍：该量化的量化、空话删掉、最亮点前置、错别字校掉；缺的数据不替你编，标出来让你补。

改写前 → 改写后：

> 负责服务端开发，提升了系统性能。
> → 主导核心交易接口优化，多级缓存 + 异步解耦，P99 从 800ms 降到 120ms，QPS 提升 5 倍。

## 用它

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git ~/.claude/skills/resume-tuning
brew install pango gdk-pixbuf libffi
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
bash resume-tuning/scripts/ensure-fonts.sh   # 做中文简历前跑一次，自动拉 OFL 字体
```

然后跟 AI 助手说「帮我做份简历」「把这份旧简历优化导出 PDF」「转成英文版」就行。
凡是标了 `[DATA NEEDED]` 的地方，补真实数字再定稿——别让它编，面试一问就穿帮。

## references

判断标准在 [`references/resume-standards.md`](./references/resume-standards.md) 和 [`resume-writing.md`](./references/resume-writing.md)：简历是份只活 10 秒的销售文案，一页、用数字说话、空话带论据、实事求是；配套一份字数/强调密度硬指标和错别字校对清单。

## License

[MIT](./LICENSE)
