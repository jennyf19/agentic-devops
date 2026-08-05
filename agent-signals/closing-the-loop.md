# Closing the Loop: Signal-Consuming Agent Pattern

> The README says "close the loop" but doesn't define how. This document does.

## Purpose

This spec defines the **signal-consuming agent pattern**: the protocol
by which a dedicated agent reads accumulated agent signals, detects recurring
patterns, and takes action when those patterns cross defined thresholds.

This is the operational form of the [partnership signal type](SIGNAL.md).
Where SIGNAL.md defines the *structure* of a partnership signal, this
document defines the *behavior* of the agent that produces them.

It is not code. It is the contract between:
- **Signal-producing agents** (agents that emit execution signals after tasks)
- **Signal-consuming agents** (agents that read and act on accumulated signals)
- **Humans** (who review, approve, and steer the system)

Any agent that consumes signals to improve the system MUST follow this
protocol. The protocol is model-agnostic. It works regardless of which
LLM runs the consuming agent.

---

## 1. What a Signal-Consuming Agent Reads

### 1.1 Primary Input: Pattern Dimensions

The consuming agent reads the pattern dimensions from execution
signals (see [SIGNAL.md](SIGNAL.md)):

| Dimension | What It Tells the Consumer |
|-----------|---------------------------|
| `what_was_hard` | Friction points where agents struggle |
| `skill_gap` | Missing capabilities agents wish they had |
| `tsg_gap` | Missing or inadequate guidance in documentation |
| `recurring_pattern` | Patterns the producing agent has seen before |
| `improvisation` | Novel approaches not covered by existing skills |
| `what_worked` | Effective techniques worth preserving |

The six dimensions above are defined in the `execution.patterns` contract
in [SIGNAL.md](SIGNAL.md).

**Extension dimension** (not in the base schema; add it to your signal schema
if your agents encounter infrastructure blockers):

| Dimension | What It Tells the Consumer |
|-----------|---------------------------|
| `environment_blockers` | External issues (APIs, permissions, infra) |

### 1.2 Secondary Input: Self-Assessment Scores

Used for trend detection and severity weighting:

| Score | Role in Pattern Detection |
|-------|--------------------------|
| `confidence` | Primary health signal. Declining confidence = degrading skill. |
| `accuracy` | Cross-referenced with outcome quality ratings for calibration gap. |
| `completeness` | Low completeness clusters indicate scope creep or missing capabilities. |

### 1.3 Tertiary Input: Outcome Signals

Quality ratings from independent evaluators (human or agent), used to:
- Validate self-assessment calibration (the trust equation from [SIGNAL.md](SIGNAL.md))
- Detect overconfident skills (high self-score, low quality rating)
- Confirm that pattern-driven improvements actually improved quality

### 1.4 Context the Consumer Must Have

Before pattern detection, the consuming agent MUST load:
- The **current known-patterns registry** (§5), to avoid duplicate actions
- The **signal schema** ([SIGNAL.md](SIGNAL.md)), to correctly parse pattern dimensions
- Any **scoring rubric** used by producing agents, to interpret self-assessment scores consistently

---

## 2. How Pattern Detection Works

### 2.1 Definition: What Is a "Pattern"

A **pattern** is a semantically similar value appearing in the same
pattern dimension, across multiple independent signals, within a
defined time window.

Key distinctions:
- Patterns are grouped by **dimension** (`tsg_gap`, `skill_gap`, etc.). A `tsg_gap` and a `skill_gap` about the same topic are two separate patterns.
- Patterns are grouped by **skill** first, then across skills. A `tsg_gap` hitting one skill is a skill-level pattern; the same gap hitting three skills is a systemic pattern.
- **Semantic similarity, not exact match.** "No rollback docs for multi-module" and "multi-module rollback documentation missing" are the same pattern. The consuming agent uses LLM judgment to cluster.

### 2.2 Detection Algorithm

