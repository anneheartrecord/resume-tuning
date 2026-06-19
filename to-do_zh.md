# resume-tuning 商业化 to-do

创建日期：2026-06-18

这份文档把 `resume-tuning` 从本地 agent skill 拆成一条可商业化的产品路线。当前仓库已经有一个很强的技术楔子：结构化简历 profile、诚实 JD 匹配、ATS 检查、本地 PDF 渲染、CJK 字体处理和回归测试。商业化应该围绕这些强项展开，不要一开始就去和泛泛的“AI 简历生成器”拼模板数量和营销话术。

## 定位

- [ ] 写清一句话定位。
  - 草案：`隐私优先的简历工作流，把真实经历变成诚实、ATS 可解析、页数取舍清楚的 PDF 简历。`
  - 避免承诺“保证拿面试”“保证过 ATS”。这类话会制造信任风险和合规风险。
- [ ] 选定第一批商业用户。
  - 建议首批人群：中文 / 中英双语求职者，目标是投递全球岗位，需要按 JD 定制英文或双语简历。
  - 第二梯队：转行者、学生 / 应届生、学术 / 研究申请者、产品 / 增长 / 市场候选人。
  - 不要一开始就平均服务所有求职者；“所有岗位可用”是能力，不是首个 go-to-market 切口。
- [ ] 写清竞品差异。
  - Teal / Simplify：更像求职流程工作台，覆盖 job tracker、自动填写和流程管理。
  - Rezi / Kickresume / Resume Worded：强调 AI 写作、简历评分、模板和 review loop。
  - Jobscan：强调 ATS match、关键词覆盖和缺口报告。
  - Reactive Resume / FlowCV：强调简历 builder、开源或隐私友好体验。
  - resume-tuning：强调诚实 JD surface、本地 / 私密工作流、稳定 PDF 交付、中文 / CJK 质量、agent-native 流程。
- [ ] 固化产品原则。
  - 不编造经历、技能、职位、数字、学历、公司或证书。
  - 把 JD 要求分成“已覆盖”“真实具备但没突出”“真实缺口”三档。
  - ATS 覆盖率只是事实信号，不是堆关键词的借口。
  - 最终交付默认推荐一页；资深、学术、作品型或用户明确要求完整展开时支持多页。

## 市场验证

- [ ] 先做 landing page，不要先做完整 SaaS。
  - 必须包含：一句话定位、改写前后对比、上传简历 / 粘贴 JD 流程、隐私承诺、价格预告、waitlist 表单。
  - 至少放 5 个非技术岗示例：产品经理、增长 / 市场、运营、学生 / 应届生、学术 / 研究。
- [ ] 做 20 次人工 concierge 服务。
  - 目标用户：未来 30 天内真实投递岗位的人。
  - 交付物：一份 master resume，加一份按目标 JD 定制的 variant。
  - 记录指标：首稿耗时、修改轮次、用户信任顾虑、付费意愿、是否愿意推荐。
- [ ] 用真实付款意向测试价格。
  - 一次性 AI 初稿：低门槛入口。
  - AI 初稿 + 人工 review：高价 SKU。
  - 月度求职 workspace：只有用户反复要求多份 variant 和 job tracking 时再做。
- [ ] 跟踪验证指标。
  - landing page 到 waitlist 的转化率。
  - 上传简历到付款的转化率。
  - 付费用户中生成 2 份以上 JD variant 的比例。
  - 需要人工 review 的用户比例。
  - 退款 / 不满意原因。
- [ ] 写清不服务的人群。
  - 明确要求伪造经历的人。
  - 需要移民 / 法律类简历保证的人。
  - 只想要花哨模板、不关心内容质量的人。

## 产品 MVP

- [ ] 做一个无代码 Web 流程。
  - 上传旧简历：PDF、DOCX、图片或粘贴文本。
  - 粘贴或上传目标 JD。
  - 确认目标岗位、语言、隐私模式、最想突出的优势和可选模块。
  - 生成前展示结构化 profile，让用户先改事实。
  - 生成 2-3 个版式预览，让用户选择。
  - 导出最终 PDF，并保留可点击链接。
- [ ] 加 master resume 和 variant 模型。
  - master resume 存 canonical facts。
  - JD variant 存针对某个岗位的排序、关键词 surface、弱项删除和 summary 调整。
  - 每个 variant 都保留相对 master resume 的 diff。
- [ ] 把 JD 匹配产品化。
  - UI 上展示 `已覆盖`、`真实具备但没突出`、`真实缺口`。
  - `真实具备但没突出` 进入简历前，必须让用户确认确实是真的。
  - `真实缺口` 只作为求职建议展示，不暗中写进简历。
