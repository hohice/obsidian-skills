---
name: obsidian-graph-rag
description: Multi-turn, graph-native RAG workflow for Obsidian. Uses links, tags, properties, and CLI to iteratively retrieve context without vector embeddings. Targets the current Obsidian Vault (detected via .obsidian/). Orchestrates obsidian-cli, obsidian-markdown, obsidian-bases, json-canvas, and defuddle.
---

# Obsidian Graph RAG

A vector-embedding-free, graph-native retrieval system for Obsidian. Leverages the knowledge graph (Wikilinks, Backlinks, Tags, Properties) and CLI to perform multi-turn iterative information retrieval.

## Core Principles
- **Vault-Scoped**: Defaults to the Obsidian Vault containing `.obsidian/` in the current directory or ancestors. All retrieval is isolated to this Vault.
- **No Vector Embeddings**: Uses symbolic retrieval + graph traversal + heuristic scoring.
- **Multi-turn Iteration**: Maintains session state (`session.json`) to track scope, feedback, and query history across turns.
- **CLI-Native**: All operations use `obsidian-cli` (`search`, `eval`, `read`) via the `obsidian-rag.sh` helper.

## Workflow
1. **Initialize**: Verify Vault root, create `.obsidian-rag-session/` and `session.json`.
2. **Retrieve**: Use `obsidian-cli` for text search + graph scoring.
3. **Iterate**: Update session scope/feedback based on user input (narrow, broaden, shift, path-trace).
4. **Synthesize**: Generate structured research notes using `obsidian-markdown`.
5. **Visualize**: Export to `.base` (tracking dashboard) and `.canvas` (graph visualization).
6. **Augment** (Optional): Use `defuddle` to fetch external documentation if Vault content is insufficient.

## Skill Dependencies
- **Required**: `obsidian-cli` (core retrieval & graph ops)
- **Export**: `obsidian-markdown`, `obsidian-bases`, `json-canvas`
- **Optional**: `defuddle` (web augmentation)

## Graph Retrieval Strategy
- **Seed**: `obsidian search query="..." limit=20` (Vault-scoped)
- **Expand**: 1-3 hop BFS via `obsidian eval` + `app.metadataCache`
- **Score**: `outlinks*2 + backlinks*3 + tagOverlap*5 + textScore`
- **Filter**: tags, folders, exclude lists, score threshold
- See [GRAPH-RETRIEVAL.md](references/GRAPH-RETRIEVAL.md) for formulas & strategies.

## Multi-turn Protocol
- Maintain `session.json` with `scope`, `feedback`, `query_history`
- Support actions: `narrow`, `broaden`, `shift_focus`, `path_trace`, `export`
- Always present graph metadata (`score`, `depth`, `reason`) with results
- See [MULTI-TURN-PROTOCOL.md](references/MULTI-TURN-PROTOCOL.md) for schema & commands.

## CLI Integration Rules
- All graph ops use `obsidian eval code="..."`
- Force JSON output: `console.log(JSON.stringify(...))`
- Validate CLI output before parsing
- Limit graph depth to ≤3 to prevent explosion
- **Always verify Vault root before execution**
- See [CLI-HELPERS.md](references/CLI-HELPERS.md) for `obsidian-rag.sh` usage.

## Export Templates
- Research Note: See [EXPORT-TEMPLATES.md](references/EXPORT-TEMPLATES.md)
- Bases Dashboard: See [EXPORT-TEMPLATES.md](references/EXPORT-TEMPLATES.md)
- Canvas Graph: See [EXPORT-TEMPLATES.md](references/EXPORT-TEMPLATES.md)
