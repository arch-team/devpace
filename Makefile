.PHONY: help init setup setup-hooks clean check test test-static test-hooks \
       validate lint layer-check plugin-load release-check bump \
       eval-trigger eval-trigger-one eval-behavior eval-behavior-one eval-behavior-all eval-coverage eval-stale eval-all \
       eval-trigger-smoke eval-trigger-deep eval-fix eval-fix-diff eval-fix-apply \
       eval-regress eval-regress-offline eval-baseline-save eval-baseline-diff eval-baseline-save-all \
       eval-trigger-changed \
       eval-behavior-smoke eval-benchmark \
       eval-report eval-report-open eval-viewer \
       eval-note eval-notes eval-notes-pending eval-notes-stale \
       eval-analyze eval-compare \
       eval-deep eval-all-deep

# Eval 配置
RUNS ?= 3
TIMEOUT ?= 90
SMOKE_N ?= 5
MAX_TURNS ?= 5
MODEL ?=

# Skill 列表（排除 *-workspace 目录）
SKILLS := $(shell ls -d skills/pace-*/ 2>/dev/null | xargs -I{} basename {} | grep -v '\-workspace$$')

help: ## 显示帮助
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} \
		/^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)} \
		/^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Development

init: setup setup-hooks ## 完整开发环境初始化（依赖 + hooks + lint 工具）
	@command -v node >/dev/null 2>&1 || echo "⚠️  Node.js not found — needed for lint & hook tests"
	@command -v markdownlint-cli2 >/dev/null 2>&1 || \
		(command -v npx >/dev/null 2>&1 && echo "ℹ️  markdownlint-cli2 will run via npx") || \
		echo "⚠️  markdownlint-cli2 not available — run: npm install -g markdownlint-cli2"
	@echo "✅ Development environment ready. Run 'make check' to verify."

setup: ## 安装 Python 开发依赖
	pip install -r requirements-dev.txt

setup-hooks: ## 启用本地 git hooks
	git config core.hooksPath .githooks
	@echo "Git hooks path set to .githooks"

clean: ## 清理缓存文件和 eval workspace
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*-workspace" -path "*/skills/*" -exec rm -rf {} + 2>/dev/null || true

plugin-load: ## 以插件模式启动 Claude
	@command -v claude >/dev/null 2>&1 || { echo "Error: claude CLI not found. Install: https://docs.anthropic.com/en/docs/claude-code"; exit 1; }
	claude --plugin-dir ./

##@ Testing

check: layer-check lint test ## 快速本地验证（无需 claude CLI）

test-static: ## 仅运行 Python 静态测试
	pytest tests/static/ -v

test-hooks: ## 运行 Node.js Hook 测试
	node --test tests/hooks/test_*.mjs

test: test-static test-hooks ## 运行所有测试（静态 + Hook）

##@ Quality

validate: ## 运行完整验证（含集成测试）
	bash dev-scripts/validate-all.sh

lint: ## Markdown 格式检查（产品层）
	npx markdownlint-cli2 "rules/**/*.md" "skills/**/*.md" "knowledge/**/*.md"

layer-check: ## 检查分层完整性
	@echo "检查产品层是否引用开发层..."
	@result=$$(grep -r --exclude-dir='*-workspace' "docs/\|\.claude/" rules/ skills/ knowledge/ 2>/dev/null || true); \
	if [ -z "$$result" ]; then \
		echo "通过：产品层未引用开发层"; \
	else \
		echo "失败：发现违规引用："; \
		echo "$$result"; \
		exit 1; \
	fi

##@ Release

release-check: ## 预发布验证（validate-all + 版本 + eval 健康）
	@echo "Running pre-release checks..."
	bash dev-scripts/validate-all.sh
	@PLUGIN_V=$$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])"); \
	MARKET_V=$$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['version'])"); \
	echo "plugin.json: $$PLUGIN_V"; \
	echo "marketplace.json: $$MARKET_V"; \
	if [ "$$PLUGIN_V" != "$$MARKET_V" ]; then \
		echo "ERROR: Version mismatch!"; \
		exit 1; \
	fi; \
	echo "Version consistency: OK ($$PLUGIN_V)"
	@echo ""; echo "Checking eval freshness..."
	@$(MAKE) eval-stale

