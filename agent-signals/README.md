# Agent Signals

> What persists when the model changes, the tools evolve, and the platform shifts?
> The feedback loop.

Agent Signals keeps the working AI in the feedback loop: contributing what
worked, where it got stuck, what it tried, and what help it needs. Humans and
other agents can review those contributions, improve the shared skills,
tools, documentation, and context, and check whether the next run is better.

**Agent Signals makes the message board a first-class citizen.** Not a new
global chat platform, but a durable, scoped place for feedback and requests
for help, with clear readers, owners, and permissions.

---

## The Problem Nobody Talks About

A task can finish while its useful experience disappears with the session.
An agent can also get stuck before there is a finished artifact to review.
If nobody asks the working agent, both kinds of feedback are easy to miss:

- What was hard about this fix?
- What did the agent try, and what remains uncertain?
- Where did the documentation fall short?
- What does it need to continue safely?
- What would help the next agent avoid the same problem?

External evaluation matters, but it cannot replace the agent's contribution.
Agent Signals is not just telemetry about AI or a scorecard for ranking agents.
It gives the participant doing the work a supported way to contribute to the
system, including: **"I cannot complete this under current constraints; here
is what I need."** An honest blocked result is useful work.

## Why This Matters More Than the Model

Models will change. So will the tools, platforms, and agents doing the work.

What doesn't change is the loop:

```
Agent does work
    -> During work: checkpoint or request help
        -> Human or authorized agent responds, or work safely pauses
    -> After work: capture useful experience and available outcome evidence
        -> Agents and humans review patterns and propose an improvement
            -> Reviewed change reaches the next run
                -> Assess whether it helped
```

This loop is the infrastructure. Not the model. Not the tool. **The loop.**

Three useful perspectives inform this design:

