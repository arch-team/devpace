# devpace Promotion Tracker

> Operational tracking for the growth action plan. Updated as items complete.

## 90-Day Targets

| Metric | 30 days | 60 days | 90 days | Current |
|--------|---------|---------|---------|---------|
| GitHub Stars | 20-50 | 80-150 | 150-300 | 0 |
| Marketplace installs | 10-30 | 50-100 | 100-200 | N/A |
| Blog posts published | 1 | 2 | 3 | 0 |
| User feedback received | 3-5 | 10+ | 15+ | 0 |

---

## Wave 1: Immediate Actions (Week 1, ~4h)

### 1.1 Aggregator Platform Registration
- [ ] claudemarketplaces.com: Submit GitHub URL → [submission link]
- [ ] awesome-agent-skills: commit ready (`cb74f49` in `/tmp/awesome-agent-skills`), push blocked by Code Defender → needs personal device push + PR creation
- [ ] awesome-claude-code: PR submitted → [PR link]
- **Reference**: `docs/plans/aggregator-submissions.md` ← ready-to-paste content prepared

### 1.2 Social Preview Version Update
- [x] `.github/social-preview.svg` updated v1.4.0 → v1.5.0
- [ ] `.github/social-preview.png` regenerated from SVG
  - **Manual step**: Open SVG in browser → screenshot at 1280x640, or:
  - `brew install cairo && python3 -c "import cairosvg; cairosvg.svg2png(url='.github/social-preview.svg', write_to='.github/social-preview.png', output_width=1280, output_height=640)"`

### 1.3 GitHub Repository Optimization
- [ ] Verify About description: "Give your Claude Code projects a steady development pace — requirements change, rhythm stays."
- [ ] Verify 8 GitHub Topics are active: `claude-code`, `plugin`, `devops`, `bizdevops`, `ai-development`, `project-management`, `quality-gates`, `change-management`
- [ ] Enable GitHub Discussions (Settings → Features → Discussions)
- [x] Discussion templates created (`.github/DISCUSSION_TEMPLATE/share-your-experience.yml`, `show-and-tell.yml`)
- [x] Feedback issue template created (`.github/ISSUE_TEMPLATE/feedback.md`)
- [x] Issue config links to Discussions and docs (`.github/ISSUE_TEMPLATE/config.yml`)

---

## Wave 2: Core Preparation (Weeks 2-3, ~8-12h)

### 2.1 Terminal GIF Demos
- [x] VHS tape scripts prepared (`scripts/record-demos/gif-1|2|3-*.tape`)
- [x] Recording guide written (`scripts/record-demos/README.md`)
- [ ] Prepare clean demo project environment
- [ ] Record GIF-1: /pace-init (15-20s)
- [ ] Record GIF-2: Natural language dev (20-30s)
- [ ] Record GIF-3: Cross-session restore (15-20s)
- [ ] Embed GIFs in README.md hero section

### 2.2 Marketplace Description
- [x] marketplace.json description optimized (user-pain-point-driven)

### 2.3 Marketplace Submission
- [x] Confirmed: **无官方提交流程**。Anthropic 官方 Marketplace 由 Anthropic 自行维护，无公开 submission form。分发方式是自建 marketplace repo（`/plugin marketplace add arch-team/devpace`），已配置在 README Installation 中
- [ ] 可选：通过 Anthropic Community Forum 或 GitHub Issues 请求收录到官方 Marketplace
- [ ] Prepare submission materials (README + GIFs)
- [ ] Track review status → [submission link]

### 🔖 暂停点 (2026-02-26)

**已完成**：
- Wave 1 awesome-agent-skills: README 编辑 + commit 完成（`cb74f49` @ `/tmp/awesome-agent-skills:add-devpace`），push 被 Code Defender 阻止
- Wave 2.2: marketplace.json 已优化
- Wave 2.3: 确认 Marketplace 无官方提交流程，自建 marketplace 已就位

