#!/bin/bash
# setup-init-test-envs.sh — Create simulated project environments for pace-init manual testing
#
# Usage:
#   bash tests/integration/setup-init-test-envs.sh          # Create all environments
#   bash tests/integration/setup-init-test-envs.sh --cleanup # Remove all environments
#
# Environments created in /tmp/devpace-test-envs/:
#   ENV-A: Empty git repo (Stage A - new project)
#   ENV-B: Node.js project, 15+ source files, 8+ commits, 2 unmerged branches (Stage B)
#   ENV-C: 100+ commits, 3 git tags, CHANGELOG.md, fly.toml (Stage C)
#   ENV-D: Existing CLAUDE.md with custom content (merge test)
#   ENV-E: Existing .devpace/ and CLAUDE.md with devpace markers (idempotency + verify test)
#   ENV-F: state.md with version v1.5.0 (migration test)
#   ENV-G: Monorepo with pnpm-workspace.yaml (monorepo detection test)
#   ENV-H: Python project with PRD doc + OpenAPI spec (--from test)
#   ENV-I: .devpace/ with insights + sync mapping (--reset --keep-insights test)
#   ENV-J: Non-git project, no .git/ directory (fallback test)
#   ENV-K: Go project with golangci-lint (ecosystem coverage test)

set -euo pipefail

BASE_DIR="/tmp/devpace-test-envs"

cleanup() {
    echo "Cleaning up test environments..."
    rm -rf "$BASE_DIR"
    echo "Done. Removed $BASE_DIR"
}

if [[ "${1:-}" == "--cleanup" ]]; then
    cleanup
    exit 0
fi

# Clean slate
rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"

echo "Creating test environments in $BASE_DIR ..."

# ── ENV-A: Empty git repo (Stage A) ────────────────────────────────────
create_env_a() {
    local dir="$BASE_DIR/ENV-A"
    mkdir -p "$dir"
    cd "$dir"
    git init -q
    echo "# New Project" > README.md
    git add README.md
    git commit -q -m "Initial commit"
    echo "  ENV-A: Empty git repo (Stage A) ✓"
}

# ── ENV-B: Node.js project (Stage B) ───────────────────────────────────
create_env_b() {
    local dir="$BASE_DIR/ENV-B"
    mkdir -p "$dir/src/auth" "$dir/src/api" "$dir/src/utils" "$dir/tests"
    cd "$dir"
    git init -q

    # package.json
    cat > package.json << 'PKGJSON'
{
  "name": "test-webapp",
  "version": "0.1.0",
  "description": "A test web application for devpace testing",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest",
    "lint": "eslint src/"
  }
}
PKGJSON

    # Source files (15+)
    echo 'const express = require("express"); const app = express(); module.exports = app;' > src/index.js
    echo 'module.exports = { login: () => {}, logout: () => {} };' > src/auth/login.js
    echo 'module.exports = { register: () => {} };' > src/auth/register.js
    echo 'module.exports = { validateToken: () => {} };' > src/auth/middleware.js
    echo 'module.exports = { getUsers: () => {} };' > src/api/users.js
    echo 'module.exports = { getProducts: () => {} };' > src/api/products.js
    echo 'module.exports = { getOrders: () => {} };' > src/api/orders.js
    echo 'module.exports = { createPayment: () => {} };' > src/api/payments.js
    echo 'module.exports = { logger: console.log };' > src/utils/logger.js
    echo 'module.exports = { validate: () => true };' > src/utils/validator.js
    echo 'module.exports = { formatDate: () => {} };' > src/utils/helpers.js
    echo 'module.exports = { DB_URL: "localhost" };' > src/config.js
    echo 'module.exports = { errorHandler: () => {} };' > src/middleware.js
    echo 'module.exports = { ROLES: ["admin", "user"] };' > src/constants.js
    echo 'module.exports = { User: class {} };' > src/models.js
    echo 'module.exports = { cache: new Map() };' > src/cache.js
    echo 'test("placeholder", () => expect(true).toBe(true));' > tests/index.test.js

    # .eslintrc
    echo '{ "extends": "eslint:recommended" }' > .eslintrc.json

    # Commits (8+)
    git add .
    git commit -q -m "feat: initial project setup"
    echo '// v2' >> src/index.js && git add . && git commit -q -m "feat: add express server"
    echo '// v2' >> src/auth/login.js && git add . && git commit -q -m "feat: add auth module"
    echo '// v2' >> src/api/users.js && git add . && git commit -q -m "feat: add users API"
    echo '// v2' >> src/api/products.js && git add . && git commit -q -m "feat: add products API"
    echo '// v2' >> src/api/orders.js && git add . && git commit -q -m "feat: add orders API"
    echo '// v2' >> src/utils/logger.js && git add . && git commit -q -m "feat: add logging"
    echo '// v2' >> src/cache.js && git add . && git commit -q -m "feat: add caching layer"
    echo '// v3' >> src/index.js && git add . && git commit -q -m "fix: server startup"

    # Unmerged branches
    git checkout -q -b feature/notifications
    echo 'module.exports = { notify: () => {} };' > src/notifications.js
    git add . && git commit -q -m "feat: add notifications"
    git checkout -q -b feature/search
    echo 'module.exports = { search: () => {} };' > src/search.js
    git add . && git commit -q -m "feat: add search"
    git checkout -q main 2>/dev/null || git checkout -q master

    echo "  ENV-B: Node.js project (Stage B) ✓"
}

