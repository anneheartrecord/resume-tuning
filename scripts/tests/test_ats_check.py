#!/usr/bin/env python3
"""ats_check.py 的回归测试。

分两层：
  1. 文本级 / 纯逻辑（无需 PDF/weasyprint/rapidfuzz）：匹配语义、章节识别、联系方式、
     覆盖率、模糊匹配护栏（注入 fake fuzz）、硬伤判定 _hard_failures、退出码 run()/main()。
     这层覆盖了**决定退出码的全部逻辑**和**反编造第一约束**，在任何 python3 上都能跑。
  2. PDF 集成（需 weasyprint + pypdf）：渲染真实模板后跑可读性检查，验证三套模板
     都能被 ATS 正确解析（含 modern 彩色页眉阅读顺序）。缺依赖时显式标「跳过」，不冒充通过。

跑法：python3 scripts/tests/test_ats_check.py
"""

import os
import sys
import tempfile

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, TESTS_DIR)

import ats_check  # noqa: E402


def _check(failures: "list[str]", cond: bool, msg: str) -> None:
    """cond 为假就记一条失败。"""
    if not cond:
        failures.append(msg)


class _FakeFuzz:
    """模拟 rapidfuzz.fuzz：ratio 恒返回固定分。用于在没装 rapidfuzz 时确定性测模糊护栏。"""

    def __init__(self, score: float) -> None:
        self._score = score

    def ratio(self, left: str, right: str) -> float:
        return self._score


def _make_readability(**overrides) -> dict:
    """构造一个「干净通过」的 readability dict，按需覆盖某字段以测单个硬伤分支。"""
    base = {
        "pages": 1,
        "chars": 500,
        "text_extractable": True,
        "sections": {"experience": True, "education": True, "skills": True},
        "contact": {"email": ["a@b.com"], "phone": []},
        "placeholder_leak": [],
        "reading_order_ok": True,
        "text": "John Smith backend engineer Go Redis",
    }
    base.update(overrides)
    return base


def test_text_logic(failures: "list[str]") -> None:
    """匹配语义、章节识别、联系方式、阅读顺序——纯标准库。"""
    norm = ats_check._normalize

    # 词边界：java 不命中 javascript；c 不命中 c++/c#（符号延伸的 token 不该被短词吃掉）
    _check(failures, not ats_check.contains_term(norm("I love javascript"), "java"),
           "词边界：java 不该命中 javascript")
    _check(failures, ats_check.contains_term(norm("backend in Java and Go"), "java"),
           "词边界：java 该命中独立 Java")
    _check(failures, not ats_check.contains_term(norm("wrote C++ daily"), "c"),
           "词边界：c 不该假命中 c++")
    _check(failures, not ats_check.contains_term(norm("C# and F# shop"), "c"),
           "词边界：c 不该假命中 c#")
    _check(failures, ats_check.contains_term(norm("wrote C++ and Node.js"), "c++"),
           "c++ 该命中")
    _check(failures, ats_check.contains_term(norm("wrote C++ and Node.js"), "node.js"),
           "node.js 该命中")
    _check(failures, ats_check.contains_term(norm("shipped Python. fast"), "python"),
           "句末句号不该挡住命中：Python. 该命中 python")
    _check(failures, ats_check.contains_term(norm("applied machine learning models"), "machine learning"),
           "短语 machine learning 该命中")
    # CJK 子串
    _check(failures, ats_check.contains_term(norm("构建分布式存储系统"), "分布式存储"),
           "CJK 子串：分布式存储 该命中")
    _check(failures, not ats_check.contains_term(norm("做过后端开发"), "分布式存储"),
           "CJK 子串：分布式存储 不该命中无关文本")

    # 章节识别：正例（中英）+ 负例（花哨自造标题应全 False）
    _check(failures, all(ats_check.detect_sections("Work Experience ... Education ... Technical Skills").values()),
           "英文章节识别不全")
    _check(failures, all(ats_check.detect_sections("项目经历 ... 教育经历 ... 专业技能").values()),
           "中文章节识别不全")
    fancy = ats_check.detect_sections("我的旅程 ... 求学历程 ... 能力雷达")
    _check(failures, not any(fancy.values()),
           f"花哨自造标题不该被认作标准章节：{fancy}")

    # 联系方式：email（含 mailto: 链接里的）+ phone 误报负例
    contact = ats_check.detect_contact("reach me at john.doe@example.com or +1 (415) 555-1234")
    _check(failures, contact["email"] == ["john.doe@example.com"], f"email 抽取错：{contact['email']}")
    _check(failures, len(contact["phone"]) >= 1, f"phone 该抽到至少一个：{contact['phone']}")
    _check(failures, ats_check.detect_contact("正文无邮箱 mailto:ada@site.com")["email"] == ["ada@site.com"],
           "mailto: 链接里的 email 也该被抽到")
    _check(failures, ats_check.detect_contact("在职 2020.09 – 2024.06 经历")["phone"] == [],
           "日期范围（含点/en-dash）不该被误判成电话")

    # 阅读顺序
    _check(failures, ats_check.reading_order_ok("John Smith\nSoftware Engineer\n...", "John Smith"),
           "阅读顺序：姓名在最前该判 ok")
    _check(failures, ats_check.reading_order_ok("x" * 2000 + " John Smith", "John Smith") is False,
           "阅读顺序：姓名在末尾该判 False")
    _check(failures, ats_check.reading_order_ok("anything", None) is None,
           "阅读顺序：没给 name 该返回 None")


