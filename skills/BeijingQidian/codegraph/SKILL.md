---
name: codegraph
description: "Use when exploring code: codegraph knowledge-graph queries."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [codegraph, code-intelligence, knowledge-graph, mcp, exploration]
    related_skills: [spec-kit-sdd, code-audit-and-review, debugging]
---

# CodeGraph — Semantic Code Intelligence

## Overview

[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) (MIT, ~69k stars) is a **100% local code knowledge graph** for AI coding agents. A native **Rust kernel** parses source with tree-sitter (20+ languages), extracts symbols + edges (calls, imports, extends, implements), stores them in a local SQLite DB (`.codegraph/codegraph.db`, FTS5 search), and **auto-syncs on every file change** (native OS watcher, 2s debounce). It officially supports **Hermes Agent** (auto-detected by `codegraph install`).

**Why it beats grep loops**: one query returns verbatim source of all relevant symbols + the call paths between them + a blast-radius summary — including dynamic-dispatch hops (callbacks, React re-render, interface→impl) that grep cannot follow.

## When to Use

- Understanding an unfamiliar / large codebase: "how does X work", "how does X reach Y"
- Cross-file dependency questions: "who calls this function", "what does this method call"
- Change-impact analysis BEFORE editing: "what breaks if I change this symbol"
- Finding affected tests: `codegraph affected` after a diff
- Code review / audit: survey an area, trace request flows end-to-end
- Answering structural questions directly (the index already did the grep work — do not re-verify with grep)

Do NOT use for: prose questions about a single small file (read it directly), non-code questions.

## Setup

### 1. Install the CLI (once per machine)

```bash
# macOS / Linux (no Node required — self-contained bundle)
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Or with Node: npm install -g @colbymchenry/codegraph
```

Install takes a while (downloads a vendored Node runtime + Rust kernel bundle). Verify: `codegraph version`. Upgrade any time: `codegraph upgrade` (or `codegraph upgrade <version>` to pin).

### 2. Wire up Hermes (MCP)

```bash
codegraph install --target=hermes --yes        # non-interactive, only Hermes
# or plain `codegraph install` → pick Hermes from the detected-agent list
```

What it does: writes the CodeGraph MCP server entry into Hermes' MCP config (stdio: `codegraph serve --mcp`) and appends a marker-fenced CodeGraph section to the project `AGENTS.md` (so subagents / non-MCP harnesses learn the `codegraph explore` CLI). **It does NOT index any code** — that's the separate `codegraph init` per project.

Inspect before writing: `codegraph install --print-config hermes` (prints snippet, no file writes).

Manual alternative (if you prefer not to run the installer): add the MCP server entry to Hermes config.yaml (top-level `mcp_servers` key — Hermes' canonical key, confirmed in `hermes_cli/config.py`):

```yaml
mcp_servers:
  codegraph:
    command: codegraph
    args: ["serve", "--mcp"]
    timeout: 120
    connect_timeout: 60
    enabled: true
```

(CodeGraph's own `codegraph install --print-config hermes` emits exactly this shape. Optionally also add `mcp-codegraph` to `platform_toolsets.cli`.)

**Restart Hermes** (gateway `/restart`, or new CLI session) for the MCP server to load. Verify with `hermes mcp list` / `hermes mcp test codegraph`.

### 3. Initialize each project

```bash
cd your-project
codegraph init          # creates .codegraph/ + builds full graph in one step
```

Auto-sync is on by default — the graph stays fresh as code changes. Verify with `codegraph status` (shows stats + any `### Pending sync:` section). Remove from a project: `codegraph uninit`.

## Usage

### Via MCP (main path)

The MCP server exposes one default tool — **`codegraph_explore`** — designed to answer almost anything in one call: name a file/symbol, describe a flow ("how does X reach Y"), or survey an area; returns verbatim source grouped by file + call paths + blast-radius summary. Other tools (`codegraph_node`, `codegraph_search`, `codegraph_callers`, `codegraph_callees`, `codegraph_impact`, `codegraph_files`, `codegraph_status`) stay functional but unlisted by default; re-enable via `CODEGRAPH_MCP_TOOLS=explore,node,search,callers` env var.

Trust the results — the returned source is already read; don't re-verify with grep (a staleness banner `⚠️` after edits means: read that file directly for live content).

### Via CLI (same power, no MCP)

```bash
codegraph explore <query>     # one-shot: relevant source + call paths (same as MCP tool)
codegraph node <symbol|file>  # one symbol's source + callers, or read a file with line numbers
codegraph query <search>      # search symbols (--kind, --limit, --json)
codegraph callers <symbol>    # who calls it (--limit, --json)
codegraph callees <symbol>    # what it calls (--limit, --json)
codegraph impact <symbol>     # blast radius of changing a symbol (--depth, --json)
codegraph affected [files...] # which test files are affected by changed files
codegraph files [path]        # file structure (--filter, --max-depth, --json)
codegraph ui [path]           # browser viewer at http://127.0.0.1:4747 (--read-only)
codegraph status [path]       # index stats + pending syncs
```

`affected` CI pattern:

```bash
git diff --name-only HEAD | codegraph affected --stdin --quiet   # list affected test files
```

## Maintenance

```bash
codegraph upgrade            # update in place (--check to see if update available)
codegraph uninstall          # remove from agents AND CLI (--keep-cli = configs only)
codegraph uninit [path]      # remove CodeGraph from a project (--force)
codegraph daemon             # manage background watcher daemons
codegraph telemetry [on|off] # anonymous usage telemetry
codegraph unlock [path]      # remove a stale lock blocking indexing
codegraph index [path]       # full re-index (--force), sync [path] for incremental
```

## Common Pitfalls

- **Install ≠ wired ≠ indexed**: three separate steps (CLI install → `codegraph install` wires the agent → `codegraph init` builds each project's index). Missing the last one is the #1 "nothing happens" cause.
- **MCP not loaded after install**: restart Hermes (gateway `/restart` or new session). `hermes mcp list` to confirm.
- **New project, no index**: without `.codegraph/`, tools return guidance to use built-in tools — indexing stays your decision. Run `codegraph init` in the project.
- **Sandboxed envs / CI**: file watcher may be disabled (`CODEGRAPH_NO_DAEMON=1`) → run `codegraph sync` manually before scripting against the index.
- **Staleness banner**: after agent edits, a `⚠️` banner means the file changed within the debounce window — `Read` it directly instead of trusting graph output for that file.
- **Don't re-grep**: the graph already resolved calls/imports/extends. Re-verifying with grep wastes context; trust `codegraph_explore`.
- **Config writes are global**: `codegraph install` (global location) writes Hermes MCP config + AGENTS.md marker — review what `--print-config hermes` shows before running; `uninstall` removes cleanly.

## Verification Checklist

- [ ] `codegraph version` prints a version
- [ ] `hermes mcp list` shows `codegraph`; `hermes mcp test codegraph` succeeds
- [ ] Project has `.codegraph/` after `codegraph init`; `codegraph status` shows symbol/file counts
- [ ] `codegraph explore "how does <feature> work"` returns source + call paths in an indexed project
- [ ] `codegraph callers <symbol>` / `codegraph impact <symbol>` return meaningful results
- [ ] `codegraph affected` lists expected test files after a change
- [ ] After editing a file, `codegraph status` shows no pending sync (auto-sync working) or manual `codegraph sync` applied

## Relationship to Other Skills

- Use with **spec-kit-sdd** plan step: `codegraph explore` grounds design docs in real code (which classes exist, how flows reach the DB) instead of guesses.
- Use with **code-audit-and-review** / debugging: trace call chains and blast radius before changing anything.