# ── ENV-C: Mature project (Stage C) ────────────────────────────────────
create_env_c() {
    local dir="$BASE_DIR/ENV-C"
    mkdir -p "$dir/src" "$dir/deploy"
    cd "$dir"
    git init -q

    cat > package.json << 'PKGJSON'
{
  "name": "mature-app",
  "version": "2.3.1",
  "description": "A mature application with releases"
}
PKGJSON

    echo '# Mature App' > README.md
    echo 'console.log("app");' > src/app.js

    git add .
    git commit -q -m "Initial commit"

    # Generate 100+ commits
    for i in $(seq 2 105); do
        echo "// commit $i" >> src/app.js
        git add . && git commit -q -m "commit $i" --allow-empty 2>/dev/null || git commit -q --allow-empty -m "commit $i"
    done

    # Git tags (3 version tags)
    git tag v2.1.0
    echo '// post v2.1.0' >> src/app.js && git add . && git commit -q -m "feat: post 2.1.0"
    git tag v2.2.0
    echo '// post v2.2.0' >> src/app.js && git add . && git commit -q -m "feat: post 2.2.0"
    git tag v2.3.1

    # CHANGELOG.md
    cat > CHANGELOG.md << 'CHANGELOG'
# Changelog

## [2.3.1] - 2025-12-01
### Fixed
- Fixed memory leak in connection pool

## [2.2.0] - 2025-10-15
### Added
- New search API endpoint
- Rate limiting middleware

## [2.1.0] - 2025-08-01
### Added
- Initial stable release
CHANGELOG

    # fly.toml (deployment config)
    cat > fly.toml << 'FLYTOML'
app = "mature-app"
primary_region = "nrt"

[env]
  NODE_ENV = "production"

[http_service]
  internal_port = 3000
  force_https = true
FLYTOML

    git add . && git commit -q -m "docs: add changelog and deploy config"

    echo "  ENV-C: Mature project (Stage C) ✓"
}

# ── ENV-D: Existing CLAUDE.md (merge test) ─────────────────────────────
create_env_d() {
    local dir="$BASE_DIR/ENV-D"
    mkdir -p "$dir"
    cd "$dir"
    git init -q

    cat > CLAUDE.md << 'CLAUDEMD'
# My Project

This is an existing CLAUDE.md with custom instructions.

## Build Commands

```bash
npm run build
npm test
```

## Architecture

The project uses a modular architecture with separate concerns.

## Custom Rules

- Always use TypeScript strict mode
- Prefer functional patterns over classes
CLAUDEMD

    cat > package.json << 'PKGJSON'
{
  "name": "merge-test-project",
  "description": "Project for testing CLAUDE.md merge behavior"
}
PKGJSON

    echo 'console.log("hello");' > index.js

    git add .
    git commit -q -m "Initial commit with CLAUDE.md"

    echo "  ENV-D: Existing CLAUDE.md (merge test) ✓"
}

