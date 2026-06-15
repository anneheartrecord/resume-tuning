#!/usr/bin/env python3
"""resume-tuning 的 PDF 工具：提取来源简历、渲染并自动压到一页。

子命令：
  extract <in.pdf>            提取文本 + 已嵌超链接，并判断是否图片/扫描型（需走视觉 OCR）。
  render  <in.html> <out.pdf> 渲染成 PDF；若超过一页，自动逐级压缩重渲染，直到一页或压无可压。

设计目标：把「渲染到刚好一页」「核对链接」「识别扫描件」这些机械活做成确定性流程，
而不是每次让模型手工试。依赖 weasyprint + pypdf。
"""

import os
import re
import subprocess
import sys


def _ensure_native_libs_then_reexec() -> None:
    """macOS 上 WeasyPrint 需要 Homebrew 的 pango/cairo 等原生库。

    dyld 在 dlopen 时读取 DYLD_FALLBACK_LIBRARY_PATH，所以这里设好环境变量后
    重新 exec 一次本进程，保证 import weasyprint 时能找到库。只重 exec 一次。
    """
    if os.environ.get("_RESUME_PDF_REEXEC"):
        return
    fallback = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if sys.platform == "darwin" and "/lib" not in fallback:
        try:
            brew_prefix = subprocess.check_output(
                ["brew", "--prefix"], text=True
            ).strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            brew_prefix = ""
        if brew_prefix:
            lib_dir = f"{brew_prefix}/lib"
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
                f"{lib_dir}:{fallback}" if fallback else lib_dir
            )
            os.environ["_RESUME_PDF_REEXEC"] = "1"
            os.execv(sys.executable, [sys.executable, *sys.argv])


def pdf_pages_and_links(pdf_path: str) -> tuple[int, list[str]]:
    """返回 PDF 的页数和所有嵌入的超链接 URI。"""
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    links: list[str] = []
    for page in reader.pages:
        for annotation in page.get("/Annots") or []:
            obj = annotation.get_object()
            if obj.get("/Subtype") == "/Link":
                uri = (obj.get("/A") or {}).get("/URI")
                if uri:
                    links.append(uri)
    return len(reader.pages), links


def extract_source(pdf_path: str) -> int:
    """打印来源简历的文本、链接，并判断是否为图片/扫描型。

    图片型 PDF（扫描件、导出的图片）几乎提不出文本层，必须改用视觉 OCR：
    让 agent 直接用多模态能力读这张 PDF 并转写内容，而不是依赖 pypdf。
    """
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = "".join((page.extract_text() or "") for page in reader.pages)
    _, links = pdf_pages_and_links(pdf_path)

    chars_per_page = len(text) / max(len(reader.pages), 1)
    is_image_based = chars_per_page < 120

    print(f"pages: {len(reader.pages)}")
    print(f"text_chars: {len(text)}")
    print(f"links: {links}")
    if is_image_based:
        print("VERDICT: IMAGE_BASED — 文本层几乎为空，pypdf 提不出内容。")
        print("ACTION: 改用视觉 OCR — 让 agent 直接读这张 PDF（多模态）转写正文，别依赖本提取结果。")
    else:
        print("VERDICT: TEXT_BASED — 可直接使用下面的文本。")
        print("----- TEXT -----")
        print(text)
    return 0


def _scale_style_block(html: str, factor: float) -> str:
    """把 <style> 里所有 pt / mm 尺寸整体乘以 factor，实现等比缩放。

    factor>1 放大（内容少时撑满一页），factor<1 缩小（内容多时压进一页）。
    只动 <style> 块内的尺寸，不碰正文；字号、边距、间距、边框、圆角一起等比变，
    视觉比例不变，只是整体大小变。
    """
    def scale_match(match: re.Match) -> str:
        value = float(match.group(1)) * factor
        return f"{value:.2f}{match.group(2)}"

    def scale_style(style_match: re.Match) -> str:
        scaled = re.sub(r"([\d.]+)(pt|mm)", scale_match, style_match.group(1))
        return f"<style>{scaled}</style>"

    return re.sub(r"<style>(.*?)</style>", scale_style, html, count=1, flags=re.DOTALL)


