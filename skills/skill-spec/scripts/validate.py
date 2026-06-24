#!/usr/bin/env python3
"""Validate a skill directory against the Agent Skills specification.

Usage:
    python3 validate.py <path-to-skill>
"""

import os
import re
import sys
from pathlib import Path


SPEC_URL = "https://agentskills.io/specification"


def error(msg: str) -> dict:
    return {"level": "error", "message": msg}


def warn(msg: str) -> dict:
    return {"level": "warn", "message": msg}


def parse_frontmatter(text: str) -> tuple[dict, str, list]:
    """Extract YAML frontmatter and remaining body from SKILL.md content.

    Returns (frontmatter_dict, body, issues).
    """
    issues = []
    if not text.startswith("---"):
        return {}, text, [error("SKILL.md must start with YAML frontmatter delimited by '---'")]

    # Find end of frontmatter
    end_match = re.search(r"\n---\s*(?:\n|$)", text, re.MULTILINE)
    if not end_match:
        return {}, text, [error("SKILL.md frontmatter is not closed with '---'")]

    fm_text = text[3:end_match.start()]
    body = text[end_match.end():]

    try:
        data = parse_simple_yaml(fm_text)
    except ValueError as exc:
        return {}, body, [error(f"Failed to parse YAML frontmatter: {exc}")]

    return data, body, issues


def parse_simple_yaml(text: str) -> dict:
    """Parse a simple subset of YAML used by SKILL.md frontmatter.

    Supports:
      - key: value
      - nested mapping under a key (e.g. metadata:)
    """
    result: dict = {}
    lines = text.splitlines()
    i = 0
    current_key = None
    current_indent = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key
        if indent == 0:
            if ":" not in stripped:
                raise ValueError(f"Invalid line in frontmatter: {line!r}")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value == "":
                # Could be a nested mapping; peek next line
                if i + 1 < len(lines) and (lines[i + 1].strip().startswith("-") or lines[i + 1].strip() == ""):
                    # We don't support lists in this minimal parser, but metadata is a mapping.
                    # Treat as mapping start if next non-empty line is indented.
                    current_key = key
                    current_indent = None
                else:
                    current_key = key
                    current_indent = None
                result[key] = {}
            else:
                result[key] = unquote(value)
                current_key = None
                current_indent = None

        elif current_key is not None and indent > 0:
            if ":" not in stripped:
                raise ValueError(f"Invalid nested line in frontmatter: {line!r}")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if current_key not in result or not isinstance(result[current_key], dict):
                result[current_key] = {}
            result[current_key][key] = unquote(value)

        i += 1

    return result


def unquote(value: str) -> str:
    """Remove matching surrounding quotes from a YAML scalar."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
            return value[1:-1]
    return value


def validate_name(name: any, dir_name: str) -> list:
    """Validate the name field per the spec."""
    issues = []
    if not isinstance(name, str):
        return [error("'name' must be a string")]

    if not name:
        issues.append(error("'name' must be 1-64 characters"))
    elif len(name) > 64:
        issues.append(error(f"'name' is {len(name)} characters; max is 64"))

    if name and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        issues.append(
            error(
                "'name' may only contain lowercase letters, numbers, and single hyphens, "
                "and must not start or end with a hyphen"
            )
        )

    if name != dir_name:
        issues.append(
            error(
                f"'name' ({name!r}) must match the parent directory name ({dir_name!r})"
            )
        )

    return issues


def validate_description(description: any) -> list:
    """Validate the description field per the spec."""
    issues = []
    if not isinstance(description, str):
        return [error("'description' must be a string")]

    if not description:
        issues.append(error("'description' must be 1-1024 characters"))
    elif len(description) > 1024:
        issues.append(error(f"'description' is {len(description)} characters; max is 1024"))

    return issues


def validate_compatibility(compatibility: any) -> list:
    issues = []
    if not isinstance(compatibility, str):
        return [error("'compatibility' must be a string")]
    if not compatibility:
        issues.append(error("'compatibility' must be 1-500 characters"))
    elif len(compatibility) > 500:
        issues.append(error(f"'compatibility' is {len(compatibility)} characters; max is 500"))
    return issues


def validate_metadata(metadata: any) -> list:
    issues = []
    if not isinstance(metadata, dict):
        return [error("'metadata' must be a mapping of string keys to string values")]

    for key, value in metadata.items():
        if not isinstance(key, str):
            issues.append(error(f"metadata key {key!r} must be a string"))
        if not isinstance(value, str):
            issues.append(error(f"metadata value for key {key!r} must be a string"))
    return issues


def validate_skill(skill_path: Path) -> list:
    """Validate a skill directory and return a list of issues."""
    issues = []
    dir_name = skill_path.name

    if not skill_path.exists():
        return [error(f"Skill directory does not exist: {skill_path}")]
    if not skill_path.is_dir():
        return [error(f"Path is not a directory: {skill_path}")]

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        issues.append(error(f"Required file missing: {skill_md}"))
        return issues

    text = skill_md.read_text(encoding="utf-8")
    if not text.strip():
        issues.append(error("SKILL.md is empty"))
        return issues

    frontmatter, body, fm_issues = parse_frontmatter(text)
    issues.extend(fm_issues)

    if "name" not in frontmatter:
        issues.append(error("Required frontmatter field missing: 'name'"))
    else:
        issues.extend(validate_name(frontmatter["name"], dir_name))

    if "description" not in frontmatter:
        issues.append(error("Required frontmatter field missing: 'description'"))
    else:
        issues.extend(validate_description(frontmatter["description"]))

    if "license" in frontmatter and not isinstance(frontmatter["license"], str):
        issues.append(error("'license' must be a string"))

    if "compatibility" in frontmatter:
        issues.extend(validate_compatibility(frontmatter["compatibility"]))

    if "metadata" in frontmatter:
        issues.extend(validate_metadata(frontmatter["metadata"]))

    if "allowed-tools" in frontmatter and not isinstance(frontmatter["allowed-tools"], str):
        issues.append(error("'allowed-tools' must be a string"))

    # Optional directories are allowed; only warn about unexpected top-level files if they look wrong.
    # The spec allows "Any additional files or directories", so we don't flag them.

    # Recommended: main SKILL.md under 500 lines
    line_count = len(text.splitlines())
    if line_count > 500:
        issues.append(
            warn(
                f"SKILL.md is {line_count} lines; consider keeping it under 500 lines "
                "and moving detailed reference material to files in references/"
            )
        )

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-skill>", file=sys.stderr)
        return 1

    skill_path = Path(sys.argv[1]).resolve()
    issues = validate_skill(skill_path)

    if not issues:
        print(f"✅ {skill_path.name} is valid according to {SPEC_URL}")
        return 0

    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warn"]

    print(f"Validation results for {skill_path}:")
    for issue in errors:
        print(f"  ❌ {issue['message']}")
    for issue in warnings:
        print(f"  ⚠️  {issue['message']}")

    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
