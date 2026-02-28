🌐 [中文版](pace-retro_zh.md) | English

# Iteration Retrospective & Metrics (`/pace-retro`)

`/pace-retro` is devpace's retrospective and metrics analysis skill. It generates iteration retrospective reports, updates the metrics dashboard, and provides multi-granularity analysis perspectives -- from quick mid-iteration checks to full retrospective with experience distillation and cross-iteration trend analysis. Runs in a forked context via the `pace-analyst` agent with project-level memory, enabling cross-session analysis acceleration.

Where `/pace-plan close` performs a lightweight auto-retrospective (3 baseline metrics), `/pace-retro` delivers deep multi-dimensional analysis with improvement recommendations, experience distillation, and knowledge loop closure.

## Quick Start

```
1. /pace-retro              --> Full iteration retrospective (action summary + dimension details)
2. /pace-retro update       --> Refresh metrics only (with change feedback)
3. /pace-retro focus quality --> Deep dive into a single dimension
4. /pace-retro compare      --> Compare current vs previous iteration
5. /pace-retro history      --> Trend overview across 3+ iterations
6. /pace-retro mid          --> Mid-iteration checkpoint (lightweight, no baseline update)
7. /pace-retro accept       --> Confirm suggested actions (MoS updates, etc.)
```

## Subcommands

| Subcommand | When to Use | What It Does |
|------------|-------------|--------------|
| `(empty)` | Iteration end | Full retrospective: collect data, update dashboard, generate report, distill experience, produce handoff checklist |
| `update` | Anytime | Refresh dashboard metrics only; outputs a change summary showing which metrics changed and by how much |
| `focus <dim>` | Deep dive needed | Single-dimension analysis: `quality` / `delivery` / `dora` / `defects` / `value` / `knowledge` |
| `compare` | After iteration close | Side-by-side comparison of current vs previous iteration on key metrics |
| `history` | Trend analysis | Trend overview across 3+ iterations based on dashboard history snapshots |
| `mid` | Mid-iteration | Lightweight checkpoint; does not update dashboard baselines |
| `accept` | After retrospective | Execute suggested actions from the last retrospective (e.g., mark MoS as achieved) |

## Core Features

### Two-Layer Output Structure

Every retrospective report uses a two-layer design to solve information overload:

- **Layer 1 -- Action Summary (~10 lines, always output)**: Key metrics with trend arrows, top concern, highlight, core recommendation, and pending confirmations. A human reader gets 80% of the critical information from this layer alone.
- **Layer 2 -- Dimension Details (follows the summary)**: Delivery, quality, defects, value, and cycle dimensions, plus conditional sections (DORA, risk trends, knowledge-driven improvements, knowledge base health) that appear only when data is available.

### Multi-Granularity Analysis

From lightest to deepest, pick the right level for the situation:

| Granularity | Command | Scope | Updates Dashboard? |
|-------------|---------|-------|--------------------|
| Metrics refresh | `update` | Data only, no report | Yes |
| Mid-iteration check | `mid` | Lightweight report, no experience distillation | No |
| Focused deep dive | `focus <dim>` | Single dimension analysis | Yes |
| Full retrospective | `(empty)` | All dimensions + experience + handoff | Yes |
| Cross-iteration compare | `compare` | Delta between two iterations | No |
| Trend overview | `history` | 3+ iteration trends | No |

### Experience Distillation Transparency

After full retrospective, a "Lessons Learned" transparency section shows exactly what was extracted:

```
### Lessons Learned This Retrospective

**Patterns submitted to knowledge base**:
1. (new) [improvement] "Boundary condition tests prevent 60% of defects" (confidence 0.5, pending verification)
2. (validated) [defense] "Auth changes need integration tests" (confidence 0.7 -> 0.8, +1 verification)
3. (conflict) [improvement] "Fast iteration over thorough testing" -- tension with pattern #5

Status: submitted to pace-learn pipeline (dedup check + write)
```

This makes the learning process visible -- users see new patterns, validated patterns, and conflicts at a glance.

### Cross-Iteration Trend Analysis

Dashboard history snapshots are preserved across iterations, enabling `compare` and `history` subcommands:

