#!/usr/bin/env python3
"""resume-tuning 的 JD 三档匹配工具。

脚本只根据 profile 文本与关键词给出候选分档：
  covered      简历文本已明确命中。
  surface      可能真实具备但没用 JD 原词，需要 agent/用户确认后改写。
  gap          没找到证据，不能写进简历。

surface 的判定只使用保守别名表，避免把无关技能误判为可补。
"""

import argparse
import json
import os
import sys
from typing import Any

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import ats_check  # noqa: E402
import resume_profile  # noqa: E402


ALIASES: dict[str, list[str]] = {
    "kubernetes": ["k8s", "容器编排"],
    "k8s": ["kubernetes", "容器编排"],
    "postgresql": ["postgres", "pgsql"],
    "postgres": ["postgresql", "pgsql"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "node.js": ["nodejs", "node"],
    "react": ["react.js", "reactjs"],
    "machine learning": ["ml", "机器学习"],
    "large language model": ["llm", "大语言模型"],
    "llm": ["large language model", "大语言模型"],
    "ci/cd": ["cicd", "持续集成", "持续交付"],
}


def _walk_strings(value: Any) -> list[str]:
    """递归提取 JSON 中所有字符串，用于关键词匹配。"""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_walk_strings(item))
        return strings
    return []


def profile_text(profile: dict[str, Any]) -> str:
    """把 profile 中可搜索的真实内容合并为文本。"""
    return "\n".join(_walk_strings(profile))


def classify_keywords(profile: dict[str, Any], keywords: list[str]) -> dict[str, list[dict[str, str]]]:
    """按 covered / surface / gap 给关键词分档。"""
    text = profile_text(profile)
    normalized = ats_check._normalize(text)
    result: dict[str, list[dict[str, str]]] = {"covered": [], "surface": [], "gap": []}
    for keyword in [item.strip() for item in keywords if item.strip()]:
        if ats_check.contains_term(normalized, keyword):
            result["covered"].append({"keyword": keyword, "reason": "profile contains exact term"})
            continue
        alias_hit = ""
        for alias in ALIASES.get(keyword.lower(), []):
            if ats_check.contains_term(normalized, alias):
                alias_hit = alias
                break
        if alias_hit:
            result["surface"].append({
                "keyword": keyword,
                "reason": f"profile contains alias '{alias_hit}', confirm truth before rewriting",
            })
        else:
            result["gap"].append({"keyword": keyword, "reason": "no evidence found in profile"})
    return result


def _keywords_from_args(args: argparse.Namespace) -> list[str]:
    """从 --keywords 或 --jd 中获取关键词。"""
    if args.keywords:
        return [item.strip() for item in args.keywords.split(",") if item.strip()]
    if args.jd:
        with open(args.jd, encoding="utf-8") as jd_file:
            return ats_check.keywords_from_jd(jd_file.read())
    return []


def print_report(report: dict[str, list[dict[str, str]]]) -> None:
    """打印三档匹配报告。"""
    labels = {"covered": "✅ 已覆盖", "surface": "🟡 有但没突出", "gap": "🔴 真没有证据"}
    for key in ("covered", "surface", "gap"):
        print(f"[{labels[key]}] {len(report[key])}")
        for item in report[key]:
            print(f"  - {item['keyword']}: {item['reason']}")


def main(argv: list[str]) -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="Classify JD keywords against a resume profile.")
    parser.add_argument("profile")
    parser.add_argument("--keywords", help="comma-separated keywords extracted by agent")
    parser.add_argument("--jd", help="JD text file; heuristic keyword extraction")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv[1:])

    if not os.path.exists(args.profile):
        print(f"找不到 profile：{args.profile}", file=sys.stderr)
        return 2
    if args.jd and not os.path.exists(args.jd):
        print(f"找不到 JD 文件：{args.jd}", file=sys.stderr)
        return 2
    keywords = _keywords_from_args(args)
    if not keywords:
        print("必须提供 --keywords 或 --jd", file=sys.stderr)
        return 2

    profile = resume_profile.load_profile(args.profile)
    validation = resume_profile.validate_profile(profile)
    if validation["errors"]:
        resume_profile.print_report(validation)
        return 2
    report = classify_keywords(profile, keywords)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
