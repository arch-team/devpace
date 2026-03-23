🌐 [中文版](pace-next_zh.md) | English

# Next-Step Navigation (`/pace-next`)

`/pace-next` is devpace's cross-domain global navigator. It synthesizes signals from CRs, iterations, releases, metrics, risks, the feature tree, and more, then recommends the single most important action right now. Uses the haiku model (lightweight and fast) with read-only tools (Read/Glob/Grep).

Where `/pace-status` answers "where are we?", `/pace-next` answers "where should we go?" — the key differentiator that shifts devpace from passive state viewing to proactive action guidance.

## Quick Start

```
1. /pace-next              --> Top-1 recommendation (3 lines: suggestion + reason + action)
2. /pace-next detail       --> Top-3 candidates (up to 8 lines)
3. /pace-next why          --> Expand reasoning chain (2-5 lines: signal scan, priority comparison, alternatives)
4. /pace-next journey      --> Full workflow journey from current state to goal (auto-selects template)
5. /pace-next journey hotfix --> Journey with a specific template
6. /pace-trace next        --> Full signal collection and traversal trace
```

The default output is designed to answer "what should I do next?" in under three seconds of reading time. Use `detail` when you want alternatives, `why` when you want to understand the reasoning, and `journey` when you want to see the full path ahead.

## Core Features

### Grouped Priority Matrix

16 signals organized into 5 priority groups, traversed top-to-bottom. The first signal that fires wins.

| Group | Priority | Signals | Scope |
|-------|----------|---------|-------|
| **Blocking** | Highest | Review backlog (S1), High-risk items (S2) | All roles, equal priority |
| **In Progress** | High | Continue developing (S3), Resume paused (S4) | Workflow continuity |
| **Delivery** | Medium-High | Release verification (S5), Risk backlog (S6), Iteration deadline (S7), Iteration near-complete (S8) | Value delivery pipeline |
| **Strategic** | Medium | Retro reminder (S9), Defect ratio (S10), Sync lag (S11), MoS achievement (S12) | Review and optimization |
| **Growth** | Low | Unstarted features (S13), Plan new iteration (S14), All complete (S15) | New value creation |
| **Idle** | Fallback | No signal (S16) | Free exploration |

Signal definitions are maintained in `knowledge/_signals/signal-priority.md` (the single source of truth shared by pace-next, pace-status overview, and pace-pulse session-start).

### Value Chain Visibility

Recommendations don't just name a CR -- they show the value chain context above it. Each suggestion template embeds the parent PF (product feature) and, for Biz/PM roles, the parent BR (business requirement) or OBJ (objective). This lets users see not just "what to do" but "why it matters in the delivery chain."

Example: `Continue "OAuth integration" (part of Login Module) -- left off at token validation`

### Risk Awareness

Risk signals are woven into the priority matrix at two levels:

- **High severity risks** (S2): Blocking group -- global blocker, equal to review backlog
- **Medium risk backlog** (S6): Delivery group -- accumulated open risks that need attention before they escalate

High risks cannot bypass human confirmation, reinforcing devpace's safety-first principle.

### Three-Layer Progressive Transparency

The reasoning behind every recommendation is accessible at three progressively deeper levels:

| Layer | Trigger | Output | Lines |
|-------|---------|--------|-------|
| **Surface** | `/pace-next` (default) | Suggestion + reason + action, with a 15-char reasoning suffix on the reason line | 3 |
| **Middle** | `/pace-next why` | Signal scan results, priority comparison, alternative candidates | 2-5 |
| **Deep** | `/pace-trace next` | Full signal collection log and traversal process | Unlimited |

Each layer naturally guides to the next: the reason line ends with "(...why)" hint, and the why output ends with "(...trace)" hint.

### Role Adaptation

Five roles (Dev / PM / Biz / Tester / Ops) don't just change wording -- they **reorder signals within groups**:

| Role | Promoted Signals | Effect |
|------|-----------------|--------|
| PM | S8 (iteration complete), S13 (unstarted features) | Iteration and feature tree signals surface earlier |
| Biz | S12 (MoS achievement), S13 (unstarted features) | Business objective signals surface earlier |
| Ops | S5 (release verification), S11 (sync lag) | Deployment and operations signals surface earlier |
| Tester | S10 (defect ratio), S6 (risk backlog) | Quality and risk signals surface earlier |
| Dev | No adjustment | Default signal order |

Blocking signals (S1-S2) are never reordered -- they remain highest priority for all roles.

### Experience Enhancement

When `.devpace/metrics/insights.md` exists, pace-next matches the current recommendation type against historical experience patterns (confidence > 0.7). Matched insights are appended as a single-line suffix on the reason line, connected with "--".

Example: `Reason: 1 change awaiting review -- last time similar changes had auth edge cases`

### Multi-CR Parallel Handling

When multiple CRs are in `developing` state, pace-next ranks them by:

1. **Session continuity** -- the CR mentioned in `state.md` as current work
2. **Completion progress** -- CRs closer to completion get priority
3. **PF priority** -- higher-priority product features first

The top-1 CR becomes the recommendation; others appear in `detail` mode.

### Time Dimension

Time-sensitive signals add urgency awareness:

- **Iteration deadline pressure** (S7): Fires when < 2 days remain and completion rate < 50%
- **Developing CR stalling**: Implicit in the session continuity ranking -- long-idle CRs are deprioritized in favor of recently active ones
- **Retro reminder** (S9): Fires when last metrics update > 7 days old

### Detail Mode

`/pace-next detail` traverses all 16 signals, collects every hit, and outputs the top-3 candidates in up to 8 lines.

```
Suggestion: continue "OAuth integration" (Login Module)
   Reason: left off at token validation, 70% complete
   Action: /pace-dev or say "continue"

Candidates (by priority):
  2. 1 change awaiting review -- /pace-review
  3. Feature "MFA Support" not started -- say "implement MFA Support"
```