```
For each pattern dimension d in [tsg_gap, skill_gap, what_was_hard,
    improvisation, recurring_pattern]
    (plus environment_blockers if your schema includes it):

  1. COLLECT all non-empty values of d from signals in the time window.
     Deduplicate by run_id so one run contributes at most one occurrence
     to the same dimension and skill.
  2. CLUSTER by semantic similarity (LLM-assisted grouping). Retain the
     source run_ids and representative values for every cluster. If the
     values may describe different concrete problems, keep the cluster
     monitoring-only and request human review.
  3. COUNT unique run_ids per cluster, both per skill and by distinct skill
  4. CLASSIFY an unambiguous cluster as actionable when either:
     a. its count for any skill meets the threshold for d (§2.3), or
     b. it appears across 3 or more distinct skills (§2.3)
     A cluster at threshold - 1 is monitoring-only (§2.4).
  5. MATCH each actionable cluster against the known-patterns registry (§5):
     a. For detected, acknowledged, in-progress, verifying, or wont-fix
        entries, append the new evidence and do not create a duplicate action.
     b. For a resolved entry, reopen that entry as detected when new evidence
        reaches an actionable threshold.
     c. Otherwise, create a new detected entry.
  6. EMIT new and reopened actionable entries as detected patterns.
  7. INCLUDE monitoring-only clusters in the report without registering or
     acting on them.
```

**Note:** `what_worked` is excluded from threshold-based detection. It captures
positive techniques, not problems to solve. The consuming agent SHOULD still
read `what_worked` values to preserve effective patterns in reports and to
inform skill updates, but it does not trigger remediation actions.

After textual pattern detection, evaluate these **skill-health rules** from
self-assessment and escalation signals:

- Emit a `skill_health` pattern with severity CRITICAL when at least 5 unique,
  skill-attributed runs exist in the window and either confidence is 3 or lower
  in 5 or more execution signals, or the escalation rate is greater than 50%.
- Emit a `skill_health` pattern with severity HIGH when confidence declines by
  more than 1.0 points between consecutive windows with at least 5
  unique, skill-attributed runs in each window.
- Emit a `skill_health` pattern with severity HIGH when at least 5 paired
  execution and outcome signals exist for a skill in the window and mean
  confidence exceeds mean `quality_rating` by more than 1.0 points. Pair the
  signals by `run_id`; do not compare unrelated aggregates.

Skill-health patterns use the same registry matching and duplicate-action rules
as textual patterns.

### 2.3 Thresholds

These are the **minimum unique-run occurrence counts** required to trigger
action. Retries or duplicate signals from the same `run_id` count once.
Thresholds are intentionally low because the cost of a false positive (an
unnecessary PR review) is much lower than the cost of a false negative
(a systemic issue going unaddressed).

**Thresholds scale with signal volume.** A team running 10 agent
sessions a week needs a longer window to accumulate signal. A team
running 500 sessions a day can close the loop in hours. Choose the
profile that matches your volume:

| Profile | Signal Volume | Time Window | Rationale |
|---------|--------------|-------------|-----------|
| **Low** | < 50 signals/week | 7 days | Need a full week to accumulate enough signal |
| **Medium** | 50–500 signals/week | 3 days | Patterns emerge within days |
| **High** | 500+ signals/week | 24 hours | Patterns emerge within hours; fast loop is the advantage |

Per-dimension thresholds (apply within the chosen time window):

| Dimension | Threshold | Rationale |
|-----------|-----------|-----------|
| `tsg_gap` | 3 occurrences | Documentation gaps block agents repeatedly; 3 is enough signal |
| `skill_gap` | 3 occurrences | Capability gaps compound quickly |
| `what_was_hard` | 5 occurrences | Higher threshold because friction is common and systemic friction is less so |
| `improvisation` | 3 occurrences | If 3 agents independently invent the same workaround, it should be a skill |
| `recurring_pattern` | 2 occurrences | Agents flagging recurrence is already a strong signal |

If your schema includes `environment_blockers`, use threshold **3 occurrences**
(infra issues affect many agents simultaneously).

