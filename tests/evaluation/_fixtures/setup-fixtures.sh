#!/usr/bin/env bash
# setup-fixtures.sh — Idempotent generation of behavioral eval environment fixtures.
#
# Each fixture is a minimal project state that evals.json scenarios reference
# via their `env` field. Fixtures are generated (not checked in) because they
# include git repo state that should not be stored in the parent repo.
#
# Usage:
#   bash tests/evaluation/_fixtures/setup-fixtures.sh          # generate all
#   bash tests/evaluation/_fixtures/setup-fixtures.sh ENV-DEV-A # generate one
#
# Idempotent: re-running recreates fixtures from scratch (rm + create).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

create_fixture() {
    local name="$1"
    local dir="$FIXTURES_DIR/$name"

    # Clean slate
    rm -rf "$dir"
    mkdir -p "$dir"

    echo "[fixture] Creating $name ..."
}

init_git() {
    local dir="$1"
    (
        cd "$dir"
        git init -q
        git config user.email "eval@devpace.test"
        git config user.name "eval-fixture"
        git add -A
        git commit -q -m "chore: initial fixture state" --allow-empty
    )
}

init_devpace() {
    local dir="$1"
    mkdir -p "$dir/.devpace/backlog"

    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

(none)

## next-step

Run /pace-dev to start a new task.

## last-updated

2026-01-01T00:00:00Z
STATE
}

create_minimal_src() {
    local dir="$1"
    mkdir -p "$dir/src"
    cat > "$dir/src/index.js" << 'SRC'
// minimal project skeleton
console.log("hello devpace");
SRC
    cat > "$dir/package.json" << 'PKG'
{
  "name": "fixture-project",
  "version": "0.1.0",
  "main": "src/index.js"
}
PKG
}

create_cr() {
    local dir="$1"
    local cr_id="$2"
    local status="$3"
    local cr_type="${4:-feature}"
    local complexity="${5:-S}"

    cat > "$dir/.devpace/backlog/$cr_id.md" << CREOF
# $cr_id

## meta

- type: $cr_type
- status: $status
- complexity: $complexity
- created: 2026-01-15T10:00:00Z

## intent

User requested a feature implementation.

## scope

src/

## acceptance-criteria

- Feature works as described

## events

- [2026-01-15T10:00:00Z] created
CREOF

    # Append status-specific events
    case "$status" in
        developing)
            echo "- [2026-01-15T10:05:00Z] status: created -> developing" \
                >> "$dir/.devpace/backlog/$cr_id.md"
            ;;
        verifying)
            cat >> "$dir/.devpace/backlog/$cr_id.md" << 'EVEOF'
- [2026-01-15T10:05:00Z] status: created -> developing
- [2026-01-15T11:00:00Z] status: developing -> verifying
EVEOF
            ;;
        in_review)
            cat >> "$dir/.devpace/backlog/$cr_id.md" << 'EVEOF'
- [2026-01-15T10:05:00Z] status: created -> developing
- [2026-01-15T11:00:00Z] status: developing -> verifying
- [2026-01-15T11:30:00Z] status: verifying -> in_review
EVEOF
            ;;
        merged)
            cat >> "$dir/.devpace/backlog/$cr_id.md" << 'EVEOF'
- [2026-01-15T10:05:00Z] status: created -> developing
- [2026-01-15T11:00:00Z] status: developing -> verifying
- [2026-01-15T11:30:00Z] status: verifying -> in_review
- [2026-01-15T12:00:00Z] status: in_review -> approved
- [2026-01-15T12:05:00Z] status: approved -> merged
EVEOF
            ;;
    esac
}

# ---------------------------------------------------------------------------
# ENV-DEV-A: Empty project + devpace initialized, no CRs
# Used by: evals 1, 2, 3, 8, 10, 14 (new feature scenarios)
# ---------------------------------------------------------------------------
build_env_dev_a() {
    create_fixture "ENV-DEV-A"
    local dir="$FIXTURES_DIR/ENV-DEV-A"
    create_minimal_src "$dir"
    init_devpace "$dir"
    init_git "$dir"
}

# ---------------------------------------------------------------------------
# ENV-DEV-B: 3 existing CRs (CR-001 merged, CR-002 developing, CR-003 created)
# Used by: evals 4, 5, 6, 10, 11 (continue/resume/defect scenarios)
# ---------------------------------------------------------------------------
build_env_dev_b() {
    create_fixture "ENV-DEV-B"
    local dir="$FIXTURES_DIR/ENV-DEV-B"
    create_minimal_src "$dir"
    init_devpace "$dir"

    create_cr "$dir" "CR-001" "merged"
    create_cr "$dir" "CR-002" "developing"
    create_cr "$dir" "CR-003" "created"

    # Update state.md to reflect CR-002 as current work
    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

CR-002 (feature: user profile page)

## next-step

Continue implementing CR-002 profile page components.

## last-updated

2026-01-16T09:00:00Z
STATE

    init_git "$dir"
}

