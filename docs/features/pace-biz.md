# Business Planning (`/pace-biz`)

devpace has always managed the flow from product features (PF) down to code changes (CR), but the upstream question — *where do these features come from?* — was left outside the system. Business opportunities were captured in scattered notes, epics lived in external tools, and the link between strategic objectives and day-to-day development was implicit at best. `/pace-biz` closes this gap by bringing structured business planning into the same value chain, so that every line of code can be traced back to a business opportunity.

## Quick Start

```
1. /pace-biz opportunity "Enterprise clients need SSO"  → Capture opportunity → OPP-001 created
2. /pace-biz epic OPP-001 "Enterprise Authentication"   → Create epic → EPIC-001 with OBJ alignment
3. /pace-biz decompose EPIC-001                         → Break down → BRs and PFs generated
4. /pace-biz refine BR-003                              → Enrich details → Acceptance criteria added
```

Or let Claude guide you interactively:

```
You:    /pace-biz
Claude: [Scans project context and recommends next action]
        Detected: meeting-notes.md in working directory → Recommend: /pace-biz import meeting-notes.md
        Detected: 1 Epic with empty BRs → Recommend: /pace-biz decompose EPIC-001
        Or choose: opportunity / epic / decompose / refine / align / view / discover / import / infer
```

Start from a vague idea:

```
5. /pace-biz discover "I want to build a task management tool"  → Multi-turn discovery → Full candidate tree
6. /pace-biz import meeting-notes.md                            → Extract requirements → Merge into tree
7. /pace-biz infer                                              → Scan codebase → Gap report
```

## User Journeys

> Not sure where to start? The table below helps you find the right path.