- [ ] 把质量检查产品化。
  - 页数是否符合目标场景。
  - 文本层是否可提取。
  - 标准 section 是否可识别。
  - 邮箱和链接是否可解析。
  - 是否残留 `[DATA NEEDED]` 或模板占位符。
  - 中文简历是否通过 CJK glyph 渲染核验。
  - 阅读顺序是否从姓名 / 抬头开始。
- [ ] 增加结构化 profile 编辑器。
  - Header / 联系方式编辑。
  - 工作经历 / 项目 / 教育 section 编辑。
  - 技能分组编辑。
  - 待补数据 checklist。
  - 链接校验状态。
- [ ] 增加导出模式。
  - PDF 优先。
  - Markdown 和 JSON profile 给高级用户。
  - DOCX 等 PDF 流程验证出需求后再做。

## 技术平台

- [ ] 拆出适合产品化的边界。
  - 当前 skill 和 CLI scripts 继续作为可信 engine。
  - 只有人工服务验证出需求后，再加 Web app。
  - 公开示例只能用合成数据或公共人物公开资料，不提交真实用户简历。
- [ ] 定义后端数据模型。
  - User。
  - ResumeProfile。
  - ResumeVariant。
  - JobDescription。
  - RenderArtifact。
  - ReviewRequest。
  - Payment。
  - AuditLog。
- [ ] 定义处理 pipeline。
  - Intake extraction。
  - OCR fallback。
  - Profile validation。
  - JD extraction and matching。
  - 真实性敏感改动的用户确认。
  - Resume lint。
  - Template preview render。
  - Final render。
  - ATS / report generation。
- [ ] 设计异步任务。
  - 简历提取和 OCR 可能很慢。
  - PDF 渲染不应该阻塞请求。
  - 大模型调用需要 retry、timeout、cancel 和用户可见状态。
- [ ] 加 artifact storage。
  - 原始上传和生成产物分开存储。
  - 敏感文件静态加密。
  - 每个 artifact 都带 retention 和删除策略。
- [ ] 给 CI 加质量门禁。
  - 跑现有脚本测试。
  - 增加 fixture-based PDF render 测试。
  - 增加 JD matching 和 lint 的 golden examples。
  - 给模板加视觉回归快照。
- [ ] 加 observability。
  - Render 失败率。
  - OCR fallback 比例。
  - 平均首稿生成耗时。
  - Placeholder leak 次数。
  - ATS hard failure 次数。
  - 每个流程步骤的用户修改次数。

## AI 与 review 质量

- [ ] 定义 prompt 和 policy 层。
  - 系统规则：永远不编事实。
  - 输出契约：每个简历改动必须能映射到来源证据或用户确认。
  - 缺失数据只能变成问题，不能变成编造的指标。
- [ ] 增加 evidence tracing。
  - 每条生成 bullet 都链接到源简历文本、用户 note 或显式确认。
  - 标记只做措辞推断但没有新增事实的 bullet。
  - 没有来源的事实不能进入最终导出。
- [ ] 建立分岗位 eval。
  - 工程。
  - 产品。
  - 设计。
  - 增长 / 市场。
  - 销售 / 运营。
  - 学生 / 应届生。
  - 学术 / 研究。
  - 转行者。
- [ ] 建立双语质量检查。
  - 纯中文简历。
  - 纯英文简历。
  - 中文源材料生成英文简历。
  - 英文源材料生成中文简历。
  - 混合语言姓名、学校、公司和链接。
- [ ] 做人工 review 工作流。
  - Reviewer 能看到源简历、JD、生成 profile、diff 和最终 PDF。
  - Reviewer 可以 approve、要求用户补数据或直接改文案。
  - Reviewer 不能 approve 没有证据支持的虚假 claim。
  - 每次 reviewer edit 都记录下来，用于后续 eval 改进。
- [ ] 建 red-team checklist。
  - 用户要求伪造工作年限。
  - 用户要求加自己不会的技能。
  - 用户要求把 intern 改成 manager。
  - 用户要求用假日期掩盖职业空窗。
  - 模型从模糊源文本里编出具体指标。

## 隐私、安全与合规

- [ ] 收集真实简历前先写 privacy policy。
  - 收集什么。
  - 为什么收集。
  - 哪些处理方可能收到数据。
  - 数据保留多久。
  - 用户如何删除数据。
- [ ] 写 terms of service。
  - 不保证就业结果。
  - 用户对事实准确性负责。
  - 服务可以拒绝伪造资历、经历或技能的请求。
  - 人工 review 是建议，不是法律或职业保证。
- [ ] 增加账号级删除。
  - 删除原始上传。
  - 删除生成 PDF。
  - 删除抽取文本和结构化 profile。
  - 删除或匿名化与用户关联的日志。
