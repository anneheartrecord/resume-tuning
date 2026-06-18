#!/usr/bin/env python3
"""Generate synthetic resume demo PNGs for README showcase tables."""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPTS_DIR.parent
TEMPLATES_DIR = REPO_DIR / "assets" / "templates"
DEMOS_DIR = REPO_DIR / "assets" / "demos"

sys.path.insert(0, str(SCRIPTS_DIR))

import resume_pdf  # noqa: E402


@dataclass(frozen=True)
class ResumeExperience:
    """One resume experience block rendered into the demo templates."""

    company: str
    date: str
    role: str
    tier: str
    bullets: tuple[str, ...]


@dataclass(frozen=True)
class ResumeCase:
    """A synthetic resume case used to generate one README demo image."""

    slug: str
    template: str
    language: str
    name: str
    native_name: str
    role: str
    email: str
    primary_link_label: str
    primary_link_url: str
    secondary_link_label: str
    secondary_link_url: str
    location: str
    section_titles: dict[str, str]
    summary: tuple[str, ...]
    experiences: tuple[ResumeExperience, ...]
    skills: tuple[str, ...]
    education: str
    education_date: str


def _demo_cases() -> tuple[ResumeCase, ...]:
    """Return six synthetic, role-diverse resume cases for the README."""
    return (
        ResumeCase(
            slug="backend-classic",
            template="classic",
            language="en",
            name="Maya Chen",
            native_name="",
            role="Backend Platform Engineer",
            email="maya.chen@example.com",
            primary_link_label="github.com/maya-platform",
            primary_link_url="https://example.com/maya-platform",
            secondary_link_label="maya.dev",
            secondary_link_url="https://example.com/maya",
            location="Singapore · Remote",
            section_titles={
                "summary": "Summary",
                "experience": "Experience",
                "skills": "Skills",
                "education": "Education",
            },
            summary=(
                '<span class="lead">Platform:</span> Built high-throughput Python and Go services for billing, search, and job orchestration.',
                '<span class="lead">Reliability:</span> Cut payment incident MTTR from 42m to <span class="hl">11m</span> with typed runbooks and queue-level alerts.',
            ),
            experiences=(
                ResumeExperience(
                    company="Nimbus Cloud",
                    date="2023.04 - Present",
                    role="Senior Backend Engineer",
                    tier="Platform",
                    bullets=(
                        'Owned the order orchestration service used by <span class="hl">1.8M</span> monthly transactions across subscription and usage billing.',
                        '<span class="lead">Queues:</span> Reworked idempotency, retry windows, and dead-letter handling; duplicate charge reports dropped by <span class="hl">76%</span>.',
                        '<span class="lead">Observability:</span> Added service-level dashboards and alert routing for Kafka lag, payment retries, and partner API failures.',
                    ),
                ),
                ResumeExperience(
                    company="Orbit Systems",
                    date="2020.07 - 2023.03",
                    role="Backend Engineer",
                    tier="Core Infrastructure",
                    bullets=(
                        'Migrated account search from a monolith query path to a dedicated indexing pipeline serving <span class="hl">90ms</span> p95 reads.',
                        '<span class="lead">API:</span> Introduced typed request validation and contract tests for 18 partner-facing endpoints.',
                    ),
                ),
            ),
            skills=(
                '<span class="k">Backend:</span> Go, Python, PostgreSQL, Redis, Kafka, Temporal.',
                '<span class="k">Reliability:</span> SLO dashboards, incident review, queue backpressure, contract testing.',
            ),
            education="National University of Singapore · B.Comp. Computer Science",
            education_date="2016 - 2020",
        ),
        ResumeCase(
            slug="product-modern",
            template="modern",
            language="en",
            name="Avery Brooks",
            native_name="",
            role="AI Product Manager",
            email="avery.brooks@example.com",
            primary_link_label="portfolio.example.com/avery",
            primary_link_url="https://example.com/avery",
            secondary_link_label="linkedin.com/in/avery",
            secondary_link_url="https://example.com/avery-linkedin",
            location="San Francisco · Hybrid",
            section_titles={
                "summary": "Summary",
                "experience": "Experience",
                "skills": "Skills",
                "education": "Education",
            },
            summary=(
                '<span class="lead">Product:</span> Ships AI workflow products from ambiguous user problems to measurable adoption loops.',
                '<span class="lead">Impact:</span> Grew weekly active teams from 420 to <span class="hl">2,900</span> by tightening activation and template discovery.',
            ),
            experiences=(
                ResumeExperience(
                    company="Foundry AI",
                    date="2022.11 - Present",
                    role="Product Manager",
                    tier="Agent Workflows",
                    bullets=(
                        'Led roadmap for an internal agent builder used by sales, support, and operations teams.',
                        '<span class="lead">Activation:</span> Rebuilt onboarding around first-success templates; team activation rose from 31% to <span class="hl">58%</span>.',
                        '<span class="lead">Quality:</span> Defined eval review loops with PM, design, and ML; reduced low-confidence launches by <span class="hl">43%</span>.',
                    ),
                ),
                ResumeExperience(
                    company="Northstar Apps",
                    date="2019.08 - 2022.10",
                    role="Associate Product Manager",
                    tier="Growth",
                    bullets=(
                        'Owned signup, workspace invite, and trial conversion experiments for a B2B collaboration product.',
                        '<span class="lead">Conversion:</span> Raised self-serve trial-to-paid from 8.4% to <span class="hl">12.7%</span> through segment-specific onboarding.',
                    ),
                ),
            ),
            skills=(
                '<span class="k">Product:</span> discovery, roadmap, activation funnels, pricing tests, AI evals.',
                '<span class="k">Tools:</span> SQL, Amplitude, Linear, Figma, prompt QA, stakeholder narrative.',
            ),
            education="University of Michigan · B.A. Economics",
            education_date="2015 - 2019",
        ),
        ResumeCase(
            slug="research-minimal",
            template="minimal",
            language="en",
            name="Dr. Elise Martin",
            native_name="",
            role="Applied ML Research Scientist",
            email="elise.martin@example.com",
            primary_link_label="scholar.example.com/elise",
            primary_link_url="https://example.com/elise-scholar",
            secondary_link_label="elise-lab.example.com",
            secondary_link_url="https://example.com/elise-lab",
            location="Toronto",
            section_titles={
                "summary": "Summary",
                "experience": "Research",
                "skills": "Methods",
                "education": "Education",
            },
            summary=(
                '<span class="lead">Research:</span> Works on retrieval-augmented generation, evaluation reliability, and dataset shift in production systems.',
                '<span class="lead">Output:</span> Published 7 peer-reviewed papers and released <span class="hl">3</span> open datasets for model evaluation.',
            ),
            experiences=(
                ResumeExperience(
                    company="Vector Institute",
                    date="2023 - Present",
                    role="Research Scientist",
                    tier="Evaluation Systems",
                    bullets=(
                        'Designed benchmark suites for long-context retrieval and answer attribution across legal and biomedical corpora.',
                        '<span class="lead">Evaluation:</span> Built human-in-the-loop adjudication protocol that improved label agreement from 0.62 to <span class="hl">0.81</span> kappa.',
                        '<span class="lead">Transfer:</span> Partnered with platform engineers to turn offline metrics into release-blocking quality gates.',
                    ),
                ),
                ResumeExperience(
                    company="University of Toronto",
                    date="2018 - 2023",
                    role="PhD Researcher",
                    tier="Machine Learning",
                    bullets=(
                        'Studied robust retrieval under noisy supervision with experiments across web-scale and domain-specific datasets.',
                        '<span class="lead">Publication:</span> First-author work accepted at ACL and NeurIPS workshops; code released for reproducibility.',
                    ),
                ),
            ),
            skills=(
                '<span class="k">Methods:</span> retrieval evaluation, weak supervision, calibration, annotation design.',
                '<span class="k">Stack:</span> Python, PyTorch, FAISS, Hugging Face, statistical testing.',
            ),
            education="University of Toronto · PhD Computer Science",
            education_date="2018 - 2023",
        ),
        ResumeCase(
            slug="growth-modern",
            template="modern",
            language="zh",
            name="林夏然",
            native_name="",
            role="增长营销负责人",
            email="xiaoran.lin@example.com",
            primary_link_label="portfolio.example.com/xiaoran",
            primary_link_url="https://example.com/xiaoran",
            secondary_link_label="linkedin.com/in/xiaoran",
            secondary_link_url="https://example.com/xiaoran-linkedin",
            location="上海 · 可远程",
            section_titles={
                "summary": "自我评价",
                "experience": "工作经历",
                "skills": "能力",
                "education": "教育经历",
            },
            summary=(
                '<span class="lead">增长:</span> 擅长把定位、内容、广告和转化漏斗连成闭环，负责过 0 到 1 海外获客。',
                '<span class="lead">结果:</span> 12 个月内把自然线索从 1,200/月提升到 <span class="hl">8,400/月</span>，CAC 降低 37%。',
            ),
            experiences=(
                ResumeExperience(
                    company="Harbor SaaS",
                    date="2022.06 - 至今",
                    role="增长营销负责人",
                    tier="Global GTM",
                    bullets=(
                        '负责从定位、SEO、付费投放到站内转化的全链路增长，服务 B2B SaaS 海外市场。',
                        '<span class="lead">SEO:</span> 重构高意图关键词集和内容集群，非品牌自然流量增长 <span class="hl">5.8 倍</span>。',
                        '<span class="lead">转化:</span> 设计按行业分流的 landing page，demo 预约率从 3.1% 提升到 <span class="hl">6.9%</span>。',
                    ),
                ),
                ResumeExperience(
                    company="BluePeak Studio",
                    date="2019.07 - 2022.05",
                    role="市场经理",
                    tier="内容与增长",
                    bullets=(
                        '搭建内容日历、案例库和渠道归因报表，让销售团队能按行业复用获客素材。',
                        '<span class="lead">线索:</span> 通过 webinar 和客户案例组合，季度 MQL 从 380 提升到 <span class="hl">1,150</span>。',
                    ),
                ),
            ),
            skills=(
                '<span class="k">增长:</span> SEO、内容策略、付费投放、转化率优化、漏斗分析。',
                '<span class="k">工具:</span> GA4、Search Console、HubSpot、Notion、Figma、SQL 基础分析。',
            ),
            education="复旦大学 · 新闻传播学 · 本科",
            education_date="2015.09 - 2019.06",
        ),
        ResumeCase(
            slug="operations-classic",
            template="classic",
            language="zh",
            name="周昀",
            native_name="",
            role="运营策略经理",
            email="yun.zhou@example.com",
            primary_link_label="casebook.example.com/yun",
            primary_link_url="https://example.com/yun",
            secondary_link_label="linkedin.com/in/yunzhou",
            secondary_link_url="https://example.com/yun-linkedin",
            location="深圳",
            section_titles={
                "summary": "自我评价",
                "experience": "工作经历",
                "skills": "能力",
                "education": "教育经历",
            },
            summary=(
                '<span class="lead">运营:</span> 从履约、客服到供应商协同都做过，擅长把复杂流程拆成可量化 SOP。',
                '<span class="lead">效率:</span> 主导城市仓补货和客服分流改造，异常工单占比从 18% 降到 <span class="hl">7%</span>。',
            ),
            experiences=(
                ResumeExperience(
                    company="DailyCart",
                    date="2021.03 - 至今",
                    role="运营策略经理",
                    tier="履约体验",
                    bullets=(
                        '负责 12 个城市仓的补货节奏、客服分流和异常订单治理，连接供应链、客服和城市团队。',
                        '<span class="lead">SOP:</span> 设计高峰期异常订单分级规则，平均处理时长从 9.6 小时降到 <span class="hl">3.1 小时</span>。',
                        '<span class="lead">协同:</span> 建立供应商履约评分卡，延迟交付率下降 28%，复盘会议从事后追责转向周度预警。',
                    ),
                ),
                ResumeExperience(
                    company="Morn Logistics",
                    date="2018.08 - 2021.02",
                    role="区域运营专员",
                    tier="华南区",
                    bullets=(
                        '跟进直营网点排班、车辆调度和投诉闭环，支持华南区 36 个站点日常运营。',
                        '<span class="lead">成本:</span> 通过线路合并和峰谷排班，单票配送成本降低 <span class="hl">11%</span>。',
                    ),
                ),
            ),
            skills=(
                '<span class="k">运营:</span> 流程优化、SOP、客服分流、履约质量、供应商管理。',
                '<span class="k">分析:</span> Excel、SQL 基础、Looker、周报体系、异常归因。',
            ),
            education="华南理工大学 · 工商管理 · 本科",
            education_date="2014.09 - 2018.06",
        ),
        ResumeCase(
            slug="newgrad-minimal",
            template="minimal",
            language="en",
            name="Jordan Lee",
            native_name="",
            role="New Grad Data Analyst",
            email="jordan.lee@example.com",
            primary_link_label="github.com/jordan-data",
            primary_link_url="https://example.com/jordan-data",
            secondary_link_label="jordanlee.example.com",
            secondary_link_url="https://example.com/jordan",
            location="New York",
            section_titles={
                "summary": "Summary",
                "experience": "Projects",
                "skills": "Skills",
                "education": "Education",
            },
            summary=(
                '<span class="lead">Analytics:</span> Combines SQL, Python, and product sense to explain user behavior and experiment results.',
                '<span class="lead">Portfolio:</span> Built 4 public analysis projects covering churn, pricing, and funnel diagnostics.',
            ),
            experiences=(
                ResumeExperience(
                    company="Campus Marketplace Capstone",
                    date="2025.01 - 2025.05",
                    role="Data Analyst",
                    tier="Product Analytics",
                    bullets=(
                        'Analyzed marketplace liquidity across 18 campus categories and identified the first-message delay as the biggest conversion blocker.',
                        '<span class="lead">Insight:</span> Modeled cohort retention and showed sellers replying within 2h had <span class="hl">2.4x</span> higher repeat listing rates.',
                        '<span class="lead">Dashboard:</span> Built Looker-style charts in Streamlit for weekly category health review.',
                    ),
                ),
                ResumeExperience(
                    company="City Transit Open Data",
                    date="2024.09 - 2024.12",
                    role="Independent Project",
                    tier="Forecasting",
                    bullets=(
                        'Cleaned 6 years of public ridership data and forecasted station-level demand for weekday peak planning.',
                        '<span class="lead">Model:</span> Reduced MAPE from 18.2% to <span class="hl">11.6%</span> with weather and event features.',
                    ),
                ),
            ),
            skills=(
                '<span class="k">Analysis:</span> SQL, Python, pandas, experiment readouts, cohort retention, funnel analysis.',
                '<span class="k">Visualization:</span> Tableau, Streamlit, matplotlib, stakeholder memos.',
            ),
            education="New York University · B.S. Data Science",
            education_date="2021 - 2025",
        ),
    )


