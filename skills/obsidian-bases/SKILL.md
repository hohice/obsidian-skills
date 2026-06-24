---
name: obsidian-bases
description: Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian.
metadata:
  version: 1.2.0
---

# Obsidian Bases Skill

## Workflow

1. **Create the file**: Create a `.base` file in the vault with valid YAML content
2. **Define scope**: Add `filters` to select which notes appear (by tag, folder, property, or date)
3. **Add formulas** (optional): Define computed properties in the `formulas` section
4. **Configure views**: Add one or more views (`table`, `cards`, `list`, or `map`) with `order` specifying which properties to display
5. **Validate**: Verify the file is valid YAML with no syntax errors. Check that all referenced properties and formulas exist. Common issues: unquoted strings containing special YAML characters, mismatched quotes in formula expressions, referencing `formula.X` without defining `X` in `formulas`
6. **Test in Obsidian**: Open the `.base` file in Obsidian to confirm the view renders correctly. If it shows a YAML error, check quoting rules below

## Design Frontmatter for Bases

Bases rely on consistent frontmatter across your notes. When creating notes with [`obsidian-markdown`](../obsidian-markdown/SKILL.md), use stable property names and types so filters and formulas work reliably.

Recommended conventions:

| Property | Type | Example use in Bases |
|----------|------|---------------------|
| `tags` | list | `filters: tag = #project` |
| `status` | text | `filters: status = "in-progress"` |
| `date` | date | `filters: date >= 2024-01-01` |
| `priority` | text | `formulas: priority_score` |
| `source` | text | display original document URL |

See [`obsidian-markdown`](../obsidian-markdown/SKILL.md) for frontmatter syntax, templates, and the Quality Checklist.

## Schema

Base files use the `.base` extension and contain valid YAML.

```yaml
# Global filters apply to ALL views in the base
filters:
  # Can be a single filter string
  # OR a recursive filter object with and/or/not
  and: []
  or: []
  not: []

# Define formula properties that can be used across all views
formulas:
  formula_name: 'expression'

# Configure display names and settings for properties
properties:
  property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"
  file.ext:
    displayName: "Extension"

# Define custom summary formulas
summaries:
  custom_summary_name: 'values.mean().round(3)'

# Define one or more views
views:
  - type: table | cards | list | map
    name: "View Name"
    limit: 10                    # Optional: limit results
    groupBy:                     # Optional: group results
      property: property_name
      direction: ASC | DESC
    filters:                     # View-specific filters
      and: []
    order:                       # Properties to display in order
      - file.name
      - property_name
      - formula.formula_name
    summaries:                   # Map properties to summary formulas
      property_name: Average
```

## Filter Syntax

Filters narrow down results. They can be applied globally or per-view.

### Filter Structure

```yaml
# Single filter
filters: 'status == "done"'

# AND - all conditions must be true
filters:
  and:
    - 'status == "done"'
    - 'priority > 3'

# OR - any condition can be true
filters:
  or:
    - 'file.hasTag("book")'
    - 'file.hasTag("article")'

# NOT - exclude matching items
filters:
  not:
    - 'file.hasTag("archived")'

# Nested filters
filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.hasTag("book")
        - file.inFolder("Required Reading")
```

### Filter Operators

See [references/FILTER_OPERATORS.md](references/FILTER_OPERATORS.md) for the full operator reference.

## Properties

### Three Types of Properties

1. **Note properties** - From frontmatter: `note.author` or just `author`
2. **File properties** - File metadata: `file.name`, `file.mtime`, etc.
3. **Formula properties** - Computed values: `formula.my_formula`

### File Properties Reference

See [references/FILE_PROPERTIES.md](references/FILE_PROPERTIES.md) for the full list of available file metadata properties.

### The `this` Keyword

- In main content area: refers to the base file itself
- When embedded: refers to the embedding file
- In sidebar: refers to the active file in main content

## Formula Syntax

Formulas compute values from properties. Defined in the `formulas` section.

