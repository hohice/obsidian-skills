---
name: obsidian-graph-rag
description: End-to-end graph-native RAG workflow for Obsidian. Orchestrates obsidian-graph-rag-ingest for knowledge base preparation and obsidian-graph-rag-retrieval for multi-turn retrieval and synthesis.
allowed-tools: obsidian
metadata:
  version: 2.0.0
---

# Obsidian Graph RAG

End-to-end, vector-embedding-free RAG for Obsidian. This skill coordinates two sub-skills:

- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) — import and normalize content into your Vault
- [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md) — retrieve, synthesize, and visualize answers from your Vault

## When to Use the Full Pipeline

Use this skill when you want to go from raw documents or web pages to synthesized research notes in one workflow.

## End-to-End Workflow

1. **Ingest**: Use `obsidian-graph-rag-ingest` to import and normalize sources.
2. **Retrieve**: Use `obsidian-graph-rag-retrieval` to run graph-native retrieval against the prepared Vault.
3. **Synthesize**: Generate research notes with `obsidian-markdown`.
4. **Visualize** (optional): Create dashboards with `obsidian-bases` or canvases with `json-canvas`.

```
source → obsidian-graph-rag-ingest → Vault → obsidian-graph-rag-retrieval → research notes → visualization
```

## When to Use Sub-Skills Directly

- Use only [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) when you just need to build or update a knowledge base.
- Use only [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md) when your Vault is already prepared and you only need retrieval.

## Skill Dependencies

- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md)
- [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md)
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — output note syntax and Quality Checklist
- [`obsidian-bases`](../obsidian-bases/SKILL.md) — optional dashboard views
- [`json-canvas`](../json-canvas/SKILL.md) — optional graph visualization

## Core Principles

- **Vault-Scoped**: All work is isolated to the Obsidian Vault containing `.obsidian/`.
- **No Vector Embeddings**: Relies on symbolic retrieval + graph traversal + heuristic scoring.
- **Multi-turn Iteration**: Maintains session state across turns.
- **CLI-Native**: Uses the `obsidian` CLI for Vault operations.

## References

- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md)
- [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md)
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md)
- [`obsidian-bases`](../obsidian-bases/SKILL.md)
- [`json-canvas`](../json-canvas/SKILL.md)

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