def test_coverage(failures: "list[str]") -> None:
    """覆盖率计算、anti-stuffing、空/边界输入、模糊护栏（注入 fake fuzz，不依赖 rapidfuzz）。"""
    resume = "Built backend services in Go and Python. Used Redis and Kafka. 做过分布式存储。"

    cov = ats_check.keyword_coverage(resume, ["Go", "Python", "Redis", "Kubernetes", "分布式存储"])
    _check(failures, cov["total"] == 5, f"total 算错：{cov['total']}")
    _check(failures, cov["hit"] == 4, f"hit 算错：{cov['hit']}（covered={cov['covered']}）")
    _check(failures, cov["missing"] == ["Kubernetes"], f"missing 算错：{cov['missing']}")
    _check(failures, abs(cov["rate"] - 0.8) < 1e-9, f"rate 算错：{cov['rate']}")
    _check(failures, "分布式存储" in cov["covered"], "CJK 关键词该命中")

    # anti-stuffing（第一约束，纯文本即可测）：用户没有的技能必须落 missing，绝不进 covered/fuzzy
    gap = ats_check.keyword_coverage("Built backend in Go, used Redis and Kafka", ["Kubernetes", "K8s"])
    _check(failures, set(gap["missing"]) == {"Kubernetes", "K8s"} and not gap["covered"] and not gap["fuzzy"],
           f"anti-stuffing：用户无 K8s 必须全落 missing，实际 {gap}")

    # 空/纯空白关键词不计入总数；全空时 rate=0.0 不抛异常（防除零）
    cov_empty = ats_check.keyword_coverage(resume, ["Go", "", "   ", "Rust"])
    _check(failures, cov_empty["total"] == 2, f"空关键词该被跳过，total 应为 2：{cov_empty['total']}")
    cov_allempty = ats_check.keyword_coverage(resume, ["", "   "])
    _check(failures, cov_allempty["total"] == 0 and cov_allempty["rate"] == 0.0,
           f"全空关键词该 total=0 rate=0.0 不崩：{cov_allempty}")

    # 不启用模糊（threshold=None）：fuzzy 恒空，不依赖 rapidfuzz
    cov_nofuzz = ats_check.keyword_coverage("used PostgreSQL", ["Postgres"])
    _check(failures, cov_nofuzz["fuzzy"] == [] and cov_nofuzz["missing"] == ["Postgres"],
           f"未启用模糊：Postgres 精确不命中 PostgreSQL，该 missing：{cov_nofuzz}")

    # 启用模糊但 rapidfuzz 缺失 → 降级精确，不崩、fuzzy 恒空
    original = ats_check._load_fuzzy
    try:
        ats_check._load_fuzzy = lambda: None
        degraded = ats_check.keyword_coverage("used PostgreSQL", ["Postgres"], fuzzy_threshold=90)
        _check(failures, degraded["fuzzy"] == [] and degraded["fuzzy_available"] is False
               and degraded["missing"] == ["Postgres"],
               f"rapidfuzz 缺失该降级：{degraded}")

        # 注入 fake fuzz，确定性验证模糊护栏：
        # (a) 前缀式词形变体 + 高分 → 进 fuzzy 而非 covered
        ats_check._load_fuzzy = lambda: _FakeFuzz(95)
        a = ats_check.keyword_coverage("experience with postgresql", ["Postgres"], fuzzy_threshold=90)
        _check(failures, a["fuzzy"] == ["Postgres"] and a["covered"] == [] and a["fuzzy_available"] is True,
               f"模糊正例：Postgres↔postgresql 该进 fuzzy：{a}")
        # (b) 前缀式但分数低于阈值 → missing
        ats_check._load_fuzzy = lambda: _FakeFuzz(85)
        b = ats_check.keyword_coverage("experience with postgresql", ["Postgres"], fuzzy_threshold=90)
        _check(failures, b["missing"] == ["Postgres"] and b["fuzzy"] == [],
               f"模糊低于阈值该 missing：{b}")
        # (c) 互不为前缀的近似异名（react↔preact）即便高分也拒（anti-stuffing 红线）
        ats_check._load_fuzzy = lambda: _FakeFuzz(99)
        c = ats_check.keyword_coverage("built UI with preact", ["React"], fuzzy_threshold=90)
        _check(failures, c["missing"] == ["React"] and c["fuzzy"] == [],
               f"模糊护栏：react↔preact 该被前缀约束拒掉：{c}")
        # (d) 短词（<5）不参与模糊：SQL 不该模糊命中 SQS
        ats_check._load_fuzzy = lambda: _FakeFuzz(99)
        d = ats_check.keyword_coverage("we use sqs heavily", ["SQL"], fuzzy_threshold=90)
        _check(failures, d["missing"] == ["SQL"] and d["fuzzy"] == [],
               f"模糊护栏：短词 SQL 不该模糊命中 SQS：{d}")
        # (e) CJK / 含空格短语不走模糊
        ats_check._load_fuzzy = lambda: _FakeFuzz(99)
        e = ats_check.keyword_coverage("only english text here", ["机器学习", "deep reinforcement"], fuzzy_threshold=90)
        _check(failures, set(e["missing"]) == {"机器学习", "deep reinforcement"} and e["fuzzy"] == [],
               f"模糊护栏：CJK/短语不走模糊：{e}")
    finally:
        ats_check._load_fuzzy = original

    # 装了真 rapidfuzz 时补充验证一条真实词形变体（没装则跳过，不影响上面的确定性测试）
    if ats_check._load_fuzzy() is not None:
        real = ats_check.keyword_coverage("experience with PostgreSQL", ["Postgres"], fuzzy_threshold=80)
        _check(failures, "Postgres" in real["fuzzy"],
               f"真 rapidfuzz：Postgres↔PostgreSQL 该模糊命中：{real}")


