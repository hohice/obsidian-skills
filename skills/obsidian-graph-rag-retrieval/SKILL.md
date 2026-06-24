---
name: obsidian-graph-rag-retrieval
description: Multi-turn, graph-native retrieval and synthesis for Obsidian. Use after obsidian-graph-rag-ingest has prepared the Vault. Targets the current Obsidian Vault (detected via .obsidian/).
allowed-tools: obsidian
metadata:
  version: 1.0.0
---

# Obsidian Graph RAG Retrieval

A vector-embedding-free, graph-native retrieval system for Obsidian. Leverages the knowledge graph (Wikilinks, Backlinks, Tags, Properties) and the `obsidian` CLI to perform multi-turn iterative information retrieval.

Before using this skill, ensure your Vault has been prepared with [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md).

## Core Principles

- **Vault-Scoped**: Defaults to the Obsidian Vault containing `.obsidian/` in the current directory or ancestors. All retrieval is isolated to this Vault.
- **No Vector Embeddings**: Uses symbolic retrieval + graph traversal + heuristic scoring.
- **Multi-turn Iteration**: Maintains session state (`session.json`) to track scope, feedback, and query history across turns.
- **CLI-Native**: All operations use `obsidian` (`search`, `eval`, `read`) via the `obsidian-rag.sh` helper.

## Workflow

1. **Initialize**: Verify Vault root, create `.obsidian-rag-session/` and `session.json`.
2. **Retrieve**: Use `obsidian` for text search + graph scoring.
3. **Iterate**: Update session scope/feedback based on user input (narrow, broaden, shift, path-trace).
4. **Synthesize**: Generate structured research notes using `obsidian-markdown`.
5. **Visualize** (Optional): Create `.base` (tracking dashboard) and `.canvas` (graph visualization) using the reference templates.
6. **Augment** (Optional): Use [`defuddle`](../defuddle/SKILL.md) to fetch external documentation if Vault content is insufficient.

## Skill Dependencies

- **Core**: [`obsidian-cli`](../obsidian-cli/SKILL.md)
- **Ingestion**: [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md)
- **Synthesis**: [`obsidian-markdown`](../obsidian-markdown/SKILL.md)
- **Visualization** (Optional): [`obsidian-bases`](../obsidian-bases/SKILL.md), [`json-canvas`](../json-canvas/SKILL.md)
- **Augmentation** (Optional): [`defuddle`](../defuddle/SKILL.md)

## Graph Retrieval Strategy

- **Seed**: `obsidian search query="..." limit=20` (Vault-scoped)
- **Expand**: 1-3 hop BFS via `obsidian eval` + `app.metadataCache`
- **Score**: `outlinks*2 + backlinks*3 + tagOverlap*5 + textScore`
- **Filter**: tags, folders, exclude lists, score threshold
- See [GRAPH-RETRIEVAL.md](references/GRAPH-RETRIEVAL.md) for formulas & strategies.

## Multi-turn Protocol

- Maintain `session.json` with `scope`, `feedback`, `query_history`
- Support actions: `narrow`, `broaden`, `shift_focus`, `path_trace`
- Always present graph metadata (`score`, `depth`, `reason`) with results
- See [MULTI-TURN-PROTOCOL.md](references/MULTI-TURN-PROTOCOL.md) for schema & commands.

## CLI Integration Rules

- All graph ops use `obsidian eval code="..."`
- Force JSON output: `console.log(JSON.stringify(...))`
- Validate CLI output before parsing
- Limit graph depth to ≤3 to prevent explosion
- **Always verify Vault root before execution**
- See [CLI-HELPERS.md](references/CLI-HELPERS.md) for `obsidian-rag.sh` usage.

## Synthesis & Visualization

- Use `obsidian-markdown` to generate research notes from retrieved context.
- Optionally use `obsidian-bases` and `json-canvas` to create tracking dashboards and graph visualizations.
- See [EXPORT-TEMPLATES.md](references/EXPORT-TEMPLATES.md) for reference templates.

## Visualization Scenarios

Choose the right visualization format for the retrieved results:

- **Research Note (`.md`)**: Default output. Use for text-heavy synthesis with a simple Mermaid graph. For complex Mermaid diagrams, generate the diagram with [`mermaid-visualizer`](../mermaid-visualizer/SKILL.md) and embed the result.
- **Tracking Dashboard (`.base`)**: Use when you need to filter, sort, or summarize retrieval candidates by score, depth, or tags. See [`obsidian-bases`](../obsidian-bases/SKILL.md).
- **Interactive Graph (`.canvas`)**: Use when you want to explore nodes and edges visually in Obsidian Canvas. See [`json-canvas`](../json-canvas/SKILL.md).
- **Presentation Diagram (`.md` Excalidraw)**: Use for hand-drawn style conceptual diagrams to present findings. Generate with [`excalidraw-diagram`](../excalidraw-diagram/SKILL.md).

Keep diagrams focused: show the retrieval subgraph (seed + 1-2 hop neighbors), not the entire Vault.

## References

- [Obsidian Help: Internal links](https://help.obsidian.md/links)
- [Obsidian Help: Properties](https://help.obsidian.md/properties)
- [`obsidian-graph-rag`](../obsidian-graph-rag/SKILL.md) — full pipeline orchestrator
- [`obsidian-graph-rag-ingest`](../obsidian-graph-rag-ingest/SKILL.md) — Vault preparation
- [`obsidian-cli`](../obsidian-cli/SKILL.md) — core CLI dependency
- [`obsidian-markdown`](../obsidian-markdown/SKILL.md) — output note syntax and Quality Checklist
- [`obsidian-bases`](../obsidian-bases/SKILL.md) — optional dashboard views
- [`json-canvas`](../json-canvas/SKILL.md) — optional graph visualization
- [`defuddle`](../defuddle/SKILL.md) — optional external web augmentation

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
