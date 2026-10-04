"""
Skill integrity tests.

Guard the ADI-OS skill document against drift: valid frontmatter, the advertised
26 roles and 7 gates, and every referenced file actually existing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "autonomous-data-org"
SKILL_MD = SKILL_DIR / "SKILL.md"


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


@pytest.mark.unit
def test_frontmatter_is_valid(skill_text: str) -> None:
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    meta = yaml.safe_load(match.group(1))
    assert meta["name"] == "autonomous-data-org"
    description = " ".join(str(meta["description"]).split())
    assert "Use when" in description, "description must say when to use the skill"
    assert len(description) < 1500


@pytest.mark.unit
def test_has_26_roles(skill_text: str) -> None:
    section = skill_text.split("## 2. AGENT DOMAINS")[1].split("## 3.")[0]
    roles = re.findall(r"^(\d+)\. \*\*", section, re.MULTILINE)
    assert [int(n) for n in roles] == list(range(1, 27))


@pytest.mark.unit
def test_has_7_gates(skill_text: str) -> None:
    section = skill_text.split("## 6. QUALITY GATES")[1].split("## 7.")[0]
    gates = re.findall(r"\*\*Gate (\d) ", section)
    assert gates == [str(n) for n in range(1, 8)]


@pytest.mark.unit
def test_sections_are_sequential(skill_text: str) -> None:
    numbers = [int(n) for n in re.findall(r"^## (\d+)\. ", skill_text, re.MULTILINE)]
    assert numbers == list(range(0, len(numbers)))


@pytest.mark.unit
def test_referenced_paths_exist(skill_text: str) -> None:
    refs = re.findall(r"`((?:references|\.agents|templates)/[^`\s]+)`", skill_text)
    assert refs, "expected path references in the Reference Map"
    missing = []
    for ref in refs:
        if "*" in ref:
            continue
        base = SKILL_DIR if ref.startswith("references/") else REPO_ROOT
        if not (base / ref).exists():
            missing.append(ref)
    assert not missing, f"Broken references in SKILL.md: {missing}"


@pytest.mark.unit
def test_reference_files_are_non_trivial() -> None:
    for path in (SKILL_DIR / "references").glob("*.md"):
        assert len(path.read_text(encoding="utf-8")) > 1500, f"{path.name} looks empty"
