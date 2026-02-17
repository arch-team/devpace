<!-- Generated: 2026-02-18 | Files scanned: 68 | Token estimate: ~500 -->

# Testing — devpace Plugin

## Test Tiers

```
Tier 1: Static (pytest)     ← automated, CI-ready
Tier 2: Integration (bash)  ← requires claude CLI
Tier 3: Scenarios (manual)  ← Claude-in-the-loop, human tester
Tier 4: Evaluation (manual) ← acceptance matrix, UX rubric
```

## Tier 1: Static Tests (9 modules, 802 lines total)

| Test Module | Lines | Validates |
|-------------|-------|-----------|
| test_schema_compliance | 117 | Schema structure, required fields |
| test_frontmatter | 114 | SKILL.md frontmatter legality |
| test_markdown_structure | 94 | §0 cards, skill split heuristic |
| test_template_placeholders | 84 | {{PLACEHOLDER}} format compliance |
| test_cross_references | 75 | Inter-file reference integrity |
| test_state_machine | 66 | CR states/transitions consistency |
| test_layer_separation | 45 | Product→Dev reference prohibition |
| test_naming_conventions | 42 | kebab-case enforcement |
| test_plugin_json_sync | 37 | plugin.json ↔ filesystem sync |

Shared: conftest.py (128 lines) — paths, inventories, fixtures, CR states

## Tier 2: Integration (1 script)

```
tests/integration/test_plugin_loading.sh
  → `claude --plugin-dir ./` load verification
  → Exit 77 = skip (no CLI available)
```

## Tier 3: Scenarios (13 files)

| Scenario | Requirement | File |
|----------|-------------|------|
| S01 首次初始化 | S1, F1.1 | S01-init.md |
| S02 日常推进 | S2, F1.2-F1.3 | S02-daily-advance.md |
| S03 查看进度 | S3, F1.5 | S03-status-levels.md |
| S04-S07 变更管理 | S4-S7, F2.x | S04-S07 change-*.md |
| S08 Code Review | S8, F1.7 | S08-review-flow.md |
| S09 迭代回顾 | S9, F3.x | S09-retro.md |
| S10-S12 辅助功能 | S10-S12 | S10-S12 *.md |
| V 新项目验证 | V2.14-V2.16 | V-new-project.md |

## Tier 4: Evaluation (3 files)

- acceptance-matrix.md — Pass/Partial/Fail per requirement
- ux-rubric.md — UX quality scoring
- v2-verification.md — Phase 2 verification plan

## Validation Pipeline

```
pytest tests/static/ -v          # Tier 1 (primary)
bash scripts/validate-all.sh     # Tier 1 + 1.5 (layer grep) + Tier 2
claude --plugin-dir ./            # Manual load check
```
