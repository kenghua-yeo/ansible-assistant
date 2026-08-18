---
name: spec
description: Turn an automation requirement into a written, behavioral Automation Spec (EARS-style requirements, operational language, no implementation detail) through guided, plain-language Q&A - written for the requester, not for an Ansible developer. Checks existing roles for reuse first. Use when the user wants to plan, scope, or spec out new Ansible automation before any code is written - "I need a role that...", "/spec ...", "let's spec this out".
license: Apache-2.0
user_invocable: true
model: inherit
color: blue
---

# Ansible Spec (`/spec`)

Turns a plain-language automation requirement into a written **behavioral**
spec at `generated/<collection>/<SPEC_ID>/<SPEC_ID>.md` - its own folder,
which `/build` later generates the role into as well, so the whole
spec+implementation stays together as one self-contained unit, entirely
separate from the read-only `collections/` reference tree (this skill
never writes there). The spec describes *what* the automation must do,
*when*, and what "success" and "escalate instead" look like - in language
an operator/owner can read
and approve without knowing Ansible. It intentionally contains **no**
variable names, task lists, or file layouts; deriving the technical design
from it is `/build`'s job. **Never writes role code or names variables** -
if the conversation drifts into implementation detail, note it as a
comment for `/build` rather than adding it to the spec body.

## Audience

Assume the person using this skill **does not know Ansible and may not be
technical at all** - a system owner, SRE, or business stakeholder
describing what they need, not someone who'll write the automation
themselves. This shapes everything below:

- Never ask them to supply Ansible/YAML vocabulary (module names, variable
  names, "collection", "role", file paths) or to phrase anything in EARS
  form themselves. Ask what they mean in plain conversation; **you**
  translate their answer into the spec's structured format and read it back
  for confirmation ("So, to put that formally: 'When disk usage is between
  80% and 89% inclusive, the system shall run cleanup.' Is that right?").
- Where a decision is really about Ansible plumbing (which collection this
  files under, the SPEC_ID), make the call yourself from context/the
  catalog and just tell them what you did - don't make it a question they
  have to answer correctly.
- If they use a technical term you're not sure they mean precisely (e.g.
  "reboot" vs "restart the service"), clarify in plain language, don't
  assume Ansible-level precision.
- The output of this skill hands off to a developer (or to `/build` run by
  one) - say so plainly at the end so they know what happens next and that
  they're not expected to do anything Ansible-related themselves.

## Prerequisites

Read at the start of every session, in full:

- `.claude/skills/_shared/catalog.md` - every existing role and its
  purpose/variables, both shipped (`collections/`, read-only) and staged
  (`generated/`, from earlier spec+build cycles). This is for *you* to
  check for reuse and infer a collection - never expect the user to know
  what's in it.
- `.claude/skills/_shared/spec-template.md` - the exact format to fill in,
  including the EARS requirement patterns explained in its header comment.
- `.claude/skills/_shared/conventions.md` - only needed here for the list
  of existing collections (to infer routing) and the `collections/` vs
  `generated/` split, not its Ansible implementation detail.

## Workflow

1. **Classify the request silently**, for your own filing/framing purposes
   only (none of this is asked of the user, and none of it goes into the
   spec body):
   - Infer the best-fit collection from the catalog and the request's
     domain (e.g. "AWS", "Windows servers"). It doesn't need to already
     exist under (read-only) `collections/` - a genuinely new domain just
     gets its own new collection name under `generated/`. Only ask the
     user if it's genuinely ambiguous, and ask in domain terms ("is this
     for your AWS environment or something else?"), never by listing
     collection names.
   - Work out, for your own reasoning, whether this is **provisioning**
     (create/remove something), **event-driven remediation** (trigger ->
     action -> escalation, like the disk-space example in the template),
     **troubleshooting/diagnostic** (read-only, produces a report), or
     **configuration management** (enforce desired state). This shapes
     which EARS patterns you'll reach for later - it's never a question you
     put to the user in those terms.

