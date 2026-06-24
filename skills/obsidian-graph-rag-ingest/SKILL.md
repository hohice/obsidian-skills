---
name: obsidian-graph-rag-ingest
description: Prepare and import external content into an Obsidian Vault for graph-native RAG. Use before obsidian-graph-rag-retrieval, or when building a knowledge base from documents and web pages.
metadata:
  version: 1.0.0
---

# Obsidian Graph RAG Ingest

Prepare external content so it can be retrieved by [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md). This skill covers ingestion from files, web pages, and existing notes, plus normalization of frontmatter, links, and attachments.

## When to Use

- You have documents (PDF, Word, PowerPoint, Excel, images, etc.) that need to become Obsidian notes.
- You want to fetch web content into your Vault for RAG.
- You need to normalize existing notes so they work well with graph retrieval.
- You are setting up a Vault before running `obsidian-graph-rag-retrieval`.

## Ingestion Workflow

1. **Identify sources**: files, web pages, or existing notes.
2. **Convert to Markdown**:
   - Simple text-heavy files → [`markitdown`](../markitdown/SKILL.md)
   - Complex PDFs, tables, multi-column layouts, scanned documents → [`marker`](../marker/SKILL.md)
   - Web pages → [`defuddle`](../defuddle/SKILL.md)
3. **Move into Vault**: place `.md` files in an inbox or topic folder.
4. **Normalize every note** with [`obsidian-markdown`](../obsidian-markdown/SKILL.md):
   - Add frontmatter (`title`, `date`, `tags`, `source`, `status`)
   - Move attachments to `attachments/`
   - Update relative paths
   - Add wikilinks to related notes
5. **Run the Quality Checklist** from `obsidian-markdown`.
6. **Verify graph connectivity**: ensure notes are linked and not orphans.

```
external source → markitdown / marker / defuddle → Markdown → obsidian-markdown normalization → Vault → obsidian-graph-rag-retrieval
```

## Frontmatter Design for RAG

Use stable property names and types so retrieval and downstream views work reliably.

| Property | Type | Purpose |
|----------|------|---------|
| `title` | text | Display name |
| `date` | date | Creation or import date |
| `tags` | list | Categories for filtering |
| `source` | text | Original file or URL |
| `status` | text | `draft`, `imported`, `processed` |
| `aliases` | list | Alternative names |
| `related` | list | Wikilinks to related notes |

See [`obsidian-markdown`](../obsidian-markdown/SKILL.md) for frontmatter syntax and templates.

## Linking Strategy for Graph RAG

- Link the **first mention** of each concept to its note.
- Avoid orphan notes: every imported note should be reachable from at least one other note or MOC.
- Use MOCs (Maps of Content) to group topics and improve discoverability.
- Add bidirectional links when two notes strongly relate to each other.

## Source-Specific Guidance

### Files

```bash
# Simple PDF
markitdown report.pdf -o report.md

# Complex PDF
marker_single report.pdf --output_dir . --output_format markdown
```

After conversion, move the note and any extracted images into the Vault and add frontmatter.

### Web Pages

```bash
defuddle parse https://example.com/article --md -o article.md
```

Store the URL in the `source` property.

### Existing Notes

If your Vault already contains notes, audit them for:
- Consistent frontmatter
- Meaningful tags
- Working wikilinks
- No orphan pages

## Attachment Management

- Store images and extracted files in a dedicated folder such as `attachments/`.
- Use relative paths in Markdown: `![[attachments/screenshot.png]]`.
- Keep filenames descriptive and avoid spaces when possible.

## Quality Gates

Before finishing ingestion:

- [ ] frontmatter is valid YAML at the top of each file
- [ ] `title`, `date`, `tags`, and `source` are populated
- [ ] tags follow vault conventions (lowercase, no spaces)
- [ ] attachments are in the designated folder
- [ ] wikilinks point to existing or intended notes
- [ ] no orphan notes remain
- [ ] the [`obsidian-markdown` Quality Checklist](../obsidian-markdown/SKILL.md#quality-checklist) has passed

## References

- [`obsidian-graph-rag`](../obsidian-graph-rag/SKILL.md) — full pipeline orchestrator
- [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md) — retrieval step that consumes prepared notes
- [`markitdown`](../markitdown/SKILL.md) — file-to-Markdown conversion
- [`marker`](../marker/SKILL.md) — complex PDF and image conversion
- [`defuddle`](../defuddle/SKILL.md) — web page extraction
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — note syntax, templates, and Quality Checklist

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
