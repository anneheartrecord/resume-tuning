# CJK 字体 / CJK fonts

为了渲染中文简历，把一个**单文件**的开源 CJK 字体放进这个目录，脚本会自动识别。

WeasyPrint 用系统 PingFang（.ttc 字体集合）会大面积丢字形，所以必须用单文件 @font-face 字体。

推荐 OFL 协议、可自由分发的字体（任选其一，下载后放到本目录）：

- **Noto Sans SC** — https://fonts.google.com/noto/specimen/Noto+Sans+SC
- **Source Han Sans / 思源黑体** — https://github.com/adobe-fonts/source-han-sans
- **霞鹜文楷 LXGW WenKai** — https://github.com/lxgw/LxgwWenKai

放好后命名带 `regular` / `bold`（或 `W04` / `W05`）即可被自动识别；
也可以用环境变量显式指定：

```bash
export RESUME_CJK_REGULAR=/path/to/NotoSansSC-Regular.otf
export RESUME_CJK_BOLD=/path/to/NotoSansSC-Bold.otf
```

只做英文简历的话，不放字体也能正常渲染。
