---
name: review
description: Review Ansible roles, playbooks, or task files for syntax/lint issues, idempotency and security risks, and convention compliance, with concrete refactor suggestions shown in the response - strictly read-only, never modifies files (including anything under generated/). Use when the user wants a code review of Ansible content - "/review ...", "review this role", "is this playbook safe/idempotent".
license: Apache-2.0
user_invocable: true
model: inherit
color: yellow
---

# Ansible Review (`/review`)

Structured code review for Ansible roles, playbooks, or task snippets.
Works on both freshly `/build`-generated code and hand-written code the
user brings.

## Read-Only

**This skill never creates, edits, deletes, or moves any file. Ever.**
That holds no matter what's under review or where it lives - content
staged under `generated/` (even though `/build` writes there) is reviewed
exactly as read-only as anything under `collections/`. `/review` only
reads and reports.

- Every fix is shown as text/a diff-style before/after **in the response**
  - never written back to the file it came from, even for a one-line,
  obviously-correct change.
- If asked to "just fix it" or "apply the fixes," say plainly that
  `/review` doesn't modify files, then either point out that the user (or
  `/build`, if the code hasn't been promoted yet) can apply the shown
  fix, or offer to hand the finding to another skill/action explicitly -
  don't quietly do it yourself.
- If you run diagnostic tools (`ansible-lint`, `ansible-test sanity`,
  `ansible-playbook --syntax-check`), use **diagnostic-only invocations
  only** - never pass `--fix`, `--write`, or any other auto-correct flag.
  If a tool would modify files by default, don't run it that way; run its
  check-only mode instead.

## Prerequisites

Read `.claude/skills/_shared/conventions.md` first - convention compliance
is one of the three review categories below, and it only means something if
you know what the convention actually is.

## Workflow

Review in this order, and structure the response into exactly these three
sections:

### 1. Lint / Syntax Issues

- Anything `ansible-lint` or `ansible-test sanity` would flag: FQCN usage
  (`ansible.builtin.x`, not bare `x`), `name:` on every task, no jinja in
  `when:` conditions (`when: x` not `when: "{{ x }}"`), consistent YAML
  style, deprecated module/argument usage.
- If a real `ansible-lint`/`ansible-playbook --syntax-check` run is
  possible (files on disk, tools available), run it **diagnostic-only**
  (see "Read-Only" above) and report actual output rather than only
  inferring issues by reading.

### 2. Idempotency & Security Risks

- **Idempotency**: does re-running this produce the same end state without
  errors or duplicate resources? Look specifically for: missing
  state-checks before create, `command`/`shell` used where a proper module
  exists, missing `changed_when`/`failed_when` on `command`/`shell` tasks,
  loops that create rather than converge.
  For AWS provisioning roles, cross-check against the "reject if a resource
  with this name already exists" guard-clause pattern in the catalog roles
  (e.g. `manage_ec2_instance`) - flag its absence if this role also
  provisions named resources.
- **Security**: hardcoded secrets/credentials, missing `no_log: true` on
  tasks handling keys/passwords/tokens, overly broad IAM actions vs. what
  `conventions.md`/the role's own README claims it needs, missing Vault
  usage for sensitive defaults, `command`/`shell` with unsanitized
  variable interpolation (injection risk).

### 3. Convention Compliance & Suggested Refactor

- Check against `conventions.md`: variable prefixing (`<role>_...`,
  `<role>__...` for internal), presence and correctness of
  `meta/argument_specs.yml`, README shape, shared-credentials reuse instead
  of a new auth mechanism, `<role>_operation` dispatch pattern where
  applicable.
- Provide the refactored code, not just a description of the fix - show a
  diff-style before/after **in the response** for each finding that has a
  concrete fix (see "Read-Only" - this is never written to the file).

## Output Format

For each finding: file/line if known, one-sentence problem statement, why
it matters (concrete failure scenario, not just "best practice"), and the
fix. Group by the three sections above; skip a section entirely if there's
nothing to report in it rather than writing "no issues found" filler for
every category.

## What NOT to do

- Never write, edit, delete, or move a file - not the code under review,
  not a "quick fix" while you're in there, not a lint auto-fix, nothing.
  This applies identically under `generated/` and `collections/`.
- Don't run a lint/test tool in a mode that mutates files (`--fix`,
  `--write`, autocorrect) even if the user asks for it - explain why, run
  the check-only equivalent instead.
