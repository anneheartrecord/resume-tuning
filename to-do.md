# resume-tuning commercialization to-do

Created: 2026-06-18

This document turns `resume-tuning` from a local agent skill into a commercial product roadmap. The current repo already has the strongest technical wedge: structured resume profiles, honest JD matching, ATS checks, local PDF rendering, CJK font handling, and regression tests. Commercialization should build around that wedge instead of competing on generic "AI resume builder" claims.

## Positioning

- [ ] Define the primary wedge in one sentence.
  - Draft: "Privacy-first resume workflow that turns real experience into honest, ATS-readable one-page PDFs."
  - Avoid claims like "guaranteed interview" or "beats ATS" because they create trust and compliance risk.
- [ ] Pick the first commercial audience.
  - Recommended first audience: Chinese / bilingual job seekers applying to global roles who need JD-specific English or bilingual resumes.
  - Secondary audiences: career switchers, students/new grads, academic/research applicants, product/growth/marketing candidates.
  - Do not start by serving every job seeker equally; "any role" is a capability, not the initial go-to-market segment.
- [ ] Write the competitive contrast.
  - Teal/Simplify: broader job tracker and workflow automation.
  - Rezi/Kickresume/Resume Worded: AI writing, resume scoring, templates, and review loops.
  - Jobscan: ATS match and keyword coverage.
  - Reactive Resume/FlowCV: builder experience, open-source or privacy-friendly tooling.
  - resume-tuning: honest JD surfacing, local/private workflow, strong PDF delivery, Chinese/CJK quality, agent-native process.
- [ ] Define the product principles.
  - Never fabricate experience, skills, titles, numbers, education, company names, or certifications.
  - Separate "covered", "real but buried", and "missing" JD requirements.
  - Treat ATS coverage as a signal, not a license to stuff keywords.
  - Keep the final deliverable one page unless the user explicitly selects an academic CV mode.

## Market validation

- [ ] Create a landing page before building a full SaaS.
  - Required sections: one-line positioning, before/after example, upload/JD workflow, privacy promise, pricing teaser, waitlist form.
  - Include at least 5 non-technical examples: product manager, growth marketer, operations, student/new grad, academic/researcher.
- [ ] Run 20 manual concierge sessions.
  - Target: users who are actively applying within the next 30 days.
  - Deliverable: one master resume plus one JD-specific variant.
  - Measure: time to first draft, revision count, user trust objections, willingness to pay, referral intent.
- [ ] Test pricing with real payment intent.
  - One-off AI draft: low-friction entry price.
  - AI draft + human review: premium SKU.
  - Monthly job-search workspace: only after users ask for repeated variants and tracking.
- [ ] Track validation metrics.
  - Waitlist conversion rate from landing page.
  - Upload-to-payment conversion.
  - Paid users who create at least 2 JD variants.
  - Percentage of users who request human review.
  - Refund / dissatisfaction reasons.
- [ ] Document ICP exclusions.
  - Users asking for fabricated experience.
  - Users needing regulated immigration/legal resume guarantees.
  - Users who only want decorative templates and do not care about content quality.

## Product MVP

- [ ] Build a no-code web flow.
  - Upload old resume: PDF, DOCX, image, or pasted text.
  - Paste or upload target JD.
  - Confirm target role, language, privacy mode, strongest selling point, and optional modules.
  - Show structured profile before generation so users can correct facts.
  - Generate 2-3 layout previews and let the user choose.
  - Export final PDF with clickable links.
- [ ] Add a master resume and variant model.
  - Master resume stores canonical facts.
  - JD variants store reordered bullets, surfaced keywords, omitted weak items, and target-specific summary.
  - Every variant keeps a diff against the master resume.
- [ ] Productize JD matching.
  - Show `covered`, `real but buried`, and `missing` groups.
  - Let users confirm whether a `real but buried` item is genuinely true before it enters the resume.
  - Keep missing requirements as coaching feedback, not hidden prompts to stuff terms.
- [ ] Productize quality checks.
  - One page.
  - Text layer extractable.
  - Standard sections recognized.
  - Email and links parseable.
  - No `[DATA NEEDED]` or template placeholder leaks.
  - CJK glyph rendering verified for Chinese resumes.
  - Reading order starts with name/header.