```yaml
formulas:
  # Simple arithmetic
  total: "price * quantity"

  # Conditional logic
  status_icon: 'if(done, "✅", "⏳")'

  # String formatting
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'

  # Date formatting
  created: 'file.ctime.format("YYYY-MM-DD")'

  # Calculate days since created (use .days for Duration)
  days_old: '(now() - file.ctime).days'

  # Calculate days until due date
  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
```

## Key Functions

Most commonly used functions. For the complete reference of all types (Date, String, Number, List, File, Link, Object, RegExp), see [FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md).

| Function | Signature | Description |
|----------|-----------|-------------|
| `date()` | `date(string): date` | Parse string to date (`YYYY-MM-DD HH:mm:ss`) |
| `now()` | `now(): date` | Current date and time |
| `today()` | `today(): date` | Current date (time = 00:00:00) |
| `if()` | `if(condition, trueResult, falseResult?)` | Conditional |
| `duration()` | `duration(string): duration` | Parse duration string |
| `file()` | `file(path): file` | Get file object |
| `link()` | `link(path, display?): Link` | Create a link |

### Duration Type

When subtracting two dates, the result is a **Duration** type (not a number).

**Duration Fields:** `duration.days`, `duration.hours`, `duration.minutes`, `duration.seconds`, `duration.milliseconds`

**IMPORTANT:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` directly. Access a numeric field first (like `.days`), then apply number functions.

```yaml
# CORRECT: Calculate days between dates
"(date(due_date) - today()).days"                    # Returns number of days
"(now() - file.ctime).days"                          # Days since created
"(date(due_date) - today()).days.round(0)"           # Rounded days

# WRONG - will cause error:
# "((date(due) - today()) / 86400000).round(0)"      # Duration doesn't support division then round
```

### Date Arithmetic

```yaml
# Duration units: y/year/years, M/month/months, d/day/days,
#                 w/week/weeks, h/hour/hours, m/minute/minutes, s/second/seconds
"now() + \"1 day\""       # Tomorrow
"today() + \"7d\""        # A week from today
"now() - file.ctime"      # Returns Duration
"(now() - file.ctime).days"  # Get days as number
```

## View Types

### Table View

```yaml
views:
  - type: table
    name: "My Table"
    order:
      - file.name
      - status
      - due_date
    summaries:
      price: Sum
      count: Average
```

### Cards View

```yaml
views:
  - type: cards
    name: "Gallery"
    order:
      - file.name
      - cover_image
      - description
```

### List View

```yaml
views:
  - type: list
    name: "Simple List"
    order:
      - file.name
      - status
```

### Map View

Requires latitude/longitude properties and the [Maps community plugin](https://github.com/esm7/obsidian-map-view).

Store coordinates in frontmatter:

```yaml
---
location: [40.7128, -74.0060]
city: "New York"
---
```

Then configure a map view:

```yaml
views:
  - type: map
    name: "Locations"
    order:
      - file.name
      - city
    # The Maps plugin uses the `location` property by default
```

## Default Summary Formulas

See [references/SUMMARY_FORMULAS.md](references/SUMMARY_FORMULAS.md) for the full list of built-in summaries.

## Complete Examples

### Task Tracker Base

```yaml
filters:
  and:
    - file.hasTag("task")
    - 'file.ext == "md"'

formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
  priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'

properties:
  status:
    displayName: Status
  formula.days_until_due:
    displayName: "Days Until Due"
  formula.priority_label:
    displayName: Priority

views:
  - type: table
    name: "Active Tasks"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - formula.priority_label
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
    summaries:
      formula.days_until_due: Average

  - type: table
    name: "Completed"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - completed_date
```

### Reading List Base

```yaml
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")

formulas:
  reading_time: 'if(pages, (pages * 2).toString() + " min", "")'
  status_icon: 'if(status == "reading", "📖", if(status == "done", "✅", "📚"))'
  year_read: 'if(finished_date, date(finished_date).year, "")'

properties:
  author:
    displayName: Author
  formula.status_icon:
    displayName: ""
  formula.reading_time:
    displayName: "Est. Time"

views:
  - type: cards
    name: "Library"
    order:
      - cover
      - file.name
      - author
      - formula.status_icon
    filters:
      not:
        - 'status == "dropped"'

  - type: table
    name: "Reading List"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - pages
      - formula.reading_time