def _replace_template_body(template_html: str, body_html: str, resume_case: ResumeCase) -> str:
    """Replace a template body and metadata with one synthetic resume body."""
    head, separator, tail = template_html.partition("</head>")
    rendered_tail = re.sub(
        r"<body([^>]*)>.*?</body>",
        lambda match: f'<body{match.group(1)}>{body_html}</body>',
        tail,
        flags=re.DOTALL,
    )
    metadata_head = (
        head.replace("<html lang=\"en\">", f"<html lang=\"{resume_case.language}\">")
        .replace("{{NAME}}", resume_case.name)
        .replace("{{ONE_LINE_SUMMARY ≤150 chars}}", resume_case.role)
        .replace("{{3-6 keywords：优先填 JD 高频且你真有的技能词，利于 ATS 检索；不堆砌虚假词}}", resume_case.role)
    )
    return metadata_head + separator + rendered_tail


def _header_html(resume_case: ResumeCase) -> str:
    """Render the shared resume header HTML for all templates."""
    native_name = f'<span class="zh">{resume_case.native_name}</span>' if resume_case.native_name else ""
    return f"""
<div class="header">
  <div>
    <div class="name">{resume_case.name}{native_name}</div>
    <div class="role">{resume_case.role}</div>
  </div>
  <div class="contact">
    <a href="mailto:{resume_case.email}">{resume_case.email}</a><br>
    <a href="{resume_case.primary_link_url}">{resume_case.primary_link_label}</a><span class="sep">·</span><a href="{resume_case.secondary_link_url}">{resume_case.secondary_link_label}</a><br>
    {resume_case.location}
  </div>
</div>
"""


