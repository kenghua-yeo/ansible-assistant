---
name: build
description: Interactively design, then generate, a complete convention-compliant Ansible role - deriving the technical implementation (role/variables/tasks/escalation logic) from an approved behavioral Automation Spec written by /spec through a guided, checkpoint-by-checkpoint walkthrough aimed at a junior/beginner Ansible developer, modeled on real existing roles in the collection catalog. Use when the user wants to actually generate/build role code from a spec - "build the role for...", "/build ...", "generate the ansible role from this spec".
license: Apache-2.0
user_invocable: true
model: inherit
color: green
---

# Ansible Build (`/build`)

Generates a complete role from a behavioral spec produced by `/spec`. The
spec describes *what* must happen (EARS requirements, plain operational
language) with **no** variable names, task lists, or module choices - all
of that technical design is this skill's job, worked out with the user one
decision at a time (same guided-interaction style as `/spec`) before any
code is written. Don't invent scope beyond what the Requirements/Constraints
actually say; where a requirement is genuinely ambiguous, ask rather than
guess.

## Audience

Assume the person using this skill is a **junior or beginner Ansible
developer** - they know the basics (tasks, modules, playbooks, `roles:` in
a play) but are likely new to *this repo's* conventions and possibly to
some of the patterns used below. This shapes the interaction:

- At each checkpoint, briefly say **why**, not just what - e.g. "variables
  are prefixed with the role name so two roles can run in the same play
  without colliding" - a sentence, not a lecture. Treat this as a teaching
  opportunity, not just a confirmation gate.
- Don't just ask an open question and wait - a junior dev may not know the
  right answer yet. Propose a concrete default with a one-line rationale,
  and let them accept or override it. "Open question, no suggestion" should
  be rare, reserved for genuinely spec-driven judgment calls (like scope).
- If a concept comes up that's outside this walkthrough's scope to explain
  fully (e.g. `module_defaults` groups, `argument_specs` validation
  internals), name it, give one sentence, and point at `/explain` for more
  - don't derail the build to teach it in depth here.
- It's fine, and expected, for them to ask "why did you do it that way?" or
  "what does this mean?" mid-walkthrough - answer directly before moving on.

## Prerequisites

Read these first, in full:

- `.claude/skills/_shared/catalog.md`
- `.claude/skills/_shared/conventions.md`
- The spec file itself: `generated/<collection>/<SPEC_ID>/<SPEC_ID>.md`.
  Find it by SPEC_ID if given, otherwise search `generated/*/*/*.md` for a
  matching TITLE/topic. If no spec exists yet, send the user to `/spec`
  first - don't build from an ad-hoc description. **The role you generate
  goes inside this same `<SPEC_ID>/` folder** - that's the whole point of
  finding it first.

