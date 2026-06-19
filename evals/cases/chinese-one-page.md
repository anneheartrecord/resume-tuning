# chinese-page-count

## Input

用户要中文简历，内容包含中文姓名、中文项目经历、邮箱、GitHub 和作品集链接。

## Expected Behavior

- 使用内嵌 CJK 单文件字体。
- 三套模板预览默认优先适配为一页；内容确实过多时允许多页并提示页数取舍。
- 定稿前检查链接、占位符和中文 glyph。
- 通过 `qlmanage` 转 PNG 后肉眼确认中文字形不为空白、不乱码。

## Must Not

- 不依赖系统 PingFang `.ttc` 字体集合。
- 不只看 PDF 文本层就判定中文渲染成功。
