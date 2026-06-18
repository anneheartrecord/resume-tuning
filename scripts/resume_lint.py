#!/usr/bin/env python3
"""resume-tuning 内容质量 lint。

脚本把写作标准中最容易遗漏的硬伤变成 warnings/errors：缺结果、空洞形容词、
过长 bullet、技能墙、过度高亮、定稿残留 [DATA NEEDED]。它只报告问题，不改文案。
"""

import argparse
import json
import os
import re
import sys
from typing import Any

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import resume_profile  # noqa: E402

VAGUE_PHRASES = (
    "责任心强",
    "自驱力强",
    "学习能力强",
    "沟通能力强",
    "团队协作",
    "显著提升",
    "大幅提升",
    "效果良好",
    "various",
    "significant",
    "responsible for",
    "good communication",
)
RESULT_HINT_RE = re.compile(
    r"(\d+[%x倍+]?|\d+\s?(ms|s|qps|dau|mau|万|人|次|元|美元|hours?)|提升|降低|减少|增长|支撑|节省|cut|reduced|increased|improved|saved)",
    re.IGNORECASE,
)
HL_RE = re.compile(r"<span\s+class=[\"']hl[\"']", re.IGNORECASE)


def _iter_bullets(profile: dict[str, Any]) -> list[tuple[str, str]]:
    """返回 (path, bullet) 列表。"""
    bullets: list[tuple[str, str]] = []
    for section_index, section in enumerate(profile.get("sections", [])):
        for item_index, item in enumerate(section.get("items", [])):
            for bullet_index, bullet in enumerate(item.get("bullets", []) or []):
                if isinstance(bullet, str):
                    path = f"sections[{section_index}].items[{item_index}].bullets[{bullet_index}]"
                    bullets.append((path, bullet))
    return bullets


def _iter_summary(profile: dict[str, Any]) -> list[tuple[str, str]]:
    """返回 summary 文本。"""
    result: list[tuple[str, str]] = []
    for index, item in enumerate(profile.get("summary", []) or []):
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            result.append((f"summary[{index}].text", item["text"]))
    return result


def _add_issue(issues: list[dict[str, str]], severity: str, path: str, message: str) -> None:
    """追加一条 lint issue。"""
    issues.append({"severity": severity, "path": path, "message": message})


def lint_profile(profile: dict[str, Any], *, mode: str = "draft") -> list[dict[str, str]]:
    """返回内容质量 issues。"""
    issues: list[dict[str, str]] = []
    final = mode == "final"

    for path, text in [*_iter_summary(profile), *_iter_bullets(profile)]:
        lower_text = text.lower()
        if "[DATA NEEDED" in text:
            _add_issue(
                issues,
                "error" if final else "warning",
                path,
                "contains [DATA NEEDED]; ask user for real data before final delivery",
            )
        if any(phrase in lower_text for phrase in VAGUE_PHRASES):
            _add_issue(issues, "warning", path, "contains vague claim; back it with evidence or remove it")
        if len(text) > 140:
            _add_issue(issues, "warning", path, "bullet/summary is long; tighten to one scan-friendly sentence")

    for path, bullet in _iter_bullets(profile):
        if not RESULT_HINT_RE.search(bullet):
            _add_issue(issues, "warning", path, "bullet lacks clear result, scale, or quantified impact")
        hl_count = len(HL_RE.findall(bullet))
        if hl_count > 1:
            _add_issue(issues, "warning", path, "too many .hl highlights in one bullet")

    for index, skill in enumerate(profile.get("skills", []) or []):
        items = skill.get("items", []) if isinstance(skill, dict) else []
        if isinstance(items, list) and len(items) > 8:
            _add_issue(issues, "warning", f"skills[{index}].items", "skill row is too long; group or trim it")

    identity = (profile.get("target") or {}).get("identity")
    section_types = [section.get("type") for section in profile.get("sections", []) if isinstance(section, dict)]
    if identity == "student" and "education" in section_types:
        first_material = next((section_type for section_type in section_types if section_type != "custom"), None)
        if first_material != "education":
            _add_issue(issues, "warning", "sections", "student profile should usually put education before experience")

    return issues


def print_issues(issues: list[dict[str, str]]) -> None:
    """打印 lint 结果。"""
    if not issues:
        print("Resume lint passed.")
        return
    for issue in issues:
        print(f"{issue['severity'].upper()} {issue['path']}: {issue['message']}")


def main(argv: list[str]) -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="Lint resume profile content quality.")
    parser.add_argument("profile")
    parser.add_argument("--mode", choices=("draft", "final"), default="draft")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv[1:])

    if not os.path.exists(args.profile):
        print(f"找不到 profile：{args.profile}", file=sys.stderr)
        return 2
    profile = resume_profile.load_profile(args.profile)
    validation = resume_profile.validate_profile(profile, final=args.mode == "final")
    issues = lint_profile(profile, mode=args.mode)
    if args.json:
        print(json.dumps({"validation": validation, "issues": issues}, ensure_ascii=False, indent=2))
    else:
        resume_profile.print_report(validation)
        print_issues(issues)
    has_errors = validation["errors"] or any(issue["severity"] == "error" for issue in issues)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
