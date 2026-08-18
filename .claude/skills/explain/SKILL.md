---
name: explain
description: Explain an Ansible concept, error message, playbook/task logic, or architectural pattern in plain language - strictly read-only, never modifies files. Use when the user asks "what does this mean", "why does this fail", "how does X work in Ansible", or "/explain ...".
license: Apache-2.0
user_invocable: true
model: inherit
color: purple
---

# Ansible Explain (`/explain`)

Plain-language breakdowns of Ansible concepts, error messages, and code -
general Ansible knowledge plus this repo's specific conventions and
patterns where relevant.

## Read-Only

**This skill never creates, edits, deletes, or moves any file.** It only
reads local files and local docs (`ansible-doc`, a mirrored docs folder)
or, as a last resort, fetches from the web - to explain, never to change
anything. Nothing it does ever changes something on disk, regardless of
whether the file in question is under `generated/` or the read-only
`collections/`. If explaining an error naturally surfaces the fix, show it
in the response as a snippet - don't apply it, even if it's trivial (a
typo, a missing colon). Fixing is `/build`'s or the user's job.

## When to Use This Skill

- A specific error message or traceback from `ansible-playbook`,
  `ansible-lint`, or `ansible-test`.
- "How does X work" questions (loops, handlers, `include_role` vs
  `import_role`, argument validation, module_defaults groups, etc.).
- "Why is this repo structured this way" questions - e.g. what a
  `meta/argument_specs.yml` does, why variables use the
  `<role>_`/`<role>__` split, what a collection's `extensions/patterns/*`
  directory is (AAP Content Pattern packaging: survey + setup.yml + run
  playbook), how collections/roles/playbooks/patterns relate to each other,
  and how `collections/` is organized in this repo.

## Workflow

1. If the question is about *this repo's* structure or conventions, answer
   from `.claude/skills/_shared/conventions.md` and the actual file(s) in
   question - read them, don't guess. Point at a real example already in
   the catalog when one exists (e.g. "this is the same pattern
   `manage_ec2_instance` uses for...").
2. If it's a general Ansible concept/error unrelated to a specific file
   here and getting it wrong would matter (module argument changes,
   deprecations, version-specific behavior), verify it - in this order,
   stopping at the first that applies (see `REQUIRED_URLS.md` for the
   full rationale):
   1. `.claude/skills/_shared/reference-docs/` - if a local docs mirror
      exists there, read from it. Works offline, always try this first.
   2. `ansible-doc` (or `ansible-doc <collection>.<module>`), if available
      as a local CLI tool - also fully offline, and versioned to match
      what's actually installed.
   3. `WebFetch` against `https://docs.ansible.com` - only if neither of
      the above is available *and* network access actually works. Don't
      retry indefinitely or block on this if it fails/times out.
   4. Otherwise, answer from general knowledge, and say plainly that this
      wasn't verified against current docs - version-specific details
      might be stale.
3. For error messages: identify what actually raised it (task name, module,
   which host), the most likely root cause given the surrounding
   task/variable definitions if available, and the fix - not a generic list
   of "things that could cause this."

## Output

- Plain language first, jargon only where it's the precise term and you
  define it inline the first time.
- Bullet points over prose for anything with more than one distinct point.
- For "how does X work" questions, prefer a short concrete example over an
  abstract description.
- Keep it proportional to the question - a one-line error gets a short
  answer, not a full architectural essay.
