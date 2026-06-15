#!/usr/bin/env bash
# ensure-fonts.sh —— 确保 assets/fonts/ 下有一个可用的单文件 CJK 字体。
#
# 为什么需要：WeasyPrint 直接用系统 PingFang(.ttc) 子集化会大面积丢中文字形，
# PDF 在预览里是乱码/空白。必须用单文件 @font-face 字体。本脚本在没有字体时，
# 下载一个 OFL 协议（可自由分发）的中文字体放进 assets/fonts/，让 skill 开箱即用。
#
# 已经有字体（含自备的商业字体）就直接跳过，不覆盖。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/assets/fonts"
mkdir -p "$FONTS_DIR"

# 已有任意 ttf/otf 就认为齐了，不重复下载（ttf / otf 分开判，避免某一类无匹配时误判）。
if compgen -G "$FONTS_DIR/*.ttf" >/dev/null || compgen -G "$FONTS_DIR/*.otf" >/dev/null; then
  echo "已有 CJK 字体，跳过下载:"
  ls -1 "$FONTS_DIR"/*.ttf "$FONTS_DIR"/*.otf 2>/dev/null | sed 's|.*/|  |' || true
  exit 0
fi

# 霞鹜文楷 LXGW WenKai（OFL，单文件 TTF，含简繁，适合简历的人文楷体观感）。
# 主源 + 镜像都试，任一成功即停。
URLS=(
  "https://github.com/lxgw/LxgwWenKai/releases/download/v1.520/LXGWWenKai-Regular.ttf"
  "https://cdn.jsdelivr.net/gh/lxgw/LxgwWenKai@v1.520/fonts/TTF/LXGWWenKai-Regular.ttf"
)
target="$FONTS_DIR/LXGWWenKai-Regular.ttf"

echo "未找到 CJK 字体，开始下载霞鹜文楷（OFL）..."
for url in "${URLS[@]}"; do
  echo "  尝试：$url"
  if curl -fSL --connect-timeout 15 --retry 2 -o "$target" "$url" 2>/dev/null && [ -s "$target" ]; then
    size=$(wc -c < "$target")
    # 粗校验：字体文件应远大于 1MB，太小多半是错误页。
    if [ "$size" -gt 1000000 ]; then
      echo "已下载: ${target} ($((size / 1024 / 1024)) MB)"
      exit 0
    fi
    echo "  下载内容过小 (${size} 字节), 换下一个源"
    rm -f "$target"
  fi
done

rm -f "$target"
cat >&2 <<'EOF'
自动下载失败（可能无网络）。请手动下载任一 OFL 中文字体放进 assets/fonts/：
   - 霞鹜文楷 https://github.com/lxgw/LxgwWenKai/releases
   - Noto Sans SC https://fonts.google.com/noto/specimen/Noto+Sans+SC
   - 思源黑体 https://github.com/adobe-fonts/source-han-sans/releases
或用环境变量指定已有字体：export RESUME_CJK_REGULAR=/path/to/font.otf
EOF
exit 1
