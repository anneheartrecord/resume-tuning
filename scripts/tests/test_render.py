#!/usr/bin/env python3
"""resume-tuning 渲染回归测试。

覆盖这个 skill 开发时踩过的真实回归：
  1. 三套模板各能渲染；短简历仍优先适配为 1 页。
  2. 中文内容渲染后 PDF 里真有 CJK 字体（防「字形丢失、文字层却正确」的乱码回归）。
  3. 占位符泄漏检查能正确报警（防半成品当成品交付）。
  4. 多页简历允许导出，不因页数返回失败。
  5. resume_pdf.py 能 import（防 Python 注解之类语法回归）。

跑法：python3 scripts/tests/test_render.py
依赖 weasyprint + pypdf；需要 assets/fonts/ 有 CJK 字体（先跑 ensure-fonts.sh）。
"""

import os
import sys
import tempfile
import json
import contextlib
import io

# 让本测试能 import 同级 scripts/ 下的 resume_pdf
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)
TEMPLATES_DIR = os.path.join(SKILL_DIR, "assets", "templates")
sys.path.insert(0, SCRIPTS_DIR)

# 回归 4：import 不报错（曾因 `tuple | None` 运行时注解崩过）
import resume_pdf  # noqa: E402

# 一段含中文的最小内容，套进每个模板的 <body> 测试。
_CN_BODY = """
<div class="header"><div><div class="name">张三<span class="zh"></span></div>
<div class="role">后端开发工程师</div></div>
<div class="contact"><a href="mailto:a@b.com">a@b.com</a><span class="sep">·</span>北京</div></div>
<div class="sec"><span class="tag">自我评价</span><span class="line"></span></div>
<ul><li class="b"><span class="lead">后端:</span>主攻 Go，做过分布式存储，对一致性有完整实现经验。</li></ul>
<div class="sec"><span class="tag">项目经历</span><span class="line"></span></div>
<div class="job"><div class="job-head"><span class="job-co">键值存储</span><span class="job-date">2023</span></div>
<ul><li class="b">实现 Raft 选举与日志复制，保证线性一致。</li></ul></div>
<div class="sec"><span class="tag">教育经历</span><span class="line"></span></div>
<div class="edu"><div><span class="school">某大学</span><span class="meta"> · 计算机 本科</span></div>
<div class="date">2020 – 2024</div></div>
"""


def _fill_template(template_name: str, body: str) -> str:
    """把 body 塞进模板的 <body>...</body>，返回完整 HTML 文本。

    注意：模板顶部注释里也有「<body>」字样，必须先按 </head> 切开、只在 body 段替换，
    否则正则会从注释里的 <body> 一路贪到真正的 </body>，把整个 <head><style> 吃掉。
    """
    import re

    src = os.path.join(TEMPLATES_DIR, template_name)
    html = open(src, encoding="utf-8").read()
    head, sep, tail = html.partition("</head>")
    tail = re.sub(
        r"<body([^>]*)>.*?</body>",
        lambda m: f"<body{m.group(1)}>{body}</body>",
        tail,
        flags=re.DOTALL,
    )
    return head + sep + tail


def _pdf_has_cjk_font(pdf_path: str) -> bool:
    """检查 PDF 的 /Font 资源里是否真的嵌入了 CJK 字体。"""
    from pypdf import PdfReader

    for page in PdfReader(pdf_path).pages:
        fonts = (page.get("/Resources") or {}).get("/Font") or {}
        for value in (fonts.values() if hasattr(fonts, "values") else []):
            base = str(value.get_object().get("/BaseFont", ""))
            # 模板 @font-face 把 CJK 字体统一命名为 ResumeCJK，子集名形如 ABCDEF+ResumeCJK。
            # 出现它就说明中文真用上了内嵌字体（而非掉回无 CJK 的 Helvetica）。
            if "ResumeCJK" in base:
                return True
            # 兜底：直接用了具名 CJK 字体的情况
            if any(k in base for k in ("Tsanger", "LXGW", "Noto", "Han", "PingFang", "Song", "Kai")):
                return True
            # 名字里直接含中日韩字符
            if any("一" <= ch <= "鿿" for ch in base):
                return True
    return False