- [ ] 增加数据保留控制。
  - 上传文件默认保留窗口。
  - 用户可选“导出后立即删除”。
  - 付费人工 review 订单有单独策略。
- [ ] 增加 secrets 和访问控制。
  - API key 不进仓库。
  - 上传简历最小权限访问。
  - 人工 reviewer 独立角色。
  - 每次访问用户文档都写 audit log。
- [ ] 决定模型数据策略。
  - 给隐私敏感用户 BYOK 选项。
  - 使用外部模型 API 时，尽量选择关闭训练 / 数据保留的模式。
  - 只要内容离开本机，就必须明确告知用户。
- [ ] 准备合规 backlog。
  - GDPR 删除 / 导出请求流程。
  - CCPA 风格的数据访问请求流程。
  - 面向 career coach、学校或企业销售时的 DPA 模板。
  - 简历数据泄露 incident response plan。

## 变现

- [ ] 定义初始 SKU。
  - Free：上传简历，给有限诊断报告。
  - One-off：一份打磨好的 PDF 简历。
  - JD pack：3-5 份目标岗位 variant。
  - Premium：AI 初稿 + 人工 review。
  - Coach / B2B：席位、共享 review queue、管理后台。
- [ ] 增加支付流程。
  - 国际用户优先 Stripe。
  - 如果直接服务中国大陆用户，再考虑支付宝 / 微信支付。
  - 支付成功后解锁导出或 review workflow。
  - 支付失败不能丢用户草稿。
- [ ] 增加 quota 和 entitlement。
  - 简历数量。
  - JD variant 数量。
  - PDF 导出次数。
  - 人工 review credits。
  - 不同 plan 的数据保留时长。
- [ ] 增加退款和支持政策。
  - 首稿不满意的明确退款窗口。
  - 因伪造信息请求被拒绝，不退款。
  - 人工 review 的 SLA 和修改次数限制。
- [ ] 跟踪单位经济模型。
  - 每份简历的模型成本。
  - 每次上传的 OCR 成本。
  - PDF 渲染 / 存储成本。
  - 每单人工 reviewer 时间。
  - 每个付费用户的支持成本。

## 增长与分发

- [ ] 做高意图 SEO 页面。
  - `ATS resume checker`。
  - `resume tailored to job description`。
  - `Chinese to English resume`。
  - `one-page resume builder`。
  - `multi-page CV builder`。
  - `product manager resume examples`。
  - `new grad resume examples`。
- [ ] 做样例库。
  - 改写前后对比。
  - 分岗位一页优先模板，并提供页数取舍建议。
  - 带诚实缺口输出的 JD matching 示例。
  - 中文到英文的本地化示例。
- [ ] 做 lead magnets。
  - 免费 ATS 可读性检查。
  - 免费 JD 关键词缺口报告。
  - 免费页数适配检查。
  - 免费错别字 / 一致性检查。
- [ ] 增加分享 loop。
  - 付费用户导出的 PDF 不加公开水印。
  - 免费报告可以带低调的 `generated with resume-tuning` attribution。
  - Referral credits 等付费转化跑通后再加。
- [ ] MVP 后再探索扩展。
  - 浏览器插件，从招聘网页导入 JD。
  - LinkedIn profile import。
  - Job tracker。
  - Autofill helper。
  - 基于最终简历生成面试准备材料。
- [ ] 做渠道合作。
  - Career coaches。
  - 留学 / 海外求职咨询。
  - 大学 career center。
  - Bootcamp。
  - 招聘机构。

## 运营

- [ ] 定义支持流程。
  - 上传失败。
  - PDF 渲染失败。
  - 用户需要判断是否保留多页简历。
  - 用户不同意 JD 缺口分类。
  - 用户要求删除所有数据。
  - 用户要求伪造 claim。
- [ ] 写 reviewer guidelines。
  - 语气和文案风格。
  - Reviewer 可以改什么。
  - Reviewer 必须拒绝什么。
  - 如何追问缺失数据。
  - 如何处理敏感个人信息。
- [ ] 写 incident runbooks。
  - 模型服务故障。
  - 支付服务故障。
  - PDF 渲染服务故障。
  - 数据删除失败。
  - 疑似数据泄露。
- [ ] 定义服务指标。
  - AI-only 首稿耗时。
  - 人工 review 交付时长。
  - 支持首次响应时间。
  - 导出可靠性。

## 文档 backlog

- [ ] 重写 `README.md`，改成 product-first 叙事。
  - 第一屏说明帮助谁、交付什么结果。
  - 保留现有技术细节，但移到价值主张后面。
  - 加一条从 example profile + JD 到最终 PDF 的完整 demo flow。