# ── ENV-E: Existing .devpace/ (idempotency + verify test) ──────────────
create_env_e() {
    local dir="$BASE_DIR/ENV-E"
    mkdir -p "$dir/.devpace/backlog" "$dir/.devpace/rules"
    cd "$dir"
    git init -q

    cat > package.json << 'PKGJSON'
{
  "name": "idempotent-test",
  "description": "Project for testing idempotent init and verify"
}
PKGJSON

    # Existing state.md
    cat > .devpace/state.md << 'STATE'
# 项目状态

> 目标：测试幂等性 → 成效指标：初始化无副作用

## 当前工作

- **进行中**：（无）
- **待 Review**：（无）
- **阻塞**：（无）

## 下一步

继续开发

<!-- devpace-version: 1.6.0 -->
STATE

    # Existing project.md
    cat > .devpace/project.md << 'PROJECT'
# 产品全景

## 项目名称：idempotent-test

> 测试幂等性项目

## 价值功能树

（空）
PROJECT

    # Existing CLAUDE.md with devpace markers
    cat > CLAUDE.md << 'CLAUDEMD'
# idempotent-test

> Some custom content above

<!-- devpace-start -->
# idempotent-test

> 测试幂等性项目

## 研发协作

本项目使用 `.devpace/` 管理迭代研发。
<!-- devpace-end -->

## My Custom Section

This should be preserved.
CLAUDEMD

    git add .
    git commit -q -m "Initial setup with .devpace/"

    echo "  ENV-E: Existing .devpace/ (idempotency + verify) ✓"
}

# ── ENV-F: Old version state.md (migration test) ───────────────────────
create_env_f() {
    local dir="$BASE_DIR/ENV-F"
    mkdir -p "$dir/.devpace/backlog" "$dir/.devpace/rules"
    cd "$dir"
    git init -q

    cat > package.json << 'PKGJSON'
{
  "name": "migration-test",
  "description": "Project for testing version migration"
}
PKGJSON

    # Old version state.md
    cat > .devpace/state.md << 'STATE'
# 项目状态

> 目标：迁移测试 → 成效指标：版本升级无损

## 当前工作

- **进行中**：CR-001 用户认证

## 下一步

完成认证模块

<!-- devpace-version: 1.5.0 -->
STATE

    # Old project.md (may need migration)
    cat > .devpace/project.md << 'PROJECT'
# 产品全景

## 项目名称：migration-test

> 迁移测试项目
PROJECT

    git add .
    git commit -q -m "Initial setup with v1.5.0"

    echo "  ENV-F: Old version state.md v1.5.0 (migration) ✓"
}

# ── ENV-G: Monorepo (pnpm workspace, Stage B) ─────────────────────────
create_env_g() {
    local dir="$BASE_DIR/ENV-G"
    mkdir -p "$dir/packages/web/src" "$dir/packages/api/src" "$dir/packages/shared/src"
    cd "$dir"
    git init -q

    # pnpm-workspace.yaml
    cat > pnpm-workspace.yaml << 'PNPM'
packages:
  - 'packages/*'
PNPM

    # Root package.json
    cat > package.json << 'PKGJSON'
{
  "name": "monorepo-test",
  "private": true,
  "description": "A monorepo for testing devpace monorepo detection"
}
PKGJSON

    # Sub-packages
    echo '{"name": "@monorepo/web", "version": "0.1.0"}' > packages/web/package.json
    echo '{"name": "@monorepo/api", "version": "0.1.0"}' > packages/api/package.json
    echo '{"name": "@monorepo/shared", "version": "0.1.0"}' > packages/shared/package.json
    echo 'console.log("web");' > packages/web/src/index.js
    echo 'console.log("api");' > packages/api/src/index.js
    echo 'module.exports = {};' > packages/shared/src/index.js

    git add .
    git commit -q -m "feat: initial monorepo setup"
    # Add enough commits for Stage B
    for i in $(seq 2 8); do
        echo "// v$i" >> packages/web/src/index.js
        git add . && git commit -q -m "feat: update $i"
    done

    echo "  ENV-G: Monorepo pnpm workspace (Stage B) ✓"
}