bump: ## 版本 bump（make bump V=1.5.0）
	@if [ -z "$(V)" ]; then echo "Usage: make bump V=1.5.0"; exit 1; fi
	bash dev-scripts/bump-version.sh $(V)

##@ Eval

eval-coverage: ## 报告 eval 覆盖率（哪些 Skill 有/缺 eval）
	@echo "Eval coverage report:"; \
	total=0; covered=0; \
	for skill in $(SKILLS); do \
		total=$$((total + 1)); \
		if [ -f "tests/evaluation/$$skill/evals.json" ] && [ -f "tests/evaluation/$$skill/trigger-evals.json" ]; then \
			echo "  ✅ $$skill (evals + trigger)"; covered=$$((covered + 1)); \
		elif [ -f "tests/evaluation/$$skill/evals.json" ]; then \
			echo "  ⚠️  $$skill (evals only, missing trigger)"; \
		elif [ -f "tests/evaluation/$$skill/trigger-evals.json" ]; then \
			echo "  ⚠️  $$skill (trigger only, missing evals)"; \
		else \
			echo "  ⬜ $$skill (no evals)"; \
		fi; \
	done; \
	echo ""; echo "Coverage: $$covered/$$total Skills fully covered"

eval-stale: ## 检测过期 eval（Skill 变更但 eval 未更新）
	@echo "Stale eval detection:"; \
	for skill in $(SKILLS); do \
		eval_dir="tests/evaluation/$$skill"; \
		[ -d "$$eval_dir" ] || continue; \
		skill_ts=$$(git log -1 --format=%ct -- "skills/$$skill/" 2>/dev/null); \
		[ -z "$$skill_ts" ] && continue; \
		eval_ts=$$(git log -1 --format=%ct -- "$$eval_dir/" 2>/dev/null); \
		if [ -z "$$eval_ts" ]; then \
			echo "  ⚠️  $$skill — eval has no git history"; continue; \
		fi; \
		if [ "$$skill_ts" -gt "$$eval_ts" ]; then \
			echo "  ⚠️  $$skill — Skill updated after eval (eval may be stale)"; \
		fi; \
	done; \
	echo "Done."

eval-trigger-one: ## 单 Skill 触发测试（make eval-trigger-one S=pace-dev [RUNS=3] [TIMEOUT=90] [MODEL=<id>]）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-trigger-one S=<skill-name>"; exit 1; fi
	@echo "Running trigger eval for $(S)..."
	python3 -m eval trigger --skill "$(S)" --runs $(RUNS) --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) $(if $(MODEL),--model $(MODEL))

eval-trigger-e2e: ## 端到端触发测试（含 slash 路由 + forced eval hook）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-trigger-e2e S=<skill-name> [RUNS=3]"; exit 1; fi
	@echo "Running e2e trigger eval for $(S) (with hooks)..."
	python3 -m eval trigger --skill "$(S)" --runs $(RUNS) --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) --with-hooks $(if $(MODEL),--model $(MODEL))

