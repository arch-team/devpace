# Risk Management (`/pace-guard`)

devpace risk management provides unified lifecycle risk tracking: from pre-coding Pre-flight scans, to runtime monitoring during development, to cross-iteration trend analysis — making risks visible, trackable, and resolvable.

## Prerequisites

| Requirement | Purpose | Required? |
|-------------|---------|:---------:|
| `.devpace/` initialized | Project structure, CR tracking | Yes |
| `.devpace/risks/` directory | Risk file storage (auto-created on first scan) | Auto |

> **Graceful degradation**: Without `.devpace/`, `scan` still works (instant assessment based on codebase). `trends`, `report`, and `resolve` require historical data and are unavailable in degraded mode.

## Quick Start

```
1. /pace-guard scan              --> Pre-flight 5-dimension risk assessment
2. /pace-guard monitor           --> Real-time risk status summary
3. /pace-guard resolve RISK-001 mitigated  --> Update risk status
4. /pace-guard trends            --> Cross-iteration trend analysis
5. /pace-guard report            --> Project-level risk dashboard
```

Daily workflow: L/XL CRs auto-trigger `scan` at intent checkpoint. Use `monitor` during development to track risk status. Run `trends` and `report` at iteration boundaries.

## Command Reference

### `scan` (default, no arguments)

Pre-flight risk scan with 5-dimension assessment:

| Dimension | What it checks | Data source |
|-----------|---------------|-------------|
| Historical lessons | Similar CR failure/rejection patterns | insights.md (defense type, confidence ≥ 0.5) |
| Dependency impact | Reverse dependency chain of changed files | Code file import/require analysis |
| Architecture compatibility | Changes vs project technical conventions | .devpace/context.md |
| Scope complexity | Actual workload vs expected | CR description + file tree |
| Security sensitivity | Auth/crypto/secret/token/password involvement | File path keyword analysis |

**Complexity-adaptive**: Explicit `scan` adjusts depth by CR complexity — S-level scans only 2 dimensions (historical + security), M-level scans 3 dimensions, L/XL runs full 5 dimensions. Use `scan --full` to force complete scan regardless of complexity.

**Anomaly-driven output**: By default, only Medium/High dimensions are displayed. If all Low, outputs a single line: "5-dimension scan all Low — risk is manageable." Use `--detail` for the full matrix.

### `monitor`

Real-time risk status summary for the current CR.

**Layered output**:
- **Brief** (default): `CR-003 risk: 0 new / 1 pending(M) / 2 mitigated — manageable`
- **Standard** (`--detail` or auto-upgrade when Medium/High detected): Full table format
- **Detail**: Historical comparison + mitigation suggestions expanded

### `trends`

Cross-CR trend analysis across iterations.

**Default**: 3-5 line trend summary (direction indicators + most critical pattern). Full output with `--detail` or when consumed by `/pace-retro`.

**Risk aging**: Risks open for 2+ iterations are flagged with aging warnings and upgrade/resolve suggestions.

### `report`

Project-level risk dashboard showing all open risks grouped by severity.

### `resolve`

Update risk status: `resolve <RISK-ID> <target-status>` where target is `mitigated`, `accepted`, or `resolved`.

**Batch resolve**: `resolve --batch <severity>` processes multiple risks of the same severity level at once.

**Auto-suggestions**: Gate 2 pass suggests resolving associated Low risks. `/pace-plan close` suggests resolving all risks for completed CRs.

## Risk Levels and Responses

| Level | Standard mode | Autonomous mode |
|-------|-------------|-----------------|
| Low | Silent logging | Silent logging |
| Medium | Log + reminder + suggestions | Log + auto-mitigate + report |
| High | **Pause, await human confirmation** | Reminder + suggestions + **await human confirmation** |

> **Iron rule**: High risks cannot bypass human confirmation — same level as Gate 3 approval.

## Auto-Triggers

- L/XL CRs auto-trigger `scan` when entering development (intent checkpoint)
- Advance mode runs lightweight risk detection at each checkpoint
- Pulse check triggers `monitor` when risk backlog detected (>3 open or any High)

## Cross-Skill Integration

| Integration point | Behavior |
|-------------------|----------|
| `/pace-change` risk assessment | Reads `.devpace/risks/` history to improve risk scoring accuracy |
| `/pace-review` Gate 2 | Review summary includes risk status line (highlights unresolved High risks) |
| `/pace-plan close` | Suggests batch-resolving risks for completed CRs |
| `/pace-test impact` | Consumes scan-marked high-risk modules for test prioritization |

## Related Resources

- [Risk format schema](../../knowledge/_schema/risk-format.md)
- [Risk metrics](../../knowledge/metrics.md#风险管理指标)
- [Pulse risk signal](../../skills/pace-pulse/pulse-procedures-core.md)