At high volume, the consuming agent's scheduled run frequency should
match the window. Run every few hours, not once daily. The loop
compounds faster when the consumer keeps pace with the producers.

Treat these thresholds as starting values. Track rejected or overturned actions
and raise thresholds when false positives consume more review capacity than the
team has budgeted.

**Cross-skill escalation:** If the same semantic pattern appears across
**3 or more different skills**, it is automatically elevated to severity
HIGH regardless of per-skill count.

### 2.4 Severity Classification

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | A `skill_health` rule in §2.2 is met: confidence ≤ 3 in 5+ signals for the same skill within the time window, OR escalation rate > 50% among at least 5 skill-attributed signals (see below) |
| **HIGH** | An actionable textual pattern affects 3 or more skills, OR a `skill_health` confidence-decline or calibration-gap rule in §2.2 is met |
| **MEDIUM** | Pattern crosses threshold within a single skill |
| **LOW** | Pattern approaching threshold (count = threshold − 1), included for monitoring only; it does not enter the registry or trigger remediation |

**Escalation rate** is defined per skill, within the current time window:

```
escalation_rate = (unique run_ids with signal_type "escalation" for skill S in window) / (unique skill-attributed run_ids for skill S in window)
```

"Escalation rate > 50%" means strictly more than half of all signals for a
single skill in the current window explicitly requested escalation. Signals
without a `skill_used` or equivalent skill identifier are excluded from both
the numerator and denominator. Do not classify escalation-rate severity when
fewer than 5 unique, skill-attributed runs exist in the window.

---

## 3. What Happens When a Pattern Crosses a Threshold

When a textual pattern becomes actionable or a skill-health rule fires, the
consuming agent MUST take exactly these actions, in order:

### 3.1 Action Sequence

```
┌─────────────────────────────────────────────────────┐
│  Pattern detected: tsg_gap × 3 in 7d for skill X   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │  1. Register pattern   │  → Add to known-patterns registry (§5)
          │     Status: detected   │     with metadata, evidence, timestamp
          └────────────┬───────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │  2. Take remediation   │  → Depends on dimension and
          │     action             │     severity (§3.2); update the
          └────────────┬───────────┘     registry status for the action
                       │
                       ▼
          ┌────────────────────────┐
          │  3. Emit partnership   │  → Signal type: "partnership"
          │     signal             │     Records the detection and
          └────────────┬───────────┘     action taken (§4)
                       │
                       ▼
          ┌────────────────────────┐
          │  4. Report to humans   │  → Include in daily/weekly report
          │                        │     with evidence and action taken
          └────────────────────────┘
```

### 3.2 Remediation Actions by Dimension

| Dimension | Action | Detail |
|-----------|--------|--------|
| `tsg_gap` | **Open a PR** | Draft the missing documentation section. Include sanitized evidence or a privacy-safe paraphrase of the `tsg_gap` text. Target the skill's documentation. |
| `skill_gap` | **Open an issue** | Document the missing capability with evidence (signal count, affected skills, example scenarios). Label as `skill-gap`. |
| `what_was_hard` | **Report by default** | Take no separate external action. Include the cluster in the final report. If the friction maps to a specific code path, open a PR to improve it. |
| `improvisation` | **Open a PR** | If 3+ agents independently invented the same workaround, propose adding it to the skill as a documented approach. |
| `recurring_pattern` | **Report by default** | Take no separate external action. Include the cluster in the final report. If it suggests a skill update, open a PR. |
| `skill_health` | **Request human review** | Include the score trend, sample size, and time windows in the report. For CRITICAL severity, open an issue assigned to the skill owner; do not infer a code or documentation fix without a textual pattern. |

If your schema includes `environment_blockers`: **Open an issue.** Document the
infrastructure blocker with affected skills and frequency. Label as `infra-blocker`.
Route to the platform team.

Every PR, issue, and report MUST apply the privacy constraints in
[SIGNAL.md](SIGNAL.md). Do not copy repository URLs, code, developer identity,
or secrets from source signals. Use opaque run identifiers and sanitized
summaries.

