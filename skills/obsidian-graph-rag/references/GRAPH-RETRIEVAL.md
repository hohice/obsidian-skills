# Graph Retrieval Strategies

## Scoring Formula
Relevance is calculated using a weighted heuristic score combining graph topology and text relevance:

```
score = (outlinks * 2) + (backlinks * 3) + (tagOverlap * 5) + textScore
```

| Component | Weight | Description |
|-----------|--------|-------------|
| `outlinks` | 2 | Number of wikilinks pointing out from the note (knowledge hub) |
| `backlinks` | 3 | Number of notes linking to this note (core concept) |
| `tagOverlap` | 5 | Number of tags matching query keywords |
| `textScore` | 1 | Raw keyword frequency in note content (BM25 alternative) |

## Traversal Strategies

### 1. BFS Expansion (1-3 Hops)
```javascript
async function expandGraph(seedFiles, maxDepth = 2) {
  const visited = new Set(seedFiles.map(f => f.path));
  const queue = seedFiles.map(f => ({ file: f, depth: 0 }));
  const results = [];
  
  while (queue.length > 0) {
    const { file, depth } = queue.shift();
    if (depth >= maxDepth) continue;
    
    const cache = app.metadataCache.getFileCache(file);
    const links = cache?.links || [];
    
    for (const link of links) {
      const linked = app.metadataCache.getFirstLinkpathDest(link.link, '');
      if (linked && !visited.has(linked.path)) {
        visited.add(linked.path);
        results.push({ file: linked, depth: depth + 1, via: file.basename });
        queue.push({ file: linked, depth: depth + 1 });
      }
    }
  }
  return results;
}
```

### 2. Shortest Path Finding
Finds the shortest link path between two notes using BFS:
```javascript
async function findPath(startName, endName) {
  const startFile = app.metadataCache.getFirstLinkpathDest(startName, '');
  const endFile = app.metadataCache.getFirstLinkpathDest(endName, '');
  if (!startFile || !endFile) return null;
  
  const queue = [[startFile]];
  const visited = new Set([startFile.path]);
  
  while (queue.length > 0) {
    const path = queue.shift();
    const current = path[path.length - 1];
    
    if (current.path === endFile.path) {
      return path.map(f => f.basename);
    }
    
    const cache = app.metadataCache.getFileCache(current);
    for (const link of (cache.links || [])) {
      const next = app.metadataCache.getFirstLinkpathDest(link.link, '');
      if (next && !visited.has(next.path)) {
        visited.add(next.path);
        queue.push([...path, next]);
      }
    }
  }
  return null; // No path found
}
```

## Performance Guards
- **Depth Limit**: Hard limit at 3 hops to prevent graph explosion
- **Result Cap**: Max 10 results per retrieval turn
- **Vault Size Check**: If `app.vault.getFiles().length > 5000`, recommend `scope.folders` restriction
- **Timeout**: CLI `eval` commands should complete within 5 seconds

## Filtering
- **Tags**: `scope.tags` array, notes must contain at least one tag
- **Folders**: `scope.folders` array, notes must be in specified paths
- **Exclude**: `feedback.exclude` array, notes containing these tags/keywords are filtered out
- **Score Threshold**: `scope.score_threshold`, only notes with `score >= threshold` are kept
