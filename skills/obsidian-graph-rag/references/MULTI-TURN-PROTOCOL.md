# Multi-turn Protocol

## Session State Schema (`session.json`)
```json
{
  "session_id": "rag_20240115_001",
  "turn": 2,
  "query_history": ["auth JWT", "JWT token refresh flow"],
  "retrieved": [
    {
      "path": "notes/JWT-Auth.md",
      "score": 14,
      "depth": 1,
      "reason": "backlinks=8, tag=auth"
    }
  ],
  "scope": {
    "depth": 2,
    "mode": "explore",
    "tags": ["auth", "security"],
    "folders": ["projects/backend"],
    "score_threshold": 5
  },
  "feedback": {
    "action": "narrow",
    "focus": "refresh token logic",
    "exclude": ["OAuth2"]
  }
}
```

## Iteration Commands

| Action | Description | State Update |
|--------|-------------|--------------|
| `narrow` | Focus on specific subtopic | `feedback.focus` set, `scope.tags` updated, `score_threshold` increased |
| `broaden` | Expand search scope | `scope.depth` increased (max 3), `score_threshold` decreased |
| `shift_focus` | Change topic entirely | `query_history` appended, `retrieved` cleared, new seed search |
| `path_trace` | Find link path between notes | `scope.mode = "path_trace"`, run BFS path finder |
| `export` | Save research artifacts | Generate `.md`, `.base`, `.canvas` files |

## Turn Flow
1. **User Input**: Query or feedback action
2. **State Update**: Modify `session.json` based on action
3. **Retrieve**: Run `obsidian-rag.sh retrieve` or `refine`
4. **Present**: AI shows results with graph metadata (`score`, `depth`, `reason`)
5. **Guide**: AI suggests next actions (narrow, broaden, path-trace, export)
6. **Repeat**: Until user satisfied or max turns reached

## Best Practices
- Always show graph metadata alongside retrieved notes
- Limit turns to 5-7 to prevent context drift
- Clear `retrieved` array on `shift_focus`
- Merge results on `narrow`/`broaden` (deduplicate by `path`)
- Save session state after every turn for crash recovery