# ── ENV-H: Python project with PRD doc (--from test) ──────────────────
create_env_h() {
    local dir="$BASE_DIR/ENV-H"
    mkdir -p "$dir/src/auth" "$dir/docs"
    cd "$dir"
    git init -q

    cat > pyproject.toml << 'PYPROJ'
[project]
name = "py-api-service"
version = "0.1.0"
description = "Python API service for devpace testing"

[tool.pytest]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
PYPROJ

    echo 'def main(): pass' > src/auth/handler.py
    echo 'def health(): return "ok"' > src/health.py

    # PRD document for --from testing
    cat > docs/prd.md << 'PRD'
# Product Requirements Document

## User Stories

### Authentication
As a user, I want to log in with email and password, so that I can access my account.

### User Profile
As a user, I want to view and edit my profile, so that I can keep my information up to date.

### Search
As a user, I want to search for products by keyword, so that I can find items quickly.

## Non-functional Requirements
- API response time < 200ms for 95th percentile
- Support 1000 concurrent users
- 99.9% uptime SLA

## Priority
- P0: Authentication
- P1: User Profile
- P2: Search
PRD

    # OpenAPI spec for --from testing
    cat > docs/api-spec.yaml << 'OPENAPI'
openapi: "3.0.0"
info:
  title: "Test API"
  version: "1.0.0"
paths:
  /users:
    get:
      tags: [Users]
      summary: List users
    post:
      tags: [Users]
      summary: Create user
  /auth/login:
    post:
      tags: [Auth]
      summary: User login
  /products:
    get:
      tags: [Products]
      summary: List products
OPENAPI

    git add .
    git commit -q -m "feat: initial Python API project with PRD"

    echo "  ENV-H: Python project + PRD (--from test) ✓"
}

# ── ENV-I: Reset test with insights ───────────────────────────────────
create_env_i() {
    local dir="$BASE_DIR/ENV-I"
    mkdir -p "$dir/.devpace/backlog" "$dir/.devpace/rules" "$dir/.devpace/metrics"
    cd "$dir"
    git init -q

    cat > package.json << 'PKGJSON'
{
  "name": "reset-test",
  "description": "Project for testing reset with --keep-insights"
}
PKGJSON

    # state.md
    cat > .devpace/state.md << 'STATE'
# 项目状态

> 目标：重置测试 → 成效指标：insights 保留

## 当前工作

- **进行中**：CR-001 用户认证
- **进行中**：CR-002 搜索功能

## 下一步

完成认证模块

<!-- devpace-version: 1.6.0 -->
STATE

    # project.md with real data
    cat > .devpace/project.md << 'PROJECT'
# reset-test

> 重置测试项目

## 价值功能树

```
BR-001 用户管理
├── PF-001 用户认证 → CR-001
└── PF-002 用户搜索 → CR-002
```
PROJECT

    # insights.md with valuable cross-project data
    cat > .devpace/metrics/insights.md << 'INSIGHTS'
# 经验沉淀

## pattern: test-first-development
- **置信度**: 0.85
- **验证次数**: 3
- **描述**: 先写测试再写实现，减少 50% 返工率
- **来源**: CR-001, CR-002, CR-005

## pattern: small-commits
- **置信度**: 0.72
- **验证次数**: 2
- **描述**: 每个逻辑步骤独立 commit，方便 review 和回滚
- **来源**: CR-003, CR-004
INSIGHTS

    # backlog CRs
    cat > .devpace/backlog/CR-001.md << 'CR'
# 用户认证
- **ID**: CR-001
- **状态**: developing
CR

    cat > .devpace/backlog/CR-002.md << 'CR'
# 搜索功能
- **ID**: CR-002
- **状态**: created
CR

    # integrations with sync mapping
    mkdir -p .devpace/integrations
    cat > .devpace/integrations/sync-mapping.md << 'SYNC'
# 同步映射

| CR | GitHub Issue | 状态 |
|----|-------------|------|
| CR-001 | #12 | synced |
SYNC

    # CLAUDE.md with devpace markers
    cat > CLAUDE.md << 'CLAUDEMD'
# reset-test

<!-- devpace-start -->
# reset-test
> 重置测试项目
## 研发协作
本项目使用 `.devpace/` 管理迭代研发。
<!-- devpace-end -->
CLAUDEMD

    git add .
    git commit -q -m "Initial setup for reset testing"

    echo "  ENV-I: Reset test with insights + sync mapping ✓"
}

