#!/usr/bin/env python3
"""resume-tuning 结构化 profile 校验工具。

Profile 是导入、JD 定制、内容 lint 和模板填充之间的中间数据。这个脚本只做确定性
结构校验：字段是否存在、枚举是否有效、链接和隐私 warning 是否明显。它不改写简历。
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALLOWED_TOP_LEVEL = {
    "schema_version",
    "language",
    "target",
    "header",
    "summary",
    "sections",
    "skills",
    "data_needed",
}
ALLOWED_IDENTITIES = {"experienced", "student", "academic", "career_switcher"}
ALLOWED_PRIVACY_MODES = {"private", "public", "recruiter"}
ALLOWED_LANGUAGES = {"zh", "en"}
ALLOWED_SECTION_TYPES = {
    "experience",
    "project",
    "education",
    "research",
    "publication",
    "award",
    "certificate",
    "open_source",
    "portfolio",
    "custom",
}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
VALID_URL_PREFIXES = ("http://", "https://", "mailto:")


def _is_non_empty_string(value: Any) -> bool:
    """判断 value 是否是去空白后非空的字符串。"""
    return isinstance(value, str) and bool(value.strip())


def _validate_links(links: Any, path: str, errors: list[str], warnings: list[str]) -> None:
    """校验 links 数组中 label/url 的形态。"""
    if links is None:
        return
    if not isinstance(links, list):
        errors.append(f"{path}: links must be a list")
        return
    for index, link in enumerate(links):
        item_path = f"{path}[{index}]"
        if not isinstance(link, dict):
            errors.append(f"{item_path}: link must be an object")
            continue
        if not _is_non_empty_string(link.get("label")):
            warnings.append(f"{item_path}.label: missing readable label")
        url = link.get("url")
        if not _is_non_empty_string(url):
            errors.append(f"{item_path}.url: missing url")
        elif not str(url).startswith(VALID_URL_PREFIXES):
            errors.append(f"{item_path}.url: must start with http://, https://, or mailto:")


def _validate_target(profile: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    """校验 target 字段。"""
    target = profile.get("target")
    if not isinstance(target, dict):
        errors.append("target: required object")
        return
    if not _is_non_empty_string(target.get("role")):
        errors.append("target.role: required non-empty string")
    identity = target.get("identity")
    if identity not in ALLOWED_IDENTITIES:
        errors.append(f"target.identity: must be one of {sorted(ALLOWED_IDENTITIES)}")
    privacy_mode = target.get("privacy_mode")
    if privacy_mode not in ALLOWED_PRIVACY_MODES:
        errors.append(f"target.privacy_mode: must be one of {sorted(ALLOWED_PRIVACY_MODES)}")
    if privacy_mode == "public":
        phone = (profile.get("header") or {}).get("phone") if isinstance(profile.get("header"), dict) else None
        if _is_non_empty_string(phone):
            warnings.append("header.phone: public privacy mode should confirm whether phone is hidden")
    if not _is_non_empty_string(target.get("industry")):
        warnings.append("target.industry: missing industry context")


def _validate_header(profile: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    """校验 header 字段。"""
    header = profile.get("header")
    if not isinstance(header, dict):
        errors.append("header: required object")
        return
    if not _is_non_empty_string(header.get("name")):
        errors.append("header.name: required non-empty string")
    email = header.get("email")
    if email is not None and (not _is_non_empty_string(email) or not EMAIL_RE.match(str(email))):
        warnings.append("header.email: email format looks invalid")
    _validate_links(header.get("links", []), "header.links", errors, warnings)


def _validate_summary(summary: Any, errors: list[str], warnings: list[str]) -> None:
    """校验 summary 条目。"""
    if summary is None:
        warnings.append("summary: missing summary bullets")
        return
    if not isinstance(summary, list):
        errors.append("summary: must be a list")
        return
    for index, item in enumerate(summary):
        item_path = f"summary[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_path}: must be an object")
            continue
        if not _is_non_empty_string(item.get("text")):
            errors.append(f"{item_path}.text: required non-empty string")


def _validate_sections(sections: Any, errors: list[str], warnings: list[str], *, final: bool) -> None:
    """校验 sections 数组和 bullet 中的待补数据标记。"""
    if not isinstance(sections, list):
        errors.append("sections: required list")
        return
    if not sections:
        warnings.append("sections: no experience, project, education, or custom section recorded")
    for section_index, section in enumerate(sections):
        section_path = f"sections[{section_index}]"
        if not isinstance(section, dict):
            errors.append(f"{section_path}: must be an object")
            continue
        section_type = section.get("type")
        if section_type not in ALLOWED_SECTION_TYPES:
            errors.append(f"{section_path}.type: must be one of {sorted(ALLOWED_SECTION_TYPES)}")
        if not _is_non_empty_string(section.get("title")):
            errors.append(f"{section_path}.title: required non-empty string")
        items = section.get("items", [])
        if not isinstance(items, list):
            errors.append(f"{section_path}.items: must be a list")
            continue
        for item_index, item in enumerate(items):
            item_path = f"{section_path}.items[{item_index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path}: must be an object")
                continue
            bullets = item.get("bullets", [])
            if bullets is None:
                bullets = []
            if not isinstance(bullets, list):
                errors.append(f"{item_path}.bullets: must be a list")
            else:
                for bullet_index, bullet in enumerate(bullets):
                    bullet_path = f"{item_path}.bullets[{bullet_index}]"
                    if not _is_non_empty_string(bullet):
                        errors.append(f"{bullet_path}: bullet must be non-empty string")
                    elif "[DATA NEEDED" in bullet:
                        message = f"{bullet_path}: contains [DATA NEEDED]"
                        (errors if final else warnings).append(message)
            _validate_links(item.get("links", []), f"{item_path}.links", errors, warnings)


def _validate_skills(skills: Any, errors: list[str], warnings: list[str]) -> None:
    """校验 skills 数组。"""
    if skills is None:
        warnings.append("skills: missing skills section")
        return
    if not isinstance(skills, list):
        errors.append("skills: must be a list")
        return
    for index, skill in enumerate(skills):
        path = f"skills[{index}]"
        if not isinstance(skill, dict):
            errors.append(f"{path}: must be an object")
            continue
        if not _is_non_empty_string(skill.get("label")):
            errors.append(f"{path}.label: required non-empty string")
        items = skill.get("items")
        if not isinstance(items, list) or not all(_is_non_empty_string(item) for item in items):
            errors.append(f"{path}.items: required list of non-empty strings")


def _validate_data_needed(data_needed: Any, errors: list[str], warnings: list[str]) -> None:
    """校验 data_needed 追问列表。"""
    if data_needed is None:
        return
    if not isinstance(data_needed, list):
        errors.append("data_needed: must be a list")
        return
    for index, item in enumerate(data_needed):
        path = f"data_needed[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: must be an object")
            continue
        if not _is_non_empty_string(item.get("question")):
            errors.append(f"{path}.question: required non-empty string")
        if not _is_non_empty_string(item.get("reason")):
            warnings.append(f"{path}.reason: missing reason")


def validate_profile(profile: dict[str, Any], *, final: bool = False) -> dict[str, list[str]]:
    """返回 profile 的 errors 和 warnings。"""
    errors: list[str] = []
    warnings: list[str] = []

    unknown = sorted(set(profile) - ALLOWED_TOP_LEVEL)
    for key in unknown:
        errors.append(f"{key}: unknown top-level field")

    if profile.get("schema_version") != "1.0":
        errors.append('schema_version: must be "1.0"')
    if profile.get("language") not in ALLOWED_LANGUAGES:
        errors.append(f"language: must be one of {sorted(ALLOWED_LANGUAGES)}")

    _validate_target(profile, errors, warnings)
    _validate_header(profile, errors, warnings)
    _validate_summary(profile.get("summary"), errors, warnings)
    _validate_sections(profile.get("sections"), errors, warnings, final=final)
    _validate_skills(profile.get("skills"), errors, warnings)
    _validate_data_needed(profile.get("data_needed"), errors, warnings)

    return {"errors": errors, "warnings": warnings}


def load_profile(path: str) -> dict[str, Any]:
    """从 JSON 文件读取 profile。"""
    with open(path, encoding="utf-8") as profile_file:
        value = json.load(profile_file)
    if not isinstance(value, dict):
        raise ValueError("profile root must be an object")
    return value


def print_report(report: dict[str, list[str]]) -> None:
    """打印校验报告。"""
    if report["errors"]:
        print(f"ERRORS ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"  - {error}")
    if report["warnings"]:
        print(f"WARNINGS ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  - {warning}")
    if not report["errors"] and not report["warnings"]:
        print("Profile valid.")


def main(argv: list[str]) -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="Validate resume-tuning profile JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("profile")
    validate_parser.add_argument("--final", action="store_true", help="treat [DATA NEEDED] as an error")
    args = parser.parse_args(argv[1:])

    if args.command == "validate":
        profile_path = Path(args.profile)
        if not profile_path.exists():
            print(f"找不到文件：{profile_path}", file=sys.stderr)
            return 2
        try:
            profile = load_profile(str(profile_path))
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"无法读取 profile：{exc}", file=sys.stderr)
            return 2
        report = validate_profile(profile, final=args.final)
        print_report(report)
        return 1 if report["errors"] else 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