- [ ] Add an editable structured profile UI.
  - Header/contact editor.
  - Experience/project/education section editor.
  - Skill group editor.
  - Data-needed checklist.
  - Link verification status.
- [ ] Add export modes.
  - PDF first.
  - Markdown and JSON profile for power users.
  - DOCX only after PDF flow proves demand.

## Technical platform

- [ ] Split the repo into product-ready surfaces.
  - Keep the current skill and CLI scripts as the trusted engine.
  - Add a web app only when the manual service validates demand.
  - Keep public examples synthetic or public-figure-derived; never commit real user resumes.
- [ ] Define the backend data model.
  - User.
  - ResumeProfile.
  - ResumeVariant.
  - JobDescription.
  - RenderArtifact.
  - ReviewRequest.
  - Payment.
  - AuditLog.
- [ ] Define the processing pipeline.
  - Intake extraction.
  - OCR fallback.
  - Profile validation.
  - JD extraction and matching.
  - User confirmation for truth-sensitive changes.
  - Resume lint.
  - Template preview render.
  - Final render.
  - ATS/report generation.
- [ ] Design asynchronous jobs.
  - Resume extraction and OCR can be slow.
  - PDF rendering should run off the request path.
  - Large model calls need retry, timeout, cancellation, and user-visible state.
- [ ] Add artifact storage.
  - Store original uploads separately from generated outputs.
  - Encrypt sensitive files at rest.
  - Attach retention and deletion policy to every artifact.
- [ ] Add quality gates to CI.
  - Run existing script tests.
  - Add fixture-based PDF render tests.
  - Add golden examples for JD matching and lint output.
  - Add visual regression snapshots for templates.
- [ ] Add observability.
  - Render failure rate.
  - OCR fallback rate.
  - Average draft generation latency.
  - Placeholder leak count.
  - ATS hard-failure count.
  - User revision count by flow step.

## AI and review quality

- [ ] Define a prompt and policy layer.
  - System-level rule: never invent facts.
  - Output contract: every resume change must map to source evidence or user confirmation.
  - Missing data must be represented as questions, not hallucinated metrics.
- [ ] Add evidence tracing.
  - Link every generated bullet to source resume text, user note, or explicit confirmation.
  - Mark bullets that contain inferred phrasing but no new fact.
  - Block final export when a fact has no source.
- [ ] Add role-specific evaluation sets.
  - Engineering.
  - Product.
  - Design.
  - Growth/marketing.
  - Sales/operations.
  - Student/new grad.
  - Academic/research.
  - Career switcher.
- [ ] Add bilingual quality checks.
  - Chinese-only resume.
  - English-only resume.
  - Chinese source to English resume.
  - English source to Chinese resume.
  - Mixed-language names, schools, companies, and links.
- [ ] Create a human review workflow.
  - Reviewer sees source resume, JD, generated profile, diff, and final PDF.
  - Reviewer can approve, request user data, or edit copy.
  - Reviewer cannot approve fabricated or unsupported claims.
  - Every reviewer edit is logged for future eval improvements.
- [ ] Build a red-team checklist.
  - User asks to fake years of experience.
  - User asks to add a skill they do not have.
  - User asks to inflate title from intern to manager.
  - User asks to hide employment gaps with false dates.
  - Model invents a metric from vague source text.

## Privacy, security, and compliance

- [ ] Write a privacy policy before collecting real resumes.
  - What is collected.
  - Why it is collected.
  - Which processors may receive it.
  - How long it is retained.
  - How users can delete it.
- [ ] Write terms of service.
  - No employment guarantee.
  - User is responsible for factual accuracy.
  - Service may refuse requests to fabricate credentials or experience.
  - Human review is guidance, not legal/career guarantee.
- [ ] Add account-level deletion.
  - Delete original uploads.
  - Delete generated PDFs.
  - Delete extracted text and structured profiles.
  - Delete or anonymize logs connected to the user.