def _section_html(title: str) -> str:
    """Render a section heading that works across all templates."""
    return f'<div class="sec"><span class="tag">{title}</span><span class="line"></span></div>'


def _experience_html(experience: ResumeExperience) -> str:
    """Render one work, project, or research experience block."""
    bullet_items = "\n".join(f'    <li class="b">{bullet}</li>' for bullet in experience.bullets)
    return f"""
<div class="job">
  <div class="job-head"><span class="job-co">{experience.company}</span><span class="job-date">{experience.date}</span></div>
  <div class="job-sub"><span class="job-role">{experience.role}</span><span class="job-tier">{experience.tier}</span></div>
  <ul>
{bullet_items}
  </ul>
</div>
"""


def _body_html(resume_case: ResumeCase) -> str:
    """Render the complete body HTML for one synthetic resume case."""
    summary_items = "\n".join(f'  <li class="b">{item}</li>' for item in resume_case.summary)
    experience_blocks = "\n".join(_experience_html(experience) for experience in resume_case.experiences)
    skill_items = "\n".join(f'<div class="skill">{skill}</div>' for skill in resume_case.skills)
    titles = resume_case.section_titles
    return f"""
{_header_html(resume_case)}

{_section_html(titles["summary"])}
<ul>
{summary_items}
</ul>

{_section_html(titles["experience"])}
{experience_blocks}

{_section_html(titles["skills"])}
{skill_items}

{_section_html(titles["education"])}
<div class="edu">
  <div><span class="school">{resume_case.education}</span></div>
  <div class="date">{resume_case.education_date}</div>
</div>
"""