def test_jd_heuristic(failures: "list[str]") -> None:
    """--jd 粗抽：过滤停用词、保前导点技术名、空格分隔的中文片段能干净抽出。"""
    kws = ats_check.keywords_from_jd(
        "We are looking for a Go developer with Kubernetes. 熟悉 分布式存储 与 高并发。")
    _check(failures, "go" in kws and "kubernetes" in kws, f"JD 粗抽该含技术词：{kws}")
    _check(failures, "the" not in kws and "looking" not in kws and "with" not in kws,
           f"JD 粗抽该过滤停用词：{kws}")
    _check(failures, "分布式存储" in kws, f"空格分隔的中文词该被干净抽出：{kws}")
    # 前导点技术名不该退化成泛化词
    dotnet = ats_check.keywords_from_jd("Looking for .NET and Node.js experience")
    _check(failures, ".net" in dotnet and "node.js" in dotnet, f"前导点技术名该保留：{dotnet}")


def test_hard_failures(failures: "list[str]") -> None:
    """_hard_failures：决定退出码的硬伤判定，逐分支测（纯标准库，不依赖 PDF）。"""
    _check(failures, ats_check._hard_failures(_make_readability()) == [],
           "干净 readability 不该有任何硬伤")

    cases = {
        "text_extractable": dict(text_extractable=False),
        "pages>1": dict(pages=2),
        "placeholder_leak": dict(placeholder_leak=["{{NAME}}"]),
        "sections<2": dict(sections={"experience": True, "education": False, "skills": False}),
        "no_email": dict(contact={"email": [], "phone": ["123"]}),
        "reading_order_false": dict(reading_order_ok=False),
    }
    for label, override in cases.items():
        result = ats_check._hard_failures(_make_readability(**override))
        _check(failures, len(result) >= 1, f"硬伤分支 [{label}] 该触发至少一条，实际 {result}")

    # 恰好认出 2 个章节 → 不算硬伤（门槛是 2/3，Skills 可缺）
    _check(failures, ats_check._hard_failures(
        _make_readability(sections={"experience": True, "education": True, "skills": False})) == [],
        "认出 2/3 章节不该算硬伤")
    # reading_order_ok=None（没给 name 无法判定）→ 不计入硬伤
    _check(failures, ats_check._hard_failures(_make_readability(reading_order_ok=None)) == [],
           "reading_order_ok=None 不该计入硬伤")


