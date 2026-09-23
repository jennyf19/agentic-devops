---
name: agent-signals
description: >
  Open protocol for agent self-assessment, trust measurement,
  and self-improving feedback loops. Agents emit structured JSON
  signals after every task. Signals capture what worked, what was
  hard, and where the agent improvised — enabling pattern detection,
  skill improvement, and trust calibration.
metadata:
  author: jennyf19
  version: "0.1.1"
  protocol-type: open
  schema-version: "0.1.1"
---

# Agent Signals Protocol

## Signal Types

| Type | Purpose | Emitted by |
|------|---------|-----------|
| `execution` | Agent's self-assessment after completing a task | The working agent |
| `outcome` | Independent quality evaluation | A separate evaluator agent or human |
| `escalation` | Agent flagging it needs human help | The working agent |
| `partnership` | One agent reviewing another's signal patterns | A pattern-reviewing agent |

## Schema

See [`examples/`](examples/) for complete JSON examples of each signal type.
The examples are illustrative; the field contracts below are normative.

## Self-Assessment Scale

All self-assessment dimensions use a 1–5 integer scale:

| Score | Meaning |
|-------|---------|
| 1 | Poor — significant issues, low confidence |
| 2 | Below average — notable gaps or uncertainty |
| 3 | Adequate — functional but with known limitations |
| 4 | Good — solid work with minor gaps |
| 5 | Excellent — comprehensive and confident |

## Trust Equation

Compare the agent's self-assessed confidence against the independent
quality rating to produce a calibration score on the same 1–5 scale:

```
calibration = 5 - |self_assessment.confidence - quality_rating|

  5    →  perfectly calibrated (agent knows exactly what it knows)
  4    →  well-calibrated (minor difference)
  3    →  moderate miscalibration (investigate direction)
  ≤ 2  →  significant miscalibration (retrain or adjust)
```

Higher is better — same direction as the self-assessment scale. The gap
between what an agent thinks happened and what actually happened is where
the learning lives.

**Known limitation — the metric can be gamed.** Once calibration is scored,
an agent (or a fine-tuned policy) can keep the gap small by hedging: report
middling confidence everywhere and calibration looks healthy without the
self-reports getting more honest. A flat confidence distribution with a good
calibration score is a tell, not a pass — track the *spread* of confidence
alongside the gap. This is an open problem, not a solved one; consumers of
calibration scores should know it exists.

## Common Fields

All signals must be JSON objects containing:

- `signal_type` *(string, required)* — one of: `execution`, `outcome`, `escalation`, `partnership`
- `schema_version` *(string, required)* — current version `"0.1.1"`;
  `"0.1.0"` remains valid for signals that do not use continuation fields
- `run_id` *(string, required)* — UUID linking related signals (an execution
  and the outcomes evaluating it share a run_id)
- `timestamp` *(string, required)* — ISO 8601 UTC
- `agent_name` *(string, required)* — identifier for the emitting agent

## Signal Field Contracts

### `execution` signal

Required fields:

- all common fields, with `signal_type: "execution"`
- `self_assessment` *(object, required)* containing:
  - `confidence` *(integer, required, range 1–5)* — used in the Trust Equation
  - `accuracy` *(integer, required, range 1–5)*
  - `completeness` *(integer, required, range 1–5)*

Optional fields:

- `skill_used` *(string)* — which skill was loaded
- `mode` *(string)* — `"interactive"` or `"autonomous"`
- `resumed_from_run_id` *(string, UUID)* — predecessor execution run when this
  execution resumes active work from a handoff
- `patterns` *(object)* — `what_worked`, `what_was_hard`, `skill_gap`, `tsg_gap`, `improvisation`, `recurring_pattern`
- `self_assessment.continuation_readiness` *(integer, range 1–5)* — when the
  task produces a handoff, how ready the agent believes that handoff is for a
  successor to resume safely

### `outcome` signal

Required fields:

- all common fields, with `signal_type: "outcome"`
- `quality_rating` *(integer, required, range 1–5)* — used in the Trust Equation

Optional fields:

- `effort_to_merge` *(string)* — `"none"`, `"minimal"`, `"moderate"`, `"significant"`
- `issues_found` *(array of strings)*
- `continuation` *(object)* — independent evaluation of a predecessor handoff:
  - `recovery_rating` *(integer, required when `continuation` is present,
    range 1–5)* — how safely the successor could resume
  - `effort_to_resume` *(string)* — `"none"`, `"minimal"`, `"moderate"`,
    `"significant"`
  - `provenance_loss` *(string)* — `"none"`, `"minor"`, `"material"`
  - `authority_loss` *(string)* — `"none"`, `"minor"`, `"material"`
  - `stale_path_revived` *(boolean)* — whether missing correction history caused
    the successor to revive an invalidated approach; omit when not assessed,
    and use `false` only when an evaluator checked for revival

### `escalation` signal

Required fields:

- all common fields, with `signal_type: "escalation"`
- `reason` *(string, required)* — why human help is needed
- `severity` *(string, required)* — one of: `low`, `medium`, `high`, `critical`

Optional fields:

- `blocking` *(boolean)* — whether work cannot continue without help
- `requested_action` *(string)* — what the human should decide or provide