def run() -> int:
    failures: list[str] = []
    skipped: list[str] = []
    tmp = tempfile.mkdtemp(prefix="resume_test_")
    cjk_available = resume_pdf._cjk_font_uris() is not None

    try:
        import weasyprint  # noqa: F401
        import pypdf  # noqa: F401
    except ImportError as exc:
        skipped.append(f"PDF 渲染回归（缺依赖：{exc}）")

    metadata_path = os.path.join(TEMPLATES_DIR, "templates.json")
    with open(metadata_path, encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
    for key in ("classic", "minimal", "modern"):
        if key not in metadata:
            failures.append(f"templates.json 缺少 {key}")
            continue
        item = metadata[key]
        for required in ("display_name", "recommended_for", "ats_level", "visual_strength"):
            if required not in item:
                failures.append(f"templates.json {key} 缺少 {required}")

    if not skipped:
        # 回归 1 + 2：三套模板可渲染；短简历仍优先适配为 1 页，中文字形在
        for tpl in ("classic.html", "minimal.html", "modern.html"):
            html = _fill_template(tpl, _CN_BODY)
            html_path = os.path.join(tmp, tpl)
            pdf_path = html_path.replace(".html", ".pdf")
            open(html_path, "w", encoding="utf-8").write(html)
            result = resume_pdf._render_autofit(html_path, pdf_path)

            if result["pages"] != 1:
                failures.append(f"{tpl}: 应为 1 页，实际 {result['pages']} 页")
            if result["placeholder_leak"]:
                failures.append(f"{tpl}: 干净内容不该报占位符泄漏：{result['placeholder_leak']}")
            if cjk_available and not _pdf_has_cjk_font(pdf_path):
                failures.append(f"{tpl}: 有 CJK 字体却没嵌进 PDF（字形丢失回归）")
            print(f"  {tpl}: pages={result['pages']} cjk_font={result['cjk_font_used']} "
                  f"scale={result['scale_factor']} leak={bool(result['placeholder_leak'])}")

        # 回归 3：占位符泄漏要能报警
        leak_body = _CN_BODY + '<div>{{LEAK}} [DATA NEEDED: x]</div>'
        leak_html = os.path.join(tmp, "leak.html")
        leak_pdf = leak_html.replace(".html", ".pdf")
        open(leak_html, "w", encoding="utf-8").write(_fill_template("classic.html", leak_body))
        leak_result = resume_pdf._render_autofit(leak_html, leak_pdf)
        if not leak_result["placeholder_leak"]:
            failures.append("占位符泄漏检查失灵：留了 {{LEAK}} 和 [DATA NEEDED] 却没报")
        else:
            print(f"  leak check: 正确报警 {len(leak_result['placeholder_leak'])} 类")

        # 回归 4：内容合理超过一页时只提示页数，不让导出/预览失败。
        long_items = "\n".join(
            f'<li class="b"><span class="lead">项目 {index}:</span> '
            f'负责跨团队交付、流程改造和指标复盘，沉淀可复用方法并推动持续改进。</li>'
            for index in range(1, 90)
        )
        long_body = _CN_BODY + (
            '<div class="sec"><span class="tag">更多经历</span><span class="line"></span></div>'
            f"<ul>{long_items}</ul>"
        )
        long_html = os.path.join(tmp, "long_classic.html")
        long_pdf = long_html.replace(".html", ".pdf")
        open(long_html, "w", encoding="utf-8").write(_fill_template("classic.html", long_body))
        long_result = resume_pdf._render_autofit(long_html, long_pdf)
        if long_result["pages"] <= 1:
            failures.append(f"多页回归样例应超过 1 页，实际 {long_result['pages']} 页")
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = resume_pdf.render_one_page(long_html, long_pdf)
            preview_code = resume_pdf.preview([long_html])
        if exit_code != 0:
            failures.append(f"多页且无占位符时 render 不应失败，实际退出码 {exit_code}")
        if preview_code != 0:
            failures.append(f"多页且无占位符时 preview 不应失败，实际退出码 {preview_code}")
        print(f"  multipage allowed: pages={long_result['pages']} exit={exit_code} preview={preview_code}")

        if not cjk_available:
            print("  NOTE: 未装 CJK 字体，跳过中文字形断言。先跑 scripts/ensure-fonts.sh")

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    if skipped:
        print(f"ALL PASSED（{len(skipped)} 项跳过，非通过）：")
        for item in skipped:
            print(f"  ⊘ {item}")
    else:
        print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