- **compare**: Side-by-side delta between current and previous iteration, highlighting improvements and regressions
- **history**: Trend lines across 3+ iterations with trend judgments (sustained improvement / improving / fluctuating / needs attention / stable)

### Iteration Handoff Checklist

Full retrospective generates a structured handoff written to `iterations/current.md`, consumed by `/pace-plan next`:

- Improvement items inherited to next iteration (with data support)
- Metrics baseline (current velocity, average cycle time)
- Incomplete PFs with deferral reasons
- Recommended focus dimensions for next iteration

This closes the retro-to-plan feedback loop with structured data rather than free-form notes.

### Role-Adapted Output

Five roles (Biz Owner / PM / Dev / Tester / Ops) reshape the summary and details to match each role's concerns:

| Role | Summary Emphasis | Wording Style |
|------|-----------------|---------------|
| Biz Owner | MoS achievement + value delivery + OBJ progress | Business terms, linked to objective IDs |
| PM | Iteration completion rate + CR cycle + scope changes | Feature-oriented, delivery rhythm focus |
| Dev (default) | Quality gate pass rate + tech debt + code quality | Technical terms, implementation quality focus |
| Tester | Defect distribution + escape rate + rejection rate + coverage trends | Quality-oriented, defect prevention focus |
| Ops | DORA proxy metrics + deploy frequency + MTTR + stability | Operations terms, delivery reliability focus |

The underlying data collection is identical across roles -- only the report ordering and wording adapt.

### DORA Proxy Metrics

When Release management is active (`.devpace/releases/` exists), the report includes a DORA section with four metrics calculated as proxy values from `.devpace/` data:

| Metric | Proxy Calculation | Grading |
|--------|------------------|---------|
| Deployment Frequency | Release close frequency | Elite (>=1/week) / High (1/2weeks) / Medium (1/month) / Low |
| Change Lead Time | Average CR created-to-released | Elite (<=1d) / High (<=3d) / Medium (<=7d) / Low |
| Change Failure Rate | Releases with post-release defects / total | Elite (<=15%) / High (<=30%) / Medium (<=45%) / Low |
| MTTR | Average defect CR created-to-merged | Elite (<=1d) / High (<=3d) / Medium (<=7d) / Low |

Each metric includes a trend arrow comparing to the previous retrospective. Metrics without sufficient data are marked with the specific reason (e.g., "No Release management used") rather than omitted.

### Report Quality Self-Assessment

Full retrospective appends a three-dimensional quality self-assessment:

| Dimension | What It Measures |
|-----------|-----------------|
| Data Sufficiency | How complete the underlying CR event data is (5/5 = all CRs have full event tables) |
| Trend Credibility | How many iterations of historical data exist (5/5 = 5+ iterations) |
| Recommendation Actionability | How specific and implementable the suggestions are (5/5 = all have concrete actions + targets) |

This helps users calibrate their trust in the report's conclusions.

### Agent Memory Utilization

The `pace-analyst` agent uses project-level persistent memory:

- **On start**: Reads previous key findings, accumulated trend directions, and project analysis models -- accelerating focus on what changed since last time
- **On end**: Saves this retrospective's key findings (max 3), updated trend directions, and refined analysis models

This means each retrospective builds on the last, reducing cold-start analysis time.

### MoS Confirmation Flow

`/pace-retro accept` executes the pending actions suggested by the last retrospective -- typically marking achieved MoS (Measures of Success) in `project.md`. The retrospective identifies metrics that have reached their targets and proposes updates, but never auto-modifies business data without human confirmation.

### Update Mode Feedback

`/pace-retro update` doesn't just silently refresh data -- it outputs a change summary:

```
dashboard.md updated (3 changes):
- First-pass rate: 70% -> 85% (up)
- Average CR cycle: 3.0 days -> 1.5 days (up)
- Iteration velocity: 3 PF -> 5 PF (up)

Unchanged metrics retained.
```

First-time metrics get a baseline establishment message instead.

### retro-learn Bidirectional Loop

Retrospective and learning form a closed knowledge loop:

- **retro -> learn**: Bulk validates patterns referenced during the iteration (confirms or challenges confidence scores)
- **learn -> retro**: Defense pattern summary feeds macro improvement direction into the "Knowledge-Driven Improvements" report section

### Knowledge Base Meta-Analysis