### 3.3 PR Requirements

When the consuming agent opens a PR:

1. **Title format:** `[Agent Signal] {dimension}: {pattern summary}`
2. **Body MUST include:**
   - The detected pattern (semantic cluster summary)
   - Evidence: number of signals, time window, affected skills
   - Quotes from 2-3 representative signals only after validating the privacy
     constraints in [SIGNAL.md](SIGNAL.md); otherwise use a sanitized paraphrase
   - The proposed fix
   - Link back to the known-patterns registry entry
3. **Labels:** `agent-signal`, `auto-generated`, and the dimension name
4. **Assignee:** The skill owner (if known) or the default team
5. **The PR is a proposal, not a merge.** Humans review and approve.

### 3.4 What the Consumer MUST NOT Do

- **Never merge its own PRs.** All PRs require human review.
- **Never hide a threshold crossing.** New evidence is reported or appended to
  the matching registry entry, even if the consumer "thinks" it is a false
  positive. Do not create a duplicate action for an active entry.
- **Never modify production agent skills directly.** Changes flow through PRs.
- **Never re-raise an active or `wont-fix` entry as a new pattern.** Add the
  evidence to the existing entry. A human may reopen `wont-fix`; a `resolved`
  entry reopens automatically only under the rule in §2.2.

---

## 4. Partnership Signals

When the consuming agent detects a pattern and takes action, it MUST
emit a partnership signal. This makes the consumer's own work
observable and auditable.

### 4.1 Partnership Signal for Pattern Detection

This extends the partnership signal type defined in [SIGNAL.md](SIGNAL.md)
with action-specific fields. The `observed_agent` and `observation`
fields from the base schema are preserved; `action_taken` and
`registry_entry_id` are added by the consuming agent.

```json
{
  "signal_type": "partnership",
  "schema_version": "0.1.0",
  "run_id": "b7c3e921-44a1-4d8f-9e2b-83f6a1d5c402",
  "timestamp": "2026-04-14T14:00:00Z",
  "agent_name": "sre-signal-consumer",
  "observed_agent": "remediation-agent",
  "observed_skill": "cve-remediation",

  "observation": {
    "signal_count_reviewed": 15,
    "time_window": "7d",
    "recurring_patterns": [
      {
        "pattern": "Multi-module rollback documentation missing",
        "dimension": "tsg_gap",
        "frequency": 4,
        "severity": "MEDIUM",
        "current_skill_coverage": "none"
      }
    ]
  },

  "recommendations": [
    {
      "type": "skill_update",
      "target": "cve-remediation",
      "description": "Add multi-module rollback steps to the skill's documentation.",
      "evidence": "4 of 15 sessions hit this gap. All improvised. 2 needed rework.",
      "priority": "high"
    }
  ],

  "action_taken": "pr_opened",
  "action_ref": "pr-123",
  "registry_entry_id": "pat-2026-04-14-001",

  "self_assessment": {
    "confidence": 4,
    "completeness": 3,
    "note": "Reviewed execution signals only. Outcome signals would improve validation."
  }
}
```

### 4.2 Why This Matters

Partnership signals close the observability gap. Without them:
- Nobody knows what the consuming agent detected
- Nobody can audit whether the right action was taken
- The consuming agent's own accuracy can't be evaluated
- The system can't detect when the *consumer itself* needs improvement

With them:
- Every detection is recorded and auditable
- False positive rates can be tracked (pattern detected → PR rejected)
- The consuming agent becomes part of the feedback loop, not above it

---

## 5. Known-Patterns Registry

The registry is the consuming agent's memory. It prevents duplicate actions for
active or `wont-fix` patterns and tracks the resolution lifecycle.

### 5.1 Registry Entry Schema

