# Export Templates

These are reference templates for synthesizing RAG retrieval results into Obsidian artifacts. They are not generated automatically by `obsidian-rag.sh`; use them as a starting point when creating research notes, dashboards, or graph visualizations with the relevant skills.

> All `.md` output should follow the conventions in [`obsidian-markdown`](../obsidian-markdown/SKILL.md). Run the generated note through its [Quality Checklist](../obsidian-markdown/SKILL.md#quality-checklist) before saving.

## 1. Research Note (`.md`)
Generated using `obsidian-markdown` syntax. Includes frontmatter, AI summary, cited snippets, and Mermaid graph.

> For simple relationship graphs, use the Mermaid snippet below. For complex diagrams with grouping, styling, or many nodes, generate the diagram with [`mermaid-visualizer`](../mermaid-visualizer/SKILL.md) and embed the resulting code block.

```markdown
---
title: "RAG Research: {{query}}"
session_id: "{{session_id}}"
turn: {{turn}}
confidence: {{confidence}}
date: {{date}}
tags:
  - rag-research
  - {{tags}}
aliases:
  - "{{query}} Research"
related:
  - "[[RAG Session {{session_id}}]]"
---

# {{query}} Research

> [!summary] AI Synthesis / AI 综合结论
> {{summary}}

## Key Context / 关键上下文
{{#each retrieved}}
- [[{{basename}}]] %%graph score: {{score}}, depth: {{depth}} / 图谱分: {{score}}, 深度: {{depth}}%%
{{/each}}

```mermaid
graph TD
{{#each edges}}
    {{from}} --> {{to}}
{{/each}}
```

%% Retrieval trace saved to .obsidian-rag-session/ / 检索轨迹已保存至 .obsidian-rag-session/ %%
```

## 2. Bases Dashboard (`.base`)
Generated using `obsidian-bases` YAML schema. Tracks retrieval candidates, scores, and iteration history.

```yaml
filters:
  and:
    - file.inFolder(".obsidian-rag-session")
    - 'file.ext == "md"'

formulas:
  confidence_label: 'if(score >= 12, "🟢 High", if(score >= 6, "🟡 Medium", "🔴 Low"))'
  depth_badge: 'if(depth == 1, "1跳", if(depth == 2, "2跳", "3跳+"))'

views:
  - type: table
    name: "Retrieved Candidates"
    order:
      - file.name
      - formula.confidence_label
      - score
      - formula.depth_badge
      - reason
    groupBy:
      property: formula.confidence_label
      direction: DESC
    summaries:
      score: Average
```

## 3. Canvas Graph (`.canvas`)
Generated using `json-canvas` schema. Visualizes retrieval nodes and their connections.

```json
{
  "nodes": [
    {
      "id": "{{node_id}}",
      "type": "text",
      "x": {{x}},
      "y": {{y}},
      "width": 300,
      "height": 100,
      "color": "{{color}}",
      "text": "## {{basename}}\nScore: {{score}}\nDepth: {{depth}}"
    }
  ],
  "edges": [
    {
      "id": "{{edge_id}}",
      "fromNode": "{{from_id}}",
      "toNode": "{{to_id}}",
      "label": "{{reason}}",
      "toEnd": "arrow"
    }
  ]
}
```

### Mapping Rules
- **X Position**: `200 + (depth - 1) * 350` (layered by depth)
- **Y Position**: `index * 150` (vertical stacking)
- **Color**: `"4"` (green) if `score >= 10`, `"3"` (yellow) if `score >= 5`, `"1"` (red) otherwise
- **Edges**: Generated from `via` field in retrieval results

## Reference Synthesis Workflow
1. Read `session.json` and `results.json`
2. Use the `.md` template to create a research note with cited snippets
3. Use the `.base` template to build a tracking dashboard (via [obsidian-bases](../obsidian-bases/SKILL.md))
4. Use the `.canvas` template to create a graph visualization (via [json-canvas](../json-canvas/SKILL.md))
5. Save artifacts to a folder such as `research/` in the Vault