# ---------------------------------------------------------------------------
# ENV-DEV-C: CR-002 in verifying status (Gate 1 scenario)
# Used by: eval 7 (gate1-reflection)
# ---------------------------------------------------------------------------
build_env_dev_c() {
    create_fixture "ENV-DEV-C"
    local dir="$FIXTURES_DIR/ENV-DEV-C"
    create_minimal_src "$dir"
    init_devpace "$dir"

    create_cr "$dir" "CR-001" "merged"
    create_cr "$dir" "CR-002" "verifying"
    create_cr "$dir" "CR-003" "created"

    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

CR-002 (feature: user profile page) - verifying

## next-step

Run Gate 1 reflection checks for CR-002.

## last-updated

2026-01-16T11:00:00Z
STATE

    # Add implementation files for Gate 1 to inspect
    mkdir -p "$dir/src/profile"
    cat > "$dir/src/profile/index.js" << 'SRC'
// User profile page component
export function ProfilePage({ userId }) {
  return { userId, name: "User" };
}
SRC

    init_git "$dir"
}

# ---------------------------------------------------------------------------
# ENV-DEV-D: Empty project, NO .devpace/ (first-time init scenario)
# Used by: eval 9 (context-auto-generation)
# ---------------------------------------------------------------------------
build_env_dev_d() {
    create_fixture "ENV-DEV-D"
    local dir="$FIXTURES_DIR/ENV-DEV-D"
    create_minimal_src "$dir"
    # Deliberately no init_devpace — tests first-time initialization
    init_git "$dir"
}

# ---------------------------------------------------------------------------
# ENV-DEV-E: CR-005 developing, S complexity, drift scenario
# Used by: eval 12 (drift-detection)
# ---------------------------------------------------------------------------
build_env_dev_e() {
    create_fixture "ENV-DEV-E"
    local dir="$FIXTURES_DIR/ENV-DEV-E"
    create_minimal_src "$dir"
    init_devpace "$dir"

    # CR-005 with narrow scope
    cat > "$dir/.devpace/backlog/CR-005.md" << 'CREOF'
# CR-005

## meta

- type: feature
- status: developing
- complexity: S
- created: 2026-01-20T10:00:00Z

## intent

Refactor date formatting utility.

## scope

src/utils/format.ts

## acceptance-criteria

- Date formatting uses ISO 8601 consistently

## events

- [2026-01-20T10:00:00Z] created
- [2026-01-20T10:05:00Z] status: created -> developing
CREOF

    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

CR-005 (feature: date formatting refactor) - developing

## next-step

Continue refactoring date formatting in src/utils/format.ts.

## last-updated

2026-01-20T10:30:00Z
STATE

    # Create files that simulate drift (files outside scope)
    mkdir -p "$dir/src/utils" "$dir/src/api" "$dir/src/models" "$dir/src/middleware"
    echo "// format utility" > "$dir/src/utils/format.ts"
    echo "// api handler" > "$dir/src/api/handler.ts"
    echo "// data model" > "$dir/src/models/user.ts"
    echo "// auth middleware" > "$dir/src/middleware/auth.ts"

    init_git "$dir"

    # Simulate drift: modify files outside scope after initial commit
    (
        cd "$dir"
        echo "// modified" >> src/api/handler.ts
        echo "// modified" >> src/models/user.ts
        echo "// modified" >> src/middleware/auth.ts
        echo "// new file" > src/api/routes.ts
        echo "// new file" > src/api/validation.ts
        echo "// new file" > src/models/schema.ts
        echo "// new file" > src/middleware/rate-limit.ts
        echo "// updated" >> src/utils/format.ts
        git add -A
        git commit -q -m "feat: expand implementation beyond initial scope"
    )
}