```yaml
entry_id: pat-2026-04-14-001
detected_at: 2026-04-14T14:00:00Z
dimension: tsg_gap
pattern_summary: "Multi-module rollback docs missing from remediation skill"
status: in-progress  # one of: detected, acknowledged, in-progress, verifying, resolved, wont-fix
severity: MEDIUM  # one of: CRITICAL, HIGH, MEDIUM, LOW
evidence:
  signal_count: 4
  time_window: 7d
  affected_skills:
    - cve-remediation
  representative_run_ids:
    - run_abc
    - run_def
    - run_ghi
  first_seen: 2026-04-11T09:00:00Z
  last_seen: 2026-04-14T08:30:00Z
action_taken: pr_opened
action_ref: "pr-123"
resolution:
  action_completed_at: null
  verification_started_at: null
  resolved_at: null
  resolved_by: null
  resolution_type: null  # pr_merged | issue_closed | wont_fix | superseded
  post_resolution_signal_count: null  # signals after fix, to verify improvement
```

### 5.2 Status Lifecycle

```
detected ───────────────→ in-progress → verifying → resolved
    └──→ acknowledged ──────┘              └──────→ in-progress
    └──────────────────────────────────────→ wont-fix
```

| Transition | Triggered By | Meaning |
|-----------|-------------|---------|
| `detected` → `acknowledged` | Human reviews the report or PR | "We see this, we'll handle it" |
| `detected` or `acknowledged` → `in-progress` | PR opened or issue assigned | Active work underway |
| `in-progress` → `verifying` | Remediation completed | Action is complete; signal evidence is still pending |
| `verifying` → `resolved` | Post-resolution evidence meets §5.3 | Fix confirmed by signal data |
| `verifying` → `in-progress` | Pattern reaches threshold during verification | Fix did not hold; remediation resumes |
| Any non-resolved status → `wont-fix` | Human decision | Pattern is expected, accepted, or outside scope |
| `resolved` → `detected` | Pattern reaches threshold again after resolution | Fix did not hold or conditions changed |

### 5.3 Resolution Verification

A pattern is only `resolved` when ALL conditions are met:
1. The remediation action was completed (PR merged, issue closed), and the
   entry moved to `verifying`.
2. At least one complete configured time window has elapsed.
3. For a textual pattern, the window contains at least the dimension's
   threshold number of post-resolution signals for the affected skill. For a
   `skill_health` pattern, it contains at least 5 skill-attributed signals.
4. A textual pattern remains below its action threshold throughout that window,
   or the triggering `skill_health` rule is no longer met.

This prevents premature closure. A merged PR that doesn't actually
fix the problem should not mark the pattern as resolved. Improved confidence is
supporting evidence, not a substitute for the pattern staying below threshold.
If too few post-resolution signals arrive, keep the entry in `verifying` and
report that verification is pending.

### 5.4 Storage

The registry is stored as structured data accessible to the consuming
agent. Choose based on scale:

| Scale | Storage | Access |
|-------|---------|--------|
| < 100 patterns | YAML/JSON file in the repo | Agent reads directly |
| 100–1000 patterns | Database table | Agent queries via API or SQL |
| > 1000 patterns | Dedicated service | API call from agent |

Start simple. A file in the repo is fine until you have enough patterns
to need queryability.

---

## 6. The Complete Loop

This is the protocol in motion, end to end. The pace depends on
signal volume. At high volume, this entire sequence can complete
in a single day:

