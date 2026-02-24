.PHONY: help test validate lint layer-check plugin-load setup clean

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
