#!/usr/bin/env python3
"""resume_lint.py 的回归测试。"""

import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, TESTS_DIR)

import resume_lint  # noqa: E402
from test_resume_profile import _valid_profile  # noqa: E402


def _check(failures: list[str], cond: bool, msg: str) -> None:
    """cond 为假时记录失败。"""
    if not cond:
        failures.append(msg)


def run() -> int:
    failures: list[str] = []

    profile = _valid_profile()
    profile["summary"] = [{"label": "软实力", "text": "责任心强，自驱力强。"}]
    profile["sections"][0]["items"][0]["bullets"] = [
        "负责开发系统。",
        "优化接口 <span class=\"hl\">P99</span> 和 <span class=\"hl\">QPS</span>，提升 30%。",
        "减少 [DATA NEEDED: 部署耗时下降幅度]。",
    ]
    issues = resume_lint.lint_profile(profile, mode="draft")
    messages = "\n".join(item["message"] for item in issues)
    _check(failures, "vague claim" in messages, "空洞形容词应被提示")
    _check(failures, "lacks clear result" in messages, "无结果 bullet 应被提示")
    _check(failures, "too many .hl" in messages, "过度高亮应被提示")
    _check(failures, any(item["severity"] == "warning" and "[DATA NEEDED]" in item["message"] for item in issues),
           "draft DATA NEEDED 应为 warning")

    final_issues = resume_lint.lint_profile(profile, mode="final")
    _check(failures, any(item["severity"] == "error" and "[DATA NEEDED]" in item["message"] for item in final_issues),
           "final DATA NEEDED 应为 error")

    student = _valid_profile()
    student["target"]["identity"] = "student"
    student["sections"] = [
        {"type": "project", "title": "项目经历", "items": []},
        {"type": "education", "title": "教育经历", "items": []},
    ]
    issues = resume_lint.lint_profile(student)
    _check(failures, any("student profile" in item["message"] for item in issues),
           "学生简历教育未前置应提示")

    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
