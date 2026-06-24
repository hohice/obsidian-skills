---
name: markitdown
description: Convert various files (PDF, Word, PowerPoint, Excel, images, audio, HTML, ZIP, YouTube, and more) to Markdown for use in Obsidian vaults and LLM pipelines. Use when the user wants to extract text from documents, import external files into Obsidian, or preprocess files for RAG and knowledge management.
metadata:
  version: 1.1.0
---

# MarkItDown

Convert files to Markdown. MarkItDown is a Microsoft open-source tool that extracts text and structure from many file formats into clean Markdown, optimized for LLMs and text analysis.

## When to use

- Importing PDFs, Word docs, PowerPoints, or Excel files into an Obsidian vault
- Extracting text from images (OCR) or audio (transcription)
- Preprocessing documents for RAG, GraphRAG, or LLM-based analysis
- Converting web pages (HTML) or YouTube transcripts to Markdown notes
- Batch-processing ZIP archives containing multiple documents

## Supported formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text extraction with structure preservation |
| Word | `.docx` | Headings, lists, tables, links |
| PowerPoint | `.pptx` | Slides with LLM image descriptions optional |
| Excel | `.xlsx`, `.xls` | Sheets to Markdown tables |
| Images | `.jpg`, `.png`, `.gif`, etc. | EXIF metadata + optional OCR via LLM Vision |
| Audio | `.wav`, `.mp3` | EXIF metadata + speech transcription |
| HTML | `.html`, `.htm` | Clean conversion to Markdown |
| Text data | `.csv`, `.json`, `.xml` | Structured to Markdown tables/lists |
| ZIP | `.zip` | Iterates and converts contents |
| YouTube | URL | Fetches transcript |
| EPub | `.epub` | E-book text extraction |
| Outlook | `.msg` | Email content |

## Command-line usage

### Basic conversion

```bash
markitdown document.pdf > document.md
```

### Specify output file

```bash
markitdown report.docx -o report.md
```

### Pipe content

```bash
cat file.pdf | markitdown > output.md
```

### List plugins

```bash
markitdown --list-plugins
```

### Enable plugins

```bash
markitdown --use-plugins file.pdf -o output.md
```

### Azure Document Intelligence (advanced PDF parsing)

```bash
markitdown file.pdf -o document.md -d -e "<document_intelligence_endpoint>"
```

## Python API

Use in scripts for custom workflows:

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.xlsx")
print(result.text_content)
```

### With LLM for image descriptions

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("presentation.pptx")
print(result.text_content)
```

### Stream conversion (most secure)

```python
with open("document.pdf", "rb") as f:
    result = md.convert_stream(f)
    print(result.text_content)
```

## Workflow: Import a file into Obsidian

Follow these steps to turn a converted file into a first-class Obsidian note:

1. **Convert the file** to Markdown:
   ```bash
   markitdown "Meeting Notes.pdf" -o "Meeting Notes.md"
   ```
2. **Move into vault** (or use `obsidian create` if [`obsidian-cli`](../obsidian-cli/SKILL.md) is available):
   ```bash
   mv "Meeting Notes.md" ~/Vault/Imports/
   ```
3. **Add Obsidian frontmatter** following [`obsidian-markdown`](../obsidian-markdown/SKILL.md) conventions:
   ```markdown
   ---
   title: Meeting Notes
   date: 2024-01-15
   tags:
     - import
     - meeting
   source: "Meeting Notes.pdf"
   ---
   ```
4. **Store attachments** in a dedicated folder such as `attachments/` and update relative paths if the converter produced images.
5. **Add wikilinks** to connect with existing notes.
6. **Run the [`obsidian-markdown` Quality Checklist](../obsidian-markdown/SKILL.md#quality-checklist)** before finishing.

> For complex PDFs with tables, multi-column layouts, or scanned pages, consider using [`marker`](../marker/SKILL.md) instead.

See [`obsidian-markdown`](../obsidian-markdown/SKILL.md) for full syntax, templates, and additional note types.

## Workflow: Batch process a folder

Convert all PDFs in a directory:

```bash
for f in *.pdf; do
  markitdown "$f" -o "${f%.pdf}.md"
done
```

## Security best practices

- **Sanitize inputs** in server-side or untrusted environments
- **Use narrow APIs** when possible:
  - `convert_local()` for local files only
  - `convert_stream()` for maximum control over input streams
- Avoid passing untrusted user paths directly to `markitdown`

## Optional dependencies

Install only what you need:

```bash
pip install 'markitdown[pdf,docx,pptx]'
```

Available extras: `all`, `pptx`, `docx`, `xlsx`, `xls`, `pdf`, `outlook`, `az-doc-intel`, `audio-transcription`, `youtube-transcription`.

## References

- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — Obsidian note syntax, templates, and Quality Checklist
- [`obsidian-cli`](../obsidian-cli/SKILL.md) — for creating and moving notes into vaults via CLI
- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) — downstream RAG knowledge base preparation workflow

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
