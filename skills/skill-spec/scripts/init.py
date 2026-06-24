#!/usr/bin/env python3
"""Initialize a new skill directory according to the Agent Skills specification.

Usage:
    python3 init.py <skill-name> <description>

Example:
    python3 init.py data-analysis "Analyze CSV and JSON data. Use when working with tabular data."
"""

import re
import sys
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "SKILL.template.md"


def validate_skill_name(name: str) -> None:
    """Raise ValueError if the skill name does not meet spec constraints."""
    if not name:
        raise ValueError("Skill name must not be empty")
    if len(name) > 64:
        raise ValueError(f"Skill name must be 1-64 characters (got {len(name)})")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        raise ValueError(
            "Skill name may only contain lowercase letters, numbers, and single hyphens, "
            "and must not start or end with a hyphen"
        )


def initialize_skill(name: str, description: str, parent_dir: Path = Path.cwd()) -> Path:
    """Create a new skill directory with a valid SKILL.md and optional folders."""
    validate_skill_name(name)

    if not description:
        raise ValueError("Description must not be empty")
    if len(description) > 1024:
        raise ValueError(f"Description must be 1-1024 characters (got {len(description)})")

    skill_dir = parent_dir / name
    if skill_dir.exists():
        raise ValueError(f"Directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    (skill_dir / "assets").mkdir()

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    skill_md = template.replace("{{NAME}}", name).replace("{{DESCRIPTION}}", description)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    return skill_dir


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <skill-name> <description>", file=sys.stderr)
        print(f"Example: {sys.argv[0]} data-analysis \"Analyze CSV and JSON data.\"", file=sys.stderr)
        return 1

    name = sys.argv[1]
    description = sys.argv[2]

    try:
        skill_dir = initialize_skill(name, description)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Created skill at {skill_dir}")
    print("\nNext steps:")
    print(f"  1. Edit {skill_dir / 'SKILL.md'} to add instructions, examples, and references.")
    print(f"  2. Add scripts to {skill_dir / 'scripts/'}")
    print(f"  3. Validate with: python3 {Path(__file__)} {skill_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
