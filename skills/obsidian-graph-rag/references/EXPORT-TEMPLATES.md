# Export Templates

## 1. Research Note (`.md`)
Generated using `obsidian-markdown` syntax. Includes frontmatter, AI summary, cited snippets, and Mermaid graph.

```markdown
---
title: "RAG Research: {{query}}"
session_id: "{{session_id}}"
turn: {{turn}}
confidence: {{confidence}}
tags: [rag-research, {{tags}}]
created: {{date}}
---

# {{query}} Research

> [!summary] AI 综合结论
> {{summary}}

## 关键上下文
{{#each retrieved}}
- [[{{basename}}]] %%图谱分: {{score}}, 深度: {{depth}}%%
{{/each}}

```mermaid
graph TD
{{#each edges}}
    {{from}} --> {{to}}
{{/each}}
```

%% 检索轨迹已保存至 .obsidian-rag-session/ %%
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

## Export Workflow
1. Read `session.json` and `results.json`
2. Generate `.md` note with cited snippets
3. Generate `.base` file for tracking dashboard
4. Generate `.canvas` file for graph visualization
5. Save all to `research/` folder in Vault