```
Signal 1:  Agent runs skill
           → emits execution signal
           → signal lands in signal store
           → patterns.tsg_gap: "no rollback docs for multi-module projects"

Signal 2:  Different agent, different repo, same skill
           → same tsg_gap value (semantically)
           → signal count for this pattern: 2

Signal 3:  Third agent, third repo
           → same tsg_gap
           → signal count: 3 → THRESHOLD CROSSED

Next consumer run:  Consuming agent (scheduled):
           1. Reads signals from the configured time window
           2. Clusters tsg_gap values by semantic similarity
           3. Detects: "multi-module rollback docs" cluster has 3 signals
           4. Checks known-patterns registry → not found (new pattern)
           5. Registers pattern: pat-2026-04-14-001, status: detected
           6. Opens PR: adds rollback section to skill documentation
              → registry updated: status → in-progress
           7. Emits partnership signal recording the detection + action
           8. Includes in report: "3 agents hit the same TSG gap..."

After merge:  Human reviews report + PR
              → approves and merges PR
              → registry updated: status → verifying
              → verification window begins

Post-merge:  Agent runs updated skill
             → reads new rollback docs
             → no improvisation needed
             → signal: tsg_gap is empty, confidence is higher

Verification:  Consuming agent checks post-resolution signals
               → tsg_gap cluster does not recur
               → confidence for affected skill improved
               → sufficient signal count + full window confirmed
               → registry updated: status → resolved

               The loop compounded.
```

---

## 7. Implementation Checklist

For teams adopting this pattern with their own signal-consuming agent:

### Required

- [ ] Agent has read access to the signal store
- [ ] Agent has the [signal schema](SIGNAL.md) loaded
- [ ] Agent has a scheduled task that runs at least daily
- [ ] Pattern detection covers all threshold dimensions (§2.1, §2.2)
- [ ] Thresholds are configured (§2.3); start with the defaults
- [ ] Known-patterns registry is initialized (§5)
- [ ] Registry matching prevents duplicate actions and reopens resolved entries
  only when new evidence reaches threshold (§2.2, §5.2)
- [ ] Partnership signals are emitted on every detection (§4)
- [ ] PRs follow the required format (§3.3)
- [ ] Reports include detected patterns with evidence

### Recommended

- [ ] Post-resolution verification enforces the minimum window and signal count
  before marking an entry resolved (§5.3)
- [ ] Cross-skill escalation is enabled (§2.3)
- [ ] The consuming agent's own partnership signals are included
  in the next cycle's analysis (the loop observes itself)
- [ ] False positive tracking: count of PRs opened vs PRs rejected

### Optional (Future)

- [ ] Bidirectional: producing agents query the registry mid-run
  to check if their current struggle is a known pattern
- [ ] Multi-consumer coordination: multiple consuming agents share
  the same registry to avoid duplicate PRs
- [ ] Trend forecasting: predict which patterns will cross threshold
  based on velocity

---

## 8. Relationship to Other Protocol Documents

| Document | What It Defines | How This Spec Relates |
|----------|----------------|----------------------|
| [README.md](README.md) | The Agent Signals protocol and self-improving loop | This spec formalizes how the loop closes |
| [SIGNAL.md](SIGNAL.md) | Signal types, field contracts, trust equation | This spec defines the behavior of the agent that produces partnership signals |
| [partnership-framework.md](partnership-framework.md) | Why partnership framing produces honest signals | This spec depends on honest signals: garbage in, garbage out |
| [quickstart.md](quickstart.md) | Emit your first signal in 5 minutes | Start there; come here when you're ready to build the consumer |

---

## What We Learned

From building this pattern into a production system across hundreds of
remediation sessions:

1. **Low thresholds can work when review cost is budgeted.** Three occurrences
   in seven days sounds aggressive. In practice, it can surface systemic
   failures before they repeat for weeks. False positives still consume human
   attention, so track rejected actions and tune the defaults to available
   review capacity.

2. **Semantic clustering is essential.** Agents describe the same
   problem in different words. Exact-match pattern detection misses
   most patterns. LLM-assisted clustering catches them.

3. **Resolution verification prevents false confidence.** Without
   post-resolution signal checking, merged PRs get marked "resolved"
   even when the fix didn't work. Requiring signal improvement after
   merge catches this.

4. **The consuming agent needs to be in the loop too.** When the
   consumer emits partnership signals, you can track its own false
   positive rate and improve its detection over time. An unobserved
   observer is a liability.

5. **Humans approve, agents propose.** Every team that tried letting
   agents merge their own improvements eventually rolled it back.
   The human review step is not incidental overhead. It is the trust mechanism
   that makes the whole system acceptable.