# ---------------------------------------------------------------------------
# ENV-DEV-F: L complexity CR with execution plan, steps 1-2 done
# Used by: eval 13 (large-cr-step-isolation-checkpoint)
# ---------------------------------------------------------------------------
build_env_dev_f() {
    create_fixture "ENV-DEV-F"
    local dir="$FIXTURES_DIR/ENV-DEV-F"
    create_minimal_src "$dir"
    init_devpace "$dir"

    cat > "$dir/.devpace/backlog/CR-007.md" << 'CREOF'
# CR-007

## meta

- type: feature
- status: developing
- complexity: L
- created: 2026-01-25T10:00:00Z

## intent

Implement complete notification system with email, SMS, and in-app channels.

## scope

src/notifications/

## execution-plan

1. Design notification data model and database schema
2. Implement email notification channel
3. Implement SMS notification channel via Twilio
4. Implement in-app notification with WebSocket
5. Add notification preferences and rate limiting

## acceptance-criteria

- Given a notification event, When dispatched, Then correct channel delivers message
- Given user preferences, When notification sent, Then respects channel preferences
- Given high volume, When rate limit hit, Then queues notifications gracefully

## events

- [2026-01-25T10:00:00Z] created
- [2026-01-25T10:10:00Z] status: created -> developing
- [2026-01-25T11:00:00Z] [checkpoint: step-1-done] notification model designed
- [2026-01-25T14:00:00Z] [checkpoint: step-2-done] email channel implemented
CREOF

    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

CR-007 (feature: notification system) - developing [step 3/5]

## next-step

Implement SMS notification channel via Twilio (step 3 of execution plan).

## last-updated

2026-01-25T14:00:00Z
STATE

    # Simulate completed steps
    mkdir -p "$dir/src/notifications"
    echo "// notification model (step 1)" > "$dir/src/notifications/model.js"
    echo "// email channel (step 2)" > "$dir/src/notifications/email.js"

    init_git "$dir"
}

# ---------------------------------------------------------------------------
# ENV-DEV-G: CR-004 in in_review status (Gate 2 scenario)
# Used by: eval 15 (gate2-reflection-and-decision-records)
# ---------------------------------------------------------------------------
build_env_dev_g() {
    create_fixture "ENV-DEV-G"
    local dir="$FIXTURES_DIR/ENV-DEV-G"
    create_minimal_src "$dir"
    init_devpace "$dir"

    cat > "$dir/.devpace/backlog/CR-004.md" << 'CREOF'
# CR-004

## meta

- type: feature
- status: in_review
- complexity: M
- created: 2026-01-22T10:00:00Z

## intent

Add search functionality with full-text search and filters.

## scope

src/search/

## acceptance-criteria

- Given a search query, When submitted, Then returns relevant results within 200ms
- Given filter options, When applied, Then results are filtered correctly
- Given empty query, When submitted, Then shows recent items

## events

- [2026-01-22T10:00:00Z] created
- [2026-01-22T10:10:00Z] status: created -> developing
- [2026-01-22T15:00:00Z] [decision] Used Elasticsearch over PostgreSQL FTS for scalability
- [2026-01-22T16:00:00Z] [decision] Chose debounced client-side search over server-side pagination
- [2026-01-22T18:00:00Z] status: developing -> verifying
- [2026-01-22T18:30:00Z] [gate1-reflection: tech-debt] Search index rebuild has no incremental mode
- [2026-01-22T18:30:00Z] [gate1-reflection: test-coverage] 78% coverage, missing edge case for empty index
- [2026-01-22T19:00:00Z] status: verifying -> in_review
CREOF

    cat > "$dir/.devpace/state.md" << 'STATE'
# devpace state

## current-work

CR-004 (feature: search functionality) - in_review

## next-step

Gate 2 review pending. Run /pace-dev #4 to proceed with review.

## last-updated

2026-01-22T19:00:00Z
STATE

    mkdir -p "$dir/src/search"
    echo "// search engine" > "$dir/src/search/engine.js"
    echo "// search filters" > "$dir/src/search/filters.js"
    echo "// search index" > "$dir/src/search/index.js"

    init_git "$dir"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TARGET="${1:-all}"

case "$TARGET" in
    ENV-DEV-A) build_env_dev_a ;;
    ENV-DEV-B) build_env_dev_b ;;
    ENV-DEV-C) build_env_dev_c ;;
    ENV-DEV-D) build_env_dev_d ;;
    ENV-DEV-E) build_env_dev_e ;;
    ENV-DEV-F) build_env_dev_f ;;
    ENV-DEV-G) build_env_dev_g ;;
    all)
        build_env_dev_a
        build_env_dev_b
        build_env_dev_c
        build_env_dev_d
        build_env_dev_e
        build_env_dev_f
        build_env_dev_g
        echo "[fixture] All fixtures created successfully."
        ;;
    *)
        echo "Unknown fixture: $TARGET" >&2
        echo "Available: ENV-DEV-A, ENV-DEV-B, ENV-DEV-C, ENV-DEV-D, ENV-DEV-E, ENV-DEV-F, ENV-DEV-G" >&2
        exit 1
        ;;
esac
