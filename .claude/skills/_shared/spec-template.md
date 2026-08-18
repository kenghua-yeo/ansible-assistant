<!--
Template for an Automation Spec. Copied and filled in by the /spec skill
via guided Q&A, saved to its own folder:
generated/<dotted-collection-name>/<SPEC_ID>/<SPEC_ID>.md - NOT under
collections/, which is read-only reference material. No intermediate
specs/ layer and no generic "spec.md" name - the SPEC_ID already uniquely
identifies the folder, so the file inside it is just named after the same
SPEC_ID. /build later generates the role inside that same folder
(<SPEC_ID>/roles/<role_name>/), so everything for one spec - the
behavioral contract and its implementation - stays together as a single
self-contained, reviewable unit, entirely separate from the read-only
reference collections.

This is a BEHAVIORAL spec, not an implementation plan: it describes what
the automation must do, when, and what "success" looks like, in language an
operator/owner can read and approve without knowing Ansible. It deliberately
does NOT contain variable names, task lists, or file layouts - deriving the
technical design (argument_specs, task breakdown, module choices) from the
Requirements and Constraints below is /build's job, not /spec's. If you're
reaching for a variable name or a module while filling this out, stop -
that belongs in /build's output, not here.

Requirements are grouped into the SAME PHASES an Ansible playbook actually
executes in - not as Ansible jargon, but because "what has to be true
before we start, what we check first, what we do, what we check after,
what happens if something goes wrong" is how any careful operator already
thinks about a change, and it maps directly onto what /build generates:

  Initialization        -> what triggers this and what must be set up/
                            captured before anything else happens
                            (-> role dependencies + setup tasks)
  Connection / Access    -> what access/reachability is assumed to already
                            be in place (-> credentials role, become/user)
  Pre-Checks             -> what's verified before acting, including when
                            NOT to act at all (-> guard-clause tasks)
  Main Actions           -> what actually gets done (-> the core tasks)
  Post-Checks & Reporting -> what's verified/measured after acting, and
                            what gets reported, to whom/where
                            (-> register + outcome summary)
  Exception Handling     -> what happens if something goes wrong during
                            execution, or the result isn't what was wanted
                            (-> rescue/failure handling + escalation)

Each requirement is a single EARS (Easy Approach to Requirements Syntax)
sentence:
  - Event-driven:      "When <trigger>, the system shall <response>."
  - Unwanted behavior:  "If <condition>, then the system shall <response>."
  - State-driven:       "While <state>, the system shall <response>."
  - Ubiquitous:         "The system shall <always-true requirement>."
                         (use sparingly - prefer tying it to a trigger)
Every threshold must say inclusive/exclusive. Not every phase needs
multiple requirements - Connection is often one sentence, or "N/A, uses
existing access" - but don't skip a phase silently; say there's nothing
new to add rather than omitting the heading.
-->
## Specification

SPEC_ID: <NAMESPACE-YYYY-NNNN, e.g. AUTO-2026-0055>
TITLE: <short descriptive title>
VERSION: "1.0"
DATE: <YYYY-MM-DD>
OWNER: <email>
STATUS: draft

---
## Target

<What this runs against. Keep HOST/OS as a starting point, but swap in
whatever dimensions actually identify the target in this domain - e.g.
DEVICE/PLATFORM/FIRMWARE for network gear, RESOURCE_TYPE/REGION/ACCOUNT for
cloud, INVENTORY_GROUP for a fleet.>

HOST: <hostnames, inventory group, resource identifiers, or device list>
OS: <OS + version, or platform/firmware>

---
## Intent

<One paragraph, plain language: the operational problem this solves, why
it matters, and the desired end-state. Someone unfamiliar with Ansible
should understand the automation's purpose from this paragraph alone.>

---
## Requirements

### Initialization

<What starts this automation (schedule, threshold, event, manual trigger),
with precise/inclusive-exclusive boundaries, and what must be prepared or
captured before any action is taken (locks, baseline measurements, etc.).>

- When <trigger condition>, the system shall <begin the process / prepare by doing X>.

### Connection / Access

<What access, credentials, or reachability this assumes is already in
place. Often brief - state the assumption even if nothing new is needed.>

- The system shall operate using <existing access/credentials assumption>.

### Pre-Checks

<What's verified before acting - including, explicitly, the condition(s)
under which the system must NOT act at all and should escalate or refuse
instead. Don't skip this even if it feels obvious.>

- If <precondition not met / already in desired state>, then the system shall <skip/no-op>, not <redo the action>.
- If <out-of-bounds/unsafe condition>, then the system shall <escalate/refuse/alert> rather than act.

### Main Actions

<What actually gets done, in response to the trigger, once pre-checks pass.>

- When <pre-checks pass>, the system shall <action>.

### Post-Checks & Reporting

<What's verified/measured once the action completes, and what gets
reported - to whom/where, and in what form (structured data, ticket,
notification).>

- When <action> completes, the system shall <what is measured/reported, and where it goes>.

### Exception Handling

<What happens if the action itself fails or errors partway through
(distinct from "ran fine but didn't fix the problem," which also belongs
here). Cover both: unexpected failure during execution, and the action
completing but not achieving the desired end-state.>

- If <the action fails/errors during execution>, then the system shall <cleanup/rollback/escalation>.
- If <the action completed but the desired end-state was not reached>, then the system shall <retry/escalate/both>.

---
## Constraints

<Non-functional and operational guardrails - things that would make an
otherwise-correct implementation unacceptable here. Idempotency, blast
radius, required accounts/permissions and their scope, timing/scheduling,
change-freeze awareness, rollback expectations. Describe the constraint,
not how to satisfy it in code.>

- Running this automation more than once must not cause errors or duplicate effects.
- <account/permission constraints - who/what this runs as, and why>
- <any other guardrail that bounds the implementation without dictating it>