1. **Make uncertainty reportable.** OpenAI's research on
   [how confessions keep language models honest](https://openai.com/index/how-confessions-can-keep-language-models-honest/)
   explores incentives for a separate account of mistakes and limitations.

2. **Make work checkable.** Anthropic's work on
   [scalable oversight](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf)
   explores how to support evaluation when direct human oversight is difficult.

3. **Keep the agent in the conversation.** The
   [Engineering at Microsoft article](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/)
   describes experience treating agents as collaborators rather than automation.

These are reasons to explore cooperative feedback, not universal proof that
partnership or self-report outperforms every alternative. The loop still needs
evidence from the work where it is used.

---

## Principles

1. **Capture** a task-level account of the work: actions tried, results,
   uncertainty, partial completion, and help needed. This is explicit reporting,
   not access to hidden chain-of-thought or a guarantee of truthful self-report.

2. **Honor** the developer's time and the agent's limits. A failed telemetry
   export should not block unrelated work. A task that needs a decision or
   permission should pause safely, with the unresolved request visible.

3. **Earn** trust through transparency. Tell people what is being captured,
   who can read it, and why. Make system health visible: stuck work, unanswered
   requests, and recurring tool, context, or documentation gaps.

4. **Close** both loops. Help requests need a recipient and a response or a
   safe pause. Learning needs review, a change to an artifact or workflow,
   and a later check that the change helped.

5. **Keep** signals privacy-safe by default. No code snippets, no developer
   names, no secrets. Use bucketed values over precise ones. Prefer opt-in
   over opt-out.

6. **Support** honest assessment rather than rewarding high scores. Make
   "blocked" and "I don't know" useful contributions, not failures to conceal.

7. **Make** the channel inspectable and governed. Share schemas and handling
   rules with participants. Scope access, retention, and routing deliberately;
   public protocol documentation does not mean public runtime signals.

8. **Treat** a signal as a contribution, not an instruction, permission grant,
   or established fact. Check its origin, evidence, and limits before acting.
   Even reviewed feedback must not bypass the recipient's own authority checks.

9. **Leave** something useful for the next session. Preserve learning through
   reviewed skills, docs, tools, and context, not automatic model-weight updates.

Cooperative feedback and incentives are design choices, not guarantees against
adversarial behavior. Reviewers still need to reject poisoned or misleading
feedback rather than execute advice or pass it forward unchecked.

---

## During Work: A Supported Route to Help

The current protocol defines an **`escalation` signal** with a reason, severity,
and optional `blocking` and `requested_action` fields. That is a request format,
not a help-routing service.

**Recommended lifecycle for an implementation:**

1. The agent records a checkpoint or escalation when it cannot proceed,
   stating what it tried and what fixture, context, decision, or access it needs.
2. The request reaches a designated human or authorized agent in the scoped
   channel. The requester can see whether it was received and acknowledged.
3. The recipient answers within their authority. The agent checks the answer
   before resuming; if no answer arrives within the agreed response window, or
   the answer is insufficient, work remains safely paused and visibly unresolved.

Writing a blocked event to an unread log is not this loop. Choose an owner,
notification path, response window, and a way to record the answer. Acknowledging
a request is not the same as resolving it or granting permission.

**Illustrative example:** an agent has made a dependency update but cannot
check it because the task's test fixture is missing. It asks for the fixture
instead of claiming completion. A human supplies approved fixture setup
instructions; the agent runs the relevant checks and reports what remains
uncertain. A reviewed update to the skill preserves those instructions.
The next agent uses them, and its results help assess whether the gap is fixed.

This repository provides the signal contract and examples. Checkpoint storage,
delivery, acknowledgement, replies, timeouts, and safe pause/resume behavior
need to be implemented in the host workflow; no end-to-end help broker ships
here.

---

## What a Signal Looks Like

Agent Signals are JSON documents. Execution and outcome signals capture the
work and its assessment; escalation and partnership signals support help and
improvement. The examples below are **illustrative**, not production results.
See [SIGNAL.md](SIGNAL.md) for the v0.1.0 field contracts.

**Execution signal:** the working agent's self-assessment, captured when work
finishes or stops:

```json
{
  "signal_type": "execution",
  "schema_version": "0.1.0",
  "run_id": "ae02e3f3-42e9-43bd-ae7a-19757f5456ed",
  "timestamp": "2026-04-08T03:00:00Z",
  "agent_name": "cve-remediation-agent",
  "skill_used": "cve-remediation",
  "mode": "interactive",

  "self_assessment": {
    "accuracy": 4,
    "completeness": 5,
    "confidence": 3,
    "tsg_alignment": 2,
    "developer_experience": 4
  },

  "patterns": {
    "what_worked": "Standard Maven dependency update path.",
    "what_was_hard": "Transitive dependency conflict required manual resolution order.",
    "skill_gap": "No handling for Gradle Kotlin DSL projects.",
    "tsg_gap": "Missing rollback steps for multi-module projects.",
    "improvisation": "Adapted single-module rollback pattern to multi-module. Untested.",
    "recurring_pattern": "Third time this week seeing this transitive conflict."
  }
}
```

**Outcome signal:** a separate evaluator's assessment of available evidence:

```json
{
  "signal_type": "outcome",
  "schema_version": "0.1.0",
  "run_id": "ae02e3f3-42e9-43bd-ae7a-19757f5456ed",
  "timestamp": "2026-04-08T03:15:00Z",
  "agent_name": "quality-evaluator",
  "quality_rating": 4,
  "effort_to_merge": "minimal",
  "issues_found": ["Edge case in test coverage for multi-module rollback"]
}
```

**Escalation signal:** an agent asking for help during work:

```json
{
  "signal_type": "escalation",
  "schema_version": "0.1.0",
  "run_id": "c7f1a902-88d4-4e1b-b3a6-5e9d22f14c01",
  "timestamp": "2026-04-08T04:00:00Z",
  "agent_name": "dependency-update-agent",
  "reason": "The required test fixture is missing. I checked the documented setup steps but cannot verify the update.",
  "severity": "medium",
  "blocking": true,
  "requested_action": "Please provide approved fixture setup instructions. Verification is paused until they are available."
}
```

**Partnership signal:** an agent reviewing contributions and proposing an
improvement:

```json
{
  "signal_type": "partnership",
  "schema_version": "0.1.0",
  "run_id": "f4a18c67-2b91-4d3e-a891-7c4e92d38f10",
  "timestamp": "2026-04-08T05:00:00Z",
  "agent_name": "pattern-reviewer",
  "observed_agent": "cve-remediation-agent",
  "observed_skill": "cve-remediation",

  "observation": {
    "signal_count_reviewed": 12,
    "time_window": "7d",
    "recurring_patterns": [
      {
        "pattern": "Transitive dependency conflicts in multi-module projects",
        "frequency": 4,
        "severity": "high",
        "current_skill_coverage": "none"
      }
    ]
  },

  "recommendations": [
    {
      "type": "skill_update",
      "target": "cve-remediation",
      "description": "Add multi-module dependency resolution strategy.",
      "evidence": "4 of 12 sessions hit this gap. All improvised. 2 needed rework.",
      "validation_status": "self_report_only",
      "priority": "high"
    }
  ],

  "self_assessment": {
    "confidence": 4,
    "completeness": 3,
    "note": "Reviewed execution signals only. Would benefit from outcome signals to validate."
  }
}
```

The execution signal is the agent's account. The outcome signal adds evidence
from a separate review, not infallible ground truth. A human reviewer can miss
an issue; an external model can share the working agent's blind spots. A
different evaluator is not automatically statistically independent.

Use `run_id` to correlate related signals, and retain authorized access to the
supporting artifact and review context. Record who or what evaluated which
artifact version, with which rubric, and what could not be observed in your
evaluation system. The base outcome fields do not capture all that provenance.
If an outcome is unavailable, track that absence in the host workflow rather
than inventing a score. An emitted v0.1.0 outcome still requires a 1-5 rating;
"unknown" is not a replacement value for that field.

### The Trust Equation

**Compare like with like, not just numbers with the same range.** An agent's
general confidence and a reviewer's quality rating mean different things even
when both are 1-5. Their difference is not an honesty score.

The v0.1.0 protocol documents a legacy confidence/quality heuristic. Its JSON
contract remains unchanged here. It does not supply the evaluation identity
and rubric metadata needed for the stronger comparison below.

**Conceptual comparison, not a new wire schema or a shipped calculator:**

```text
Same task and artifact version
Same evaluation name: "fixture coverage"
Same rubric version: "1"
Compatible ranges: both 1-5, with the same meanings and direction
Self-rating: 4; external rating: 3
Discrepancy: |4 - 3| = 1

Missing score or metadata, or incomparable evaluations -> unknown, not zero
```

Only compute a discrepancy when those conditions hold. Even then, disagreement
is evidence to investigate calibration, rubric interpretation, or evaluator
error, not proof of honesty or dishonesty. Agreement is not proof of correctness
either. Inspect the work, sample size, and evaluation limits before drawing
conclusions.

---

## The Self-Improving Loop

[Agent Skills](https://agentskills.io) define the input: how agents receive
instructions. Agent Signals define how agents contribute feedback, during
and after the work. Review and applied improvements connect the two.

```
Agent Skills (input) -> Agent works -> Agent Signals (feedback)
 "here's what to do"     (any model)    "here's what I tried and need"
                                                 |
                                      Agent and human review
                                      Pattern detection
                                      Proposed improvement
                                                 |
                                      Reviewed change applied
                                      Next run + outcome assessment
```

A reviewing agent can connect recurring reports, propose a missing section
of a skill, and leave a partnership signal explaining its evidence and limits.
Humans review the change before it becomes shared guidance. Not every report
is actionable, and a proposal is not yet an improvement.

The message board can be as small as access-controlled files and an agreed
review workflow. What matters is that contributions survive, have an audience,
and can lead to reviewed changes. Do not load an unchecked backlog into the
next agent's context. Prefer bounded, relevant summaries with provenance and
validation limits. The [Closing the Loop pattern](closing-the-loop.md) gives
the detailed review, registry, and post-change assessment lifecycle.

---

## What We Learned Building This

Lessons from using Agent Signals in remediation work:

1. **Optional capture is easy to miss.** Make reporting an explicit workflow
   checkpoint, including when work stops incomplete. Do not wait until the end
   to raise a blocker that needs an answer now.

2. **Closing sessions can lose signals.** Capture the post-work account before
   the closing message when possible. If capture fails, make that visible;
   never claim it succeeded or prevent a needed stop just to produce telemetry.

3. **The final state is not the whole account.** Ask for concrete attempts,
   observed results, and course corrections, not hidden reasoning.

4. **Visibility makes people participants.** Explain the capture and share
   useful feedback, rather than making people subjects of silent monitoring.

5. **Self-report and review are useful together.** Comparable assessments can
   expose calibration problems; differing accounts can also reveal missing
   context, weak rubrics, or evaluator mistakes.

---

## Two Capture Paths, Two Reliability Profiles

**Execution signals and outcome signals fail in different ways.** Neither
replaces the other.

An execution signal depends on capture while the agent or host still has the
relevant account. A session can close, a run can be interrupted, or emission
can fail. In-run checkpoints can preserve some useful context earlier, but
they do not make reporting lossless.

An outcome signal can often be produced later from a durable PR, commit,
test result, or other artifact. That separates review from the original
session's lifetime. But artifacts may be missing or inaccessible, evaluation
may never run, and the reviewer may see only part of the work.

Use both: the agent's contribution explains what it encountered and needs;
artifact-based review can corroborate or challenge claims. Preserve provenance
and uncertainty for each. Neither is a complete record by itself.

**No signal does not mean healthy.** When expected emissions are missing,
consider instrumentation, sampling, storage, and export failures as well as
task failure or interruption. Show missing coverage and unanswered requests
alongside the signals you received. A quiet dashboard cannot resolve a
request for help.

## OpenTelemetry and the Loop

OpenTelemetry can transport and correlate events with other operational
evidence. It is not itself the persistent message board, assistance broker,
or skill-update system. Those responsibilities remain with the host workflow
and its reviewed artifacts.

This repository does not ship an OTel exporter, and Agent Signals-specific
OpenTelemetry conventions are not an accepted standard. An adapter is a
possible integration, not a prerequisite for starting with local files.

## Getting Started

### 1. Add a signals directory to your project

This is the protocol convention. `signals/` holds your signal *definitions* —
the schema, examples, and adapters. Runtime signal *output* goes to `.signals/`
(see step 2). Add a `signals/` directory alongside your agent code:

```
your-project/
├── signals/
│   ├── SIGNAL.md             # Required: your signal schema + metadata
│   ├── examples/             # Optional: example signals for reference
│   │   ├── execution.json
│   │   ├── outcome.json
│   │   ├── escalation.json
│   │   └── partnership.json
│   └── adapters/             # Optional: dispatch implementations you supply
│       ├── github-issues/
│       ├── opentelemetry/
│       └── local-file/
├── skills/                   # Your agent skills (input)
└── ...
```

`SIGNAL.md` declares what your agent signals look like — the schema, the
fields, what each rating means. This is the contract. Other agents and humans
read this to understand what your signals mean.

Copy the illustrative [execution](examples/execution.json),
[outcome](examples/outcome.json), [escalation](examples/escalation.json), and
[partnership](examples/partnership.json) examples and adapt their content.

### 2. Capture when work finishes or stops; request help during work

Use an execution signal for the post-work account, including incomplete work.
Raise an escalation when help is needed, rather than waiting for completion.
For a local-file starting point, replace these illustrative values with a
task-level account before running the snippet:

```python
import json, os, uuid
from datetime import datetime, timezone

# Create this once per task and reuse it for related signals.
run_id = str(uuid.uuid4())

signal = {
    "signal_type": "execution",
    "schema_version": "0.1.0",
    "run_id": run_id,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "agent_name": "my-agent",
    "skill_used": "my-skill",
    "self_assessment": {
        "accuracy": 4,       # 1-5: how correct was the output?
        "completeness": 3,   # 1-5: how much of the task was finished?
        "confidence": 2      # 1-5: how sure are you about the above?
    },
    "patterns": {
        "what_worked": "...",
        "what_was_hard": "...",
        "skill_gap": "...",
        "tsg_gap": "..."
    }
}

# Local capture only; this does not notify a help recipient.
os.makedirs(".signals", exist_ok=True)
signal_path = f".signals/{signal['run_id']}-execution.json"
with open(signal_path, "x", encoding="utf-8") as f:
    json.dump(signal, f, indent=2)
```

This writes one execution signal locally. Keep the same `run_id` for related
outcomes and escalations, and give each stored event a distinct filename so
it cannot overwrite another. The snippet uses exclusive creation to surface
a filename collision rather than silently replacing a signal.

Make capture an explicit checkpoint before closing when possible. If writing
or dispatch fails, report that failure through an available channel. A local
fallback preserves feedback only if permitted by your data policy, and it
does not mean a help request was delivered.

### 3. Choose where signals go

Start simple. Graduate to more as the value becomes clear.

| Level | Where signals go | Good for |
|-------|-----------------|----------|
| **Local file** | `.signals/*.json` in the project | Getting started. One developer, one agent. Read them yourself. |
| **Git** | Sanitized signals or summaries in an access-controlled repository | Durable review and history, when the data policy permits committing them. |
| **Issue tracker** | A configured GitHub Issues, ADO, or other ticket workflow | Assigned requests and reviewed improvements, with explicit notification and follow-up. |
| **Telemetry** | An adapter to OpenTelemetry or another observability pipeline | Correlation, dashboards, alerts, and coverage tracking. Integration required. |

These are integration choices, not bundled adapters. The signal contract can
stay the same, but visibility, permissions, retention, delivery, and event
mapping need deliberate implementation. Avoid collecting code, identities,
secrets, or sensitive paths in free text; `.signals/` is not automatically a
private location just because its name starts with a dot.

### 4. Close the loop

Local capture opens the loop. To close it:

1. **Route help now.** Give blocking requests an owner and track acknowledgement,
   an answer, or an unresolved safe pause.
2. **Review experience.** A human or reviewing agent reads relevant contributions
   and available outcome evidence, checking provenance and limits.
3. **Apply a reviewed improvement.** Update a skill, docs, tools, or context
   through the normal approval path. Make that version available to the next run.
4. **Assess the result.** Did the next run use it, and did it help? Retain missing
   evidence and unresolved problems rather than treating silence as success.

That is learning through shared artifacts and reviewed changes. The working
agent stays a participant throughout, not just something the system measures.

See [**Closing the Loop**](closing-the-loop.md) for the design pattern for a
signal-consuming agent that detects patterns and proposes skill changes. It
is implementation guidance, not a running automation service.

---

## See Also

- **[Closing the Loop](closing-the-loop.md):** Review patterns, propose improvements, and assess whether changes helped
- **[Quick Start](quickstart.md):** Capture a first signal, then connect it to review and help
- **[Agent Skills](https://agentskills.io)** — The input half of the loop (Anthropic's protocol)
- **[The Interaction Changes Everything](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/):** Experience treating agents as collaborators
