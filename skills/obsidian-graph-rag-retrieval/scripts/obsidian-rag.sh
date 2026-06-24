#!/bin/bash
# obsidian-rag.sh - Vault-scoped Graph RAG Helper
# Usage: ./obsidian-rag.sh <action> [params]

set -euo pipefail

ACTION="${1:-help}"
SESSION_DIR=".obsidian-rag-session"

# Output helpers ---------------------------------------------------------------
error_exit() {
  python3 - "$1" <<'PY'
import json, sys
print(json.dumps({"status": "error", "message": sys.argv[1]}))
PY
  exit 1
} >&2

# Vault detection --------------------------------------------------------------
detect_vault_root() {
  local dir="$(pwd)"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/.obsidian" ]]; then
      printf '%s' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  error_exit "No Obsidian Vault detected. Run from Vault root."
}

# Main commands ----------------------------------------------------------------
case $ACTION in
  help|--help|-h)
    cat <<EOF
Usage: obsidian-rag.sh {init|retrieve|refine|status} [params]

Commands:
  init                 Initialize a new RAG session
  retrieve <query>     Search and score notes for a query
  refine <focus>       Narrow scope to a focus topic
  status               Show current session state

All commands output JSON for easy parsing by agents.
EOF
    exit 0
    ;;
esac

VAULT_ROOT="$(detect_vault_root)"
mkdir -p "$VAULT_ROOT/$SESSION_DIR"

case $ACTION in
  init)
    SESSION_ID="rag_$(date +%s)"
    SESSION_FILE="$VAULT_ROOT/$SESSION_DIR/session.json"
    cat > "$SESSION_FILE" <<EOF
{
  "session_id": "$SESSION_ID",
  "turn": 0,
  "query_history": [],
  "retrieved": [],
  "scope": { "depth": 1, "mode": "explore", "tags": [], "folders": [], "score_threshold": 5 },
  "feedback": {}
}
EOF
    python3 - "$SESSION_ID" "$SESSION_FILE" <<'PY'
import json, sys
print(json.dumps({
    "status": "success",
    "action": "init",
    "session_id": sys.argv[1],
    "session_file": sys.argv[2]
}))
PY
    ;;

  retrieve)
    QUERY="${2:-}"
    [[ -z "$QUERY" ]] && error_exit "Usage: retrieve <query>"

    QUERY_FILE="$VAULT_ROOT/$SESSION_DIR/query.txt"
    SEARCH_FILE="$VAULT_ROOT/$SESSION_DIR/search.json"
    RESULTS_FILE="$VAULT_ROOT/$SESSION_DIR/results.json"
    EVAL_JS_FILE="$VAULT_ROOT/$SESSION_DIR/eval.js"

    printf '%s' "$QUERY" > "$QUERY_FILE"

    # 1. Run obsidian search and capture output
    if ! obsidian search query="$QUERY" limit=20 > "$SEARCH_FILE" 2>/dev/null; then
      error_exit "obsidian search failed (is Obsidian running and the CLI installed?)"
    fi

    # 2. Validate search output is valid JSON
    if ! python3 -c "import json; json.load(open('$SEARCH_FILE'))" 2>/dev/null; then
      error_exit "obsidian search returned invalid JSON"
    fi

    # 3. Build eval JS that reads inputs from files (no shell interpolation into code)
    python3 - "$QUERY_FILE" "$SEARCH_FILE" "$RESULTS_FILE" "$EVAL_JS_FILE" <<'PY'
import json
import sys

query_file, search_file, results_file, output_file = sys.argv[1:5]

