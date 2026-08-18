# Ansible Spec-Driven Development

A portable, agent-driven workflow for turning plain-language automation
requests into reviewed, convention-compliant Ansible roles - via four
skills: `/spec`, `/build`, `/review`, `/explain`.

This whole folder is the unit of reuse. Clone it wherever you want to run
the workflow; it carries its own reference material, its own conventions,
and its own agent instructions with it.

**If you're an AI agent:** read [`AGENTS.md`](AGENTS.md) first - it's the
concise, operational entry point (critical rules, the four workflows, how
to invoke them) written for any agent, not just Claude Code. This README
is the companion narrative doc: full architecture, rationale, and detail
that `AGENTS.md` points back to.

## What this is

A non-Ansible requester describes what they need in plain conversation.
`/spec` turns that into a written, technology-agnostic **behavioral**
spec - trigger conditions, actions, escalation paths, expected outcomes -
with zero Ansible detail in it. A junior/beginner Ansible developer then
runs `/build` against that spec, which interactively derives the actual
technical design (role name, variables, task structure) and generates a
complete role, modeled on real code already in this repository rather than
invented from scratch. `/review` and `/explain` support both of them
throughout.

The point: the person who understands the operational requirement doesn't
need to know Ansible, the person who writes the Ansible doesn't need to
extract requirements from a stakeholder, and neither has to guess at this
repository's conventions - the skills carry all of that.

## Folder structure

```
.
├── AGENTS.md                        # operational entry point for any AI agent
├── README.md                        # this file - architecture and rationale
├── .claude/
│   ├── skills/
│   │   ├── spec/SKILL.md          # /spec    - requirement -> behavioral spec
│   │   ├── build/SKILL.md         # /build   - spec -> generated Ansible role
│   │   ├── review/SKILL.md        # /review  - lint/idempotency/security/convention review
│   │   ├── explain/SKILL.md       # /explain - plain-language Ansible explainer
│   │   └── _shared/
│   │       ├── catalog.md          # auto-generated index of every existing role (read this, never hand-edit)
│   │       ├── conventions.md      # naming/anatomy rules distilled from collections/
│   │       ├── spec-template.md    # the exact spec format /spec fills in
│   │       ├── REQUIRED_URLS.md    # every external URL any skill touches - for offline/disconnected setups
│   │       └── reference-docs/     # optional: a pre-downloaded docs mirror, see REQUIRED_URLS.md
│   ├── scripts/
│   │   ├── build_catalog.py        # regenerates catalog.md - run after any role changes
│   │   └── trim_collections.py     # strips non-reference cruft (VCS/CI/tests/docs) from collections/
│   └── .gitignore
├── collections/                    # READ-ONLY, curated reference material - real, shipped Ansible
│   │                                collections, trimmed to just what the skills reference (see
│   │                                trim_collections.py). /spec and /build only ever READ from here.
│   ├── cloud.aws_ops/
│   ├── cloud.aws_troubleshooting/
│   ├── infra.windows_ops/
│   └── ...                         # currently 5 collections - see catalog.md for the live, authoritative list
└── generated/                      # WRITABLE. Everything /spec and /build produce.
    └── <collection>/
        └── <SPEC_ID>/
            ├── <SPEC_ID>.md                              # written by /spec (named after its own folder, not "spec.md")
            ├── roles/<role_name>/                        # written by /build
            └── tests/integration/targets/test_<role_name>/
```

`generated/` doesn't exist until the first time `/spec` runs - it's created
on demand, per spec.

## The four skills

| Skill | Slash command | Audience | Does |
|---|---|---|---|
| [spec](.claude/skills/spec/SKILL.md) | `/spec` | Non-Ansible requester (system owner, SRE, business stakeholder) | Guided, plain-language Q&A -> a written behavioral spec (EARS requirements, no implementation detail) |
| [build](.claude/skills/build/SKILL.md) | `/build` | Junior/beginner Ansible developer | Interactive, checkpoint-by-checkpoint technical design -> a generated role, modeled on real reference roles |
| [review](.claude/skills/review/SKILL.md) | `/review` | Either | Structured review: lint/syntax, idempotency & security, convention compliance - fixes shown in the response, **never applied** (read-only) |
| [explain](.claude/skills/explain/SKILL.md) | `/explain` | Either | Plain-language explanation of a concept, error, or piece of Ansible/repo logic (read-only) |

`/review` and `/explain` are strictly read-only - they never create, edit,
delete, or move a file, regardless of whether what they're looking at is
under the writable `generated/` tree or the read-only `collections/` tree.
Any fix either of them shows is text in the response, for a human or
`/build` to apply - never written back automatically.

Each `SKILL.md` is self-contained and states its own audience, prerequisites,
and step-by-step workflow - read the skill file itself for the authoritative
detail; this README only orients.

## Design principles (the "why" behind the structure)

- **Specs are behavioral, not technical.** A spec never contains a variable
  name, task list, or module choice - just what must happen, when, and what
  success/failure look like, in EARS form (`When <trigger>, the system
  shall <response>`), organized into the same six phases an Ansible
  playbook actually executes in: Initialization, Connection/Access,
  Pre-Checks, Main Actions, Post-Checks & Reporting, Exception Handling.
  Deriving the technical implementation from that is entirely `/build`'s
  job. This is what lets a non-Ansible person own the spec.