| Your Situation | Recommended Journey | Starting Subcommands |
|----------------|--------------------|--------------------|
| Clear business opportunity or customer feedback; want to build a planning system from scratch | [Journey A](#journey-a-business-planning-from-scratch) | `opportunity` → `epic` → `decompose` |
| Only a vague idea, not sure what to build | [Journey B](#journey-b-from-vague-idea-to-structured-requirements) | `discover` |
| Team has scattered requirement documents (meeting notes, PRDs, issue lists) | [Journey C](#journey-c-importing-existing-documents) | `import` → `align` |
| Inheriting a legacy project with missing documentation | [Journey D](#journey-d-legacy-project-feature-inventory) | `infer` → `align` |
| Project has grown; time to check planning health | [Journey E](#journey-e-routine-maintenance-and-strategic-alignment) | `align` + `view` + `refine` |

**Lite mode note**: In lite mode (OBJ→PF→CR), `opportunity`, `epic`, and `decompose` are unavailable. Journey A requires upgrading to full mode via `/pace-init --upgrade-mode`. Journeys B/C/D automatically simplify in lite mode — OPP/Epic/BR layers are skipped and PF candidates are produced directly. Journey E's `align` simplifies to OBJ→PF→CR chain checks.

---

### Journey A: Business Planning from Scratch

**Trigger**: A customer reported a clear need, or the team spotted a new market opportunity. You want to build a complete planning structure starting from the business opportunity.

**Full path**: `opportunity` → `epic` → `decompose` → `/pace-plan`

**Step-by-step**:

**Step 1: Capture the business opportunity**

```
You:    /pace-biz opportunity Enterprise clients need SSO login, currently each integration requires custom development
Claude: Captured business opportunity: OPP-001 — Enterprise clients need SSO login
        Source: Customer feedback (enterprise integration needs)
        Status: Evaluating
        → Next: /pace-biz epic OPP-001 to evaluate and convert to Epic
```

Claude automatically infers the source type (customer feedback / competitive observation / technical discovery, etc.). Multiple opportunities can point to the same strategic objective, building a natural demand signal.

**Step 2: Create a strategic epic**

```
You:    /pace-biz epic OPP-001 "Enterprise Authentication System"
Claude: Which business objective does this epic serve?
        1. OBJ-1: Improve enterprise customer retention
        2. OBJ-2: Expand B2B market share
You:    1
Claude: How will we measure success? (you can skip and fill in later)
You:    Enterprise onboarding time reduced from 2 weeks to 2 days; SSO coverage reaches 80%
Claude: Created epic: EPIC-001 — Enterprise Authentication System
        Alignment: OBJ-1 (Improve enterprise customer retention) ← OPP-001
        MoS:
        - [ ] Enterprise onboarding time reduced from 2 weeks to 2 days
        - [ ] SSO coverage reaches 80%
        → Next: /pace-biz decompose EPIC-001 to break down into business requirements
```

**Step 3: Decompose into deliverables**

```
You:    /pace-biz decompose EPIC-001
Claude: Based on EPIC-001 background and MoS, suggested business requirements:

        BR-001: SSO Protocol Integration    Value: High × Effort: Medium → P0
        BR-002: Session & Permission Mgmt   Value: High × Effort: High   → P1
        BR-003: Enterprise Admin Console    Value: Medium × Effort: Low  → P1

        Does BR-002 depend on BR-001?
You:    Yes, SSO needs to work before we can manage sessions
Claude: Recorded dependency: BR-002 → BR-001
        Confirm this decomposition? (you can adjust names, priorities, or add/remove items)
You:    Confirm
Claude: Decomposed EPIC-001:
        ├── BR-001: SSO Protocol Integration P0
        ├── BR-002: Session & Permission Mgmt P1 (depends on BR-001)
        └── BR-003: Enterprise Admin Console P1
        → Continue decomposing: /pace-biz decompose BR-001 → produces PFs
        → Plan iteration: /pace-plan next
```

You can continue with `decompose BR-001` to break business requirements into product features (PFs). The resulting PFs feed directly into `/pace-plan next` as iteration candidates.

---

### Journey B: From Vague Idea to Structured Requirements

**Trigger**: You only have a vague idea — "I want to build a task management tool" — and aren't sure what to build exactly.

**Full path**: `discover` (multi-turn conversation) → candidate tree confirmation → write

**Step-by-step**:

**Step 1: Start a discovery session**

```
You:    /pace-biz discover I want to build a team task management tool
Claude: Let's work through this step by step.
        What problem are you trying to solve? Who are the target users?
You:    Our team tracks tasks in spreadsheets, we keep missing deadlines. Need something simple
Claude: How urgent is this for users? Nice-to-have or real pain point?
        Are there existing alternatives?
You:    It's a pain point. We tried Trello but it's too complex — we just need kanban + reminders
```

The session state is automatically persisted to `.devpace/scope-discovery.md`. If the conversation is interrupted, you can pick up where you left off next time.

**Step 2: Feature brainstorming**

```
Claude: Based on your description, what are the core capabilities?
        What must users be able to do? What are the most basic operations?
You:    Create tasks, drag to change status, set due dates, overdue reminders
Claude: What happens when a task is overdue? Any edge cases to handle?
You:    Just mark overdue tasks in red, no auto-closing needed
Claude: Organizing... Initial candidates:
        BR-001: Task Lifecycle Management
        ├── PF-001: Kanban View with Drag-and-Drop
        ├── PF-002: Due Date Setting
        └── PF-003: Overdue Reminder Notifications
        Does this look right? Any other features?
You:    Add a simple member assignment feature
```

After each round, Claude organizes candidates in real time and shows them for your confirmation.

**Step 3: Confirm candidate tree and write**

```
Claude: Requirements Discovery Summary:

        Goal: Lightweight task management tool to replace spreadsheets
        Users: 5-10 person teams

        Candidate value chain:
        OBJ-1 (Improve team collaboration efficiency)
        └── OPP-001: Team task tracking needs
            └── EPIC-001: Lightweight Kanban Tool
                ├── BR-001: Task Lifecycle Management P0
                │   ├── PF-001: Kanban View with Drag-and-Drop
                │   ├── PF-002: Due Date Setting
                │   └── PF-003: Overdue Reminder Notifications
                └── BR-002: Team Collaboration P1
                    └── PF-004: Member Assignment

        Scope:
          In: Kanban, due dates, reminders, member assignment
          Out: Gantt charts, time tracking, workflow automation

        Will write to .devpace/ after confirmation. Please review and adjust.
You:    Confirm
Claude: Created from discovery session:
        - 1 business opportunity (OPP-001)
        - 1 epic (EPIC-001)
        - 2 business requirements (BR-001 ~ BR-002)
        - 4 product features (PF-001 ~ PF-004)
        → /pace-biz decompose EPIC-001 to further refine specific requirements
        → /pace-biz align to check strategic alignment
        → /pace-plan next to schedule into iteration
```

> **Lite mode difference**: The candidate tree simplifies to `OBJ→PF` structure (no OPP/Epic/BR layers), with PFs placed directly under OBJs.

---

### Journey C: Importing Existing Documents

**Trigger**: The team has scattered requirement documents — meeting notes, PRDs, user feedback surveys, competitor analyses — and you want to consolidate them into a unified feature tree.

**Full path**: `import` → `align`

**Step-by-step**:

**Step 1: Import documents**

```
You:    /pace-biz import meeting-notes-0315.md user-feedback-summary.md
Claude: Analyzing 2 files...

        [meeting-notes-0315.md] Detected as: Meeting minutes
        [user-feedback-summary.md] Detected as: User feedback

        Import analysis:

        NEW (4 items to add):
          + BR-005: Mobile Adaptation (source: meeting-notes-0315.md L23)
          + PF-010: Offline Cache Mode (source: meeting-notes-0315.md L31)
          + PF-011: Push Notification Optimization (source: user-feedback-summary.md L15)
          + PF-012: Batch Operations (source: user-feedback-summary.md L42)

        DUPLICATE (2 items already exist):
          = "Task reminders" ≈ PF-003 (exists, skipping)
          = "Kanban drag" ≈ PF-001 (exists, skipping)

        ENRICHMENT (1 item to enrich):
          ~ PF-002: Adding acceptance criterion "Support natural language date input (e.g., 'next Friday')"

        Confirm: accept all / reject all / review individually
You:    accept all
Claude: Import complete (from 2 files):
        - Added: 1 BR + 3 PFs
        - Enriched: 1 existing entity
        - Skipped: 2 duplicates
        → /pace-biz align to check strategic alignment of new items
```

Claude auto-detects document types (meeting minutes / user feedback / competitor analysis / technical debt lists, etc.) and classifies entities as NEW / DUPLICATE / ENRICHMENT / CONFLICT to avoid duplicate imports.

**Step 2: Check alignment**

```
You:    /pace-biz align
Claude: Strategic Alignment Report
        ══════════════════════════

        OBJ coverage: [1/1] OBJs have Epic/BR coverage ✅

        Orphan entities:
        └── Orphan BR: BR-005 (Mobile Adaptation) not linked to any Epic
            → /pace-change modify BR-005 to link to EPIC-001

        MoS completeness:
        └── Epic-level MoS: [1/1] defined ✅

        Priority distribution: P0 ×2 / P1 ×3 / P2 ×1 — Healthy ✅

        Recommendations:
        1. Link BR-005 to an existing Epic or create a new one
```

> **Lite mode difference**: `import` extracts PF candidates directly (skipping BR mapping). `align` simplifies to OBJ→PF→CR chain checks.

---

### Journey D: Legacy Project Feature Inventory

**Trigger**: You've inherited a legacy project with missing documentation. You're not sure what features exist in the code and want to establish a feature tracking system.

**Full path**: `infer` → `align`

**Step-by-step**:

**Step 1: Scan the codebase**

```
You:    /pace-biz infer
Claude: Scanning codebase...

        Codebase Analysis Report:

        1. Untracked features (code exists, not in feature tree):
           Module [auth/]:
           + PF candidate: User Authentication (routes: login, register, logout)
           + PF candidate: Permission Management (middleware: checkPermission)

           Module [api/export/]:
           + PF candidate: Data Export API (endpoints: /export/csv, /export/json)

        2. Unimplemented features (in feature tree, no code):
           ? PF-003: Overdue Reminder Notifications — Status: planned / abandoned / other?

        3. Technical debt (high TODO/FIXME concentration):
           ! src/utils/parser.js (8 TODOs) — Track this?
           ! src/db/migration.py (5 FIXMEs) — Track this?

        [Git enhanced] Hotspot: src/core/engine.js (42 changes in 30 days)
        [Git enhanced] Coupling: auth/ ↔ session/ (frequently changed together)

        Select per item: accept / skip / adjust grouping
You:    Accept all untracked features, mark PF-003 as planned, accept parser.js debt
Claude: Codebase inference complete:
        - Newly tracked: 3 product features
        - Technical debt: 1 item to address
        - Unimplemented confirmed: 1 feature status updated
        → /pace-biz align to check strategic alignment of new items
        → /pace-dev to start working on priority items
```

`infer` scans across multiple dimensions — directory structure, route definitions, API endpoints, data models — and combines Git history analysis for hotspots and coupling. Technical debt PFs are suffixed with "(technical debt)" for easy filtering.

**Step 2: Align and fill gaps**

Run `/pace-biz align` to verify that newly added items are properly linked to OBJs and Epics. Fix orphan entities using the suggested commands.

> **Lite mode difference**: `infer` scan results map directly to PFs (skipping BR grouping), appended under OBJs.

---

### Journey E: Routine Maintenance and Strategic Alignment

**Trigger**: The project has been running for a while. The feature tree has grown, and it's time for a periodic health check and requirement refinement.

**Recommended path**: `align` → `view` → `refine`

**Step-by-step**:

**Step 1: Health check**

```
You:    /pace-biz align
Claude: Strategic Alignment Report
        ══════════════════════════

        OBJ coverage: [2/2] fully covered ✅

        Orphan entities:
        └── Empty Epic: EPIC-002 (Data Analytics Platform) — no BRs
            → /pace-biz decompose EPIC-002

        MoS completeness:
        ├── OBJ-level MoS: [2/2] defined ✅
        └── Epic-level MoS: [1/2] defined — EPIC-002 missing
            → Add: describe metrics directly, or /pace-change modify EPIC-002

        Priority distribution: P0 ×5 / P1 ×2 / P2 ×1 — ⚠️ Priority inflation (P0 at 62%)

        MoS achievement:
        └── EPIC-001: MoS [0/2] checked (BR completion 100%)
            → Recommend /pace-retro to assess achievement

        Recommendations:
        1. Decompose EPIC-002 → /pace-biz decompose EPIC-002
        2. Re-evaluate P0 priorities, suggest downgrading 2-3 to P1
        3. Assess EPIC-001 MoS achievement → /pace-retro
```

`align` covers 10 checks: OBJ coverage, orphan entities, MoS completeness, decomposition gaps, staleness detection, priority distribution, dependency health, MoS achievement, readiness distribution, and stakeholder coverage. Each issue comes with an inline fix command.

**Step 2: View the business panorama**

```
You:    /pace-biz view
Claude: Business Panorama (TaskFlow)
        ════════════════════════════

        [OBJ-1: Improve team collaboration efficiency]
        ├── [EPIC-001: Lightweight Kanban Tool] (in progress) ← OPP-001
        │   MoS: 0/2 achieved
        │   ├── BR-001: Task Lifecycle Management P0 in progress
        │   │   ├── PF-001 → CR-001 ✅
        │   │   ├── PF-002 → CR-002 ✅
        │   │   └── PF-003 → (CR pending)
        │   └── BR-002: Team Collaboration P1 not started
        │       └── PF-004 → (CR pending)
        └── [EPIC-002: Data Analytics Platform] (planning)
            └── (needs decomposition → /pace-biz decompose EPIC-002)

        [Statistics]
        ├── Epics: 2 total (1 in progress / 1 planning)
        ├── BRs: 3 total
        ├── PFs: 7 total (2 complete)
        └── CRs: 2 total (2 complete)
```

**Step 3: Refine requirement details**

```
You:    /pace-biz refine BR-002
Claude: Current BR-002: Team Collaboration
        ├── User story: undefined
        ├── Acceptance criteria: undefined
        ├── Priority: P1
        └── Linked to: EPIC-001 → OBJ-1

        How do we know this requirement is done? What are the verifiable conditions?
You:    Tasks can be assigned to team members, assignees get notified
Claude: Any business constraints? For example, can a task be assigned to multiple people?
You:    Single assignee for now, multi-assign later
Claude: Refinement preview for BR-002:
          + New user story: As a team lead, I want to assign tasks to members so that ownership is clear
          + New acceptance criteria:
            - [ ] Tasks can be assigned to one team member
            - [ ] Assignees receive notification (in-app + email)
            - [ ] Task list displays current assignee
          + New business rule: Single assignment (v1); multi-assignment deferred

        Confirm write?
You:    Confirm
Claude: Refined BR-002: Team Collaboration
        + Added 3 acceptance criteria
        + Added user story and business rules
        → /pace-biz decompose BR-002 to break down into PFs
        → /pace-dev to start development
```

`refine` only supplements and deepens existing requirement details (acceptance criteria, boundary conditions, user stories) without changing the requirement direction. To adjust scope or priority, use `/pace-change modify`.

## Workflow

### `opportunity` — Capture Business Opportunities

Business opportunities are the raw inputs to the planning process — market signals, customer feedback, stakeholder requests, or competitive observations. `/pace-biz opportunity` captures them with structured metadata so nothing falls through the cracks.

Each opportunity receives:
- **Auto-numbered ID** (OPP-001, OPP-002, ...)
- **Source classification** — customer feedback, market research, stakeholder request, competitive analysis, technical debt, or internal initiative
- **Initial assessment** — Claude suggests relevance to existing OBJs and potential impact level
- **Persisted record** — Written to `.devpace/opportunities.md` with creation date and status (new / evaluating / accepted / declined / deferred)

Multiple opportunities can reference the same strategic objective, building a natural demand signal for prioritization.

### `epic` — Create Strategic Epics

Epics are the bridge between raw opportunities and actionable business requirements. `/pace-biz epic` creates a structured epic that groups related work under a clear business intent.

An epic includes:
- **OBJ alignment** — Which strategic objectives does this epic serve? Claude suggests mappings based on the epic description and linked opportunities
- **Measures of Success (MoS)** — Concrete, verifiable outcomes that define "done" at the business level
- **Stakeholders** (optional) — Key roles, their concerns, and impact levels, progressively enriched during discover/decompose
- **Scope boundary** — What is in scope and what is explicitly excluded
- **Independent file** — Each epic is stored as `epics/EPIC-xxx.md` for traceability and cross-referencing

Epics can be created from an existing opportunity (`/pace-biz epic OPP-001 "title"`) or directly (`/pace-biz epic "title"`). When created from an opportunity, the link is recorded in both directions.

### `decompose` — Break Down into Deliverables

Decomposition is where strategic intent meets execution planning. `/pace-biz decompose` supports two decomposition paths:

1. **Epic → BR** — Break an epic into business requirements, each representing a distinct business capability or outcome
2. **BR → PF** — Break a business requirement into product features, each deliverable in one or two iterations

Claude analyzes the parent entity and suggests a decomposition plan — number of children, proposed titles, scope for each. The user reviews, adjusts, and confirms before any files are created. Decomposition respects the existing value chain: new BRs link back to their epic, new PFs link back to their BR.

**Priority framework** — Three complementary methods are available:

| Method | When to use | How it works |
|--------|-------------|-------------|
| **Value x Effort** (default) | General decomposition | High Value + Low Effort = P0, etc. |
| **MoSCoW** (`--moscow`) | Large BR sets needing triage | Must/Should/Could/Won't → P0/P1/P2/exclude |
| **Kano** (`--kano`) | User-facing product features | Basic/Expected/Excitement → P0/P1/P2 |

The default remains Value x Effort for backward compatibility. Claude may suggest MoSCoW or Kano when the context fits (e.g., many BRs to classify, or user-facing features). Users can always override by specifying priority directly.

**Dependency tracking and visualization** — During Epic → BR decomposition, Claude asks whether each new BR depends on existing BRs under the same epic. Dependencies are recorded in the epic file, visualized in the output (`BR-002 ──depends on──→ BR-001`), and surfaced during `/pace-biz align` health checks. A suggested implementation order based on topological sort is automatically provided.

### `refine` — Enrich Existing Requirements

While `decompose` breaks entities into children, `refine` deepens an existing BR or PF by filling in missing details — acceptance criteria, boundary conditions, user stories, error handling, and non-functional requirements.

The refinement process:
1. **Locate entity with readiness score** — Read current content and calculate a readiness score (0-100%) based on dimension coverage (user story, acceptance criteria, priority, upstream links, edge cases, NFRs). Scores >= 80% are "ready", 60-79% are "mostly ready", <60% are "needs refinement"
2. **Gap analysis** — Claude identifies which dimensions are missing or incomplete (acceptance criteria, user stories, edge cases, NFRs, etc.)
3. **Guided questioning** — 2-3 targeted questions per round, only for dimensions that need attention; dimensions already well-defined are skipped
4. **Preview and confirm** — Changes are shown as a diff-style preview before writing, including a readiness score comparison (before → after)
5. **Dynamic next-step recommendation** — Based on the post-refinement readiness score: >= 80% suggests entering development, 60-79% suggests optional further refinement, and if sibling PFs under the same BR have low readiness, they are highlighted as candidates for attention
6. **Constructive exit** — If users skip all dimensions, Claude provides constructive guidance (view the panorama for context, refine later as the project progresses) rather than a bare "no changes" message

When a BR involves multi-step operations, approval flows, or conditional branching, `refine` detects process keywords and offers to document the key process flow — numbered steps with branches and exception paths — in the BR's overflow file under an optional "Key Process" section.

`refine` differs from `/pace-change modify`: refine deepens the same requirement direction (richer content, same intent), while modify changes direction (renamed, rescoped, reprioritized).

### `align` — Strategic Alignment Check

As the project grows, it is easy for the business plan to drift. `/pace-biz align` performs a health check across the entire upstream value chain:

| Check | What it detects |
|-------|-----------------|
| **OBJ coverage** | Strategic objectives with no epics or BRs mapped to them |
| **Orphan detection** | Epics, BRs, or PFs that are not linked to any upstream entity |
| **MoS completeness** | Epics or BRs missing measurable success criteria |
| **Decomposition gaps** | Epics with no BRs, or BRs with no PFs |
| **Staleness** | Opportunities stuck in "new" status beyond a configurable threshold |
| **Priority distribution** | Detects priority inflation (>60% P0) or missing core priorities (no P0), with healthy ratio guidance |
| **Dependency health** | Circular dependencies, critical-path bottlenecks, and readiness risks (BR scheduled but dependencies incomplete) |
| **MoS achievement** | Reverse-traces epic MoS completion against BR/PF progress; flags epics where BRs are done but MoS unchecked |
| **Readiness distribution** | Calculates readiness scores for all BRs/PFs; warns when P0 requirements average below 70%; recommends top-3 entities most in need of refinement |
| **Stakeholder coverage** | For epics with stakeholder data, checks whether BRs address all high-impact stakeholder concerns; flags active epics with no stakeholder identification |

The output is a concise alignment report with specific recommendations — each issue is paired with an inline fix command (e.g., `→ /pace-biz decompose EPIC-002`, `→ /pace-change modify EPIC-001`).

**Historical trend tracking** — After each `align` run, key metrics (OBJ coverage, orphan count, P0 readiness, MoS completeness) are appended to `.devpace/metrics/insights.md`. On subsequent runs, the report includes a trend comparison section showing how each metric changed since the last check. Three consecutive declines in any metric trigger a focused warning.

### `view` — Business Panorama

`/pace-biz view` renders the full value stream from opportunities down to CRs, giving a bird's-eye view of how business intent flows through the system:

```
OPP-001 "Enterprise SSO demand"
  └─ EPIC-001 "Enterprise Authentication"  [OBJ-1]
       MoS: 2/3 achieved
       ├─ BR-003 "SSO Integration" P0
       │    ├─ PF-007 "SAML Provider"      → CR-012 (developing)
       │    └─ PF-008 "OIDC Provider"      → CR-013 (created)
       └─ BR-004 "Session Management" P1
            └─ PF-009 "Token Lifecycle"     → CR-014 (created)
```

Filters are available by OBJ, epic, status, or depth level. When called without filters, the full tree is displayed with status indicators. BRs and PFs include readiness scores when available (e.g., `BR-001: Task Lifecycle P0 [Readiness 85%]`).

**Coverage summary** — At the end of the statistics section, a coverage summary shows the decomposition rate at each value chain layer (OBJ→Epic, Epic→BR, BR→PF, PF→CR), highlighting where gaps exist (e.g., "Epic→BR decomposition: 3/4 (75%, EPIC-003 pending)").

**Problem-first mode** — When 3 or more entities need attention (empty MoS, undecomposed, orphaned, etc.), the view automatically switches to problem-first layout: actionable items are grouped at the top under a "Needs Attention" section with inline fix commands, while healthy entities are collapsed below.

**Inline action guidance** — Entities in actionable states show next-step hints: empty MoS prompts for definition, undecomposed epics/BRs suggest `/pace-biz decompose`, evaluating opportunities suggest `/pace-biz epic`, low-readiness items suggest `/pace-biz refine`.

**Role-adapted display** — When a preferred role is set via `/pace-role`, the view adds role-specific columns without changing the base structure (e.g., Biz Owner sees MoS progress per epic, PM sees PF completion rates and dependency info, Tester sees acceptance criteria counts and Gate 2 status).

### `discover` — Interactive Requirements Discovery

When starting from a vague idea — "I want to build a smart customer service system" — `/pace-biz discover` launches a guided multi-turn conversation that progressively shapes the idea into a structured value chain.

**Smart routing** — Before entering the discovery flow, Claude checks whether the user's input might be better served by another subcommand: file paths are redirected to `import`, code-related keywords to `infer`. The user can always continue with `discover` if preferred.

The process unfolds in stages:
1. **Goal framing** (1-2 rounds) — What problem are we solving? Who are the users? Optionally identifies key stakeholders and their concerns
2. **Feature brainstorming** (2-4 rounds) — What must users be able to do? What happens in edge cases?
3. **Boundary definition** (1-2 rounds) — What is explicitly out of scope? What constraints exist?
4. **Validation** (1 round) — Lightweight deduplication check flags candidates that overlap with existing entities (> 70% keyword similarity), then review the structured candidate tree (OPP → Epic → BR → PF) and adjust

Session state is persisted to `.devpace/scope-discovery.md`, so discovery can span multiple conversations. Once confirmed, all candidates are written to the appropriate `.devpace/` files and the temporary session file is removed.

**Role-adapted questioning** — When a preferred role is set, the brainstorming phase adjusts its focus: Biz Owner questions emphasize revenue impact and market influence, PM questions target user scenarios and competitive landscape, Dev questions probe technical feasibility and architecture constraints, Tester questions focus on testability and boundary conditions, Ops questions address deployment and infrastructure needs. The core flow and output structure remain unchanged regardless of role.

### `import` — Multi-Source Document Import

Teams accumulate requirements in many places — meeting notes, user feedback surveys, competitor analyses, technical debt lists. `/pace-biz import` reads these documents, extracts requirement entities, and merges them into the existing feature tree.

Supported source types (auto-detected):
- **Meeting minutes** — action items become BR/PF candidates
- **User feedback** — pain points become BRs, feature requests become PFs
- **Competitor analysis** — gap features become PF candidates
- **Technical debt lists** — debt items become PFs tagged as technical debt
- **Issue exports** (CSV/JSON) — issues map to PF/CR candidates
- **PRD / API specs** — same parsing as `/pace-init --from`

Each extracted entity is classified as NEW, DUPLICATE, ENRICHMENT, or CONFLICT relative to the existing tree. The merge plan includes source cross-references — each item shows its origin (file + line number), related existing entities, similarity scores for duplicates, and before/after comparisons for enrichments — enabling informed accept/reject decisions. The similarity threshold defaults to 80% but can be adjusted via `--threshold` (e.g., `import doc.md --threshold 0.7`). A two-layer mechanism combines fast keyword overlap screening with semantic analysis for borderline cases. Import operates at the OPP/Epic/BR/PF level — it does not create CRs.

### `infer` — Codebase Feature Inference

For legacy projects or projects that outgrew their documentation, `/pace-biz infer` scans the codebase and reverse-engineers a feature map:

- **Structure analysis** — directories, routes, API endpoints, data models, UI components
- **Signal mining** — TODO/FIXME density, README vs code drift, package scripts
- **Git-enhanced analysis** (when available) — file hotspots, co-change coupling, contributor distribution

The output is a three-part gap report:
1. **Untracked features** — code exists but the feature tree has no corresponding PF
2. **Unimplemented features** — feature tree has PFs but no code exists
3. **Technical debt** — high TODO/FIXME concentration areas

Users select which items to add to the feature tree. Technical debt PFs are suffixed with "(technical debt)" for easy filtering.

## Role Awareness

`/pace-biz` adapts its behavior based on the preferred role set via `/pace-role`. Role awareness affects three dimensions without changing core workflow or output structure:

| Dimension | How role affects behavior |
|-----------|-------------------------|
| **Questioning** | `discover` and `decompose` adjust follow-up question focus (e.g., Biz Owner → revenue impact, Dev → technical constraints, Tester → acceptance criteria) |
| **Display** | `view` adds role-specific columns (e.g., PM sees dependency info, Ops sees release status) |
| **Prompting** | `decompose` appends role-relevant considerations during BR/PF creation |

Default role (Dev) produces zero behavioral change — role adaptation is purely additive.

## Write Scope Protection

`/pace-biz` is a planning-domain skill and must never modify source code or non-planning files. A PreToolUse hook enforces this at runtime:

- **Allowed targets**: Any file under `.devpace/` (opportunities.md, epics/, project.md, requirements/, scope-discovery.md, state.md, etc.)
- **Blocked targets**: All files outside `.devpace/` — the hook exits with code 2 and a descriptive error message
- **Epic quality gate**: A prompt hook validates that epic files being written have valid OBJ references and measurable MoS definitions

This protection runs automatically — users do not need to configure or invoke it.

## Backward Compatibility

Projects initialized before `/pace-biz` was introduced — those without `opportunities.md`, `epics/`, or upstream BR linkage — continue to work without any changes. The existing PF → CR flow is unaffected. `/pace-biz` capabilities become available incrementally: capture your first opportunity or create your first epic whenever you are ready, and the value chain extends upward naturally.

## Integration with Other Commands

| Command | Relationship |
|---------|-------------|
| `/pace-init` | Initializes the `.devpace/` structure. After `/pace-biz` is available, `pace-init` can optionally scaffold `opportunities.md` and `epics/` directory. |
| `/pace-change` | Handles PF-level requirement changes. `/pace-biz` operates upstream — creating the BRs and PFs that `/pace-change` later manages. |
| `/pace-plan` | Plans iterations by selecting PFs. `/pace-biz decompose` produces the PFs that feed into `/pace-plan next`. |
| `/pace-status` | Reflects the full project state. With `/pace-biz` data present, status views can include upstream context (epic progress, OBJ coverage). |
| `/pace-trace` | Traces value chain connections. `/pace-biz` enriches traceability by adding the OPP → EPIC → BR layers above the existing BR → PF → CR chain. |
| `/pace-role` | Sets the preferred role perspective. `/pace-biz` reads this setting to adapt questioning focus, display columns, and decomposition prompts per role. |

## Related Resources

- [epic-format.md](../../knowledge/_schema/epic-format.md) — Epic file schema
- [br-format.md](../../knowledge/_schema/br-format.md) — Business requirement file schema
- [opportunity-format.md](../../knowledge/_schema/opportunity-format.md) — Opportunity record schema
- [skills/pace-biz/](../../skills/pace-biz/) — Operational procedures
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules
- [User Guide](../user-guide.md) — Quick reference for all commands
