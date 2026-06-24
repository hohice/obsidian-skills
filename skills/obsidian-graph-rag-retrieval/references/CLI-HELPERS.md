# CLI Helpers

## `obsidian-rag.sh`

Vault-scoped Graph RAG helper script. Automates initialization, retrieval, refinement, and session management.

The actual script lives at [`../scripts/obsidian-rag.sh`](../scripts/obsidian-rag.sh). Refer to that file for the latest implementation.

### Usage

```bash
./obsidian-rag.sh {init|retrieve|refine|status} [params]
```

### Commands

| Command | Params | Description |
|---------|--------|-------------|
| `init` | - | Initialize session & `session.json` |
| `retrieve` | `<query>` | Search & score notes for query |
| `refine` | `<focus>` | Update scope/feedback & re-retrieve |
| `status` | - | Show current session state |

### Installation

1. Copy [`scripts/obsidian-rag.sh`](../scripts/obsidian-rag.sh) to your Vault root or a directory in your `PATH`
2. Make it executable:
   ```bash
   chmod +x obsidian-rag.sh
   ```
3. Run from Vault root:
   ```bash
   ./obsidian-rag.sh init
   ```

### Output Format

All commands output JSON for easy parsing by agents.

**Success example (`init`):**
```json
{"status":"success","action":"init","session_id":"rag_1234567890","session_file":"/path/to/.obsidian-rag-session/session.json"}
```

**Error example:**
```json
{"status":"error","message":"No Obsidian Vault detected. Run from Vault root."}
```

### Requirements

- `obsidian` CLI in `PATH` (see the [obsidian-cli](../../obsidian-cli) skill)
- `python3` for JSON manipulation
- Session state is stored in `.obsidian-rag-session/` (add this folder to `.gitignore`)