eval-trigger: ## 全量触发测试（所有有 trigger-evals.json 的 Skill）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running trigger evals for all Skills..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/trigger-evals.json" ] || continue; \
		echo "  → $$skill"; \
		if python3 -m eval trigger --skill "$$skill" --runs $(RUNS) --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-trigger-smoke: ## 快速冒烟测试（runs=1, 每 Skill 取 5 条关键查询）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running smoke trigger evals..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/trigger-evals.json" ] || continue; \
		echo "  → $$skill"; \
		if python3 -m eval trigger --skill "$$skill" --runs 1 --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) --smoke --smoke-n $(SMOKE_N) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Smoke done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-trigger-deep: ## 深度测试（runs=5, 全部查询）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running deep trigger evals (runs=5)..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/trigger-evals.json" ] || continue; \
		echo "  → $$skill"; \
		if python3 -m eval trigger --skill "$$skill" --runs 5 --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Deep done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-trigger-changed: ## 仅测试有变更的 Skill（make eval-trigger-changed [BASE=origin/main]）
	@echo "Detecting changed skills..."; \
	changed=$$(python3 -m eval changed --base $(or $(BASE),origin/main) 2>/dev/null | grep "changed:" | awk '{print $$NF}'); \
	if [ -z "$$changed" ]; then echo "  no skill changes detected"; exit 0; fi; \
	passed=0; failed=0; \
	for skill in $$changed; do \
		[ -f "tests/evaluation/$$skill/trigger-evals.json" ] || continue; \
		echo "  → $$skill (changed)"; \
		if python3 -m eval trigger --skill "$$skill" --runs $(RUNS) --timeout $(TIMEOUT) --max-turns $(MAX_TURNS) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	echo "Changed skills: $$passed passed, $$failed failed"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-behavior-one: ## 单 Skill 单 Case 行为 eval（make eval-behavior-one S=pace-dev CASE=1）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-behavior-one S=<skill-name> CASE=<case-id>"; exit 1; fi
	@if [ -z "$(CASE)" ]; then echo "Usage: make eval-behavior-one S=<skill-name> CASE=<case-id>"; exit 1; fi
	python3 -m eval behavior --skill "$(S)" --case $(CASE) --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL))

eval-behavior: ## 单 Skill 全量行为 eval（make eval-behavior S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-behavior S=<skill-name>"; exit 1; fi
	python3 -m eval behavior --skill "$(S)" --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL))

eval-behavior-smoke: ## 单 Skill 冒烟行为 eval（make eval-behavior-smoke S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-behavior-smoke S=<skill-name>"; exit 1; fi
	python3 -m eval behavior --skill "$(S)" --smoke --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL))

eval-behavior-all: ## 全量行为测试（所有有 evals.json 的 Skill）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running behavioral evals for all Skills..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/evals.json" ] || continue; \
		echo "  → $$skill"; \
		if python3 -m eval behavior --skill "$$skill" --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-all: ## 一键运行所有 eval（trigger + behavior + coverage + stale + report）
	@echo "=== Trigger Evals ==="; $(MAKE) eval-trigger; \
	echo ""; echo "=== Behavioral Evals ==="; $(MAKE) eval-behavior-all; \
	echo ""; echo "=== Coverage Report ==="; $(MAKE) eval-coverage; \
	echo ""; echo "=== Stale Detection ==="; $(MAKE) eval-stale; \
	echo ""; echo "=== Generate Report ==="; $(MAKE) eval-report

##@ Eval Optimize

eval-fix: ## 自动改进 description（make eval-fix S=pace-dev MODEL=<id> [N=5]）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix S=<skill-name> MODEL=<model-id> [N=5]"; exit 1; fi
	@if [ -z "$(MODEL)" ]; then echo "Error: MODEL is required (e.g. MODEL=claude-sonnet-4-20250514)"; exit 1; fi
	python3 -m eval loop --skill "$(S)" --model "$(MODEL)" --iterations $(or $(N),5) --timeout $(TIMEOUT) --max-turns $(MAX_TURNS)

eval-fix-diff: ## 对比当前 vs 最优 description（make eval-fix-diff S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix-diff S=<skill-name>"; exit 1; fi
	python3 eval/apply.py diff --skill "$(S)"

eval-fix-apply: ## 应用最优 description 到 SKILL.md（make eval-fix-apply S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix-apply S=<skill-name>"; exit 1; fi
	python3 eval/apply.py apply --skill "$(S)"

##@ Eval Regression

eval-regress: ## 全量回归检查（重新运行 eval + 多维对比）
	@echo "Running regression check..."
	@$(MAKE) eval-trigger
	@python3 -m eval regress

eval-regress-offline: ## 离线回归检查（仅 JSON diff，零 API 调用）
	@echo "Running offline regression check (baseline vs latest)..."
	@python3 -m eval regress

eval-baseline-save: ## 将当前 latest.json 保存为 baseline（make eval-baseline-save S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-baseline-save S=<skill-name>"; exit 1; fi
	python3 -m eval baseline save --skill "$(S)"

