"""TC-AST: Agent-Skill tool consistency for context:fork skills."""
import pytest
import yaml
from tests.conftest import DEVPACE_ROOT, SKILL_NAMES


def _parse_frontmatter(path):
    """Extract YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


def _parse_tools_list(raw):
    """Parse a comma-separated tools string into a set of tool names."""
    if raw is None:
        return set()
    if isinstance(raw, list):
        return {t.strip() for t in raw}
    return {t.strip() for t in str(raw).split(",")}


def _forked_skill_agent_pairs():
    """Discover all Skill-Agent pairs where context:fork + agent is declared.

    Returns list of (skill_name, agent_name, skill_path, agent_path) tuples.
    """
    skills_root = DEVPACE_ROOT / "skills"
    agents_root = DEVPACE_ROOT / "agents"
    pairs = []
    for name in SKILL_NAMES:
        skill_md = skills_root / name / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = _parse_frontmatter(skill_md)
        if fm is None:
            continue
        if fm.get("context") != "fork" or "agent" not in fm:
            continue
        agent_name = fm["agent"]
        agent_path = agents_root / f"{agent_name}.md"
        pairs.append((name, agent_name, skill_md, agent_path))
    return pairs


_PAIRS = _forked_skill_agent_pairs()
_PAIR_IDS = [f"{skill}->{agent}" for skill, agent, _, _ in _PAIRS]


@pytest.mark.static
class TestAgentSkillTools:
    """Verify that forked Agent tools are a superset of Skill allowed-tools."""

    def test_tc_ast_00_forked_skills_exist(self):
        """TC-AST-00: At least one Skill uses context:fork + agent."""
        assert len(_PAIRS) > 0, (
            "No Skill with context:fork and agent found. "
            "Either no such Skills exist or discovery logic is broken."
        )

    @pytest.mark.parametrize(
        "skill_name,agent_name,skill_path,agent_path",
        _PAIRS,
        ids=_PAIR_IDS,
    )
    def test_tc_ast_01_agent_file_exists(
        self, skill_name, agent_name, skill_path, agent_path
    ):
        """TC-AST-01: The agent referenced by a forked Skill must exist."""
        assert agent_path.exists(), (
            f"Skill '{skill_name}' declares agent:'{agent_name}' "
            f"but agents/{agent_name}.md does not exist"
        )

    @pytest.mark.parametrize(
        "skill_name,agent_name,skill_path,agent_path",
        _PAIRS,
        ids=_PAIR_IDS,
    )
    def test_tc_ast_02_agent_has_tools(
        self, skill_name, agent_name, skill_path, agent_path
    ):
        """TC-AST-02: The referenced Agent must declare a tools field."""
        if not agent_path.exists():
            pytest.skip(f"Agent file {agent_path.name} missing (covered by TC-AST-01)")
        fm = _parse_frontmatter(agent_path)
        assert fm is not None, f"Agent {agent_name} has no frontmatter"
        assert "tools" in fm, (
            f"Agent '{agent_name}' (used by Skill '{skill_name}') "
            f"has no 'tools' field in frontmatter"
        )

    @pytest.mark.parametrize(
        "skill_name,agent_name,skill_path,agent_path",
        _PAIRS,
        ids=_PAIR_IDS,
    )
    def test_tc_ast_03_agent_tools_superset_of_skill(
        self, skill_name, agent_name, skill_path, agent_path
    ):
        """TC-AST-03: Agent tools must be a superset of Skill allowed-tools.

        When a Skill forks to an Agent (context:fork, agent:<name>), the Agent
        must have at least all the tools the Skill declares in allowed-tools.
        Otherwise the forked Agent cannot perform operations the Skill expects.
        """
        if not agent_path.exists():
            pytest.skip(f"Agent file {agent_path.name} missing (covered by TC-AST-01)")

        skill_fm = _parse_frontmatter(skill_path)
        agent_fm = _parse_frontmatter(agent_path)

        if skill_fm is None or "allowed-tools" not in skill_fm:
            pytest.skip(f"Skill '{skill_name}' has no allowed-tools")
        if agent_fm is None or "tools" not in agent_fm:
            pytest.skip(f"Agent '{agent_name}' has no tools (covered by TC-AST-02)")

        skill_tools = _parse_tools_list(skill_fm["allowed-tools"])
        agent_tools = _parse_tools_list(agent_fm["tools"])

        missing = skill_tools - agent_tools
        assert not missing, (
            f"Skill '{skill_name}' needs tools {sorted(missing)} "
            f"but Agent '{agent_name}' only provides {sorted(agent_tools)}. "
            f"Add the missing tools to agents/{agent_name}.md frontmatter 'tools' field."
        )