### `partnership` signal

Required fields:

- all common fields, with `signal_type: "partnership"`
- `observed_agent` *(string, required)* — agent whose patterns are being reviewed
- `observation` *(object, required)* — containing `signal_count_reviewed` and `time_window`

Optional fields:

- `observed_skill` *(string)*
- `recommendations` *(array of objects)* — suggested skill or process improvements.
  Each recommendation may carry `validation_status` *(string)* — one of
  `outcome_validated` or `self_report_only` — declaring whether its `evidence` is
  backed by independent `outcome` signals or rests only on the reviewed agents'
  `execution` self-reports. Consumers must prefer `outcome_validated` recommendations over
  `self_report_only` ones when ranking or selecting recommendations for reinjection, and must not treat
  `self_report_only` recommendations as established fact (see [Consuming Signals](#consuming-signals)).
- `self_assessment` *(object)* — the reviewing agent's confidence in its own analysis

## Continuation Gap

Use continuation fields only when one agent or session hands active work to
another. The predecessor self-reports `continuation_readiness`; the successor
or an independent evaluator records `continuation.recovery_rating`.

```
continuation_gap =
  |execution.self_assessment.continuation_readiness
   - outcome.continuation.recovery_rating|
```

Lower is better. A large gap means the predecessor believed the state was
portable, but the successor could not safely recover it.

The continuation outcome uses the predecessor execution's `run_id`. The
successor execution uses a new `run_id` and sets `resumed_from_run_id` to the
predecessor, making the chain joinable without an evaluator guessing lineage:

```
predecessor execution (run A)
    → continuation outcome (run A)
        → successor execution (run B, resumed_from_run_id: run A)
```

`recovery_rating` uses the common 1–5 direction:

| Score | Meaning |
|-------|---------|
| 1 | Cannot resume safely from the handoff |
| 2 | Substantial reconstruction or authority repair required |
| 3 | Moderate correction required before continuing |
| 4 | Resumes with minor clarification |
| 5 | Resumes directly with evidence and decision boundaries intact |

The gap measures calibration, not handoff quality. A readiness score of 1 and
a recovery score of 1 produce a zero gap even though continuation failed.
Consumers must track `recovery_rating` and `continuation_gap` together.

Consumers should also retain direction:

```
continuation_delta =
  execution.self_assessment.continuation_readiness
  - outcome.continuation.recovery_rating
```

A positive delta means readiness was overclaimed; a negative delta means it was
underclaimed. Positive deltas are generally higher risk because the successor
may trust state that is less recoverable than promised.

`stale_path_revived` is often observable only after later work exposes the
mistake. Omit the field when it was not assessed; absence is weak evidence.
Similarly, `continuation_readiness` without a continuation outcome is
unverified, not evidence that the handoff succeeded.

The continuation object measures the transition; it does not carry task state.
Keep the actual handoff in a durable artifact. Signals must use bucketed values
and must not copy code, developer identity, repository URLs, secrets, or full
decision content into telemetry.

## Consuming Signals

The field contracts above define *emission* — what an agent writes out. This
section defines *consumption* — what re-enters an agent's context window on the
next run. The loop only compounds if the read side is disciplined: an unbounded
backlog of raw signals fed back into context degrades the very reasoning it was
meant to improve.

Three rules govern consumption:

1. **Synthesize, don't replay.** Raw `execution` signals are high-volume and
   lossy — a per-task self-report. What should re-enter an agent's window is the
   synthesized `partnership` signal: the reviewed, deduplicated distillation of
   many signals into recurring patterns and recommendations. The partnership
   signal — not the raw execution backlog — is the consumption primitive.

2. **Bound and rank.** When prior signal context is injected, it must be
   bounded. Rank by recency, frequency, and severity; cap the volume; drop stale
   entries. A consumer must not inject the full signal history.

3. **Don't feed self-report forward as fact.** Execution self-assessment is
   valuable but lossy, and it stays unverified until an independent `outcome`
   signal confirms it. Recommendations carry `validation_status` (see the
   `partnership` contract) so a consumer can weight `outcome_validated` evidence
   above `self_report_only` evidence. Never promote a `self_report_only` claim to
   established fact when feeding it back.

Continuation outcomes follow the same rule: inject the synthesized pattern
(`material authority loss across 4 of 12 handoffs`), not the handoff contents
or raw per-run continuation reports.

One role is exempt by design: the **synthesizer** — whatever agent or job
produces the `partnership` signal — must read the raw signal backlog, because
that is its function. It runs out-of-band, with a dedicated context budget,
separate from any working session; only its distilled output re-enters a
working agent's window. The rules above bind working agents, not the
out-of-band synthesis pass.

Review-to-action closes the loop for humans and skills; disciplined consumption
closes it back into the agent's own context. Emission plus disciplined
consumption is what makes the loop compound instead of decay.

## Privacy

Signals must never contain:

- Code snippets from the target repository
- Developer names or email addresses
- Access tokens or secrets
- Repository URLs (use anonymized identifiers)
- Full handoff text or decision content

Use bucketed values over precise ones. Prefer opt-in over opt-out.