eval-baseline-diff: ## 对比当前结果与基线（make eval-baseline-diff S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-baseline-diff S=<skill-name>"; exit 1; fi
	python3 -m eval baseline diff --skill "$(S)"

eval-baseline-save-all: ## 保存所有 Skill 的基线
	@for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/results/latest.json" ] || continue; \
		echo "  saving baseline: $$skill"; \
		python3 -m eval baseline save --skill "$$skill"; \
	done

##@ Eval Benchmark

eval-benchmark: ## 基线对照测试（make eval-benchmark S=pace-dev [RUNS=3] [MODEL=<id>]）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-benchmark S=<skill-name> [RUNS=3]"; exit 1; fi
	python3 -m eval benchmark --skill "$(S)" --runs $(RUNS) $(if $(MODEL),--model $(MODEL))

##@ Eval Report

eval-report: ## 生成静态 HTML 仪表盘
	python3 -m eval report

eval-report-open: ## 生成并打开 HTML 仪表盘
	python3 -m eval report --open

eval-viewer: ## 启动交互式 eval viewer（make eval-viewer S=pace-dev [PORT=8420]）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-viewer S=<skill-name> [PORT=8420]"; exit 1; fi
	python3 -m eval viewer --skill "$(S)" $(if $(PORT),--port $(PORT))

##@ Eval Feedback

eval-note: ## 添加 eval 反馈 note（make eval-note S=pace-dev CASE=1 NOTE="..."）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-note S=<skill-name> CASE=<id> NOTE=\"...\""; exit 1; fi
	@if [ -z "$(CASE)" ]; then echo "Usage: make eval-note S=<skill-name> CASE=<id> NOTE=\"...\""; exit 1; fi
	@if [ -z "$(NOTE)" ]; then echo "Usage: make eval-note S=<skill-name> CASE=<id> NOTE=\"...\""; exit 1; fi
	python3 -m eval note --skill "$(S)" --case $(CASE) --note "$(NOTE)"

eval-notes: ## 查看 Skill 的 eval notes（make eval-notes S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-notes S=<skill-name>"; exit 1; fi
	python3 -m eval notes --skill "$(S)"

eval-notes-pending: ## 查看所有待处理 notes
	python3 -m eval notes --pending

eval-notes-stale: ## 查看所有过期 notes
	python3 -m eval notes --stale

##@ Eval Analysis

eval-analyze: ## 断言质量分析（make eval-analyze [S=pace-dev]）
	python3 -m eval analyze $(if $(S),--skill $(S))

eval-compare: ## 盲 A/B 版本比较（make eval-compare S=pace-dev OLD=HEAD~5 NEW=HEAD）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-compare S=<skill-name> OLD=<ref> NEW=<ref>"; exit 1; fi
	@if [ -z "$(OLD)" ]; then echo "Usage: make eval-compare S=<skill-name> OLD=<ref> NEW=<ref>"; exit 1; fi
	@if [ -z "$(NEW)" ]; then echo "Usage: make eval-compare S=<skill-name> OLD=<ref> NEW=<ref>"; exit 1; fi
	python3 -m eval compare --skill "$(S)" --old "$(OLD)" --new "$(NEW)"

##@ Eval Deep

eval-deep: ## 单 Skill 深度评估（trigger + behavior + benchmark + report）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-deep S=<skill-name>"; exit 1; fi
	@echo "=== Deep Eval: $(S) ==="; \
	echo "--- Trigger ---"; $(MAKE) eval-trigger-one S=$(S); \
	echo ""; echo "--- Behavior ---"; $(MAKE) eval-behavior S=$(S); \
	echo ""; echo "--- Benchmark ---"; $(MAKE) eval-benchmark S=$(S); \
	echo ""; echo "--- Report ---"; $(MAKE) eval-report

eval-all-deep: ## 全量深度评估（所有有 evals.json 的 Skill）
	@start=$$(date +%s); \
	echo "Running deep eval for all Skills..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/evals.json" ] || continue; \
		echo ""; echo "=== Deep Eval: $$skill ==="; \
		$(MAKE) eval-deep S=$$skill || true; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "All deep evals done in $${elapsed}s"; \
	$(MAKE) eval-report
