---
name: defuddle
description: Extract clean markdown content from web pages using Defuddle CLI, removing clutter and navigation to save tokens. Use instead of WebFetch when the user provides a URL to read or analyze, for online documentation, articles, blog posts, or any standard web page. Do NOT use for URLs ending in .md — those are already markdown, use WebFetch directly.
metadata:
  version: 1.1.0
---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages. Prefer over WebFetch for standard web pages — it removes navigation, ads, and clutter, reducing token usage.

If not installed: `npm install -g defuddle`

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |

## References

- [Defuddle GitHub](https://github.com/kepano/defuddle-cli)
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — save fetched content as a properly formatted Obsidian note
- [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md) — use fetched content to augment Vault retrieval
- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) — import fetched content as part of RAG knowledge base preparation

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).