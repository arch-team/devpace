"""TC-NC: File and directory naming convention checks."""
import re
import pytest
from tests.conftest import DEVPACE_ROOT, SKILL_NAMES, TEMPLATE_FILES, _is_workspace_path

KEBAB_CASE_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
EXEMPT_MD_NAMES = {"SKILL.md", "CLAUDE.md", "README.md"}

@pytest.mark.static
class TestNamingConventions:
    def test_tc_nc_01_markdown_kebab_case(self):
        """TC-NC-01: Markdown filenames are kebab-case (with exceptions)."""
        violations = []
        for d in ["rules", "skills", "knowledge"]:
            dirpath = DEVPACE_ROOT / d
            if not dirpath.is_dir():
                continue
            for f in dirpath.rglob("*.md"):
                if _is_workspace_path(f):
                    continue
                fname = f.name
                if fname in EXEMPT_MD_NAMES:
                    continue
                stem = f.stem
                if not KEBAB_CASE_RE.match(stem):
                    violations.append(f"{f.relative_to(DEVPACE_ROOT)}: '{fname}' is not kebab-case")
        assert not violations, f"Naming violations:\n" + "\n".join(violations)

    def test_tc_nc_02_skill_dirs_kebab_case(self):
        """TC-NC-02: Skill directory names are kebab-case."""
        violations = []
        for name in SKILL_NAMES:
            if not KEBAB_CASE_RE.match(name):
                violations.append(f"Skill dir '{name}' is not kebab-case")
        assert not violations, "\n".join(violations)

    def test_tc_nc_03_template_names_kebab_case(self):
        """TC-NC-03: Template filenames are kebab-case."""
        violations = []
        for name in TEMPLATE_FILES:
            stem = name.rsplit(".", 1)[0]
            if not KEBAB_CASE_RE.match(stem):
                violations.append(f"Template '{name}' stem '{stem}' is not kebab-case")
        assert not violations, "\n".join(violations)
