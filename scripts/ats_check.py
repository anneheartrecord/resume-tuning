#!/usr/bin/env python3
"""resume-tuning 的 ATS 自检 + JD 关键词覆盖工具。

定稿 PDF 渲染后、交付前跑一遍，回答两个问题：
  1. 这份简历过得了 ATS（机器解析）吗？—— 文本层可提取、标准章节可识别、
     联系方式可解析、阅读顺序正常、无占位符泄漏；页数只做推荐提示。
  2. 它贴目标岗位吗？—— 关键词覆盖率 M/N + 命中/缺失清单。

用法：
  python3 scripts/ats_check.py <定稿.pdf> [--keywords "k1,k2,..."] [--jd jd.txt]
                                           [--name 姓名] [--min-coverage 0.6]

设计原则（延续 resume_pdf.py）：
  - 只做机械活（确定性）：提取文本、正则识别、覆盖计数。脚本只产出事实，
    「缺失关键词要不要补、能不能写」的判断留给 agent + 用户（见
    references/ats-and-jd.md 的三档处理）。
  - 核心文本逻辑纯标准库，可脱离 PDF 独立单测；PDF 提取惰性 import pypdf；
    模糊匹配惰性 import rapidfuzz，缺了就降级精确匹配，绝不阻塞主流程。
"""

import argparse
import os
import re
import sys

# 复用 resume_pdf 的页数/链接提取与占位符泄漏检查，避免逻辑重复。
# import 本身无副作用（重 exec 只在 resume_pdf 的 __main__ 触发），不依赖 pypdf。
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import resume_pdf  # noqa: E402

# 文本层可提取的阈值（每页字符数）。与 resume_pdf.extract_source 判定图片型 PDF
# 的阈值保持一致：低于此值视为扫描件/图片，ATS 读出来是空。
_MIN_CHARS_PER_PAGE = 120

# 标准章节标题词典。来源见 references/ats-and-jd.md 第三节对照表，新增同义标题
# 两边同步，别漂移。英文按词边界匹配，中文按子串匹配（见 contains_term）。
SECTION_PATTERNS: "dict[str, list[str]]" = {
    "experience": [
        "experience", "work experience", "employment", "project", "projects",
        "工作经历", "项目经历", "工作经验", "项目经验", "实习经历",
    ],
    "education": ["education", "教育经历", "教育背景"],
    "skills": ["skills", "skill", "technical skills", "技能", "专业技能", "技术栈"],
}

# 邮箱：标准 RFC 子集，足够抓出简历里的联系邮箱。
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# 电话：宽松匹配，仅作存在性参考（可能误报日期/编号），不作硬性门槛。
# 字符类不含 '.' 和 '–'，避免把 "2020.09 – 2024.06" 这类日期连成一个长串。
_PHONE_RE = re.compile(r"(?<!\d)\+?\d[\d\-\s()]{7,}\d(?!\d)")

# CJK（中日韩统一表意 + 兼容区）与日文假名。用于判断一个词该走子串还是词边界匹配。
_CJK_RE = re.compile(r"[㐀-鿿豈-﫿぀-ヿ]")

# --jd 粗匹配时过滤的英文停用词（小集合，仅为降噪；精确覆盖应让 agent 抽词后用 --keywords）。
_STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or our the to "
    "with you your we will work role team using ability strong good plus etc "
    "experience years year skills skill required preferred responsibilities "
    "looking must need want seeking including such who that this".split()
)


def _has_cjk(text: str) -> bool:
    """文本是否含 CJK / 假名字符。"""
    return bool(_CJK_RE.search(text))


def _normalize(text: str) -> str:
    """小写化并把各类空白折叠成单空格。CJK 不受 lower() 影响；保留标点（c++/.net 需要）。"""
    return re.sub(r"\s+", " ", text.lower())


def contains_term(haystack_norm: str, term: str) -> bool:
    """已 normalize 的 haystack 是否包含 term。

    - 含 CJK 的 term：子串匹配（中文无词边界）。
    - 纯 ASCII 的 term：token 边界匹配——`java` 不命中 `javascript`、`c` 不命中 `c++`/`c#`，
      同时用 re.escape 正确处理 `c++` / `.net` / `node.js` 这类带符号的词。
    """
    term_norm = re.sub(r"\s+", " ", term.strip().lower())
    if not term_norm:
        return False
    if _has_cjk(term_norm):
        return term_norm in haystack_norm
    # 边界 = 非 token 字符。token 字符含 + #（c++/c#/f#），这样关键词 'c' 不会假命中 'c++'/'c#'，
    # 抬高覆盖率、替用户标命中没有的技能。边界**不含** '.' '-'：句末句号（"Python."）仍算命中，
    # 而连字符（go-lang / react-native）的归属本就歧义，留给 agent 抽词时消歧，脚本不强判。
    pattern = r"(?<![a-z0-9+#])" + re.escape(term_norm) + r"(?![a-z0-9+#])"
    return re.search(pattern, haystack_norm) is not None