- [ ] Add data retention controls.
  - Default retention window for uploads.
  - User-controlled "delete immediately after export" option.
  - Separate policy for paid human-review orders.
- [ ] Add secrets and access controls.
  - No API keys in repo.
  - Least-privilege access to uploaded resumes.
  - Separate admin role for human reviewers.
  - Audit logs for every access to user documents.
- [ ] Decide on model data posture.
  - BYOK option for privacy-sensitive users.
  - Option to disable training/data retention when using external model APIs.
  - Clear disclosure when content leaves the local machine.
- [ ] Prepare compliance backlog.
  - GDPR deletion/export request flow.
  - CCPA-style data access request flow.
  - DPA template if selling to career coaches, schools, or companies.
  - Incident response plan for resume data exposure.

## Monetization

- [ ] Define initial SKUs.
  - Free: upload/resume diagnosis with limited report.
  - One-off: one polished PDF resume.
  - JD pack: 3-5 target-specific variants.
  - Premium: AI draft plus human review.
  - Coach/B2B: seats, shared review queue, admin dashboard.
- [ ] Add payment flow.
  - Stripe for international users.
  - Consider Alipay/WeChat Pay only if serving mainland users directly.
  - Payment success must unlock export or review workflow.
  - Failed payment must not lose the user's draft.
- [ ] Add quota and entitlement system.
  - Number of resumes.
  - Number of JD variants.
  - Number of PDF exports.
  - Human review credits.
  - Retention period by plan.
- [ ] Add refund and support policy.
  - Clear refund window for unsatisfactory first draft.
  - No refund for fabricated-information requests that are refused.
  - Human review SLA and revision limit.
- [ ] Track unit economics.
  - Model cost per resume.
  - OCR cost per upload.
  - PDF render/storage cost.
  - Human reviewer time per order.
  - Support time per paid user.

## Growth and distribution

- [ ] Build SEO pages around high-intent queries.
  - "ATS resume checker".
  - "resume tailored to job description".
  - "Chinese to English resume".
  - "one-page resume builder".
  - "product manager resume examples".
  - "new grad resume examples".
- [ ] Create example libraries.
  - Before/after rewrite examples.
  - Role-specific one-page templates.
  - JD matching examples with honest missing-skill output.
  - Chinese to English localization examples.
- [ ] Build lead magnets.
  - Free ATS readability check.
  - Free JD keyword gap report.
  - Free one-page fit check.
  - Free resume typo/consistency check.
- [ ] Add sharing loops.
  - Exported PDF should not contain public watermark for paid users.
  - Free report can include subtle "generated with resume-tuning" attribution.
  - Add referral credits only after paid conversion works.
- [ ] Explore extensions after MVP.
  - Browser extension to import JD from job pages.
  - LinkedIn profile import.
  - Job tracker.
  - Autofill helper.
  - Interview prep generated from the final resume.
- [ ] Build partnerships.
  - Career coaches.
  - Overseas-study consultants.
  - University career centers.
  - Bootcamps.
  - Recruiting agencies.

## Operations

- [ ] Define support workflows.
  - Upload failed.
  - PDF render failed.
  - Resume exceeded one page.
  - User disagrees with JD missing-skill classification.
  - User wants to delete all data.
  - User asks for fabricated claims.
- [ ] Create reviewer guidelines.
  - Tone and copy style.
  - What reviewers may edit.
  - What reviewers must reject.
  - How to ask for missing data.
  - How to handle sensitive personal information.
- [ ] Create incident runbooks.
  - Model outage.
  - Payment provider outage.
  - PDF rendering outage.
  - Data deletion failure.
  - Suspected data exposure.
- [ ] Define service-level targets.
  - AI-only draft latency.
  - Human review turnaround.
  - Support first response time.
  - Export reliability.

## Documentation backlog

- [ ] Rewrite `README.md` for product-first positioning.
  - First screen should explain who it helps and what outcome it delivers.
  - Keep the existing technical details, but move them below the value proposition.
  - Add a full demo flow from example profile and JD to final PDF.
- [ ] Rewrite `README_EN.md` with the same structure.
  - Do not make it a literal translation if English positioning needs different phrasing.
  - Keep language switch links and badges.