When the knowledge base reaches 5+ patterns, the retrospective includes a "Knowledge Base Health" section:

- Pattern count by type and status (Active / Dormant / Archived)
- Average confidence by type
- Top-3 productive tags and high-efficiency tags
- Unresolved conflict pairs
- Growth and decay zones (which types/tags are growing or declining)

### Defect Root Cause Classification

Defects are classified into 6 base categories (logic error, boundary omission, integration issue, regression, configuration error, unknown) plus project-custom categories from `project.md` or `insights.md`. When "unknown" exceeds 30%, the report suggests refining the classification system.

### Verification-Approval Consistency Analysis

When the consistency rate between automated verification (pace-test accept) and human approval (Gate 3) drops below 80%, the report includes a detailed case-by-case analysis of discrepancies with inferred reasons and improvement suggestions fed back to the verification strategy.

## Output Examples

### Full Retrospective -- Action Summary

```
## Iteration Retrospective Summary: Sprint 3

Delivery 3/5 (60%) | Quality 85% (up) | Cycle 1.5 days (up)
Attention: Rejection rate 15% (up from 8% last iteration), 2 major defects open
Highlight: First-pass rate 85% new high, DORA lead time Elite grade
Recommendation: Focus on defect prevention next iteration (boundary omissions account for 60%)

Pending Confirmations (2 items):
- MoS achievement update: 2 metrics suggest marking as achieved (/pace-retro accept to confirm)
  - "Gate first-pass rate > 80%" -- current 85%, achieved
  - "Average CR cycle < 2 days" -- current 1.5 days, achieved

Details below...
```

### Update Mode -- Change Feedback

```
dashboard.md updated (2 changes):
- First-pass rate: 80% -> 85% (up)
- Defect count: 3 -> 5 (up, needs attention)

Unchanged metrics retained.
```

### Mid-Iteration Check

```
## Mid-Iteration Check: Sprint 3

Delivery 2/5 (40%) at 60% time elapsed
Attention: Completion behind schedule, may need scope adjustment
Quality 90% first-pass (healthy)

Quick suggestions:
1. Check if in-progress CR is blocked
2. Consider /pace-plan adjust to reduce scope
3. Prioritize P0 features for remaining time
```

### Compare Mode

```
## Iteration Comparison: Sprint 2 vs Sprint 3

| Metric | Sprint 2 | Sprint 3 | Delta | Trend |
|--------|----------|----------|-------|-------|
| PF completion | 4/5 (80%) | 3/5 (60%) | -20% | needs attention |
| First-pass rate | 80% | 85% | +5% | improving |
| Avg CR cycle | 2.5 days | 1.5 days | -1.0 day | improving |
| Rejection rate | 8% | 15% | +7% | needs attention |

Key changes:
- Delivery slowed (fewer PFs completed), but per-CR quality improved
- Recommendation: Maintain quality improvements, investigate delivery bottleneck
```

## Usage Scenarios

### Scenario 1: End-of-Iteration Full Retrospective

```
You:    /pace-retro
Claude: ## Iteration Retrospective Summary: Sprint 3

        Delivery 3/5 (60%) | Quality 85% (up) | Cycle 1.5 days (up)
        Attention: Rejection rate 15%, 2 major defects open
        Highlight: First-pass rate 85% new high
        Recommendation: Focus on defect prevention next iteration

        Pending Confirmations (2 items):
        - MoS: "Gate first-pass > 80%" -- current 85%, achieved
        - MoS: "Avg cycle < 2 days" -- current 1.5d, achieved

        [Dimension details, DORA metrics, experience distillation, handoff checklist...]

You:    /pace-retro accept
Claude: Confirmed 2 actions:
        - project.md: Marked "Gate first-pass > 80%" as achieved
        - project.md: Marked "Avg cycle < 2 days" as achieved
```

### Scenario 2: Quick Metrics Refresh

```
You:    /pace-retro update
Claude: dashboard.md updated (3 changes):
        - First-pass rate: 70% -> 85% (up)
        - Avg CR cycle: 3.0 days -> 1.5 days (up)
        - Iteration velocity: 3 PF -> 5 PF (up)

        Unchanged metrics retained.
```

### Scenario 3: Mid-Iteration Health Check