- **`collections/` is read-only; `generated/` is where everything is
  written.** Neither skill ever writes into `collections/`. This keeps the
  reference material stable and diff-free, and means the whole
  spec+implementation for one request lives together in one self-contained,
  reviewable folder under `generated/<collection>/<SPEC_ID>/` - no
  redundant intermediate `specs/` layer, and the spec file itself is named
  after its own `<SPEC_ID>`, not a generic `spec.md`.
- **Staged vs. promoted.** A role `/build` generates is real, complete
  code, but it's not resolvable via the normal Ansible FQCN
  (`<namespace>.<collection>.<role>`) or usable as a `meta/main.yml`
  dependency until a human *promotes* it - reviews it, then copies it into
  `collections/<collection>/roles/<role_name>/`. This is always a
  deliberate manual step, never automatic. `catalog.md` flags every staged
  role so neither skill mistakes one for something already promoted.
  See `conventions.md`'s "Staged vs. promoted" for the full detail.
  Scaffolding a brand-new collection (if a spec targets a domain that
  doesn't exist under `collections/` yet) happens at promotion time too.
- **Reuse-first.** Both `/spec` and `/build` check `catalog.md` - an
  auto-generated index of every role across both `collections/` (shipped)
  and `generated/` (staged) - before proposing anything net-new.
- **Grounded in real code, not just summarized rules.** `/build` doesn't
  generate from memory of `conventions.md` alone; it opens 1-2 actual
  reference roles closest in shape to the spec and models the new role's
  structure on them directly.
- **Reference material is curated, not just cloned as-is.** Real upstream
  collections carry a lot that's irrelevant to this workflow - `.git/`
  history, CI workflows, test suites, docsite source, changelog fragments
  - and an agent exploring the tree can't always tell that apart from
  content it should actually be modeling code on. `trim_collections.py`
  strips that down to what `/build` and the catalog actually reference
  (`roles/`, `extensions/patterns/`, `galaxy.yml`/`MANIFEST.json`,
  `meta/`, top-level docs/licenses), so `collections/` stays unambiguous.
- **Platform-agnostic.** All paths are relative and forward-slash; the
  catalog script uses `pathlib` throughout and documents both `python` and
  `python3` invocations. Works identically whether the agent is running in
  a container, on Windows, macOS, or Linux.
- **Designed for disconnected use.** `/spec`, `/build`, and `/review`
  never touch the network at all. `/explain` is the only skill that ever
  does (`WebFetch` against `docs.ansible.com`, and only as a last resort
  after checking for a local docs mirror and `ansible-doc`) - see
  `.claude/skills/_shared/REQUIRED_URLS.md` for the exact list and how to
  pre-mirror it for a fully offline environment.

## Getting started (for a new agent reading this cold)

Start with [`AGENTS.md`](AGENTS.md) - it has the critical rules, the
workflow index, and exactly how to invoke `/spec`/`/build`/`/review`/
`/explain` whether or not your agent has native skill-loading support.
The short version, expanded on here:

1. **Read `.claude/skills/_shared/conventions.md` and
   `.claude/skills/_shared/catalog.md` before doing anything else** - they
   are the ground truth for naming, role anatomy, and what already exists.
   Every skill's own `SKILL.md` names these as required prerequisites too.
2. **Requirements to run the maintenance scripts**: Python 3 with PyYAML
   (`pip install pyyaml`) - nothing else.
   ```
   python3 .claude/scripts/build_catalog.py       # regenerate catalog.md - after any role change
   python3 .claude/scripts/trim_collections.py    # dry-run report of what a reference-collection trim would remove
   ```
   (`python` instead of `python3` on platforms where that's what's on
   PATH.) `trim_collections.py` defaults to a dry run; pass `--apply` to
   actually delete - only needed after adding a *new* reference collection
   under `collections/`, not part of the normal spec/build loop.
3. **Never write into `collections/`.** If you're an agent about to
   generate or modify a file, and the target path starts with
   `collections/`, stop - that's a bug in the request, not something to
   route around.

## A typical session

```
Read AGENTS.md and make sure you understand your role as an AI assistant.

/explain please provide a summary of RHEL roles available in the collection

/spec please guide me to build up a spec for cleaning up disk space
  before it becomes an incident
  -> guided Q&A -> generated/cloud.aws_ops/AUTO-2026-0055/AUTO-2026-0055.md

/build AUTO-2026-0055
  -> checkpoint-by-checkpoint design walkthrough ->
     generated/cloud.aws_ops/AUTO-2026-0055/roles/disk_space_remediate/
     generated/cloud.aws_ops/AUTO-2026-0055/tests/integration/targets/test_disk_space_remediate/

/review generated/cloud.aws_ops/AUTO-2026-0055/roles/disk_space_remediate
  -> lint / idempotency & security / convention-compliance findings + fixes

/explain how should I use this role for the production web servers?

(after review passes, a human promotes the role into
 collections/cloud.aws_ops/roles/disk_space_remediate/, then:)

python3 .claude/scripts/build_catalog.py
(or ask the agent to use the script to build the catalog)
```
