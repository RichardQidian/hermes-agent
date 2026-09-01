# Official Spec Kit Integration & Distribution

## A. Official CLI Integration (optional)

The [github/spec-kit](https://github.com/github/spec-kit) project ships its own CLI
which installs `speckit-*` skills globally into `~/.hermes/skills/`:

```bash
# 1. Install the CLI (once per machine)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.0.2

# 2. Initialize a project with the Hermes integration (installs 10 speckit-* skills globally)
cd <project> && specify init --here --force --non-interactive --integration hermes

# Uninstall (removes all global speckit-* skills + project marker)
specify integration uninstall
```

Official skills installed: `speckit-constitution`, `speckit-specify`, `speckit-clarify`,
`speckit-plan`, `speckit-tasks`, `speckit-implement`, `speckit-converge`,
`speckit-analyze`, `speckit-checklist`, `speckit-taskstoissues`.

**Mode switching**:

- **Mode A (this skill, zero dependency)**: run the workflow steps from
  `spec-kit-sdd/SKILL.md` directly, using `templates/` bundled in this skill.
- **Mode B (official CLI)**: if the project has `.specify/` with templates/scripts
  (from `specify init`), prefer the project's own `.specify/scripts/*.sh` resolvers
  and templates; this skill's templates are byte-compatible fallbacks.

Both modes write the same artifact layout (`specs/NNN-name/`, `.specify/feature.json`,
`.specify/memory/constitution.md`), so they are interchangeable mid-project.

## B. Extension Hooks

Projects initialized with official spec-kit may register extensions
(`.specify/extensions.yml`): `git` (branching), `bug` (triage), `assess`, `agent-context`.
At each step boundary, check for `hooks.before_<step>` / `hooks.after_<step>`:

- Mandatory hook (`optional: false`) → MUST execute, wait for result
- Optional hook (`optional: true`) → offer to the user

## C. Distributing This Skill to Other Hermes Instances

The skill is fully self-contained (SKILL.md + templates/ + references/). Distribute via:

### 1. Copy the directory (simplest)

```bash
# On the source machine
tar czf spec-kit-sdd.tar.gz -C ~/.hermes/skills/software-development spec-kit-sdd
# On the target machine
mkdir -p ~/.hermes/skills/software-development && tar xzf spec-kit-sdd.tar.gz -C ~/.hermes/skills/software-development
# Then reload: /reload-skills (or start a new session)
```

### 2. Install from a URL (hub-style)

Host `SKILL.md` (plus templates/ + references/ alongside) at any public URL, then:

```bash
hermes skills install https://example.com/path/to/SKILL.md
# NOTE: hermes skills install fetches SKILL.md; companion files (templates/, references/)
# must be reachable relative to it or vendored into a single-file skill.
```

### 3. Publish to the skills hub

```bash
hermes skills publish ~/.hermes/skills/software-development/spec-kit-sdd
# Requires hub account; makes the skill publicly installable via `hermes skills install spec-kit-sdd`
```

### 4. Git repo as a skill source (team-internal)

```bash
hermes skills tap add <owner>/<repo>     # add repo as skill source
hermes skills install spec-kit-sdd       # install from the tap
```

## D. Versioning This Skill

- 1.x: workflow + templates compatible with official spec-kit 1.0.x layout
- Bump MAJOR if artifact layout changes incompatibly; MINOR for new steps/options;
  PATCH for clarifications
- Keep `templates/` in sync with upstream `github/spec-kit` `templates/` directory
  (currently 1.0.2)
