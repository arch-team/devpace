# pace-role — Role Perspective Switching

> Switch Claude's output perspective across five BizDevOps roles to view the same project through different lenses.

## Core Features

### Multi-Role Perspective
Switch between five built-in roles that align with BizDevOps theory:

| Role | Focus Areas | Output Style |
|------|-------------|-------------|
| **Biz Owner** | MoS achievement, business value delivery | Business terminology, linked to OBJ |
| **PM** | Iteration progress, delivery rhythm, dependencies | Feature-level, schedule-focused |
| **Dev** (default) | CR status, quality gates, technical details | Technical terminology, implementation-focused |
| **Tester** | Defect distribution, test coverage, verification | Quality metrics, defect-prevention-focused |
| **Ops** | Release status, deployment health, MTTR | Operations terminology, stability-focused |

### Auto-Inference
devpace automatically detects role context from conversation keywords and adjusts output accordingly. Inference uses sticky rules to prevent role flickering — requires consistent signals across 2+ conversation turns before switching.

### Context-Aware Adaptation
On role switch, devpace performs a relevance assessment scanning current project context (active CRs, iteration progress, risk status) to identify the 2-3 most relevant focus dimensions for the new role.

### Cross-Session Persistence
Set a preferred role via `/pace-role set-default <role>` to persist across sessions. Stored in project.md configuration.

### Multi-Perspective Snapshot
`/pace-role compare` outputs a compact 5-line snapshot showing all role perspectives simultaneously — useful at decision points (merge, change approval, iteration planning).

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `/pace-role <role>` | Switch to specified role perspective |
| `/pace-role` (no args) | Show current role with source info |
| `/pace-role auto` | Return to auto-inference mode |
| `/pace-role compare` | Multi-perspective snapshot |
| `/pace-role set-default <role>` | Set cross-session default role |
| `/pace-role pm --focus X,Y` | Switch with manual focus override |

## Cross-Skill Integration

Role awareness affects output across multiple skills:

| Skill | Integration Level | Behavior |
|-------|-------------------|----------|
| pace-status | Deep (5 role templates) | Full output restructuring per role |
| pace-next | Medium | Step 5 table adjusts terminology |
| pace-retro | Medium | Report summary reordered by role focus |
| pace-change | Light | Impact summary phrased per role |
| pace-pulse | Light | Signal messaging adapted to role context |

## Related Resources

- Role dimensions (authority source): `skills/pace-role/role-procedures-dimensions.md`
- Role switching procedures: `skills/pace-role/role-procedures-switch.md`
- Compare snapshot procedures: `skills/pace-role/role-procedures-compare.md`
- Role inference rules: `skills/pace-role/role-procedures-inference.md`
- Status role templates: `skills/pace-status/status-procedures-roles.md`
- Teaching entries: `knowledge/_guides/teaching-catalog.md` (`role_adapt`, `role_infer`)
- Theory background: `knowledge/theory.md` §4 (BizDevOps roles)
