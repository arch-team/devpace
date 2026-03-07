# Aggregator Platform Submission Content

> Ready-to-submit entries for discovery platforms. Copy-paste into PRs or submission forms.

## 1. claudemarketplaces.com

**Submission URL**: https://claudemarketplaces.com (submit GitHub repo URL)

**GitHub URL**: `https://github.com/arch-team/devpace`

**Action**: Submit the GitHub URL through their submission form. No PR needed — it's a registry-style site.

---

## 2. VoltAgent/awesome-agent-skills

**Repository**: https://github.com/VoltAgent/awesome-agent-skills

**Steps**:
1. Fork the repository
2. Add entry under "Project Management" category
3. Submit PR

**Entry to add** (in the "Project Management" section):

```markdown
- [devpace](https://github.com/arch-team/devpace) - AI-native development pace manager for Claude Code. Manages requirement changes with auto impact analysis, enforces quality gates with human approval, maintains goal-to-code traceability, and auto-restores context across sessions. 17 skills covering the full BizDevOps lifecycle.
```

**PR Title**: `Add devpace — BizDevOps pace manager for Claude Code`

**PR Description**:
```
Adding devpace, an AI-native development pace manager for Claude Code.

Key features:
- Change management with automatic impact analysis
- Quality gates (auto-check + human approval, cannot be bypassed)
- Goal-to-code traceability (Business Goal → Feature → Code Change)
- Cross-session context restore (0 manual corrections vs 8 without)
- 17 skills covering plan → develop → review → release cycle

Category: Project Management
License: MIT
```

---

## 3. awesome-claude-code

**Repository**: https://github.com/anthropics/awesome-claude-code (or community equivalent)

**Steps**:
1. Fork the repository
2. Add entry under "Plugins" section
3. Submit PR

**Entry to add**:

```markdown
- [devpace](https://github.com/arch-team/devpace) - Development pace manager that brings BizDevOps rhythm to Claude Code projects. Auto-manages requirement changes, enforces quality gates, and restores context across sessions.
```

**PR Title**: `Add devpace — development pace manager plugin`

**PR Description**:
```
Adding devpace, a Claude Code plugin for development pace management.

What it does:
- Requirement changes → auto impact analysis → orderly adjustment
- Quality gates → auto-check + human approval → cannot bypass
- Cross-session → auto-restore context → 0 re-explanations needed
- Full lifecycle: /pace-init → /pace-dev → /pace-review → /pace-release

Install: /plugin marketplace add arch-team/devpace-marketplace
License: MIT
```

---

## 4. Additional Platforms (Future)

### Product Hunt
- **Tagline**: "Give your Claude Code projects a steady development pace"
- **Description**: "Requirements change, but your development rhythm shouldn't. devpace is a Claude Code plugin that auto-manages requirement changes, enforces quality gates, and restores context across sessions — so you can focus on building, not re-explaining."
- **Topics**: AI, Developer Tools, Productivity, Open Source

### Hacker News (Show HN)
- See `community-playbook.md` for full Show HN draft

---

## Submission Checklist

- [ ] claudemarketplaces.com: Submit GitHub URL
- [ ] awesome-agent-skills: Fork → Add entry → PR
- [ ] awesome-claude-code: Fork → Add entry → PR
- [ ] Verify all PR links are tracked in promotion-tracker.md
