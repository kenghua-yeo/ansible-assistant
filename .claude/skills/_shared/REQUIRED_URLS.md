# Required URLs (for disconnected/offline setups)

Every external URL any of the four skills (`/spec`, `/build`, `/review`,
`/explain`) fetches or references during normal operation - audited by
grepping the whole `.claude/` tree for `https?://`, `WebFetch`, and
`WebSearch`. If you're setting this up somewhere without network access,
this is the complete list of what would need pre-mirroring; nothing else
here talks to the network.

## 1. `https://docs.ansible.com` - used by `/explain` only

- **Where**: `explain/SKILL.md`, workflow step 2 - for general Ansible
  concept/error questions unrelated to a specific file in this repo,
  `/explain` uses `WebFetch` against this to verify version-specific facts
  (module argument changes, deprecations, current behavior) rather than
  relying on potentially-stale training knowledge.
- **`/spec`, `/build`, and `/review` fetch nothing external.** They
  operate entirely on local files (`catalog.md`, `conventions.md`,
  `spec-template.md`, the `generated/` and `collections/` trees) and,
  optionally, local CLI tools (`ansible-lint`, `ansible-test`) if
  installed. Nothing to mirror for them.

### Scope note - this isn't one page

`docs.ansible.com` is a large, versioned documentation site, not a single
URL to save. A useful offline mirror means the *relevant subset*:

- Module/plugin reference pages for whichever collections are actually in
  play (check `catalog.md` for the current list - at minimum
  `ansible.builtin`, plus whatever `amazon.aws`, `community.aws`,
  `ansible.windows`, `community.windows`, etc. the reference collections
  under `collections/` depend on - see each collection's `galaxy.yml`).
- The core language reference (loops, handlers, blocks, roles, variables,
  templating, `argument_specs`).
- The changelog/porting guide for whichever Ansible version is actually
  installed here.

### Better option than mirroring the website

`ansible-doc` (bundled with the `ansible`/`ansible-core` package) generates
complete local documentation for every installed collection and module
with **zero network access**, and it's automatically versioned to match
what's actually installed - which a website mirror can drift from. Prefer
this over mirroring `docs.ansible.com` if `ansible-doc` is available in the
disconnected environment; treat the website as a fallback source only.

### Where to put a mirror, once you have one

`.claude/skills/_shared/reference-docs/` (create it - doesn't exist yet).
Any internal structure is fine; `/explain` has been updated (see below) to
look there first.

## `/explain`'s offline behavior (already wired up)

`explain/SKILL.md` now checks, in order:

1. `.claude/skills/_shared/reference-docs/` for locally mirrored docs -
   use these if present, regardless of network availability.
2. `WebFetch` against `https://docs.ansible.com` - only if no local mirror
   exists **and** network access actually works.
3. General knowledge, with an explicit caveat that it wasn't verified
   against current docs (version-specific details might be stale) - if
   neither of the above is available.

It never fails or hangs trying to reach the network when offline; it just
degrades to (3) and says so.

## Related, but not a URL to mirror

These block fully offline use too, but aren't "download this page" -
they're packages, so the fix is vendoring, not mirroring:

- **PyYAML**, required by `.claude/scripts/build_catalog.py`
  (`pip install pyyaml`). For offline use: vendor a wheel (e.g.
  `pip download pyyaml -d <dir>` while online, then
  `pip install --no-index --find-links <dir> pyyaml` on the disconnected
  machine).
- **`ansible-lint` / `ansible-test` / `ansible-doc`**, used only if
  `/review` (or, per above, `/explain`) chooses to run them, and only if
  they're already installed - same PyPI-vendoring consideration if you
  want those diagnostic runs to work offline too. Neither skill fails if
  these tools are simply absent; they fall back to reading the code
  directly.

## Keeping this file current

Re-audit after adding any new skill or editing an existing one's Workflow:

```
grep -rnE "https?://|WebFetch|WebSearch" .claude/skills/*/SKILL.md
```

Anything that shows up outside `_shared/catalog.md` (which just contains
incidental URL text pulled from scanned role variables - e.g. a Red Hat
API default value belonging to some role's own runtime config - not a
skill dependency) belongs in this file.
