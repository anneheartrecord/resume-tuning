#!/usr/bin/env python3
"""resume_profile.py 的回归测试。"""

import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import resume_profile  # noqa: E402


def _valid_profile() -> dict:
    """返回最小合法 profile。"""
    return {
        "schema_version": "1.0",
        "language": "zh",
        "target": {
            "role": "后端开发工程师",
            "industry": "AI tooling",
            "identity": "experienced",
            "privacy_mode": "private",
        },
        "header": {
            "name": "张三",
            "email": "zhangsan@example.com",
            "links": [{"label": "GitHub", "url": "https://github.com/example"}],
        },
        "summary": [{"label": "后端", "text": "主攻 Go，做过分布式任务系统。"}],
        "sections": [
            {
                "type": "project",
                "title": "项目经历",
                "items": [{"name": "任务平台", "bullets": ["支撑 2000+ 日任务执行。"]}],
            }
        ],
        "skills": [{"label": "Backend", "items": ["Go", "Redis"]}],
        "data_needed": [],
    }


def _check(failures: list[str], cond: bool, msg: str) -> None:
    """cond 为假时记录失败。"""
    if not cond:
        failures.append(msg)


def run() -> int:
    failures: list[str] = []

    report = resume_profile.validate_profile(_valid_profile())
    _check(failures, report["errors"] == [], f"合法 profile 不应有 errors：{report}")

    unknown = _valid_profile()
    unknown["extra"] = True
    report = resume_profile.validate_profile(unknown)
    _check(failures, any("unknown top-level" in item for item in report["errors"]), "未知顶层字段应报错")

    invalid = _valid_profile()
    invalid["target"]["identity"] = "developer"
    report = resume_profile.validate_profile(invalid)
    _check(failures, any("target.identity" in item for item in report["errors"]), "非法 identity 应报错")

    public = _valid_profile()
    public["target"]["privacy_mode"] = "public"
    public["header"]["phone"] = "+86 13800000000"
    report = resume_profile.validate_profile(public)
    _check(failures, any("public privacy" in item for item in report["warnings"]), "公开场景手机号应警告")

    draft = _valid_profile()
    draft["sections"][0]["items"][0]["bullets"] = ["提升 [DATA NEEDED: P99 降幅]。"]
    report = resume_profile.validate_profile(draft)
    _check(failures, report["errors"] == [] and any("[DATA NEEDED]" in item for item in report["warnings"]),
           "draft 的 DATA NEEDED 应为 warning")
    report = resume_profile.validate_profile(draft, final=True)
    _check(failures, any("[DATA NEEDED]" in item for item in report["errors"]),
           "final 的 DATA NEEDED 应为 error")

    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
