[中文](./README.md)

![resume-tuning](./assets/banner.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

| classic | modern | minimal |
|---|---|---|
| ![Sam Altman](./assets/demos/altman-classic.png) | ![Jony Ive](./assets/demos/ive-modern.png) | ![Andrew Ng](./assets/demos/ng-minimal.png) |

> Illustrative samples built from public figures' public bios (not their real resumes), one layout each. Typography inspired by [tw93/Kami](https://github.com/tw93/Kami).

resume-tuning is an interactive resume-building skill. Give it an old resume, or just talk through a few experiences — it goes a few rounds with you and delivers a **one-page PDF with clickable links**. Three layouts (classic / minimal / modern), any role.

It runs the content against good-resume standards: quantify what matters, cut the fluff, strongest point first, fix typos. Missing data is never invented — it's flagged for you to fill.

Before → after:

> Responsible for server-side development, improved system performance.
> → Led optimization of the core transaction API; multi-level cache + async decoupling cut P99 from 800ms to 120ms, lifted QPS 5x.

## Use it

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git ~/.claude/skills/resume-tuning
brew install pango gdk-pixbuf libffi
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
bash resume-tuning/scripts/ensure-fonts.sh   # run once before CJK resumes; auto-fetches an OFL font
```

Then tell your AI assistant "make me a resume" / "optimize this old resume into a PDF" / "translate it to English".
Wherever it leaves `[DATA NEEDED]`, fill in real numbers before finalizing — don't let it guess.

## references

Standards live in [`references/resume-standards.md`](./references/resume-standards.md) and [`resume-writing.md`](./references/resume-writing.md): a resume is sales copy with a 10-second lifespan — one page, numbers over adjectives, claims backed by evidence, honesty; plus hard limits on length/emphasis density and a proofreading checklist.

## License

[MIT](./LICENSE)
