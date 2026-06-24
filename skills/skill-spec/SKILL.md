---
name: skill-spec
description: Validate existing skills or initialize new skills according to the Agent Skills specification (agentskills.io/specification). Use when the user wants to check a skill for spec compliance, fix skill structure, or scaffold a new skill.
metadata:
  version: 1.0.0
---

# skill-spec

This skill implements the [Agent Skills specification](https://agentskills.io/specification). It can:

1. **Validate** an existing skill directory against the spec.
2. **Initialize** a new skill directory with a valid `SKILL.md` and optional folders.

## When to use

- The user asks to check, validate, lint, or review a skill.
- The user asks to create, scaffold, or initialize a new skill.
- The user asks to fix a skill that does not follow the spec.

## Validation

Run the validation script against a skill directory:

```bash
python3 skill-spec/scripts/validate.py <path-to-skill>
```

The script checks:

- The directory name matches the skill `name`.
- `SKILL.md` exists.
- Frontmatter is present and parseable.
- Required fields (`name`, `description`) are present and valid.
- `name` follows the spec constraints.
- `description` length is 1–1024 characters.
- Optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`) follow spec constraints when present.
- Optional directories (`scripts/`, `references/`, `assets/`) are allowed but not required.

If validation fails, the script reports each issue. Fix them and rerun.

## Initialization

Create a new skill directory with a valid `SKILL.md`:

```bash
python3 skill-spec/scripts/init.py <skill-name> <description>
```

Example:

```bash
python3 skill-spec/scripts/init.py data-analysis "Analyze CSV and JSON data. Use when working with tabular data, statistics, or charts."
```

This creates:

```
data-analysis/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

You can then edit `SKILL.md` to add instructions, examples, and references.

## Manual fixes

If a skill fails validation, common fixes include:

- Rename the directory to match the `name` field.
- Make sure `SKILL.md` starts with YAML frontmatter delimited by `---`.
- Use only lowercase letters, numbers, and single hyphens in the `name`.
- Keep the `description` between 1 and 1024 characters and make it actionable.
- Keep `compatibility` under 500 characters if used.
- Keep `metadata` values as strings.

## Reference

- Specification source: https://agentskills.io/specification
- Validation script: `scripts/validate.py`
- Initialization script: `scripts/init.py`
- New skill template: `assets/SKILL.template.md`

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Use `scripts/validate.py` to validate this skill like any other.