```
You:    /pace-retro mid
Claude: ## Mid-Iteration Check: Sprint 3

        Delivery 2/5 (40%) at 60% time elapsed
        Attention: Completion behind schedule
        Quality 90% first-pass (healthy)

        Suggestions:
        1. Check if in-progress CR is blocked
        2. Consider /pace-plan adjust to reduce scope
```

### Scenario 4: Focus on Quality Dimension

```
You:    /pace-retro focus quality
Claude: ## Quality Deep Dive: Sprint 3

        Gate first-pass rate: 85% (trend: improving for 3 iterations)
        Rejection rate: 15% (trend: needs attention, up from 8%)
        Test baseline: 94% pass rate, 12s execution time

        Root cause analysis of rejections:
        - 60% boundary condition omissions
        - 25% integration mismatches
        - 15% logic errors

        Recommendations:
        1. Add boundary condition checklist to pace-dev workflow
        2. Integration test coverage for cross-module changes
```

### Scenario 5: Cross-Iteration Trend Analysis

```
You:    /pace-retro history
Claude: ## Trend Overview (Sprint 1-3)

        | Metric         | Sprint 1 | Sprint 2 | Sprint 3 | Trend           |
        |----------------|----------|----------|----------|-----------------|
        | First-pass rate | 70%      | 80%      | 85%      | sustained improvement |
        | Avg CR cycle    | 3.0 days | 2.5 days | 1.5 days | sustained improvement |
        | Rejection rate  | 5%       | 8%       | 15%      | needs attention |
        | Velocity        | 3 PF     | 4 PF     | 5 PF     | sustained improvement |

        Key insights:
        - Quality and velocity consistently improving
        - Rejection rate rising -- investigate review criteria alignment
```

## Integration with Other Commands

| Command | Relationship to `/pace-retro` |
|---------|-------------------------------|
| `/pace-plan close` | Performs lightweight auto-retrospective (3 baseline metrics); `/pace-retro` provides the full deep analysis |
| `/pace-plan next` | Consumes the iteration handoff checklist written by `/pace-retro` |
| `/pace-learn` | Bidirectional: retro distills experience via pace-learn pipeline; retro validates existing patterns in bulk |
| `/pace-status` | Shows current metrics snapshot (read-only); retro analyzes and generates recommendations |
| `/pace-test` | Verification-approval consistency analysis feeds back to pace-test's verification strategy |
| `/pace-role` | Role setting adapts retro output emphasis and wording |
| `/pace-next` | Strategic signals (retro reminder, MoS achievement) direct to `/pace-retro` |
| `/pace-pulse` | Retro metrics feed pulse signals for session-start detection |
| `/pace-guard` | Risk data feeds the "Risk Trends" conditional section in retrospective reports |

## Conditional Sections (Progressive Disclosure)

Several report sections appear only when sufficient data exists:

| Section | Condition | When Missing |
|---------|-----------|--------------|
| DORA Proxy Metrics | `.devpace/releases/` exists with Release files | Silently skipped |
| Risk Trends | `.devpace/risks/` exists | Silently skipped |
| Knowledge-Driven Improvements | `insights.md` exists with defense patterns | Silently skipped |
| Knowledge Base Health | `insights.md` has >= 5 patterns | Silently skipped |
| Learning Effectiveness | Pattern reference data available | Silently skipped |
| Verification-Approval Analysis | Consistency rate < 80% | Silently skipped |
| Defect Root Cause Report | Merged defect CRs with root cause data | Silently skipped |

No errors, no empty sections -- data-absent sections are invisible.

## Related Resources

- [SKILL.md](../../skills/pace-retro/SKILL.md) -- Skill definition, input/output, routing table, and high-level flow
- [retro-procedures.md](../../skills/pace-retro/retro-procedures.md) -- Detailed execution rules: data collection, report format, experience distillation, DORA metrics, defect analysis, handoff checklist, quality self-assessment
- [metrics.md](../../knowledge/metrics.md) -- Metric definitions, calculation formulas, and DORA proxy grading
- [insights-format.md](../../knowledge/_schema/insights-format.md) -- Knowledge base entry format (used by experience distillation)
- [User Guide](../user-guide.md) -- Quick reference for all commands