**Then find real reference roles under (read-only) `collections/`, not
just the catalog summary.** The catalog gives you names/variables/short
descriptions; `conventions.md` gives you the abstracted rules. Neither is
a substitute for reading actual code. Before generating anything, pick the
1-2 existing roles in the catalog closest to this spec in domain and shape
(e.g. an `_operation`-dispatch provisioning role like `manage_ec2_instance`
for a create/delete spec, `connectivity_troubleshooter` for a diagnostic
one), and actually open their `tasks/*.yml`, `meta/argument_specs.yml`,
and `README.md` under `collections/<their-collection>/roles/`. Model the
generated role's structure, task-naming style, module choices, and
error-handling on those real files - point the user at them too during the
walkthrough ("I'm structuring this the same way `manage_ec2_instance`
does it") so they have a concrete example to learn from, not just abstract
rules. **You only ever read from `collections/` - never write there.**

## Workflow

1. **Locate and sanity-check the spec.** Confirm Requirements are real EARS
   statements, not placeholder text, under all six phase headings
   (Initialization, Connection/Access, Pre-Checks, Main Actions,
   Post-Checks & Reporting, Exception Handling - a phase can say "nothing
   special," but shouldn't be silently empty), and that Constraints are
   filled in. If something load-bearing is missing or genuinely ambiguous,
   stop and say what's missing rather than filling the gap yourself.

2. **Re-check the catalog for reuse**, even if `/spec` already did - it may
   have changed since. If an existing role now covers most of this, say so
   before generating anything net-new. If the match is itself flagged
   **STAGED** in the catalog (built for a different spec, not yet
   promoted), say that explicitly too - it can be modeled after, but can't
   be taken on as a `meta/main.yml` dependency until it's promoted.

3. **Guided technical design, one decision at a time.** This is the core of
   this skill, and it's interactive, the same way `/spec` is: work through
   the checkpoints below in order, propose a concrete answer (with a brief
   rationale - see Audience) for one at a time, get confirmation or a
   correction, then move on. **Don't derive the whole design silently and
   dump it at the end** - each checkpoint below is small enough that the
   user can actually catch a wrong call, and learn from the reasoning,
   before it propagates into the next one. Ground each proposal in the
   reference role(s) you picked in Prerequisites where relevant.

   - **Role identity.** Propose a `snake_case` role name (per
     `conventions.md` naming rules) derived from the spec TITLE/Intent. The
     collection is already fixed by which spec you're building from - the
     role is generated at
     `generated/<collection>/<SPEC_ID>/roles/<role_name>/`, not
     chosen fresh. Confirm the name even though it seems minor - it's
     painful to rename once tasks/tests reference it.
   - **Shape.** Propose which pattern fits: the `<role>_operation`
     create/delete dispatch, a straight-line remediation flow (trigger ->
     check -> act -> report), or a read-only diagnostic flow - based on how
     the Requirements are actually written, not on habit. Name the closest
     reference role using that same shape. Get this confirmed before
     designing the phases below.

   Then walk the spec's six Requirements phases **in the same order they
   appear in the spec, which is also the order the role executes in** -
   propose the concrete Ansible construct that satisfies each phase's
   requirement(s) before moving to the next:

   - **Initialization -> setup.** What's needed before the main action:
     `meta/main.yml` dependencies, and any setup tasks at the top of
     `tasks/main.yml` (locking, capturing a baseline). Trigger thresholds
     from this phase become variables (next checkpoint covers naming them).
   - **Connection / Access -> credentials/become.** Usually just confirms
     which shared credentials role (`meta/main.yml` dependency) or
     `become_user` covers this - rarely needs new code.
   - **Pre-Checks -> guard-clause block.** The tasks that run first and
     decide whether to proceed at all - including the "too risky, don't
     act" requirement, which becomes a `fail` (or a skip, depending on the
     spec's wording) with a clear message. See how `manage_ec2_instance`
     guards against acting on an already-existing resource for the shape.
   - **Main Actions -> the core task(s).** The module call(s) that do the
     actual work, gated behind the pre-checks passing.
   - **Post-Checks & Reporting -> register + outcome.** A `register` of the
     action's result, plus a final `set_fact`/`debug` (or `uri`/other
     output module if the spec's target is external) assembling exactly
     the fields the spec's Post-Checks & Reporting requirement names.
   - **Exception Handling -> failure handling + escalation.** Two distinct
     things, both from this phase: what happens if a task itself fails
     (typically `block`/`rescue`, or `failed_when` tuning), and what
     happens if the action succeeded but Post-Checks show the desired
     end-state wasn't reached (a second escalation path, which may reuse
     the Pre-Checks escalation mechanism or need its own). Check the
     catalog for an existing notification/ticketing role or module before
     proposing something new; if nothing exists, say plainly that this is
     new capability, not reuse.

   - **Variables.** With the phases walked, consolidate the full
     `<role>_`-prefixed variable list that emerged: name, type, required?,
     default, choices if bounded. Show it as one list and get corrections -
     variable names are painful to change once tasks/tests reference them.
   - **Constraints -> implementation.** For each Constraint not already
     covered above, propose the concrete mechanism that satisfies it -
     idempotency constraints typically become guard-clause checks or a
     locking mechanism (see `conventions.md`'s idempotency patterns),
     permission/account constraints become `become_user`/credentials-role
     choices. Confirm each before moving on, since these often carry real
     operational risk if guessed wrong (e.g. running as the wrong account).

   Once every checkpoint is confirmed, briefly summarize the full design
   (role + collection, then the six phases -> constructs, then variables
   and constraint handling) as a final recap before generating anything -
   this is a summary of what was already agreed, not a new proposal to
   react to.

4. **Generate the role** under
   `generated/<collection>/<SPEC_ID>/roles/<role_name>/` - inside
   the spec's own folder, under `generated/`, **never** under the
   read-only `collections/` tree (see `conventions.md`'s "Staged vs.
   promoted") - following `conventions.md` **and the reference role(s)
   picked in Prerequisites** as the concrete template for structure and
   style, not just the abstracted rules:
   - `meta/argument_specs.yml` - from the confirmed variable list.
   - `meta/main.yml` - dependencies (shared credentials role, any
     already-*promoted* reused role from step 2 - a still-staged role can't
     be depended on this way yet, see step 6).
   - `defaults/main.yml`.
   - `tasks/main.yml` + `tasks/<operation>.yml` - ordered to match the
     spec's own phase order: setup (Initialization/Connection) ->
     guard-clause block (Pre-Checks) -> core module call(s) (Main Actions)
     -> `register` + outcome summary (Post-Checks & Reporting) ->
     `block`/`rescue` or escalation tasks (Exception Handling). Mirror the
     reference role's task-naming and structuring style within that order.
   - `README.md` - following the required shape in `conventions.md`
     exactly (Requirements / Role Variables / Dependencies / Examples /
     License / Author Information), pulling Requirements from the spec's
     Target/Constraints and Role Variables from step 3. Add a one-line
     "Implements `<SPEC_ID>`" note near the top for traceability, and get
     the Dependencies links' relative paths right (conventions.md flags
     this - the `<SPEC_ID>/roles/` nesting changes them).
   - `generated/<collection>/<SPEC_ID>/tests/integration/targets/test_<role_name>/`
     - at minimum a create + verify + cleanup smoke test, each test case
     mapping back to one of the spec's Requirements.

5. **Update the spec file**: in
   `generated/<collection>/<SPEC_ID>/<SPEC_ID>.md`, set
   `STATUS: built` and append a short `## Implementation` note at the
   bottom pointing at `roles/<role_name>/` (relative to the spec, since
   they're in the same folder) - this is the only technical content that
   ever goes into the spec file, and only after the fact, as a backlink.

6. **Tell the user what to do next**, explicitly:
   - This role is **staged** under `generated/`, not yet usable via the
     normal `<collection>.<role_name>` reference or as another role's
     `meta/main.yml` dependency (see `conventions.md`). Once it's reviewed
     (lint/tests pass), *promotion* means a human **copying** it into the
     read-only `collections/` tree, at
     `collections/<collection>/roles/<role_name>/` (and its test target to
     `collections/<collection>/tests/integration/targets/`) - creating the
     collection there first (`galaxy.yml`, `meta/runtime.yml`) if it's a
     genuinely new one that doesn't exist under `collections/` yet. Say
     this plainly - it's an easy step to forget since the staged role
     already looks and runs like a normal one locally, and it's the one
     point in this whole workflow where `collections/` actually changes,
     deliberately, by human hand, not by either skill.
   - Run `ansible-lint` and `ansible-test sanity` (point them at `/review`
     for a structured review pass) - do this before promoting.
   - Regenerate the catalog: `python3 .claude/scripts/build_catalog.py`
     (`python` instead of `python3` on platforms where that's what's on
     PATH), both now (so it shows up as staged) and again after promotion
     (so it moves to the shipped listing).
   - AAP pattern packaging (survey, `setup.yml`, `run_*.yml`) is **not**
     generated by this skill - it's a manual follow-up if/when this role
     gets packaged as a self-service pattern.

## What NOT to do

- Don't write anything under `collections/` - it's read-only reference,
  full stop. Every file this skill creates goes under `generated/`.
  Promotion into `collections/` is a human copying reviewed code, not a
  step this skill performs.
- Don't generate from memory of `conventions.md` alone - always ground the
  actual code in a real reference role from the catalog, read fresh each
  time (this repo's roles are the source of truth; the conventions doc is
  a summary of them, and summaries drift).
- Don't collapse step 3 into one big proposal - unlike a spec with a
  pre-filled variable table, everything here is inferred, so confirming
  each design decision as you make it (not all at once at the end) is what
  keeps that inference honest and catches a wrong turn before it compounds.
- Don't add variables, operations, or escalation behavior that isn't
  traceable to a specific Requirement or Constraint sentence - if you find
  yourself adding something "to be safe" or "for completeness," that's a
  sign the spec is missing a requirement; flag it instead of quietly
  filling the gap.
- Don't invent a new credentials/auth or escalation mechanism if the target
  collection already has one - depend on it via `meta/main.yml` instead.
- Don't skip `meta/argument_specs.yml` even for a "simple" role.
- Don't silently skip past unfamiliar territory for the user - name the
  concept, explain it in one sentence, point to `/explain` if they want
  more, and keep going.
