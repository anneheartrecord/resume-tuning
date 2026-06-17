#!/usr/bin/env python3
"""jd_match.py 的回归测试。"""

import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, TESTS_DIR)

import jd_match  # noqa: E402
from test_resume_profile import _valid_profile  # noqa: E402


def _check(failures: list[str], cond: bool, msg: str) -> None:
    """cond 为假时记录失败。"""
    if not cond:
        failures.append(msg)


def run() -> int:
    failures: list[str] = []
    profile = _valid_profile()
    profile["sections"][0]["items"][0]["bullets"].append("把容器编排部署流程标准化。")
    report = jd_match.classify_keywords(profile, ["Go", "Kubernetes", "Rust"])

    _check(failures, [item["keyword"] for item in report["covered"]] == ["Go"],
           f"Go 应精确覆盖：{report}")
    _check(failures, [item["keyword"] for item in report["surface"]] == ["Kubernetes"],
           f"Kubernetes 应因容器编排列入 surface：{report}")
    _check(failures, [item["keyword"] for item in report["gap"]] == ["Rust"],
           f"Rust 无证据应列入 gap：{report}")

    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