def test_run_and_cli(failures: "list[str]") -> None:
    """run() 的覆盖率门槛合成 + main() 的退出码（不依赖真实 PDF，monkeypatch check_readability）。"""
    original = ats_check.check_readability
    try:
        ats_check.check_readability = lambda pdf_path, name=None: _make_readability(text="Go Redis Kafka backend")

        # 干净 + 关键词全覆盖 → 退出 0
        _check(failures, ats_check.run("x.pdf", keywords=["Go", "Redis"]) == 0,
               "run：干净 + 全覆盖该返回 0")
        # 有缺失 + min_coverage 高于实际覆盖率 → 覆盖率门槛触发，退出 1
        _check(failures, ats_check.run("x.pdf", keywords=["Go", "Rust"], min_coverage=0.9) == 1,
               "run：覆盖率低于 --min-coverage 该返回 1")
        # 有缺失但不设 min_coverage → 覆盖率仅参考，仍退出 0
        _check(failures, ats_check.run("x.pdf", keywords=["Go", "Rust"]) == 0,
               "run：不设 min_coverage 时覆盖率不门槛，该返回 0")
    finally:
        ats_check.check_readability = original

    # main：文件不存在的错误码 2（在 run 之前返回，无需 pypdf）
    _check(failures, ats_check.main(["ats_check.py", "/no/such/file.pdf"]) == 2,
           "main：pdf 不存在该返回 2")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as fake_pdf:
        _check(failures, ats_check.main(["ats_check.py", fake_pdf.name, "--jd", "/no/such/jd.txt"]) == 2,
               "main：jd 不存在该返回 2")