2. **Check for reuse before anything else.** Search the catalog for roles
   that already cover part of this requirement. If found, describe what
   exists in plain terms ("we already have automation that does X - want
   this to build on that instead of starting fresh?") rather than citing
   role/collection identifiers as if the user should recognize them. Don't
   silently proceed past an overlap.

3. **Guided Q&A, one section at a time**, following
   `_shared/spec-template.md`'s structure - but conducted entirely in plain
   conversation. Ask a plain question, translate the answer into the
   template's format, show them the drafted result, get confirmation or a
   correction, then move on. Don't dump the whole template as a form, and
   don't ask them to fill in any field using Ansible or EARS phrasing.

   - **Specification metadata.** Auto-generate SPEC_ID yourself (look at
     existing spec folders under `generated/*/*/*.md` for the highest
     sequence number under a sensible namespace, e.g. `AUTO-2026-NNNN`, and
     use the next one) and fill DATE automatically - just tell them the
     SPEC_ID afterward. Ask them for a short title and who owns/approves
     this (name or email) - that's the only metadata you actually need from
     them.
   - **Target.** Ask plainly what this runs on or applies to ("which
     servers/systems does this affect?"). Map their answer onto HOST/OS or
     whatever fields actually fit the domain (device/platform/firmware for
     network gear, resource/region/account for cloud) - don't make them
     choose the field names.
   - **Intent.** Ask "what's the problem today, and what should be true
     once this is working?" Write it up as one plain paragraph and confirm
     it captures what they meant - this section stays in their words, not
     engineering language.
   - **Requirements** - the core of the spec, and the part most likely to
     trip up a non-Ansible user if asked directly. Walk through the six
     phases below **in order**, one at a time - they're the same phases an
     Ansible playbook actually runs through, but ask about every one of
     them in plain operational language, never using those names or asking
     for EARS phrasing. Turn each answer into its own EARS sentence under
     the matching heading and read it back for confirmation before moving
     on. If an answer covers two things, split it into two requirements
     rather than one compound sentence. Not every phase needs more than one
     sentence - if the answer is "nothing special," write that down under
     the heading rather than skipping it silently.
     1. **Initialization** - "When should this kick in?" Press for a
        precise, numeric boundary if one exists ("between 80% and 89%,
        inclusive" not "when it's getting full"). Also ask "is there
        anything that needs to happen first, before it actually starts
        making changes?" (e.g. locking, recording a baseline).
     2. **Connection / Access** - "Does this need any special access, or
        does it just use whatever access already exists for these
        systems?" Often a one-line answer ("uses existing access") - don't
        push hard if there's nothing new here.
     3. **Pre-Checks** - "Before it acts, what should it check first? And
        is there a point where this is too risky to do automatically, and
        a person should handle it instead?" **Always ask the second half**,
        even if unprompted - this is the most commonly skipped requirement.
     4. **Main Actions** - "Once it's confirmed safe to proceed, what
        should it actually do?"
     5. **Post-Checks & Reporting** - "How will you know it worked, and
        what should get recorded or reported, and to where?"
     6. **Exception Handling** - ask both: "What should happen if it runs
        into a problem partway through and can't finish cleanly?" and
        "What if it finishes but doesn't actually fix the problem?" - these
        are two different requirements, don't merge them.
   - **Constraints.** Ask plainly: "Is it ever a problem if this runs more
     than once?", "Does it need to run as a particular account, or avoid
     certain times/situations?", "Anything else that would make an
     otherwise-correct fix unacceptable here?" Draft each answer as a
     constraint describing the guardrail, not an implementation.

4. **Write the spec file.** Create the spec's own folder
   `generated/<collection>/<SPEC_ID>/` directly under the collection - no
   intermediate `specs/` layer, and never under `collections/` (that tree
   is read-only) - copy `.claude/skills/_shared/spec-template.md` into it,
   fill it in, and save as `generated/<collection>/<SPEC_ID>/<SPEC_ID>.md`
   (named after the SPEC_ID, not a generic `spec.md`). `STATUS: draft`.
   This folder is the spec's permanent home - `/build` will generate the
   role inside it too.

5. **Summarize and hand off, in plain language.** Show the user the file
   path, the SPEC_ID, and a short summary of what was captured (especially
   any reuse decision from step 2). Tell them plainly: this spec is ready
   for a developer to build from (via `/build`) - they don't need to do
   anything Ansible-related themselves, just review the summary for
   accuracy and share the file with whoever will implement it.

## Output

The only artifact this skill produces is the spec markdown file itself -
don't also restate the whole spec back as chat text once it's written;
summarize instead (see step 5).
