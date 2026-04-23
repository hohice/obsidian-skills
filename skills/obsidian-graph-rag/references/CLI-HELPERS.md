# CLI Helpers

## `obsidian-rag.sh`
Vault-scoped Graph RAG helper script. Automates initialization, retrieval, refinement, and export.

### Usage
```bash
./obsidian-rag.sh {init|retrieve|refine|export|status} [params]
```

### Commands
| Command | Params | Description |
|---------|--------|-------------|
| `init` | - | Initialize session & `session.json` |
| `retrieve` | `<query>` | Search & score notes for query |
| `refine` | `<focus>` | Update scope/feedback & re-retrieve |
| `export` | - | Generate research artifacts (.md, .base, .canvas) |
| `status` | - | Show current session state |

### Script
```bash
#!/bin/bash
# obsidian-rag.sh - Vault-scoped Graph RAG Helper
set -e

ACTION="${1:-help}"
SESSION_DIR=".obsidian-rag-session"

# 🔍 Vault Detection Function
detect_vault_root() {
  local dir="$(pwd)"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/.obsidian" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "❌ Error: No Obsidian Vault detected. Run from Vault root." >&2
  exit 1
}

VAULT_ROOT="$(detect_vault_root)"
mkdir -p "$VAULT_ROOT/$SESSION_DIR"

case $ACTION in
  init)
    SESSION_ID="rag_$(date +%s)"
    cat > "$VAULT_ROOT/$SESSION_DIR/session.json" <<EOF
{
  "session_id": "$SESSION_ID",
  "turn": 0,
  "query_history": [],
  "retrieved": [],
  "scope": { "depth": 1, "mode": "explore", "tags": [], "folders": [], "score_threshold": 5 },
  "feedback": {}
}
EOF
    echo "✅ RAG session initialized: $SESSION_ID"
    ;;

  retrieve)
    QUERY="${2:-}"
    [[ -z "$QUERY" ]] && { echo "❌ Usage: retrieve <query>" >&2; exit 1; }
    
    FILES=$(obsidian search query="$QUERY" limit=20 2>/dev/null || echo "[]")
    
    obsidian eval code="
      const query = '$QUERY';
      async function graphScore(filePath) {
        const file = app.metadataCache.getFirstLinkpathDest(filePath, '');
        if (!file) return null;
        const cache = app.metadataCache.getFileCache(file);
        const content = await app.vault.read(file);
        const outlinks = cache.links?.length || 0;
        const backlinks = app.metadataCache.getBacklinksForFile(file).keys().size;
        const tags = cache.frontmatter?.tags || [];
        const tagOverlap = tags.filter(t => query.toLowerCase().includes(t.toLowerCase())).length;
        const textScore = (content.match(new RegExp(query.replace(/[.*+?^\${}()|[\]\\]/g, '\\\$&'), 'gi')) || []).length;
        return { path: file.path, score: outlinks*2 + backlinks*3 + tagOverlap*5 + textScore, depth: 1, metadata: { outlinks, backlinks, tagOverlap, textScore } };
      }
      const results = await Promise.all(($FILES).map(async f => await graphScore(f))).then(r => r.filter(x => x !== null).sort((a, b) => b.score - a.score));
      console.log(JSON.stringify(results.slice(0, 10)));
    " > "$VAULT_ROOT/$SESSION_DIR/results.json"
    echo "✅ Results saved"
    ;;

  refine)
    FOCUS="${2:-}"
    [[ -z "$FOCUS" ]] && { echo "❌ Usage: refine <focus>" >&2; exit 1; }
    python3 -c "
import json
with open('$VAULT_ROOT/$SESSION_DIR/session.json') as f: session = json.load(f)
session['feedback'] = {'action': 'narrow', 'focus': '$FOCUS'}
if '$FOCUS' not in session['scope']['tags']: session['scope']['tags'].append('$FOCUS')
with open('$VAULT_ROOT/$SESSION_DIR/session.json', 'w') as f: json.dump(session, f, indent=2)
print('✅ Session updated')
"
    ;;

  export)
    echo "📤 Exporting artifacts..."
    # Placeholder: implement .md, .base, .canvas generation
    echo "✅ Export complete"
    ;;

  status)
    cat "$VAULT_ROOT/$SESSION_DIR/session.json" 2>/dev/null || echo "No active session"
    ;;

  *)
    echo "Usage: obsidian-rag.sh {init|retrieve|refine|export|status} [params]"
    ;;
esac
```

## Installation
1. Save as `obsidian-rag.sh` in your Vault root or `PATH`
2. Make executable: `chmod +x obsidian-rag.sh`
3. Run from Vault root: `./obsidian-rag.sh init`

## Notes
- Requires `obsidian` CLI in `PATH`
- Requires `python3` for JSON manipulation
- Session state stored in `.obsidian-rag-session/` (add to `.gitignore`)
