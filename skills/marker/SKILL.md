---
name: marker
description: Convert PDFs and images to high-quality Markdown using deep-learning visual layout analysis. Use when documents contain complex tables, multi-column layouts, mixed text and graphics, or when markitdown's default text extraction produces garbled tables. Ideal for importing structured documents into Obsidian vaults.
metadata:
  version: 1.1.0
---

# Marker

Convert PDFs to Markdown with deep-learning visual analysis. Marker uses layout detection, OCR, and table recognition models to understand document structure from the visual perspective, producing significantly better results than text-stream extractors for complex documents.

## When to use

- PDFs with **complex tables** (financial reports, exam outlines, datasheets)
- **Multi-column** or magazine-style layouts
- Documents with **mixed text, images, and graphics**
- **Scanned/image PDFs** that need OCR
- When `markitdown` default output has garbled or misaligned tables
- Importing structured documents into Obsidian where table fidelity matters

## When NOT to use

- Simple text-heavy PDFs (papers, novels) — `markitdown` is faster and lighter
- Real-time or latency-sensitive pipelines — marker runs deep-learning inference
- Environments with strict disk constraints — requires ~3GB of models

## Installation

```bash
uv tool install marker-pdf
```

Or with pip:

```bash
pip install marker-pdf
```

**First run** will automatically download layout, OCR, text detection, and table recognition models (~3GB total) to `~/Library/Caches/datalab/models/` (macOS).

## Command-line usage

### Single file conversion

```bash
marker_single document.pdf --output_dir . --output_format markdown
```

This creates a folder `document/` containing:
- `document.md` — the converted Markdown
- `document_meta.json` — extracted metadata
- `_page_N_Picture_M.jpeg` — extracted inline images

### Copy the Markdown out of the output folder

```bash
marker_single "Report.pdf" --output_dir . --output_format markdown
cp "Report/Report.md" "Report.md"
```

### Batch conversion

Convert all PDFs in a directory:

```bash
for f in *.pdf; do
  marker_single "$f" --output_dir . --output_format markdown
  cp "${f%.pdf}/${f%.pdf}.md" "${f%.pdf}.md"
done
```

## Output structure

```
output_dir/
└── document/
    ├── document.md              # Main Markdown output
    ├── document_meta.json       # Title, authors, languages, etc.
    ├── _page_0_Picture_1.jpeg   # Embedded images extracted from page 0
    └── _page_2_Picture_0.jpeg   # Additional extracted images
```

Images are referenced in the Markdown via relative paths:

```markdown
![](_page_0_Picture_1.jpeg)

# Document Title

Text content...
```

## Comparison with markitdown

| Feature | markitdown (default) | marker |
|---------|---------------------|--------|
| **Underlying tech** | Text-stream extraction (`pdfplumber`) | Visual layout analysis (deep learning) |
| **Table quality** | ❌ Often misaligned | ✅ Preserves structure |
| **Multi-column** | ❌ Reads left-to-right across columns | ✅ Respects column boundaries |
| **Image extraction** | Ignores | ✅ Extracts as separate files |
| **OCR for scanned PDFs** | Limited | ✅ Built-in |
| **Speed** | ⚡ Seconds | 🐢 Slower (model inference) |
| **Model download** | None | ~3GB first run |
| **Best for** | Text-heavy docs | Complex layouts & tables |

## Workflow: Import a complex PDF into Obsidian

Follow these steps to turn a marker conversion into a first-class Obsidian note:

1. **Convert with marker**:
   ```bash
   marker_single "Annual Report.pdf" --output_dir . --output_format markdown
   ```
2. **Move the Markdown file into your vault** (e.g., `Imports/`):
   ```bash
   mv "Annual Report/Annual Report.md" ~/Vault/Imports/"Annual Report.md"
   ```
3. **Move extracted images to a dedicated attachments folder** and update paths in the note:
   ```bash
   mkdir -p ~/Vault/attachments
   mv "Annual Report"/*.jpeg ~/Vault/attachments/
   ```
   Then replace image references in the note so they point to the attachments folder, e.g.:
   ```markdown
   ![](attachments/_page_0_Picture_1.jpeg)
   ```
4. **Add Obsidian frontmatter** following [`obsidian-markdown`](../obsidian-markdown/SKILL.md) conventions:
   ```markdown
   ---
   title: Annual Report
   date: 2024-01-15
   tags:
     - import
     - finance
   source: "Annual Report.pdf"
   ---
   ```
5. **Add wikilinks** to connect with existing notes.
6. **Run the [`obsidian-markdown` Quality Checklist](../obsidian-markdown/SKILL.md#quality-checklist)** before finishing.

> For simple text-heavy PDFs, use [`markitdown`](../markitdown/SKILL.md) instead — it's faster and lighter.

See [`obsidian-markdown`](../obsidian-markdown/SKILL.md) for full syntax, templates, and additional note types.

## Workflow: Choose the right PDF converter

When a user asks to convert a PDF, assess complexity first:

1. **Does the PDF have complex tables, forms, or multi-column layout?**
   - Yes → Use **marker**
   - No → Use **markitdown** (faster)

2. **Is the PDF a scanned image or contains embedded images with critical information?**
   - Yes → Use **marker**
   - No → **markitdown** is usually sufficient

3. **Is speed or disk space a constraint?**
   - Yes → Use **markitdown**
   - No → **marker** for best quality

## References

- [marker GitHub](https://github.com/VikParuchuri/marker)
- [`markitdown`](../markitdown/SKILL.md) — for simple text-heavy documents
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — Obsidian note syntax, templates, and Quality Checklist
- [`obsidian-cli`](../obsidian-cli/SKILL.md) — for creating and moving notes into vaults via CLI
- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) — downstream RAG knowledge base preparation workflow

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