- [ ] Add `docs/overview.md`.
  - Product promise.
  - Current capabilities.
  - Non-goals.
  - Trust model.
- [ ] Add `docs/privacy.md`.
  - Local execution today.
  - Future SaaS data posture.
  - User data handling rules.
- [ ] Add `docs/comparison.md`.
  - Compare against Teal, Rezi, Jobscan, Kickresume, Resume Worded, Simplify, Reactive Resume, and FlowCV.
  - Focus on positioning and trade-offs, not feature-count marketing.
- [ ] Add `docs/roadmap.md`.
  - Manual concierge validation.
  - Web MVP.
  - Paid exports.
  - Human review.
  - B2B/coach workspace.
- [ ] Add `docs/demo-flow.md`.
  - Inputs.
  - Commands or web steps.
  - Outputs.
  - Quality gates.
  - Expected artifacts.

## Suggested phases

### Phase 0: tighten the open-source project

- [ ] Update README and README_EN for product-first positioning.
- [ ] Add docs for overview, privacy, comparison, roadmap, and demo flow.
- [ ] Add more role-diverse examples.
- [ ] Keep the current CLI and skill workflow stable.

Exit criteria:

- A new visitor understands the product promise in 10 seconds.
- A technical user can run a complete demo without reading source code.
- A non-technical user can understand what the future product will do.

### Phase 1: concierge validation

- [ ] Launch a landing page with waitlist and paid pilot.
- [ ] Deliver 20 manual resume orders using the current local workflow.
- [ ] Record every manual step that should become product UI.
- [ ] Validate at least one paid SKU.

Exit criteria:

- At least 5 paid users.
- At least 3 users request JD-specific variants.
- At least 2 users ask for human review or expert feedback.
- Clear list of the top 10 repeated support questions.

### Phase 2: web MVP

- [ ] Build upload, JD paste, profile edit, preview, and PDF export.
- [ ] Add payment before final export.
- [ ] Add account deletion and retention controls.
- [ ] Add quality gates equivalent to the current CLI checks.

Exit criteria:

- A user can complete one paid resume without manual operator help.
- Render success rate is above 95% on supported inputs.
- No final export can contain placeholders or `[DATA NEEDED]`.
- Users can delete their uploaded data.

### Phase 3: trusted review product

- [ ] Add human review queue.
- [ ] Add reviewer diff and approval tools.
- [ ] Add premium pricing.
- [ ] Add feedback loops from reviewer edits into evals.

Exit criteria:

- Human review margin is positive after reviewer time cost.
- Reviewers can process an order without using local scripts.
- Reviewer edits reduce user revision count.

### Phase 4: job-search workflow expansion

- [ ] Add job tracker only if users already create repeated JD variants.
- [ ] Add browser extension only if JD import becomes a repeated pain.
- [ ] Add interview prep generated from final resume.
- [ ] Add coach/B2B workspace after proving repeat usage.

Exit criteria:

- Repeated JD variants per paid user justify workflow expansion.
- Users ask to manage jobs inside the product instead of exporting once.
- Coach or institutional users request shared review queues.

## Near-term next actions

- [ ] Create `docs/overview.md`, `docs/privacy.md`, `docs/comparison.md`, `docs/roadmap.md`, and `docs/demo-flow.md`.
- [ ] Update `README.md` and `README_EN.md` around the new product-first story.
- [ ] Add at least one non-technical sample profile and JD.
- [ ] Add a generated demo artifact workflow that can run from fixtures.
- [ ] Draft landing page copy from the positioning section above.
- [ ] Run 5 manual resume pilots before building a web UI.

## Sources checked

- Teal: resume builder, job tracker, Chrome extension, pricing, job description keyword matching.
- Rezi: AI resume builder, ATS-friendly templates, Rezi score, expert review positioning.
- Jobscan: ATS resume checker, match-rate report, missing skills report, resume builder, ATS-specific tips.
- Simplify: Copilot autofill, auto-tailoring, application tracking, saved answers.
- Reactive Resume and FlowCV: builder and privacy-friendly/open-source positioning.