# ── ENV-J: Non-git project (no .git/) ─────────────────────────────────
create_env_j() {
    local dir="$BASE_DIR/ENV-J"
    mkdir -p "$dir/src"
    cd "$dir"
    # Intentionally NO git init
    echo '{"name": "no-git-project", "description": "A project without git"}' > package.json
    echo 'console.log("hello");' > src/index.js

    echo "  ENV-J: Non-git project (no .git/) ✓"
}

# ── ENV-K: Go project (Stage B, for ecosystem coverage) ───────────────
create_env_k() {
    local dir="$BASE_DIR/ENV-K"
    mkdir -p "$dir/cmd/server" "$dir/internal/handler"
    cd "$dir"
    git init -q

    cat > go.mod << 'GOMOD'
module github.com/test/go-service

go 1.22
GOMOD

    echo 'package main; func main() {}' > cmd/server/main.go
    echo 'package handler; func Health() string { return "ok" }' > internal/handler/health.go
    echo 'package handler; func TestHealth(t *testing.T) {}' > internal/handler/health_test.go

    cat > .golangci.yml << 'GOLINT'
linters:
  enable:
    - govet
    - errcheck
GOLINT

    git add .
    git commit -q -m "feat: initial Go service"
    for i in $(seq 2 8); do
        echo "// v$i" >> cmd/server/main.go
        git add . && git commit -q -m "feat: iteration $i"
    done

    echo "  ENV-K: Go project (Stage B) ✓"
}

# ── Execute ─────────────────────────────────────────────────────────────
create_env_a
create_env_b
create_env_c
create_env_d
create_env_e
create_env_f
create_env_g
create_env_h
create_env_i
create_env_j
create_env_k

echo ""
echo "All environments created in $BASE_DIR"
echo ""
echo "Test with:  claude --plugin-dir /path/to/devpace"
echo "Cleanup:    bash $0 --cleanup"
echo ""
echo "Environments:"
echo "  ENV-A  /tmp/devpace-test-envs/ENV-A  — Empty git repo (Stage A)"
echo "  ENV-B  /tmp/devpace-test-envs/ENV-B  — Node.js, 15+ files (Stage B)"
echo "  ENV-C  /tmp/devpace-test-envs/ENV-C  — 100+ commits, tags (Stage C)"
echo "  ENV-D  /tmp/devpace-test-envs/ENV-D  — Existing CLAUDE.md (merge test)"
echo "  ENV-E  /tmp/devpace-test-envs/ENV-E  — Existing .devpace/ (idempotency)"
echo "  ENV-F  /tmp/devpace-test-envs/ENV-F  — v1.5.0 state.md (migration)"
echo "  ENV-G  /tmp/devpace-test-envs/ENV-G  — Monorepo pnpm workspace (Stage B)"
echo "  ENV-H  /tmp/devpace-test-envs/ENV-H  — Python project + PRD (--from test)"
echo "  ENV-I  /tmp/devpace-test-envs/ENV-I  — Reset with insights + sync mapping"
echo "  ENV-J  /tmp/devpace-test-envs/ENV-J  — Non-git project (no .git/)"
echo "  ENV-K  /tmp/devpace-test-envs/ENV-K  — Go project (Stage B)"
