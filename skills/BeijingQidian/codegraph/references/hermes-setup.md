# CodeGraph × Hermes Agent — Setup Details

Verified against codegraph v1.6.0 + Hermes Agent (config key confirmed in `hermes_cli/config.py:1857`).

## Auto setup (recommended)

```bash
codegraph install --target=hermes --yes        # only Hermes, non-interactive
codegraph install --print-config hermes        # preview snippet, NO writes
```

What `codegraph install` writes for Hermes (confirmed output):

```yaml
# Add to /root/.hermes/config.yaml

mcp_servers:
  codegraph:
    command: codegraph
    args:
      - serve
      - --mcp
    timeout: 120
    connect_timeout: 60
    enabled: true

platform_toolsets:
  cli:
    - hermes-cli
    - mcp-codegraph
```

Notes:
- `mcp_servers` is the top-level canonical key in Hermes config.yaml (NOT `mcp.servers`).
- It also appends a marker-fenced CodeGraph section to the project `AGENTS.md`
  so subagents / non-MCP harnesses learn `codegraph explore`.
- Global install applies to all projects; per-project index still needs `codegraph init`.

## Verify

```bash
hermes mcp list            # shows codegraph
hermes mcp test codegraph  # handshake test
codegraph status           # per-project index stats
```

## Manual config

Edit `~/.hermes/config.yaml` and add the `mcp_servers.codegraph` block above,
then restart Hermes (gateway `/restart` or new CLI session).

## Uninstall

```bash
codegraph uninstall        # removes MCP config + AGENTS.md marker + CLI
# or codegraph uninstall --keep-cli   # keep the CLI, only unwire agents
```

## PATH note

Installer links `~/.local/bin/codegraph`. If `~/.local/bin` is not on PATH,
MCP stdio launch fails — add `export PATH="$HOME/.local/bin:$PATH"` to shell rc,
or symlink into an existing PATH dir.

## Environment knobs

- `CODEGRAPH_MCP_TOOLS=explore,node,search,callers` — re-enable hidden MCP tools
- `CODEGRAPH_WATCH_DEBOUNCE_MS` — watcher debounce (100ms–60s, default 2000)
- `CODEGRAPH_NO_DAEMON=1` — disable watcher (sandboxed envs; then use `codegraph sync`)
- `CODEGRAPH_TELEMETRY=0` — disable anonymous telemetry