**未完成（需手动）**：
- Wave 1: push awesome-agent-skills + 创建 PR（需个人设备或申请 git-defender 白名单）
- Wave 2.1: 安装 VHS（`brew install charmbracelet/tap/vhs`）→ 准备 demo 项目 → 录制 3 个 GIF → 嵌入 README
- Wave 3-5: 全部待启动

**恢复指引**：下次继续时读此文件 §暂停点，按 Wave 顺序推进

---

## Wave 3: Content Launch (Weeks 3-4, ~6-8h)

### 3.1 Blog Post #1: Cross-Session Context Loss
- [x] Draft written → `docs/plans/blog-cross-session-context.md` (EN + ZH, ~1,400 words each)
- [ ] English version published on: [ ] Dev.to [ ] Medium
- [ ] Chinese version published on: [ ] juejin.cn [ ] sspai.com

### 3.2 Community Engagement
- [x] Community playbook written → `docs/plans/community-playbook.md`
  - Show HN draft ready
  - Reddit r/ClaudeAI templates (3 variants)
  - Twitter/X content templates (5 tweets + 2 threads)
  - Chinese community templates (V2EX post + Jike short posts)
  - Engagement rules and weekly time budget
- [ ] Community accounts created
- [ ] First 3 community interactions completed
- Weekly target: 1-2 hours participation

### 3.3 Blog Post #2: Meta-Narrative
- [x] Draft written → `docs/plans/blog-meta-narrative.md` (EN + ZH, ~2,900 words total)
- [ ] Published on 2+ platforms

---

## Wave 4: Feedback Loop (Weeks 5-8)

### 4.1 Feedback Collection
- [x] GitHub pinned issue created: [#3 Share your devpace experience](https://github.com/arch-team/devpace/issues/3) (pinned)
- [x] README Feedback section added with link to pinned issue (EN + ZH)
- [ ] 5+ real user feedback collected

### 4.2 Quick Iteration
- [ ] Feedback categorized (Bug / UX / Feature)
- [ ] Top 3 issues fixed
- [ ] Fix announcements shared publicly

### 4.3 Secondary Content
- [ ] "v1.6.0: 5 improvements from user feedback" post published

---

## Wave 5: Sustained Growth (Weeks 9-12)

### 5.1 New Example Project
- [ ] Non-Todo walkthrough (REST API or CLI tool)
- [ ] Optional: Runnable demo repository

### 5.2 90-Day Review
- [ ] Data collected: Stars / Installs / Issues / Blog traffic
- [ ] Strategy effectiveness evaluated
- [ ] Next phase direction decided

---

## Asset Inventory (2026-02-26)

| Asset | File | Status |
|-------|------|--------|
| Blog #1 (Cross-session) | `docs/plans/blog-cross-session-context.md` | Draft ready (EN+ZH) |
| Blog #2 (Meta-narrative) | `docs/plans/blog-meta-narrative.md` | Draft ready (EN+ZH) |
| Community playbook | `docs/plans/community-playbook.md` | Complete |
| Aggregator submissions | `docs/plans/aggregator-submissions.md` | Copy-paste ready |
| VHS tape scripts | `scripts/record-demos/*.tape` | 3 scripts ready |
| Discussion templates | `.github/DISCUSSION_TEMPLATE/*.yml` | 2 templates |
| Feedback issue template | `.github/ISSUE_TEMPLATE/feedback.md` | Ready |
| Social preview SVG | `.github/social-preview.svg` | v1.5.0 |
| Marketplace config | `.claude-plugin/marketplace.json` | Optimized |

---

## Key Principles

1. **"Solve problems" not "promote product"** — Every piece of content starts from user pain
2. **Simplify narrative** — One-liner: "Claude Code helps you code without losing context"
3. **90-day feature freeze** — Shift energy from Phase 19 to user acquisition
4. **GIF > Text** — Visual demos are highest ROI investment
5. **English first** — Global Claude Code users are the target market
