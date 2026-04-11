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
  version: "0.1.0"
  protocol-type: open
  schema-version: "0.1.0"
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

## Common Fields

All signals must be JSON objects containing:

- `signal_type` *(string, required)* — one of: `execution`, `outcome`, `escalation`, `partnership`
- `schema_version` *(string, required)* — currently `"0.1.0"`
- `run_id` *(string, required)* — UUID linking related signals (execution + outcome share a run_id)
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
- `patterns` *(object)* — `what_worked`, `what_was_hard`, `skill_gap`, `tsg_gap`, `improvisation`, `recurring_pattern`

### `outcome` signal

Required fields:

- all common fields, with `signal_type: "outcome"`
- `quality_rating` *(integer, required, range 1–5)* — used in the Trust Equation

Optional fields:

- `effort_to_merge` *(string)* — `"none"`, `"minimal"`, `"moderate"`, `"significant"`
- `issues_found` *(array of strings)*

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
- `recommendations` *(array of objects)* — suggested skill or process improvements
- `self_assessment` *(object)* — the reviewing agent's confidence in its own analysis

## Privacy

Signals must never contain:

- Code snippets from the target repository
- Developer names or email addresses
- Access tokens or secrets
- Repository URLs (use anonymized identifiers)

Use bucketed values over precise ones. Prefer opt-in over opt-out.
