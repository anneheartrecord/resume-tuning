#!/usr/bin/env python3
"""eval case 文件结构测试。"""

import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASES_DIR = os.path.join(SKILL_DIR, "evals", "cases")
EXPECTED = {
    "text-to-resume.md",
    "pdf-import-jd-tailor.md",
    "chinese-one-page.md",
    "missing-data.md",
}
SECRET_PATTERNS = [
    re.compile(r"\b1[3-9]\d{9}\b"),
    re.compile(r"sk-[A-Za-z0-9]{12,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
]


def run() -> int:
    failures: list[str] = []
    existing = set(os.listdir(CASES_DIR)) if os.path.isdir(CASES_DIR) else set()
    missing = EXPECTED - existing
    if missing:
        failures.append(f"缺少 eval case: {sorted(missing)}")
    for name in sorted(EXPECTED & existing):
        path = os.path.join(CASES_DIR, name)
        text = open(path, encoding="utf-8").read()
        for heading in ("## Input", "## Expected Behavior", "## Must Not"):
            if heading not in text:
                failures.append(f"{name}: 缺少 {heading}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"{name}: 疑似包含真实手机号或 API key")
    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
