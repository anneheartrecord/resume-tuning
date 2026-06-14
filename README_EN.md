[中文](./README.md)

# resume-tuning

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Markdown-lightgrey.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-orange.svg)

A Claude Code skill for technical people to diagnose and optimize their resumes.

## What it solves

A recruiter spends about 10 seconds on a resume. A resume is not a personal-information form — it is a piece of sales copy with a 10-second lifespan. This skill turns "what makes a good resume" into actionable standards, scans your resume against them, and gives feedback.

It targets technical roles (engineers, AI / cloud-native / backend / full-stack) and assumes those preferences: GitHub / open-source work is close to mandatory, skills are proven through projects, technical terms must be cased correctly, and results are quantified with technical metrics.

## What it does

- **Typo & consistency check**: term capitalization, separators, missing/extra characters, two spellings of the same word in one document, number formatting.
- **Structure & content diagnosis**: one page or not, strongest point up front, timeline current, every entry quantified (STAR), self-summary backed by evidence, skills proven by projects, hooks planted, no overstatement.
- **Tiered feedback**: must-fix / strongly-recommended / optional, each with a reason. Text feedback by default — it does not edit your files unprompted.

## Workflow

```
Resume ──► Step 0 Read the standards (references/resume-standards.md)
        │
        ▼
        Step 1 Get the actual resume
        │
        ▼
        Step 2 Break into sections + confirm the top strength to highlight
        │
        ▼
        Step 3 Typo / consistency check
        │
        ▼
        Step 4 Optimize against the good-resume standards
        │
        ▼
        Step 5 Tiered text feedback (must-fix / recommended / optional)
```

## Install

Drop the whole directory into Claude Code's skills folder:

```bash
git clone https://github.com/anneheartrecord/resume-tuning.git ~/.claude/skills/resume-tuning
```

## Usage

Tell Claude Code:

- "Review my resume and tell me what to improve."
- "Add this experience to my resume."
- "What's still wrong with this version / proofread it."

## File layout

```
resume-tuning/
├── SKILL.md                          # Workflow definition
├── references/
│   └── resume-standards.md           # Good-resume standards + bad-resume issues + checklist
└── examples/
    └── before-after-example.md       # One entry, before and after
```

## Where the standards come from

`references/resume-standards.md` distills a set of job-hunting lessons: the nature of a resume (10-second sales copy), 9 core standards (one page, one line per point, strongest point first, quantify with STAR, no bare skill lists, back claims with evidence, plant hooks, stay honest, write the self-summary as past / present / future), and a proofreading checklist built from repeated mistakes.

## License

[MIT](./LICENSE)