- [ ] 同步重写 `README_EN.md`。
  - 不必逐字直译；英文定位可以按英文用户习惯表达。
  - 保留语言切换链接和 badges。
- [ ] 新增 `docs/overview.md`。
  - 产品承诺。
  - 当前能力。
  - 非目标。
  - 信任模型。
- [ ] 新增 `docs/privacy.md`。
  - 当前本地执行方式。
  - 未来 SaaS 数据策略。
  - 用户数据处理规则。
- [ ] 新增 `docs/comparison.md`。
  - 对比 Teal、Rezi、Jobscan、Kickresume、Resume Worded、Simplify、Reactive Resume、FlowCV。
  - 重点写定位和取舍，不做 feature-count 营销。
- [ ] 新增 `docs/roadmap.md`。
  - 人工 concierge 验证。
  - Web MVP。
  - 付费导出。
  - 人工 review。
  - B2B / coach workspace。
- [ ] 新增 `docs/demo-flow.md`。
  - 输入。
  - 命令或 Web 步骤。
  - 输出。
  - 质量门禁。
  - 预期 artifacts。

## 建议阶段

### Phase 0：收紧开源项目

- [ ] 更新 README 和 README_EN，改成 product-first 定位。
- [ ] 增加 overview、privacy、comparison、roadmap、demo flow 文档。
- [ ] 增加更多非技术岗样例。
- [ ] 保持现有 CLI 和 skill workflow 稳定。

退出标准：

- 新访问者 10 秒内能理解产品承诺。
- 技术用户不读源码也能跑完整 demo。
- 非技术用户能理解未来产品要解决什么问题。

### Phase 1：人工 concierge 验证

- [ ] 上线 landing page，收 waitlist 和 paid pilot。
- [ ] 用当前本地工作流交付 20 单人工简历服务。
- [ ] 记录每个应该产品化的人工步骤。
- [ ] 验证至少一个付费 SKU。

退出标准：

- 至少 5 个付费用户。
- 至少 3 个用户要求 JD-specific variants。
- 至少 2 个用户要求人工 review 或专家反馈。
- 明确排名前 10 的重复支持问题。

### Phase 2：Web MVP

- [ ] 做上传、JD 粘贴、profile 编辑、预览和 PDF 导出。
- [ ] 最终导出前增加支付。
- [ ] 增加账号删除和数据保留控制。
- [ ] 增加等价于当前 CLI 检查的质量门禁。

退出标准：

- 用户无需人工 operator 就能完成一次付费简历交付。
- 支持输入下的 render 成功率超过 95%。
- 最终导出不能包含 placeholder 或 `[DATA NEEDED]`。
- 用户能删除自己的上传数据。

### Phase 3：可信 review 产品

- [ ] 增加人工 review queue。
- [ ] 增加 reviewer diff 和 approval tools。
- [ ] 增加 premium pricing。
- [ ] 把 reviewer edits 回流到 eval。

退出标准：

- 扣掉 reviewer 时间成本后，人工 review 仍有正毛利。
- Reviewer 不用本地脚本也能处理订单。
- Reviewer edits 能降低用户修改轮次。

### Phase 4：求职工作流扩展

- [ ] 只有当用户已经频繁生成 JD variants 时，再加 job tracker。
- [ ] 只有当 JD import 成为高频痛点时，再加浏览器插件。
- [ ] 增加基于最终简历的面试准备。
- [ ] 证明重复使用后，再做 coach / B2B workspace。

退出标准：

- 每个付费用户的重复 JD variants 足以支撑工作流扩展。
- 用户主动要求在产品内管理岗位，而不是只导出一次。
- Coach 或机构用户明确需要共享 review queue。

## 近期下一步

- [ ] 创建 `docs/overview.md`、`docs/privacy.md`、`docs/comparison.md`、`docs/roadmap.md` 和 `docs/demo-flow.md`。
- [ ] 围绕 product-first 叙事更新 `README.md` 和 `README_EN.md`。
- [ ] 至少增加一个非技术岗 sample profile 和 JD。
- [ ] 增加一条能从 fixtures 跑出 demo artifacts 的工作流。
- [ ] 基于上面的定位草拟 landing page 文案。
- [ ] 做 5 次人工简历 pilot，再开始做 Web UI。

## 已参考来源

- Teal：resume builder、job tracker、Chrome extension、pricing、JD keyword matching。
- Rezi：AI resume builder、ATS-friendly templates、Rezi score、expert review 定位。
- Jobscan：ATS resume checker、match-rate report、missing skills report、resume builder、ATS tips。
- Simplify：Copilot autofill、auto-tailoring、application tracking、saved answers。
- Reactive Resume 和 FlowCV：builder、隐私友好 / 开源定位。
