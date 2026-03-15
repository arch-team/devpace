"""TC-LS: Product-layer files must not reference dev-layer paths."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, PRODUCT_DIRS, product_md_files

DEV_PATH_RE = re.compile(r'(?:\.\./|\./)?(?:docs/|\.claude/)')

@pytest.mark.static
class TestLayerSeparation:
    def test_tc_ls_01_no_docs_reference(self):
        """TC-LS-01: Product layer has no docs/ references."""
        violations = []
        for f in product_md_files():
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r'(?<!\w)docs/', line):
                    # Allow "docs" as a word in prose, only flag path-like references
                    if re.search(r'(?:\.\./|\./|`)docs/', line) or line.strip().startswith('docs/'):
                        violations.append(f"{f.relative_to(DEVPACE_ROOT)}:{i}: {line.strip()}")
        assert not violations, f"Product→dev references found:\n" + "\n".join(violations)

    def test_tc_ls_02_no_claude_dir_reference(self):
        """TC-LS-02: Product layer has no .claude/ references."""
        violations = []
        for f in product_md_files():
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if '.claude/' in line:
                    violations.append(f"{f.relative_to(DEVPACE_ROOT)}:{i}: {line.strip()}")
        assert not violations, f".claude/ references found:\n" + "\n".join(violations)

    def test_tc_ls_03_dev_can_reference_product(self):
        """TC-LS-03: Dev layer referencing product layer is allowed (no false positive)."""
        # Read CLAUDE.md which references product layer — should not cause issues
        claude_md = DEVPACE_ROOT / ".claude" / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")
            assert "rules/" in content or "skills/" in content or "knowledge/" in content, \
                "Expected dev layer to reference product layer"