def detect_sections(resume_text: str) -> "dict[str, bool]":
    """识别标准章节是否存在。返回 {experience, education, skills} 各自的 bool。"""
    haystack = _normalize(resume_text)
    return {
        name: any(contains_term(haystack, term) for term in terms)
        for name, terms in SECTION_PATTERNS.items()
    }


def _dedup(items: "list[str]") -> "list[str]":
    """去重保序。"""
    seen: "set[str]" = set()
    out: "list[str]" = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def detect_contact(text: str) -> "dict[str, list[str]]":
    """抽取 email 和电话。email 可靠、作硬性检查；phone 宽松、可能误报，仅作参考。"""
    emails = _EMAIL_RE.findall(text)
    phones = [re.sub(r"\s+", " ", p).strip() for p in _PHONE_RE.findall(text)]
    return {"email": _dedup(emails), "phone": _dedup(phones)}


def reading_order_ok(resume_text: str, name: "str | None") -> "bool | None":
    """姓名是否出现在提取文本的靠前部分（防多栏/页眉错位）。

    给了 name：检查它出现在前 1/7（至少前 120 字）文本内。
    没给 name：无法判定，返回 None（不计入硬性门槛）。
    """
    if not name or not name.strip():
        return None
    head_len = max(len(resume_text) // 7, 120)
    return name.strip() in resume_text[:head_len]


def _load_fuzzy():
    """惰性 import rapidfuzz.fuzz，没装返回 None（降级精确匹配）。"""
    try:
        from rapidfuzz import fuzz
        return fuzz
    except ImportError:
        return None


def _ascii_tokens(haystack_norm: str) -> "set[str]":
    """从已 normalize 文本里取 ASCII 技术词 token（含 + # . - 这类符号），供模糊匹配比对。"""
    return set(re.findall(r"[a-z0-9][a-z0-9+#.\-]*", haystack_norm))


def _fuzzy_hit(fuzz, keyword_norm: str, resume_tokens: "set[str]", threshold: float) -> bool:
    """关键词与简历某个 token 是否构成「词形变体」且相似度达阈值。

    只认词形/拼写变体（Postgres↔PostgreSQL、nodejs↔node、service↔services），靠两条护栏防假阳：
    1. **最短长度 5**：短词（c/cs/sql 等）相似度极不稳（sql↔sqs、cs↔css 轻易冲高分），一律只走精确。
    2. **前缀结构**：要求一方是另一方的前缀，再叠加相似度阈值。互不为前缀的近似异名（react↔preact，
       相似度高达 90.9 却是两个框架）因此被拒——这是 anti-stuffing 红线：绝不替用户把没有的技能标成命中。
    含 CJK / 含空格短语不走模糊（CJK 用子串；短语模糊易误报）。
    缩写/同义（K8s↔Kubernetes）不是词形变体，靠 agent 抽词时给别名，脚本不臆测。
    """
    if _has_cjk(keyword_norm) or " " in keyword_norm or len(keyword_norm) < 5:
        return False
    for token in resume_tokens:
        if (keyword_norm.startswith(token) or token.startswith(keyword_norm)) \
                and fuzz.ratio(keyword_norm, token) >= threshold:
            return True
    return False


def keyword_coverage(
    resume_text: str,
    keywords: "list[str]",
    *,
    fuzzy_threshold: "float | None" = None,
) -> dict:
    """计算关键词覆盖。返回 total / hit / rate / covered / fuzzy / missing。

    covered：精确命中；fuzzy：仅模糊命中（单独标注，保持透明）；missing：都没命中。
    fuzzy_threshold 为 None 时不启用模糊匹配；非 None 但未装 rapidfuzz 时自动降级（fuzzy 恒空）。
    """
    haystack = _normalize(resume_text)
    fuzz = _load_fuzzy() if fuzzy_threshold is not None else None
    resume_tokens: "set[str] | None" = None

    covered: "list[str]" = []
    fuzzy_hits: "list[str]" = []
    missing: "list[str]" = []
    for raw in keywords:
        keyword = raw.strip()
        if not keyword:
            continue
        if contains_term(haystack, keyword):
            covered.append(keyword)
        elif fuzz is not None:
            if resume_tokens is None:
                resume_tokens = _ascii_tokens(haystack)
            if _fuzzy_hit(fuzz, keyword.lower(), resume_tokens, fuzzy_threshold):
                fuzzy_hits.append(keyword)
            else:
                missing.append(keyword)
        else:
            missing.append(keyword)

    covered, fuzzy_hits, missing = _dedup(covered), _dedup(fuzzy_hits), _dedup(missing)
    hit = len(covered) + len(fuzzy_hits)
    total = hit + len(missing)
    return {
        "total": total,
        "hit": hit,
        "rate": (hit / total) if total else 0.0,
        "covered": covered,
        "fuzzy": fuzzy_hits,
        "missing": missing,
        "fuzzy_available": fuzz is not None,
    }


def keywords_from_jd(jd_text: str) -> "list[str]":
    """从 JD 原文粗抽候选关键词（去停用词的 ASCII 词 + 所有 2-4 字中文片段）。

    **这是粗匹配，含噪声**：真正的关键词抽取是 agent 的语义活，精确覆盖应让 agent
    抽词后用 --keywords 传入。这里只为「没有 agent 介入时也能要个快速信号」。
    """
    ascii_terms: "set[str]" = set()
    # 允许一个可选前导点，保住 .net / .js 这类前导符号技术名（否则会退化成泛化的 net/js）。
    for raw in re.findall(r"\.?[A-Za-z][A-Za-z0-9+#.\-]*", jd_text.lower()):
        # 去包裹括号 + 去句末标点（保留 node.js 的内部点、c++ 的尾 +），否则 "redis." 匹配不到 "Redis"。
        term = raw.strip("()").rstrip(".,;:!?-")
        if len(term) >= 2 and term not in _STOPWORDS:
            ascii_terms.add(term)
    cjk_terms = set(re.findall(r"[一-鿿]{2,6}", jd_text))
    return sorted(ascii_terms) + sorted(cjk_terms)


def extract_pdf_text(pdf_path: str) -> "tuple[str, int]":
    """提取 PDF 文本 + 页数。惰性 import pypdf。"""
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = "".join((page.extract_text() or "") for page in reader.pages)
    return text, len(reader.pages)


def check_readability(pdf_path: str, name: "str | None" = None) -> dict:
    """跑全部不依赖 JD 的 ATS 可读性检查，返回结构化结果（含提取出的 text，供覆盖复用）。"""
    text, pages = extract_pdf_text(pdf_path)
    _, links = resume_pdf.pdf_pages_and_links(pdf_path)
    # email 可能只存在于 mailto: 链接里（正文显示文本之外），把链接也并进来扫。
    contact_blob = text + " " + " ".join(links)
    chars_per_page = len(text) / max(pages, 1)
    return {
        "pages": pages,
        "chars": len(text),
        "text_extractable": chars_per_page >= _MIN_CHARS_PER_PAGE,
        "sections": detect_sections(text),
        "contact": detect_contact(contact_blob),
        "placeholder_leak": resume_pdf._check_placeholder_leak(pdf_path),
        "reading_order_ok": reading_order_ok(text, name),
        "text": text,
    }


def _hard_failures(readability: dict) -> "list[str]":
    """从可读性结果里挑出 ATS 硬伤（导致非零退出）。覆盖率不在此列，是参考非门槛。"""
    failures: "list[str]" = []
    if not readability["text_extractable"]:
        failures.append("文本层提不出内容（图片/扫描型 PDF），ATS 读出来是空")
    if readability["placeholder_leak"]:
        failures.append(f"占位符泄漏（半成品）：{readability['placeholder_leak']}")
    detected = [name for name, ok in readability["sections"].items() if ok]
    if len(detected) < 2:
        failures.append(f"标准章节不足（只认出 {detected or '无'}），用标准标题 Experience/Education/Skills")
    if not readability["contact"]["email"]:
        failures.append("没抽到可解析的 email，ATS 拿不到联系方式")
    if readability["reading_order_ok"] is False:
        failures.append("姓名不在文本靠前部分，阅读顺序可能错位（多栏/页眉问题）")
    return failures


def _print_readability(readability: dict) -> None:
    sections = readability["sections"]
    contact = readability["contact"]
    print("[ATS 可读性]")
    print(f"  pages: {readability['pages']}  text_chars: {readability['chars']}  "
          f"text_extractable: {readability['text_extractable']}")
    print(f"  sections: " + ", ".join(
        f"{name}={'✓' if ok else '✗'}" for name, ok in sections.items()))
    print(f"  email: {contact['email'] or '✗ 未抽到'}")
    print(f"  phone(参考,可能误报): {contact['phone'] or '—'}")
    order = readability["reading_order_ok"]
    print(f"  reading_order: {'✓' if order else ('✗' if order is False else '— (未给 --name，跳过)')}")
    if readability["pages"] > 1:
        print("  NOTE: 多页不是 ATS 硬伤；一页仍是默认推荐，需按目标场景确认页数取舍。")
    if readability["placeholder_leak"]:
        print(f"  WARNING 占位符泄漏: {readability['placeholder_leak']}")


def _print_coverage(coverage: dict, *, heuristic: bool, fuzzy_requested: bool) -> None:
    print("\n[JD 关键词覆盖]" + ("（--jd 粗匹配，含噪声；精确请用 --keywords）" if heuristic else ""))
    rate_pct = round(coverage["rate"] * 100)
    print(f"  覆盖率: {coverage['hit']}/{coverage['total']}  ({rate_pct}%)")
    print(f"  ✅ 命中: {coverage['covered'] or '无'}")
    if coverage["fuzzy"]:
        print(f"  ≈ 模糊命中(词形变体,待 agent 复核): {coverage['fuzzy']}")
    print(f"  ❌ 缺失: {coverage['missing'] or '无'}")
    if coverage["missing"]:
        print("  → 缺失项先分三档（见 references/ats-and-jd.md）：🟡有但没突出→改写surface / 🔴真没有→如实留，别堆砌。")
    # 仅当请求了模糊匹配却没装 rapidfuzz 时，才提示安装；没请求模糊不打扰。
    if fuzzy_requested and not coverage["fuzzy_available"]:
        print("  NOTE: 已请求模糊匹配但未装 rapidfuzz，已降级精确匹配（pip install rapidfuzz 可启用词形变体识别）。")


def run(
    pdf_path: str,
    *,
    keywords: "list[str] | None" = None,
    jd_text: "str | None" = None,
    name: "str | None" = None,
    fuzzy_threshold: "float | None" = None,
    min_coverage: "float | None" = None,
) -> int:
    """主流程：可读性检查 +（可选）覆盖检查，打印报告并返回退出码。"""
    readability = check_readability(pdf_path, name)
    _print_readability(readability)
    failures = _hard_failures(readability)

    coverage_short = False
    using_jd_heuristic = False
    if keywords is None and jd_text is not None:
        keywords = keywords_from_jd(jd_text)
        using_jd_heuristic = True
    if keywords:
        coverage = keyword_coverage(readability["text"], keywords, fuzzy_threshold=fuzzy_threshold)
        _print_coverage(coverage, heuristic=using_jd_heuristic, fuzzy_requested=fuzzy_threshold is not None)
        if min_coverage is not None and coverage["rate"] < min_coverage:
            coverage_short = True

    print()
    if failures:
        print(f"ATS 不通过（{len(failures)} 项硬伤）：")
        for item in failures:
            print(f"  ✗ {item}")
    if coverage_short:
        print(f"  ✗ 覆盖率低于阈值 {min_coverage}（按三档处理缺失项，别盲目堆词）")
    if not failures and not coverage_short:
        print("ATS 可读性通过。")
    return 1 if (failures or coverage_short) else 0


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(
        prog="ats_check.py",
        description="resume-tuning 的 ATS 自检 + JD 关键词覆盖（只产出事实，分档判断交给 agent）。",
    )
    parser.add_argument("pdf", help="定稿 PDF 路径")
    parser.add_argument("--keywords", help="agent 抽好的关键词，逗号分隔（精确覆盖的首选输入）")
    parser.add_argument("--jd", help="JD 文本文件；脚本会粗抽关键词做快速覆盖（含噪声，建议改用 --keywords）")
    parser.add_argument("--name", help="候选人姓名，用于阅读顺序检查")
    parser.add_argument("--fuzzy", type=float, metavar="THRESH",
                        help="启用 rapidfuzz 模糊匹配并设阈值（0-100，建议 90）；仅认前缀式词形变体、短词(<5)不参与；未装则降级精确匹配")
    parser.add_argument("--min-coverage", type=float, metavar="RATE",
                        help="覆盖率低于此值（0-1）则非零退出；不给则覆盖率仅作参考不门槛")
    args = parser.parse_args(argv[1:])

    if not os.path.exists(args.pdf):
        print(f"找不到文件：{args.pdf}", file=sys.stderr)
        return 2

    keywords = None
    if args.keywords:
        keywords = [k for k in args.keywords.split(",") if k.strip()]
    jd_text = None
    if args.jd:
        if not os.path.exists(args.jd):
            print(f"找不到 JD 文件：{args.jd}", file=sys.stderr)
            return 2
        with open(args.jd, encoding="utf-8") as jd_file:
            jd_text = jd_file.read()

    return run(
        args.pdf,
        keywords=keywords,
        jd_text=jd_text,
        name=args.name,
        fuzzy_threshold=args.fuzzy,
        min_coverage=args.min_coverage,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