js_template = '''
const queryPath = %(query_file)s;
const searchPath = %(search_file)s;
const resultsPath = %(results_file)s;

const query = await app.vault.adapter.read(queryPath);
const files = JSON.parse(await app.vault.adapter.read(searchPath));

async function graphScore(filePath) {
  const file = app.metadataCache.getFirstLinkpathDest(filePath, '');
  if (!file) return null;
  const cache = app.metadataCache.getFileCache(file);
  const content = await app.vault.read(file);
  const outlinks = cache.links?.length || 0;
  const backlinks = app.metadataCache.getBacklinksForFile(file).keys().size;
  const tags = cache.frontmatter?.tags || [];
  const tagOverlap = tags.filter(t => query.toLowerCase().includes(t.toLowerCase())).length;
  const escapedQuery = query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  const textScore = (content.match(new RegExp(escapedQuery, 'gi')) || []).length;
  return {
    path: file.path,
    score: outlinks*2 + backlinks*3 + tagOverlap*5 + textScore,
    depth: 1,
    reason: `outlinks=${outlinks}, backlinks=${backlinks}, tagOverlap=${tagOverlap}, textScore=${textScore}`,
    metadata: { outlinks, backlinks, tagOverlap, textScore }
  };
}

const results = await Promise.all(files.map(async f => await graphScore(f)))
  .then(r => r.filter(x => x !== null).sort((a, b) => b.score - a.score));
const topResults = results.slice(0, 10);
await app.vault.adapter.write(resultsPath, JSON.stringify(topResults, null, 2));
console.log(JSON.stringify(topResults));
'''

js = js_template % {
    "query_file": json.dumps(query_file),
    "search_file": json.dumps(search_file),
    "results_file": json.dumps(results_file),
}

with open(output_file, "w") as f:
    f.write(js.strip())
PY

    # 4. Run obsidian eval and validate output
    if ! obsidian eval code="$(cat "$EVAL_JS_FILE")" > "$RESULTS_FILE" 2>/dev/null; then
      error_exit "obsidian eval failed (is Obsidian running?)"
    fi

    if ! python3 -c "import json; json.load(open('$RESULTS_FILE'))" 2>/dev/null; then
      error_exit "obsidian eval returned invalid JSON"
    fi

    # 5. Update session state
    python3 - "$VAULT_ROOT" "$QUERY" "$RESULTS_FILE" <<'PY'
import json
import sys
vault_root, query, results_file = sys.argv[1:4]
session_file = f"{vault_root}/.obsidian-rag-session/session.json"
with open(session_file) as f:
    session = json.load(f)
with open(results_file) as f:
    results = json.load(f)
session["query_history"].append(query)
session["turn"] += 1
session["retrieved"] = results
with open(session_file, "w") as f:
    json.dump(session, f, indent=2)
PY

    COUNT=$(python3 -c "import json; print(len(json.load(open('$RESULTS_FILE'))))")
    python3 - "$QUERY" "$RESULTS_FILE" "$COUNT" <<'PY'
import json, sys
print(json.dumps({
    "status": "success",
    "action": "retrieve",
    "query": sys.argv[1],
    "results_file": sys.argv[2],
    "count": int(sys.argv[3])
}))
PY
    ;;

  refine)
    FOCUS="${2:-}"
    [[ -z "$FOCUS" ]] && error_exit "Usage: refine <focus>"

    python3 - "$VAULT_ROOT" "$FOCUS" <<'PY'
import json
import sys
vault_root, focus = sys.argv[1:3]
session_file = f"{vault_root}/.obsidian-rag-session/session.json"
with open(session_file) as f:
    session = json.load(f)
session["feedback"] = {"action": "narrow", "focus": focus}
if focus not in session["scope"]["tags"]:
    session["scope"]["tags"].append(focus)
session["turn"] += 1
with open(session_file, "w") as f:
    json.dump(session, f, indent=2)
print(json.dumps({
    "status": "success",
    "action": "refine",
    "focus": focus,
    "session_file": session_file,
    "turn": session["turn"],
    "tags": session["scope"]["tags"]
}))
PY
    ;;

  status)
    SESSION_FILE="$VAULT_ROOT/$SESSION_DIR/session.json"
    if [[ ! -f "$SESSION_FILE" ]]; then
      error_exit "No active session. Run 'init' first."
    fi
    python3 - "$SESSION_FILE" <<'PY'
import json
import sys
session_file = sys.argv[1]
with open(session_file) as f:
    session = json.load(f)
print(json.dumps({
    "status": "success",
    "action": "status",
    "session_file": session_file,
    "session": session
}))
PY
    ;;

  *)
    error_exit "Unknown action: $ACTION. Run 'obsidian-rag.sh help' for usage."
    ;;
esac