def _cjk_font_uris() -> "tuple[str, str] | None":
    """返回内嵌 CJK 字体（常规 / 加粗）的 file:// 绝对路径，找不到返回 None。

    模板里 @font-face 用 __CJK_REGULAR__ / __CJK_BOLD__ 占位，渲染前替换成这里的
    真实路径。**必须用单文件 @font-face 字体**：直接靠系统 PingFang（.ttc 字体集合）
    时 WeasyPrint 子集化会大面积丢中文字形，PDF 在预览里是乱码/空白。

    字体查找顺序：
    1. 环境变量 RESUME_CJK_REGULAR / RESUME_CJK_BOLD（显式指定）。
    2. assets/fonts/ 下的字体文件（W04/Regular 当常规，W05/Medium/Bold 当加粗）。
    找不到返回 None —— 中文会缺字形，渲染纯英文简历仍可用。装 OFL 字体见 README。
    """
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(skill_dir, "assets", "fonts")

    env_regular = os.environ.get("RESUME_CJK_REGULAR")
    env_bold = os.environ.get("RESUME_CJK_BOLD")
    if env_regular and os.path.exists(env_regular):
        bold = env_bold if (env_bold and os.path.exists(env_bold)) else env_regular
        return f"file://{env_regular}", f"file://{bold}"

    if os.path.isdir(fonts_dir):
        files = sorted(
            f for f in os.listdir(fonts_dir)
            if f.lower().endswith((".ttf", ".otf"))
        )
        if files:
            def pick(keywords: tuple[str, ...], default: str) -> str:
                for name in files:
                    if any(k in name.lower() for k in keywords):
                        return name
                return default
            regular = pick(("w04", "regular", "light"), files[0])
            bold = pick(("w05", "medium", "bold", "semibold"), regular)
            return (
                f"file://{os.path.join(fonts_dir, regular)}",
                f"file://{os.path.join(fonts_dir, bold)}",
            )
    return None


def render_one_page(html_path: str, out_path: str) -> int:
    """渲染 HTML 到 PDF；超过一页就逐级压缩重渲染，直到一页或压无可压。"""
    from weasyprint import HTML

    base_url = os.path.dirname(os.path.abspath(html_path))
    html = open(html_path, encoding="utf-8").read()
    fonts = _cjk_font_uris()
    if fonts:
        html = html.replace("__CJK_REGULAR__", fonts[0]).replace("__CJK_BOLD__", fonts[1])
    else:
        # 没有 CJK 字体：删掉占位 @font-face 行，避免 src:url("__CJK_*__") 坏链接。
        # 纯英文简历照常渲染；中文简历会缺字形，需按 README 装 OFL 字体。
        html = re.sub(r'\s*@font-face\s*\{[^}]*__CJK_(?:REGULAR|BOLD)__[^}]*\}', '', html)
        print("NOTE: 未找到 CJK 字体，中文将无法正确渲染。装 OFL 字体或设 RESUME_CJK_REGULAR，见 README。")
    def render_at(factor: float) -> tuple[int, list[str]]:
        scaled = html if factor == 1.0 else _scale_style_block(html, factor)
        HTML(string=scaled, base_url=base_url).write_pdf(out_path)
        return pdf_pages_and_links(out_path)

    pages, links = render_at(1.0)
    best_factor = 1.0

    if pages == 1:
        # 内容没撑满一页 → 等比放大，找仍能保持 1 页的最大尺寸，把页面填起来。
        factor = 1.0
        while factor < 1.6:
            factor = round(factor + 0.05, 2)
            page_count, _ = render_at(factor)
            if page_count == 1:
                best_factor = factor
            else:
                break
    else:
        # 超过一页 → 等比缩小，找第一个能塞进 1 页的尺寸。
        factor = 1.0
        while factor > 0.6:
            factor = round(factor - 0.05, 2)
            page_count, _ = render_at(factor)
            if page_count == 1:
                best_factor = factor
                break

    pages, links = render_at(best_factor)
    print(f"pages: {pages}")
    print(f"links: {links}")
    print(f"scale_factor: {best_factor}  (>1 放大填页 / <1 压缩进页)")
    if pages > 1:
        print("WARNING: 缩到最小仍超过一页 —— 内容太多，需要人工删减经历/要点再渲染。")
        return 1
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "extract" and len(argv) == 3:
        return extract_source(argv[2])
    if len(argv) >= 2 and argv[1] == "render" and len(argv) == 4:
        return render_one_page(argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    _ensure_native_libs_then_reexec()
    sys.exit(main(sys.argv))
