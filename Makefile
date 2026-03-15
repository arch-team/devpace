.PHONY: help init setup setup-hooks clean check test test-static test-hooks \
       validate lint layer-check plugin-load release-check bump \
       eval-trigger eval-trigger-one eval-behavior eval-behavior-one eval-behavior-all eval-coverage eval-stale eval-all \
       eval-trigger-smoke eval-trigger-deep eval-fix eval-fix-diff eval-fix-apply \
       eval-regress eval-baseline-save eval-baseline-diff eval-baseline-save-all

# Eval 配置
RUNS ?= 3
TIMEOUT ?= 90
SMOKE_N ?= 5
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
	python3 eval/shim.py trigger --skill "$(S)" --runs $(RUNS) --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL))

eval-trigger: ## 全量触发测试（所有有 trigger-evals.json 的 Skill）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running trigger evals for all Skills..."; \
	for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/trigger-evals.json" ] || continue; \
		echo "  → $$skill"; \
		if python3 eval/shim.py trigger --skill "$$skill" --runs $(RUNS) --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
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
		if python3 eval/shim.py trigger --skill "$$skill" --runs 1 --timeout $(TIMEOUT) --smoke --smoke-n $(SMOKE_N) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
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
		if python3 eval/shim.py trigger --skill "$$skill" --runs 5 --timeout $(TIMEOUT) $(if $(MODEL),--model $(MODEL)) > /dev/null; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Deep done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-behavior-one: eval-behavior ## eval-behavior 的别名（命名一致性）

eval-behavior: ## 单 Skill 行为 eval（make eval-behavior S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-behavior S=<skill-name>"; exit 1; fi
	@eval_file="tests/evaluation/$(S)/evals.json"; \
	if [ ! -f "$$eval_file" ]; then echo "Error: $$eval_file not found"; exit 1; fi; \
	echo "Running behavioral eval for $(S)..."; \
	bash eval/eval-runner.sh eval --skill "skills/$(S)" --evals "$$eval_file"

eval-behavior-all: ## 全量行为测试（所有有 evals.json 的 Skill）
	@start=$$(date +%s); passed=0; failed=0; \
	echo "Running behavioral evals for all Skills..."; \
	for skill in $(SKILLS); do \
		eval_file="tests/evaluation/$$skill/evals.json"; \
		[ -f "$$eval_file" ] || continue; \
		echo "  → $$skill"; \
		if bash eval/eval-runner.sh eval --skill "skills/$$skill" --evals "$$eval_file"; then \
			passed=$$((passed + 1)); \
		else \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	elapsed=$$(($$(date +%s) - start)); \
	echo ""; echo "Done in $${elapsed}s ($$passed passed, $$failed failed)"; \
	if [ $$failed -gt 0 ]; then exit 1; fi

eval-all: ## 一键运行所有 eval（trigger + behavior + coverage + stale）
	@echo "=== Trigger Evals ==="; $(MAKE) eval-trigger; \
	echo ""; echo "=== Behavioral Evals ==="; $(MAKE) eval-behavior-all; \
	echo ""; echo "=== Coverage Report ==="; $(MAKE) eval-coverage; \
	echo ""; echo "=== Stale Detection ==="; $(MAKE) eval-stale

##@ Eval Optimize

eval-fix: ## 自动改进 description（make eval-fix S=pace-dev MODEL=<id> [N=5]）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix S=<skill-name> MODEL=<model-id> [N=5]"; exit 1; fi
	@if [ -z "$(MODEL)" ]; then echo "Error: MODEL is required (e.g. MODEL=claude-sonnet-4-20250514)"; exit 1; fi
	python3 eval/shim.py loop --skill "$(S)" --model "$(MODEL)" --iterations $(or $(N),5) --timeout $(TIMEOUT)

eval-fix-diff: ## 对比当前 vs 最优 description（make eval-fix-diff S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix-diff S=<skill-name>"; exit 1; fi
	python3 eval/apply.py diff --skill "$(S)"

eval-fix-apply: ## 应用最优 description 到 SKILL.md（make eval-fix-apply S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-fix-apply S=<skill-name>"; exit 1; fi
	python3 eval/apply.py apply --skill "$(S)"

##@ Eval Regression

eval-regress: ## 跨 Skill 回归检查（make eval-regress）
	@echo "Running regression check..."
	@$(MAKE) eval-trigger
	@python3 eval/shim.py regress

eval-baseline-save: ## 将当前 latest.json 保存为 baseline（make eval-baseline-save S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-baseline-save S=<skill-name>"; exit 1; fi
	python3 eval/shim.py baseline save --skill "$(S)"

eval-baseline-diff: ## 对比当前结果与基线（make eval-baseline-diff S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-baseline-diff S=<skill-name>"; exit 1; fi
	python3 eval/shim.py baseline diff --skill "$(S)"

eval-baseline-save-all: ## 保存所有 Skill 的基线
	@for skill in $(SKILLS); do \
		[ -f "tests/evaluation/$$skill/results/latest.json" ] || continue; \
		echo "  saving baseline: $$skill"; \
		python3 eval/shim.py baseline save --skill "$$skill"; \
	done
