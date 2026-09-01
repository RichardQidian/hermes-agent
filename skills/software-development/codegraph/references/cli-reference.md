# CodeGraph CLI Reference (v1.6.0)

Source: [colbymchenry/codegraph README](https://github.com/colbymchenry/codegraph) (MIT).

## Commands

```bash
codegraph                         # Run interactive installer
codegraph install                 # Run installer (explicit) — wires agents, does NOT index
codegraph uninstall               # Remove from agents AND CLI (--keep-cli = configs only)
codegraph init [path]             # Initialize a project + build its graph (one step)
codegraph uninit [path]           # Remove CodeGraph from a project (--force)
codegraph index [path]            # Full re-index (--force, --quiet)
codegraph sync [path]             # Incremental update (manual; auto-sync is default)
codegraph status [path]           # Index stats + pending syncs
codegraph ui [path]               # Browser viewer http://127.0.0.1:4747 (alias: web; --port, --no-open, --read-only)
codegraph unlock [path]           # Remove a stale lock blocking indexing
codegraph query <search>          # Search symbols (--kind, --limit, --json)
codegraph explore <query>         # One-shot: relevant source + call paths (same as MCP tool)
codegraph node <symbol|file>      # One symbol's source + callers, or read a file with line numbers
codegraph files [path]            # File structure (--format, --filter, --max-depth, --json)
codegraph callers <symbol>        # Who calls a function/method (--limit, --json)
codegraph callees <symbol>        # What a function/method calls (--limit, --json)
codegraph impact <symbol>         # Blast radius of changing a symbol (--depth, --json)
codegraph affected [files...]     # Test files affected by changes (see below)
codegraph daemon                  # Manage background watcher daemons
codegraph telemetry [on|off]      # Anonymous usage telemetry (disable: CODEGRAPH_TELEMETRY=0)
codegraph upgrade [version]       # Update in place (--check, --force)
codegraph version                 # Installed version (-v, --version)
codegraph help [command]          # Help for one command
```

## `codegraph affected` (affected-test detection)

Traces import dependencies transitively to find test files affected by changed source files.

```bash
codegraph affected src/utils.ts src/api.ts
git diff --name-only | codegraph affected --stdin          # pipe from git diff
codegraph affected src/auth.ts --filter "e2e/*"            # custom test glob
```

| Option | Description | Default |
|--------|-------------|---------|
| `--stdin` | Read file list from stdin | false |
| `-d, --depth <n>` | Max dependency traversal depth | 5 |
| `-f, --filter <glob>` | Custom glob to identify test files | auto-detect |
| `-j, --json` | JSON output | false |
| `-q, --quiet` | File paths only | false |

CI example:

```bash
AFFECTED=$(git diff --name-only HEAD | codegraph affected --stdin --quiet)
if [ -n "$AFFECTED" ]; then npx vitest run $AFFECTED; fi
```

## Installer flags (`codegraph install`)

| Flag | Values | Default |
|------|--------|---------|
| `--target` | `auto`, `all`, `none`, csv (`claude,cursor,hermes,...`) | prompt |
| `--location` | `global`, `local` | prompt |
| `--yes` | (boolean) | prompt every step |
| `--init` | (boolean) also run `codegraph init` in current dir | — |
| `--no-permissions` | skip Claude auto-allow list | permissions on |
| `--print-config <id>` | dump snippet for one agent, no writes | — |

Install env vars: `CODEGRAPH_VERSION` (pin tag), `CODEGRAPH_INSTALL_DIR` (default `~/.codegraph`), `CODEGRAPH_BIN_DIR` (default `~/.local/bin`).

## MCP Tools

Default surface: **one tool** — `codegraph_explore` (verbatim source + call paths + blast radius in one call). Hidden-but-functional: `codegraph_node`, `codegraph_search`, `codegraph_callers`, `codegraph_callees`, `codegraph_impact`, `codegraph_files`, `codegraph_status`. Re-enable via `CODEGRAPH_MCP_TOOLS=explore,node,search,callers`.

## Internals (quick facts)

- Rust kernel + tree-sitter; 20+ languages; SQLite (`.codegraph/codegraph.db`, FTS5)
- Auto-sync: native OS watcher, 2s debounce (`CODEGRAPH_WATCH_DEBOUNCE_MS`, clamp 100ms–60s)
- 100% local, no API keys, no telemetry of code (anonymous stats only)
- Verified at: `codegraph status`