```

### Daily Notes Index

```yaml
filters:
  and:
    - file.inFolder("Daily Notes")
    - '/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)'

formulas:
  word_estimate: '(file.size / 5).round(0)'
  day_of_week: 'date(file.basename).format("dddd")'

properties:
  formula.day_of_week:
    displayName: "Day"
  formula.word_estimate:
    displayName: "~Words"

views:
  - type: table
    name: "Recent Notes"
    limit: 30
    order:
      - file.name
      - formula.day_of_week
      - formula.word_estimate
      - file.mtime
```

### Retrieval Tracking Base (RAG)

Use this base to track candidates retrieved by [`obsidian-graph-rag-retrieval`](../obsidian-graph-rag-retrieval/SKILL.md). Store retrieval results in `.obsidian-rag-session/` with properties `score`, `depth`, and `reason`.

```yaml
filters:
  and:
    - file.inFolder(".obsidian-rag-session")
    - 'file.ext == "md"'

formulas:
  confidence_label: 'if(score >= 12, "🟢 High", if(score >= 6, "🟡 Medium", "🔴 Low"))'
  depth_badge: 'if(depth == 1, "1 hop", if(depth == 2, "2 hops", "3 hops+"))'

properties:
  formula.confidence_label:
    displayName: "Confidence"
  formula.depth_badge:
    displayName: "Depth"

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

See [`obsidian-graph-rag-retrieval/references/EXPORT-TEMPLATES.md`](../obsidian-graph-rag-retrieval/references/EXPORT-TEMPLATES.md) for the companion `.base` template.

## Embedding Bases

Embed in Markdown files:

```markdown
![[MyBase.base]]

<!-- Specific view -->
![[MyBase.base#View Name]]
```

## Bases vs Dataview

Both tools create dynamic views from your notes. Choose based on your needs:

| | `obsidian-bases` | Dataview (community plugin) |
|---|---|---|
| **Availability** | Built into Obsidian | Community plugin |
| **Configuration** | YAML in `.base` files | DataviewJS or DQL inline queries |
| **Best for** | Stable, reusable views; embedding in notes | Ad-hoc complex queries; scripting |
| **Embedding** | `![[MyBase.base#View Name]]` | Dataview blocks inside notes |
| **Power** | Filters, formulas, summaries, grouping | Full JavaScript (DataviewJS), transclusion |
| **Portability** | Works in any Obsidian install | Requires Dataview plugin |

Use Bases when you want a reusable database view that feels native to Obsidian. Use Dataview when you need complex logic or one-off queries that Bases cannot express.

## Performance Tips

- **Always filter**: Avoid loading the entire vault. Use `file.inFolder()`, `file.hasTag()`, or property filters to limit scope.
- **Limit views**: Add `limit` to large views, especially when embedding bases in other notes.
- **Prefer simple formulas**: Nested formulas and date arithmetic on many rows can slow rendering. Cache results in frontmatter when possible.
- **Index tags and properties**: Use consistent tags and property names so Bases can rely on Obsidian's metadata cache.
- **Avoid deep nesting**: More than 2-3 levels of nested `and`/`or` filters become hard to maintain and slower to evaluate.

## YAML Quoting Rules

- Use single quotes for formulas containing double quotes: `'if(done, "Yes", "No")'`
- Use double quotes for simple strings: `"My View Name"`
- Escape nested quotes properly in complex expressions

## Troubleshooting

See [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for common YAML and formula errors.

## References

- [Bases Syntax](https://help.obsidian.md/bases/syntax)
- [Functions](https://help.obsidian.md/bases/functions)
- [Views](https://help.obsidian.md/bases/views)
- [Formulas](https://help.obsidian.md/formulas)
- [Complete Functions Reference](references/FUNCTIONS_REFERENCE.md)
- [File Properties Reference](references/FILE_PROPERTIES.md)
- [Filter Operators](references/FILTER_OPERATORS.md)
- [Summary Formulas](references/SUMMARY_FORMULAS.md)
- [Troubleshooting](references/TROUBLESHOOTING.md)

This skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate with [`skill-spec`](../skill-spec/scripts/validate.py).
