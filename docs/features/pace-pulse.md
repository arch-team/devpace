🌐 [中文版](pace-pulse_zh.md) | English

# pace-pulse — Rhythm Heartbeat Check

System-level Skill auto-invoked by Claude. Not user-callable.

## Core Features

- **17 Rhythm Signals**: Detects anomalies across efficiency, quality, planning, risk, ops, and governance dimensions
- **Non-Intrusive**: 0-2 line suggestions appended after checkpoints, never interrupts workflow
- **Actionable Suggestions**: Every suggestion includes executable command (e.g., `/pace-guard report`)
- **Session Lifecycle Coverage**: Session start (layered summary) + advance mode (periodic pulse) + session end (rhythm digest)

## Key Enhancements (v1.6)

### Dynamic Signal Priority
Signals are weighted by iteration phase: early stage prioritizes CR stalling and requirement conflicts; sprint phase prioritizes time pressure and review backlogs. See `pulse-procedures.md` "Dynamic Signal Weights" section.

### Signal Correlation Analysis
When 2+ signals from the same group fire simultaneously, outputs a composite diagnosis instead of individual suggestions. Groups: Efficiency, Quality, Planning, Risk. See `pulse-procedures.md` "Signal Grouping" section.

### Session End Rhythm Digest
Outputs a 1-2 line session summary with CR completion stats, notable rhythm signals, and iteration progress delta. Prefix: `📊`.

### Severity Escalation
Same signal can re-trigger if severity doubles (e.g., review backlog grows from 3 to 6+). Marked with `⚠️` prefix.

### Positive Feedback
When no anomalies are detected at key milestones (CR merged, iteration 50%), outputs `✓ Rhythm healthy` (max 1/session, does not count toward quota).

### Pulse-Counter Coordination
Write-volume hook (`pulse-counter.mjs`) checks if pace-pulse ran recently (< 5 min) and skips its reminder to avoid double-reminding.

## Related Resources

- **Authoritative source**: `skills/pace-pulse/pulse-procedures.md` (signal table, templates, grouping, dynamic weights)
- **Trigger rules**: `rules/devpace-rules.md` §10 (advance mode), §1 (session start), §6 (session end)
- **Architecture**: `docs/design/design.md` Appendix B (component dependency graph)
