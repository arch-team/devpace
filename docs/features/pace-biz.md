# Business Planning (`/pace-biz`)

devpace has always managed the flow from product features (PF) down to code changes (CR), but the upstream question — *where do these features come from?* — was left outside the system. Business opportunities were captured in scattered notes, epics lived in external tools, and the link between strategic objectives and day-to-day development was implicit at best. `/pace-biz` closes this gap by bringing structured business planning into the same value chain, so that every line of code can be traced back to a business opportunity.

## Quick Start

```
1. /pace-biz opportunity "Enterprise clients need SSO"  → Capture opportunity → OPP-001 created
2. /pace-biz epic OPP-001 "Enterprise Authentication"   → Create epic → EPIC-001 with OBJ alignment
3. /pace-biz decompose EPIC-001                         → Break down → BRs and PFs generated
```

Or let Claude guide you interactively:

```
You:    /pace-biz
Claude: [Recommends next action based on project context]
        Or choose: opportunity / epic / decompose / align / view
```

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
- **Scope boundary** — What is in scope and what is explicitly excluded
- **Independent file** — Each epic is stored as `epics/EPIC-xxx.md` for traceability and cross-referencing

Epics can be created from an existing opportunity (`/pace-biz epic OPP-001 "title"`) or directly (`/pace-biz epic "title"`). When created from an opportunity, the link is recorded in both directions.

### `decompose` — Break Down into Deliverables

Decomposition is where strategic intent meets execution planning. `/pace-biz decompose` supports two decomposition paths:

1. **Epic → BR** — Break an epic into business requirements, each representing a distinct business capability or outcome
2. **BR → PF** — Break a business requirement into product features, each deliverable in one or two iterations

Claude analyzes the parent entity and suggests a decomposition plan — number of children, proposed titles, scope for each. The user reviews, adjusts, and confirms before any files are created. Decomposition respects the existing value chain: new BRs link back to their epic, new PFs link back to their BR.

### `align` — Strategic Alignment Check

As the project grows, it is easy for the business plan to drift. `/pace-biz align` performs a health check across the entire upstream value chain:

| Check | What it detects |
|-------|-----------------|
| **OBJ coverage** | Strategic objectives with no epics or BRs mapped to them |
| **Orphan detection** | Epics, BRs, or PFs that are not linked to any upstream entity |
| **MoS completeness** | Epics or BRs missing measurable success criteria |
| **Decomposition gaps** | Epics with no BRs, or BRs with no PFs |
| **Staleness** | Opportunities stuck in "new" status beyond a configurable threshold |

The output is a concise alignment report with specific recommendations for each issue found.

### `view` — Business Panorama

`/pace-biz view` renders the full value stream from opportunities down to CRs, giving a bird's-eye view of how business intent flows through the system:

```
OPP-001 "Enterprise SSO demand"
  └─ EPIC-001 "Enterprise Authentication"  [OBJ-1]
       ├─ BR-003 "SSO Integration"
       │    ├─ PF-007 "SAML Provider"      → CR-012 (developing)
       │    └─ PF-008 "OIDC Provider"      → CR-013 (created)
       └─ BR-004 "Session Management"
            └─ PF-009 "Token Lifecycle"     → CR-014 (created)
```

Filters are available by OBJ, epic, status, or depth level. When called without filters, the full tree is displayed with status indicators.

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

## Related Resources

- [epic-format.md](../../knowledge/_schema/epic-format.md) — Epic file schema
- [br-format.md](../../knowledge/_schema/br-format.md) — Business requirement file schema
- [opportunity-format.md](../../knowledge/_schema/opportunity-format.md) — Opportunity record schema
- [skills/pace-biz/](../../skills/pace-biz/) — Operational procedures
- [devpace-rules.md](../../rules/devpace-rules.md) — Runtime behavior rules
- [User Guide](../user-guide.md) — Quick reference for all commands
