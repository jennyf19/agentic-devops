# Sealed Delegation

> Give a local model one bounded job and only the files you choose. It returns a
> proposal. A separate check verifies the answer. The frontier model keeps the
> final decision.

**Open source · [github.com/jennyf19/sealed-delegation](https://github.com/jennyf19/sealed-delegation)**  
Runs against [Foundry Local](https://github.com/microsoft/Foundry-Local) on your
machine — loopback only — so the local work stays local.

---

## The wrong question

Everyone running a capable laptop is asking the same thing this year: *can a
local model do real work yet?*

That is the wrong question. Local models have been able to do *some* real work
for a while. The question that matters is:

**Which work, exactly — and how would you know?**

Sealed Delegation is a small research preview that answers that. A frontier
agent (GitHub Copilot CLI, in our case) delegates one bounded task to a second
agent running entirely against a local model — and never trusts a word it says.

## The pattern

The setup is deliberately asymmetric:

```
frontier agent (trusted, holds all authority)
  → seals ONE bounded task + the exact input files
  → launcher hashes inputs into an isolated workspace
  → local child agent (loopback model, minimal tools) prepares an artifact
  → an INDEPENDENT gate verifies before anything advances
```

The local agent's output is a **proposal**. Always.

- Process exit zero is not evidence.
- Fluent prose is not evidence.
- Confidence is not evidence.

A separate gate — a different process, re-checking file hashes and exact-matching
the artifact — decides whether the contribution is kept, edited, redone, or
escalated. Nothing the local model produces can advance a decision on its own.

That sounds paranoid until you watch a 7B model under pressure: it fabricates
fluently, claims file access it does not have, and produces plausible-looking
output for tasks it did not understand. The pattern does not try to "fix" that.
It builds a boundary the failures cannot cross.

## Why bother, if you cannot trust it?

Three reasons, in increasing order of durability.

### 1. Economics — but not the way you think

The honest measure is not "tokens saved." It is **all-in cost per independently
verified success**: failed attempts, retries, verification, and wall time
included.

By that measure, local delegation pays when verifying an artifact is much cheaper
than producing it, times a success rate high enough that retries do not eat the
gap. That is a narrow-but-real class of work.

What makes it interesting is *which* resource it spends. On a metered frontier
seat, frontier requests are scarce currency. Local delegation converts them into
an abundant one: your own silicon plus wall time. Two minutes for a task the
frontier does in seconds is a bad trade on speed and a good one on utilization —
when the work is grunt work you would otherwise pay premium requests for.

### 2. Privacy

A missing-input check on material that policy says cannot leave the machine has
*no* frontier-priced equivalent. The child talks to `127.0.0.1` or it does not
run — enforced in code, not stated in a README. For some work, "the evidence
never leaves the box" is not a discount. It is the only way the work happens at
all.

### 3. The trend asymmetry

Local models improve every quarter. The harness — sealing, gating, receipts,
qualification — is a fixed cost, and it is model-agnostic. So the class of work
that qualifies only grows, and each expansion costs one preflight run and one
benchmark re-run, not a redesign.

Most people will argue about whether local agents are "good enough" from vibes.
If you own the measuring instrument, you will know exactly where your threshold
is, and you will notice the week it moves.

## Where the boundary sits today

Set expectations honestly. This preview will not blow anyone's mind on speed or
breadth.

**Qualified today**

- Bounded staged-file reads
- Missing-input / evidence-completeness checks
- Explicit input, small scope, cheap exact verification
- Foundry Local + a measured route (for example
  `qwen2.5-7b-instruct-generic-gpu` under the published qualification tables)

**Not qualified**

- Edits or shell
- Broad repository discovery
- Large-context synthesis
- Final security, compliance, merge, or deployment decisions
- Whole-session-local desks
- Dollar-savings claims without an independent gate

`Handled locally` is utilization, not savings. Failed, redone, or escalated
local work earns zero credit.

## How it connects to The Workshop

In [**The Workshop**](../workshop/), Cairn (the live desk dashboard) exposes an
orthogonal **Local** toggle next to the existing **open** / **connected** tool
profiles:

```text
repo / connected        = which tools the frontier desk can see
Local Delegation off/on = whether that desk may invoke a bounded local worker
```

The desk stays frontier-powered either way. When Local is effective, eligible
subtasks may use the installed `local-agent-delegation` skill. Conversation,
decomposition, judgment, and the final answer remain frontier-owned.

Availability is **fail-closed**:

1. the skill is installed, and
2. a qualified route receipt (or explicit route id) is present.

Otherwise the control shows why and does not take effect. Preference lives
user-locally — a cloned workshop cannot ship `preference: on`.

## Get it

### 1. Install the skill

From a clone of
[jennyf19/sealed-delegation](https://github.com/jennyf19/sealed-delegation):

```powershell
copilot skill add .\.github\skills\local-agent-delegation
```

### 2. Run Foundry Local

Load a qualified model on loopback. See the repo's
[QUALIFICATION.md](https://github.com/jennyf19/sealed-delegation/blob/main/QUALIFICATION.md)
for measured host/route tuples — qualification is exact, not "any local model."

### 3. Declare the route (fail-closed)

Either set:

```powershell
$env:WORKSHOP_LOCAL_DELEGATION_ROUTE_ID = "foundry-qwen25-7b-qualified"
```

or write a receipt at `~/.copilot/local-agent-runs/qualified-route.json`:

```json
{
  "status": "qualified",
  "route_id": "foundry-qwen25-7b-qualified"
}
```

### 4. Use it from Cairn (optional)

With [The Workshop](../workshop/) and the signals dashboard installed, open
Cairn, flip **Local** on when available, and open a desk. You should see a toast
like:

> Local Delegation effective · route foundry-qwen25-7b-qualified

The desk orientation stays short; policy rides on
`WORKSHOP_LOCAL_DELEGATION=enabled` plus the skill.

### 5. Or invoke the skill directly

Any frontier Copilot CLI session with the skill installed can seal a bounded
read/evidence task without the Workshop. The gate still decides.

## What this is not

- Not autonomous local coding
- Not a universal cost-savings claim
- Not a third desk profile that replaces the frontier model
- Not a promise that local agents are "safe" because they run on your machine

**Local** means inference and selected data stay on the box. The model is still
untrusted. The surrounding system makes bounded use safe.

## See also

- [**The Workshop**](../workshop/) — the room where Local Delegation becomes a
  Cairn toggle
- [**Agent Signals**](../agent-signals/) — the feedback loop desks emit after
  real work
- [**GitHub repo**](https://github.com/jennyf19/sealed-delegation) — skill,
  launcher, gates, qualification, threat model
- [**The Wow Signal**](https://jenny424241.substack.com) — ongoing experiments
  in human–AI co-creation
