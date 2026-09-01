---
name: spec-kit-sdd
description: "Use when developing features: SDD spec→plan→tasks workflow."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, spec-driven, workflow, planning, spec-kit]
    related_skills: [writing-plans, development-workflow, project-sop]
---

# Spec-Driven Development (SDD) Workflow

## Overview

SDD = **define what to build before building it**. Instead of jumping from a one-line prompt to code, this workflow produces auditable artifacts: constitution (project principles) → feature spec (WHAT/WHY) → implementation plan (HOW) → tasks (executable checklist) → implementation → convergence loop.

This skill is **self-contained**: it carries its own templates (see `templates/`) and works on ANY project, with or without the official `specify-cli`. Output layout is compatible with [github/spec-kit](https://github.com/github/spec-kit) projects, so a project initialized by `specify init --integration hermes` can be driven by this skill interchangeably.

## When to Use

- User asks to build a new feature / module / API / page (anything non-trivial)
- User asks for a plan, design doc, or task breakdown before coding
- Fixing a bug that needs root-cause analysis + verification loop (adapt: use assess → fix → test inside the workflow)
- User says "按流程来" / "先出方案" / "别直接写代码"

Do NOT use for: trivial one-liners, config tweaks, read-only questions.

## Workflow (7 Steps)

Run steps in order. Each step has a required output artifact; do not skip ahead. Steps 2/5 are quality gates; step 7 is the closure loop.

### Step 1 — Constitution

**Purpose**: Establish project principles (one-time, project-level).

1. If `.specify/memory/constitution.md` exists → load it, apply amendments only.
2. Else → create it from `templates/constitution-template.md`, filling placeholders from repo context (README, docs, coding rules).
3. Replace every `[ALL_CAPS_PLACEHOLDER]`; infer values from the repo; use `TODO(FIELD)` only when truly unknown.
4. Principles must be declarative + testable (MUST/SHOULD, no vague "should ideally").
5. Version bump: MAJOR (principle removed/redefined) / MINOR (new principle) / PATCH (wording).
6. Prepend a Sync Impact Report as an HTML comment: version change, modified/added/removed sections.
7. Output: `.specify/memory/constitution.md`. Report version + bump rationale + suggested commit message.

**Scope guard**: ONLY touch the constitution. Feature/code requests in the input must be deferred to a `Next Actions` section (suggest the specify step), never executed.

### Step 2 — Specify *(quality gate)*

**Purpose**: Turn a natural-language feature description into a business-level spec (WHAT + WHY, no HOW).

1. Derive a 2-4 word short name (action-noun, e.g. `user-auth`).
2. Create feature dir: `specs/<NNN>-<short-name>/` (NNN = next sequential 3-digit). Write `.specify/feature.json` = `{"feature_directory": "specs/<dir>"}`.
3. Copy `templates/spec-template.md` → `<dir>/spec.md`; fill all mandatory sections:
   - **User Scenarios & Testing**: prioritized user stories (P1/P2/P3), each with independent test + Given/When/Then acceptance scenarios
   - **Requirements**: FR-00N, each testable; mark genuinely ambiguous choices `[NEEDS CLARIFICATION: ...]` (MAX 3, scope > security > UX > tech)
   - **Success Criteria**: measurable + technology-agnostic (bad: "API < 200ms" → good: "users see results instantly")
   - **Key Entities / Assumptions / Out of Scope** as applicable
4. Write `<dir>/checklists/requirements.md` from `templates/checklist-template.md` (the 18-item spec quality checklist).
5. **Quality gate**: self-validate the spec against the checklist (max 3 fix iterations).
   - `[NEEDS CLARIFICATION]` markers remain → ask the user (present options table, max 3 questions, wait for answers), then update spec.
   - All items pass → proceed.
6. Output: spec.md + checklists/requirements.md + feature.json. Report paths + checklist status.

### Step 3 — Clarify

**Purpose**: De-risk ambiguity BEFORE planning. Only needed when Step 2 surfaced `[NEEDS CLARIFICATION]` or the user asks.

Ask structured questions (max 3, prioritized by scope/security/UX impact). For each: context quote from spec → what we need to know → options table (A/B/C + implications). Wait for answers, update spec + checklist, re-validate.

### Step 4 — Plan

**Purpose**: Technical design — HOW to build it.

1. Copy `templates/plan-template.md` → `<dir>/plan.md`.
2. Fill **Technical Context** from the actual project (language/framework/storage/testing/platform). Mark unknowns `NEEDS CLARIFICATION` — resolve them before continuing.
3. **Constitution Check**: verify the plan against every principle in `.specify/memory/constitution.md`. Unjustified violations = GATE FAIL (stop). Justified → record in Complexity Tracking table.
4. Phase 0 → `<dir>/research.md`: for each unknown/dependency/integration, record `Decision / Rationale / Alternatives considered`. Ground decisions in real repo inspection (grep actual code, check real schema), not guesses.
5. Phase 1 → `<dir>/data-model.md` (entities, fields, relationships, state transitions, migration SQL sketch), `<dir>/contracts/` (API/interface contracts — new + changed fields, compatibility notes; skip if purely internal), `<dir>/quickstart.md` (runnable end-to-end validation scenarios with real commands + expected outcomes).
6. Re-run Constitution Check post-design.
7. Output: plan.md + research.md + data-model.md + contracts/* + quickstart.md.

### Step 5 — Tasks

**Purpose**: Convert design into an executable checklist.

Copy `templates/tasks-template.md` → `<dir>/tasks.md`. Organize tasks **by user story** (from spec) so each story is independently implementable + testable:

```
- [ ] T001 Setup task (no story label)
- [ ] T005 [P] Foundational task (no story label)   # [P] = parallelizable
- [ ] T012 [P] [US1] Implement X in <exact file path>
```

- Phase 1 Setup → Phase 2 Foundational (blocks everything) → Phase 3+ one phase per user story (P1 first = MVP) → final Polish phase
- Each user story phase: Goal + Independent Test + implementation tasks with **exact file paths**
- Include tests only if the spec/user requested TDD
- End with: dependency graph, parallel opportunities, MVP-first implementation strategy
- Output: tasks.md. Report task count, per-story count, MVP scope, parallel opportunities.

### Step 6 — Implement

**Purpose**: Execute tasks.md.

1. Read tasks.md + all design docs + constitution. Follow the checklist strictly, in order; do not skip tasks.
2. If the project has its own SOP (coding rules / git discipline / deploy process), **follow those rules first** — they override this skill's generic advice (e.g. checkpoint commits, plan confirmation, verification reports).
3. After each task or logical group: verify (compile/test as available), then commit per project conventions.
4. Do not modify `checklists/` checkbox markers — they are reviewer-owned gates.
5. Report progress per task; stop at each user-story checkpoint for validation if requested.

### Step 7 — Converge *(closure loop)*

**Purpose**: Close the loop — verify code matches spec/plan/tasks.

1. Read spec.md, plan.md, tasks.md, constitution.md.
2. Audit the codebase against each: implemented? partial? missing? violating constitution?
3. Unfinished/missing items → append as NEW tasks to tasks.md (mark `[ ]`).
4. **Loop**: re-run Steps 6-7 until the audit finds zero gaps → `Converged`.
5. Report: what was completed, what was appended, convergence status. Suggest commit message.

## Artifact Layout (spec-kit compatible)

```text
<project>/
├── .specify/
│   ├── feature.json            # current feature pointer (written by specify)
│   └── memory/constitution.md  # project constitution (written by constitution)
└── specs/
    └── <NNN>-<short-name>/
        ├── spec.md
        ├── checklists/requirements.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── contracts/
        ├── quickstart.md
        └── tasks.md
```

If the project already has `.specify/` (initialized by official `specify init`), reuse its `templates/` and `scripts/` — this skill's templates are byte-compatible fallbacks.

## Common Pitfalls

- **Skipping steps**: never jump from user prompt straight to plan or code. Each artifact is the input of the next.
- **Spec leaking implementation**: `spec.md` must stay tech-agnostic. Framework/table names belong in plan.md. (Exception: Key Entities may name domain concepts.)
- **Vague requirements**: "should", "etc.", "and so on" fail the testable requirement checklist — rewrite as MUST/SHOULD with concrete acceptance criteria.
- **Unresolved clarifications**: never silently guess a scope/security-critical choice. Ask (max 3), then record the answer in the spec.
- **Fake grounding**: plan/research must cite real repo evidence (actual classes, real table names, real endpoints). Inspect code and DB before writing design docs.
- **Ignoring project SOP**: if the repo has its own coding rules/SOP (e.g. OpenClaw's 缺陷修复 SOP v2.2), they take precedence over this skill's generic workflow — especially git discipline and deploy verification.
- **Converge skipped**: "implemented" without the converge audit is not done. Loop until zero gaps.

## Verification Checklist

- [ ] Constitution exists at `.specify/memory/constitution.md` with version + dates, no unresolved `[PLACEHOLDER]`
- [ ] spec.md: all mandatory sections filled, `[NEEDS CLARIFICATION]` ≤ 3 (ideally 0), success criteria measurable + tech-agnostic
- [ ] checklists/requirements.md: all items pass (or documented rationale)
- [ ] plan.md: Technical Context grounded in real repo facts, Constitution Check passed (or justified in Complexity Tracking)
- [ ] research.md: every decision has Decision / Rationale / Alternatives considered
- [ ] tasks.md: every task has exact file path, organized by user story, MVP identified
- [ ] quickstart.md: commands are runnable and expected outcomes stated
- [ ] Implementation followed tasks.md in order + project SOP (git checkpoints, deploy verification)
- [ ] Converge audit: zero unmatched spec/plan/tasks items → `Converged`

## Relationship to Official Spec Kit

- Official CLI (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.0.2`) installs `speckit-*` skills into `~/.hermes/skills/` via `specify init --integration hermes`.
- This skill is a **self-contained alternative**: same process, same artifacts, no CLI requirement. Prefer it when you cannot/should not run `specify init`, or want the workflow portable across Hermes instances.
- Extension hooks (`.specify/extensions.yml`, e.g. git branching, bug triage): check for them at each step boundary; if present, honor `hooks.before_<step>` / `hooks.after_<step>` entries (mandatory hooks must run; optional hooks are offered to the user).
- See `references/official-integration.md` for CLI setup + how to switch between modes.