def test_pdf_integration(failures: "list[str]", skipped: "list[str]") -> None:
    """渲染真实模板后跑可读性检查。缺 weasyprint/pypdf 时显式标跳过（不冒充通过）。"""
    try:
        import weasyprint  # noqa: F401
        import pypdf  # noqa: F401
        from test_render import _fill_template, _CN_BODY
    except ImportError as exc:
        skipped.append(f"PDF 集成（缺依赖：{exc}）")
        return

    cjk_available = ats_check.resume_pdf._cjk_font_uris() is not None
    tmp = tempfile.mkdtemp(prefix="ats_test_")

    en_body = """
<div class="header"><div><div class="name">John Smith</div>
<div class="role">Backend Engineer</div></div>
<div class="contact"><a href="mailto:john@example.com">john@example.com</a></div></div>
<div class="sec"><span class="tag">Experience</span><span class="line"></span></div>
<div class="job"><div class="job-head"><span class="job-co">Acme</span><span class="job-date">2023</span></div>
<ul><li class="b">Built distributed storage in Go, cut P99 latency by 40%.</li></ul></div>
<div class="sec"><span class="tag">Skills</span><span class="line"></span></div>
<div class="skill"><span class="k">Backend:</span> Go, Python, Redis, Kafka.</div>
<div class="sec"><span class="tag">Education</span><span class="line"></span></div>
<div class="edu"><div><span class="school">MIT</span><span class="meta"> · CS</span></div>
<div class="date">2019 – 2023</div></div>
"""
    for tpl in ("classic.html", "minimal.html", "modern.html"):
        html_path = os.path.join(tmp, "en_" + tpl)
        pdf_path = html_path.replace(".html", ".pdf")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(_fill_template(tpl, en_body))
        ats_check.resume_pdf._render_autofit(html_path, pdf_path)

        readability = ats_check.check_readability(pdf_path, name="John Smith")
        _check(failures, ats_check._hard_failures(readability) == [],
               f"{tpl}: 合格英文简历不该有 ATS 硬伤：{ats_check._hard_failures(readability)}")
        _check(failures, readability["reading_order_ok"] is True,
               f"{tpl}: 姓名该在文本靠前（阅读顺序）")
        _check(failures, readability["contact"]["email"] == ["john@example.com"],
               f"{tpl}: 该抽到 mailto email，实际 {readability['contact']['email']}")

        cov = ats_check.keyword_coverage(readability["text"], ["Go", "Redis", "Kafka", "Rust"])
        _check(failures, set(cov["covered"]) == {"Go", "Redis", "Kafka"} and cov["missing"] == ["Rust"],
               f"{tpl}: 覆盖率分类错 covered={cov['covered']} missing={cov['missing']}")

    if cjk_available:
        cn_path = os.path.join(tmp, "cn_classic.html")
        cn_pdf = cn_path.replace(".html", ".pdf")
        with open(cn_path, "w", encoding="utf-8") as fh:
            fh.write(_fill_template("classic.html", _CN_BODY))
        ats_check.resume_pdf._render_autofit(cn_path, cn_pdf)
        cn_read = ats_check.check_readability(cn_pdf, name="张三")
        _check(failures, cn_read["text_extractable"], "中文简历文本层该可提取")
        _check(failures, cn_read["sections"]["experience"] and cn_read["sections"]["education"],
               f"中文章节该被识别：{cn_read['sections']}")
        _check(failures, cn_read["contact"]["email"] == ["a@b.com"],
               f"中文简历该抽到 email：{cn_read['contact']['email']}")
    else:
        skipped.append("中文 PDF 集成断言（未装 CJK 字体，先跑 ensure-fonts.sh）")


def run() -> int:
    failures: "list[str]" = []
    skipped: "list[str]" = []
    for test in (test_text_logic, test_coverage, test_jd_heuristic, test_hard_failures, test_run_and_cli):
        print(f"· {test.__name__}")
        test(failures)
    print("· test_pdf_integration")
    test_pdf_integration(failures, skipped)

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    if skipped:
        print(f"ALL PASSED（{len(skipped)} 项跳过，非通过）：")
        for s in skipped:
            print(f"  ⊘ {s}")
    else:
        print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