def _render_case(resume_case: ResumeCase, render_workspace: Path) -> Path:
    """Render one synthetic resume case into assets/demos and return its PNG path."""
    template_path = TEMPLATES_DIR / f"{resume_case.template}.html"
    template_html = template_path.read_text(encoding="utf-8")
    rendered_html = _replace_template_body(template_html, _body_html(resume_case), resume_case)

    html_path = render_workspace / f"{resume_case.slug}.html"
    pdf_path = render_workspace / f"{resume_case.slug}.pdf"
    html_path.write_text(rendered_html, encoding="utf-8")

    result = resume_pdf._render_autofit(str(html_path), str(pdf_path))
    if result["pages"] != 1 or result["placeholder_leak"]:
        raise RuntimeError(f"{resume_case.slug} failed render gate: {result}")

    png_path = resume_pdf._rasterize(str(pdf_path))
    if not png_path:
        raise RuntimeError(f"{resume_case.slug} did not produce a PNG preview")

    output_path = DEMOS_DIR / f"{resume_case.slug}.png"
    shutil.copyfile(png_path, output_path)
    return output_path


def main() -> int:
    """Generate every README demo PNG into assets/demos."""
    resume_pdf._ensure_native_libs_then_reexec()
    DEMOS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="resume-tuning-demos-") as workspace_name:
        render_workspace = Path(workspace_name)
        for resume_case in _demo_cases():
            output_path = _render_case(resume_case, render_workspace)
            print(f"generated {output_path.relative_to(REPO_DIR)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
