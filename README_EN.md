[中文](./README.md)

![resume-tuning](./assets/banner.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Skill](https://img.shields.io/badge/type-Skill-orange.svg)

Two things always annoyed me about resumes. One: fighting a template to fit one page, then exporting and still getting two. Two: turning X, GitHub and project links into things you can actually click, by hand, missing one every time.

resume-tuning takes care of both. Hand it an old resume, or just talk through a few experiences. It asks you some questions, generates a few layouts to choose from, and gives you a typeset, one-page **PDF** with working links.

It's a Claude Code skill, and it works for anyone — engineering, product, design, marketing, students.

## How it works

It doesn't generate in one shot. It goes a few rounds with you:

1. Figure out what you have. If there's an old resume, it reads it — including the hyperlinks already embedded inside. If you only have scattered notes, it asks for them.
2. Ask a few personalization questions: target role, what to lead with, Chinese or English, whether to include a portfolio or open-source section.
3. Run the content against the good-resume standards: quantify what should be quantified, cut the fluff, fix typos and term casing (`DevOps`, `Kubernetes`).
4. Fill the same content into three layouts — classic, minimal, modern — as drafts for you to pick from.
5. Polish the chosen one to exactly one page, make X / GitHub / site / projects / blog clickable, and export the PDF.

It won't invent missing data; it flags gaps for you to fill.

## Three layouts

| Layout | Look | Who it fits |
|---|---|---|
| **classic** | Blue section tags, steady and general | Most people, technical roles |
| **minimal** | Serif, thin rules, lots of whitespace | Senior, management, academic |
| **modern** | Colored header card, eye-catching | Product, design, marketing |

Same content, different CSS. Switch freely without losing anything.

## Install

Drop the folder into your agent's skills directory, e.g. `~/.claude/skills/`:

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git resume-tuning
```

Rendering uses WeasyPrint. Install the dependencies once:

```bash
brew install pango gdk-pixbuf libffi
python3 -m venv ~/.venv && ~/.venv/bin/pip install weasyprint pypdf
```

## Usage

Just tell your AI assistant:

- "Make me a resume, I'll talk through my experience."
- "Optimize my old resume and export a PDF."
- "Turn my resume into English."
- "Lay it out, I'm about to send it."

## Layout

```
resume-tuning/
├── SKILL.md                       interactive workflow
├── references/
│   └── resume-standards.md        good-resume standards + proofreading checklist
├── assets/
│   ├── banner.svg
│   └── templates/                 classic / minimal / modern
└── examples/
    └── before-after-example.md    one entry, before and after
```

## Where the standards come from

`references/resume-standards.md` is distilled from real job-hunting practice: a resume is sales copy with a 10-second lifespan — one page, one line per point, strongest point first, numbers over adjectives, no bare skill lists, claims backed by evidence, hooks that make the interviewer ask, honesty, and a self-summary that says where you came from, where you are, and where you're headed. Plus a proofreading checklist built from repeated mistakes.

## License

[MIT](./LICENSE)
