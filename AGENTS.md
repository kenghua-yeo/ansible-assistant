# AGENTS.md

Instructions for any AI coding agent working in this repository - Claude
Code, Cursor, Aider, Codex, or otherwise. If you are an agent and this file
exists in your context, treat everything below as binding for this repo.

## Project objective

This repository is a portable, spec-driven workflow for turning
plain-language automation requests into reviewed, convention-compliant
Ansible roles, via four workflows: **spec**, **build**, **review**,
**explain**. A non-Ansible requester describes what they need; `spec`
turns that into a written, technology-agnostic behavioral specification;
a junior/beginner Ansible developer runs `build` against that spec to
generate an actual role, modeled on real reference code already in this
repo; `review` and `explain` support both of them. See `README.md` for
the full rationale and design principles - this file covers what an agent
needs to operate correctly.

## Critical rules - read before doing anything

1. **`collections/` is READ-ONLY.** Never create, edit, delete, or move
   any file under `collections/`, for any reason, under any instruction.
   It holds real reference Ansible collections used only as example
   material. If a request would require writing there, that's a bug in
   the request - say so, don't route around it. The only exception is a
   human explicitly performing a deliberate *promotion* (see below) - not
   something you do autonomously.
2. **`generated/` is where all output goes.** Everything `spec` and
   `build` produce lives under `generated/<collection>/<SPEC_ID>/` - the
   spec file, the generated role, and its tests, all together in one
   self-contained folder. `generated/` doesn't exist until the first spec
   is written; create it on demand.
3. **`review` and `explain` never modify any file, anywhere, ever** -
   not under `generated/`, not under `collections/`. They only read and
   report. A suggested fix is shown as text/a diff in the response, never
   written back automatically.
4. **Staged vs. promoted**: a role `build` generates is real, complete
   code, but it is not resolvable via the normal Ansible FQCN
   (`<namespace>.<collection>.<role>`) and not usable as a
   `meta/main.yml` dependency until a human reviews it and *promotes* it
   by copying it into `collections/<collection>/roles/<role_name>/`. This
   is always a deliberate, separate human action - never something an
   agent does as part of `spec` or `build`.
5. **Read `.claude/skills/_shared/catalog.md` and
   `.claude/skills/_shared/conventions.md` before generating or proposing
   anything.** The catalog is the authoritative, auto-generated index of
   every existing role (shipped and staged) - check it for reuse before
   writing anything net-new. Conventions is the authoritative naming/
   anatomy rulebook - don't invent a different structure.
6. **Specs are behavioral, never technical.** A spec (written by `spec`)
   never contains a variable name, task list, or module choice - only
   trigger conditions, actions, and outcomes, in EARS form. Deriving the
   technical implementation from a spec is `build`'s job exclusively.

## The four workflows

Each is fully specified in its own file under `.claude/skills/<name>/SKILL.md`
- read that file in full before performing the corresponding task. This
summary is only an index:

| Workflow | Trigger | Audience | Summary |
|---|---|---|---|
| **spec** | `/spec ...`, or "I need automation that...", "let's spec this out" | Non-Ansible requester (system owner, SRE, stakeholder) | Guided, plain-language Q&A -> a written behavioral spec at `generated/<collection>/<SPEC_ID>/<SPEC_ID>.md`. Never writes code or names variables. |
| **build** | `/build ...`, or "build the role for...", "generate the role from this spec" | Junior/beginner Ansible developer | Interactive, checkpoint-by-checkpoint technical design, grounded in real reference roles under `collections/`, -> a generated role under `generated/<collection>/<SPEC_ID>/roles/<role_name>/`. |
| **review** | `/review ...`, "review this role", "is this safe/idempotent" | Either | Structured, strictly read-only review: lint/syntax, idempotency & security, convention compliance - fixes shown, never applied. |
| **explain** | `/explain ...`, "what does this mean", "why does this fail", "how does X work" | Either | Plain-language, strictly read-only explanation of a concept, error, or piece of repo logic. Checks a local docs mirror and `ansible-doc` before ever using the network. |

### How to invoke these on an agent without native skill support

On Claude Code, `.claude/skills/*/SKILL.md` files are auto-discovered and
`/spec`, `/build`, `/review`, `/explain` invoke them natively - nothing
else to do. **On any other agent**: when the user's message starts with
one of those four words/slashes, or clearly asks for one of these
workflows in plain language, locate and read the matching
`.claude/skills/<name>/SKILL.md` in full, then follow its instructions
exactly as written for the remainder of that task. Treat the `SKILL.md`
file itself as the authoritative, executable instructions - this table is
only for finding the right one quickly.

## Folder structure

```
.
├── AGENTS.md                    # this file
├── README.md                    # architecture, design rationale, full onboarding
├── .claude/
│   ├── skills/
│   │   ├── spec/SKILL.md
│   │   ├── build/SKILL.md
│   │   ├── review/SKILL.md
│   │   ├── explain/SKILL.md
│   │   └── _shared/
│   │       ├── catalog.md          # auto-generated - regenerate, never hand-edit
│   │       ├── conventions.md      # naming/anatomy rules
│   │       ├── spec-template.md    # exact spec format
│   │       └── REQUIRED_URLS.md    # for offline/disconnected setups
│   └── scripts/
│       ├── build_catalog.py        # regenerates catalog.md
│       └── trim_collections.py     # strips non-reference cruft from collections/
├── collections/                 # READ-ONLY reference Ansible collections
└── generated/                   # WRITABLE - all spec/build output (created on demand)
    └── <collection>/<SPEC_ID>/
        ├── <SPEC_ID>.md
        ├── roles/<role_name>/
        └── tests/integration/targets/test_<role_name>/
```

## Running the maintenance scripts

Both require Python 3 + PyYAML (`pip install pyyaml`); nothing else.
`python` instead of `python3` on platforms where that's what's on PATH.

```
python3 .claude/scripts/build_catalog.py       # regenerate catalog.md - run after any role is
                                                #  added, generated, or promoted
python3 .claude/scripts/trim_collections.py    # strip non-reference cruft from collections/ -
                                                #  dry-run by default; pass --apply to actually
                                                #  delete. Only needed after adding a NEW reference
                                                #  collection, not part of the normal spec/build loop.
```

## Portability notes

- All paths in this repo are relative and forward-slash; nothing assumes
  a particular OS, container, or drive layout. Works identically cloned
  onto Linux, macOS, Windows, or into a container.
- `spec`, `build`, and `review` never touch the network. `explain` is the
  only one that ever does, and only as a last resort - see
  `.claude/skills/_shared/REQUIRED_URLS.md` for the complete, audited list
  and how to pre-mirror it for a fully offline environment.
- This whole directory (`.claude/`, `collections/`, this file, `README.md`)
  is the unit of reuse - clone it as-is to start the same workflow
  anywhere. `generated/` is per-clone working output, not template content.

## Where to look for more detail

- `README.md` - full architecture and the "why" behind every design choice.
- `.claude/skills/_shared/conventions.md` - role naming, anatomy, README
  shape, idempotency patterns.
- `.claude/skills/_shared/catalog.md` - what roles already exist (shipped
  and staged).
- `.claude/skills/_shared/spec-template.md` - the exact spec format,
  including the EARS requirement patterns.
- `.claude/skills/<name>/SKILL.md` - the authoritative, step-by-step
  workflow for each of the four skills.
