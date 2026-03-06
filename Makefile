.PHONY: help test validate lint layer-check plugin-load setup clean release-check bump \
       eval-trigger eval-trigger-one eval-behavior eval-coverage eval-stale

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

test: ## 运行静态测试
	pytest tests/static/ -v

lint: ## Markdown 格式检查（产品层）
	npx markdownlint-cli2 "rules/**/*.md" "skills/**/*.md" "knowledge/**/*.md"

validate: ## 运行完整验证
	bash scripts/validate-all.sh

layer-check: ## 检查分层完整性
	@echo "检查产品层是否引用开发层..."
	@result=$$(grep -r "docs/\|\.claude/" rules/ skills/ knowledge/ 2>/dev/null || true); \
	if [ -z "$$result" ]; then \
		echo "通过：产品层未引用开发层"; \
	else \
		echo "失败：发现违规引用："; \
		echo "$$result"; \
		exit 1; \
	fi

plugin-load: ## 以插件模式启动 Claude
	claude --plugin-dir ./

setup: ## 安装开发依赖
	pip install -r requirements-dev.txt

clean: ## 清理缓存文件
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

release-check: ## 预发布验证（validate-all + 版本一致性）
	@echo "Running pre-release checks..."
	bash scripts/validate-all.sh
	@PLUGIN_V=$$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])"); \
	MARKET_V=$$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['version'])"); \
	echo "plugin.json: $$PLUGIN_V"; \
	echo "marketplace.json: $$MARKET_V"; \
	if [ "$$PLUGIN_V" != "$$MARKET_V" ]; then \
		echo "ERROR: Version mismatch!"; \
		exit 1; \
	fi; \
	echo "Version consistency: OK ($$PLUGIN_V)"

bump: ## 版本 bump（make bump V=1.5.0）
	@if [ -z "$(V)" ]; then echo "Usage: make bump V=1.5.0"; exit 1; fi
	bash scripts/bump-version.sh $(V)

# ── Eval targets ─────────────────────────────────────────────────────────

eval-coverage: ## 报告 eval 覆盖率（哪些 Skill 有/缺 eval）
	@echo "Eval coverage report:"; \
	total=0; covered=0; \
	for skill in $(shell ls -d skills/pace-*/  | xargs -I{} basename {}); do \
		case "$$skill" in *-workspace) continue;; esac; \
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
	for skill in $(shell ls -d skills/pace-*/  | xargs -I{} basename {}); do \
		case "$$skill" in *-workspace) continue;; esac; \
		eval_dir="tests/evaluation/$$skill"; \
		[ -d "$$eval_dir" ] || continue; \
		skill_ts=$$(git log -1 --format=%ct -- "skills/$$skill/" 2>/dev/null || echo 0); \
		eval_ts=$$(git log -1 --format=%ct -- "$$eval_dir/" 2>/dev/null || echo 0); \
		if [ "$$skill_ts" -gt "$$eval_ts" ] 2>/dev/null; then \
			echo "  ⚠️  $$skill — Skill updated after eval (eval may be stale)"; \
		fi; \
	done; \
	echo "Done."

eval-trigger-one: ## 单 Skill 触发测试（make eval-trigger-one S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-trigger-one S=<skill-name>"; exit 1; fi
	@eval_file="tests/evaluation/$(S)/trigger-evals.json"; \
	if [ ! -f "$$eval_file" ]; then echo "Error: $$eval_file not found"; exit 1; fi; \
	echo "Running trigger eval for $(S)..."; \
	skill-creator eval-trigger --skill "skills/$(S)" --evals "$$eval_file"

eval-trigger: ## 全量触发测试（所有有 trigger-evals.json 的 Skill）
	@echo "Running trigger evals for all Skills..."; \
	for skill in $(shell ls -d skills/pace-*/  | xargs -I{} basename {}); do \
		case "$$skill" in *-workspace) continue;; esac; \
		eval_file="tests/evaluation/$$skill/trigger-evals.json"; \
		[ -f "$$eval_file" ] || continue; \
		echo "  → $$skill"; \
		skill-creator eval-trigger --skill "skills/$$skill" --evals "$$eval_file" || true; \
	done

eval-behavior: ## 单 Skill 行为 eval（make eval-behavior S=pace-dev）
	@if [ -z "$(S)" ]; then echo "Usage: make eval-behavior S=<skill-name>"; exit 1; fi
	@eval_file="tests/evaluation/$(S)/evals.json"; \
	if [ ! -f "$$eval_file" ]; then echo "Error: $$eval_file not found"; exit 1; fi; \
	echo "Running behavioral eval for $(S)..."; \
	skill-creator eval --skill "skills/$(S)" --evals "$$eval_file"
