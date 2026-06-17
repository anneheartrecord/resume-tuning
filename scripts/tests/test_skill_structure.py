#!/usr/bin/env python3
"""resume-tuning skill 结构测试。"""

import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILL_PATH = os.path.join(SKILL_DIR, "SKILL.md")
REQUIRED_REFERENCES = [
    "references/intake.md",
    "references/tailor-to-jd.md",
    "references/render-and-deliver.md",
    "references/review-only.md",
    "references/resume-schema.md",
    "references/resume-standards.md",
    "references/resume-writing.md",
    "references/ats-and-jd.md",
]
REQUIRED_SCRIPTS = [
    "scripts/resume_pdf.py",
    "scripts/ats_check.py",
    "scripts/resume_profile.py",
    "scripts/jd_match.py",
    "scripts/resume_lint.py",
]


def _frontmatter(text: str) -> dict[str, str]:
    """解析最简单的 YAML frontmatter 键值。"""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def run() -> int:
    failures: list[str] = []
    text = open(SKILL_PATH, encoding="utf-8").read()
    frontmatter = _frontmatter(text)
    if set(frontmatter) != {"name", "description"}:
        failures.append(f"frontmatter 只能包含 name/description，实际 {sorted(frontmatter)}")
    if frontmatter.get("name") != "resume-tuning":
        failures.append("frontmatter.name 必须是 resume-tuning")
    if len(text.splitlines()) > 120:
        failures.append("SKILL.md 超过 120 行，入口开始膨胀，应拆到 references")
    for relative_path in REQUIRED_REFERENCES + REQUIRED_SCRIPTS:
        if not os.path.exists(os.path.join(SKILL_DIR, relative_path)):
            failures.append(f"缺少 {relative_path}")
        if relative_path not in text:
            failures.append(f"SKILL.md 未引用 {relative_path}")
    openai_yaml = os.path.join(SKILL_DIR, "agents", "openai.yaml")
    if not os.path.exists(openai_yaml):
        failures.append("缺少 agents/openai.yaml")
    else:
        yaml_text = open(openai_yaml, encoding="utf-8").read()
        if "$resume-tuning" not in yaml_text:
            failures.append("agents/openai.yaml default_prompt 必须提到 $resume-tuning")
    if re.search(r"version:\s|metadata:", text):
        failures.append("SKILL.md frontmatter 不应保留 version/metadata")
    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