When only one signal fires, the candidates section is omitted.

### Journey Mode

`/pace-next journey` shifts from "what is the single next action?" to "what is the full path from here to the goal?" It renders a step-by-step journey view showing completed steps, the current position, and remaining steps -- all advisory, with no automatic execution.

**Templates:**

| Template | Journey Path | Use Case |
|----------|-------------|----------|
| `new-feature` | biz discover → decompose → plan next → dev → review → merged | Deliver a feature from scratch |
| `iteration` | plan next → [dev → review → merged]* → plan close → retro | Full iteration cycle |
| `hotfix` | feedback report → dev → review → release deploy | Emergency fix |
| `release` | release create → deploy → verify → close | Standard release |
| `onboarding` | init → dev (first feature) → review → merged | First-time user experience |

When no template name is provided, journey auto-selects based on project state (e.g., new project with no CRs → `onboarding`; active iteration → `iteration`).

**Example output:**

```
Journey: iteration — complete the current iteration cycle

✅ Plan iteration — 3 features scoped
✅ Dev PF-001 — "OAuth integration" merged
👉 Dev PF-002 — say "implement [feature name]" or /pace-dev
⏳ Review — /pace-review
⏳ Iteration retro — /pace-retro

Progress: 2/5 steps complete
```

**Key rules:**
- Advisory only -- shows the path, never auto-executes any Skill
- Stateless -- no journey state file is persisted; the view is dynamically derived from `.devpace/` on every call
- Complementary to default mode -- journey shows the full map, default mode recommends the single next step

## Output Examples

### Default -- Quick Recommendation

```
Suggestion: continue "OAuth integration" (part of Login Module)
   Reason: left off at token validation -- session continuity
   Action: /pace-dev or say "continue"
```

### Detail -- Top-3 Candidates

```
Suggestion: 1 change awaiting review -- review before it blocks the pipeline
   Reason: "Session management" has been in review for 2 days
   Action: /pace-review

Candidates (by priority):
  2. Continue "Data export" (Data Management) -- 60% complete
  3. Iteration nearing completion (85%) -- review then plan next
```

### Role-Adapted -- Biz Perspective

```
Suggestion: MoS achievement at 82% -- review business outcome metrics
   Reason: "User Authentication" objective 4/5 measures achieved
   Action: /pace-retro
```

## Usage Scenarios

### Scenario 1: Session Start -- What to Do First?

```
You:    /pace-next
Claude: Suggestion: continue "OAuth integration" (Login Module)
           Reason: left off at token validation, nearly complete
           Action: /pace-dev or say "continue"
```

### Scenario 2: Multiple Options -- Which One Matters Most?

```
You:    /pace-next detail
Claude: Suggestion: 2 changes awaiting review -- unblock the pipeline
           Reason: reviews pending > 24h, blocking downstream work
           Action: /pace-review

        Candidates (by priority):
          2. Continue "Data export" -- 60% complete
          3. Feature "Report Generation" not started (part of Analytics)
```

### Scenario 3: Understand the Reasoning

```
You:    /pace-next why
Claude: Signal scan: S1 (review backlog) = 0, S2 (high risk) = 0, S3 (developing) = 1 CR
        Priority hit: S3 -- "OAuth integration" in developing state
        Alternatives: S8 (iteration 80% complete), S13 (1 unstarted feature)
        Decision: S3 wins -- workflow continuity outranks near-completion signals
        Full trace: /pace-trace next
```

## Relationship to Other Commands

| Command | Relationship |
|---------|-------------|
| `/pace-status` | Status answers "where are we?" (snapshot); next answers "where to go?" (navigation). Status overview includes a lightweight top-1 suggestion (subset of pace-next, no reasoning) |
| `/pace-pulse` session-start | Session-start is "push" (auto-triggered layered summary); next is "pull" (user-triggered deep navigation). Dedup: next skips the already-notified top signal within 5 minutes of session start |
| `/pace-dev` | Next often recommends resuming development; the action line directs to `/pace-dev` |
| `/pace-review` | When review backlog exists (S1), next surfaces it as the top recommendation |
| `/pace-role` | Role set via `/pace-role` drives signal reordering in pace-next; explicit role switch takes immediate effect |
| `/pace-retro` | Strategic signals (S9, S12) direct to `/pace-retro` for review and retrospective |
| `/pace-trace` | `why` provides mid-layer reasoning; `/pace-trace next` provides full signal traversal trace |

## Signal Priority Source

All signal definitions, grouping, and role reordering rules are maintained in `knowledge/_signals/signal-priority.md` -- the single source of truth shared by three consumers:

| Consumer | Visible Subset | Usage |
|----------|---------------|-------|
| pace-next | All S1-S16 | Full traversal, top-1 or top-3 |
| pace-status overview | S1/S3/S5/S8/S9/S13/S15 | Top-1 lightweight suggestion |
| pace-pulse session-start | All (with independent thresholds) | Layered summary |

## Related Resources

- [SKILL.md](../../skills/pace-next/SKILL.md) -- Skill definition, input/output, and high-level flow
- [next-procedures.md](../../skills/pace-next/next-procedures.md) -- Detailed decision algorithm, output formats, and role adaptation rules
- [next-procedures-journey.md](../../skills/pace-next/next-procedures-journey.md) -- Journey orchestration templates, auto-selection logic, and output format
- [signal-priority.md](../../knowledge/_signals/signal-priority.md) -- Signal definitions and priority groups (SSOT)
- [signal-collection.md](../../knowledge/_signals/signal-collection.md) -- Shared signal collection procedures
- [User Guide](../user-guide.md) -- Quick reference for all commands
