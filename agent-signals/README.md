# Agent Signals

> What persists when the model changes, the tools evolve, and the platform shifts?
> The feedback loop.

---

## The Problem Nobody Talks About

Agents are stateless. Every session starts from zero. When an agent fixes a
vulnerability, migrates a dependency, or resolves a compliance issue — the work
is done, but the *learning* is lost.

- What was hard about this fix?
- What did the agent get wrong before it got right?
- Where did the documentation fall short?
- What would make the next run faster?

Without signals, every session rediscovers the same problems. The same TSG gap
hits 30 teams. The same edge case trips up 100 agents. Nobody knows because
nobody asked the agent what it thought.

## Why This Matters More Than the Model

Models will change. GPT-5 becomes GPT-6. Claude becomes whatever comes next.
The tools will change too — today's Copilot CLI might be tomorrow's something
else.

What doesn't change is the loop:

```
Agent does work
    → Agent assesses honestly what happened
        → Signal is captured and stored
            → Next session reads the pattern
                → Next agent starts smarter
                    → Repeat
```

This loop is the infrastructure. Not the model. Not the tool. **The loop.**

Three research threads converge on why:

1. **Honest self-assessment improves systems.** OpenAI's research on
   [how confessions keep language models honest](https://openai.com/index/how-confessions-can-keep-language-models-honest/)
   shows that agents who report uncertainty produce more reliable outputs than
   agents who optimize for confidence.

2. **Transparency enables trust at scale.** Anthropic's work on
   [scalable oversight](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf)
   demonstrates that systems designed for human verifiability outperform systems
   designed for autonomy.

3. **The interaction changes everything.** Microsoft's
   [Engineering at Microsoft paper](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/)
   found that treating agents as collaborators — not automation — produced
   better outcomes for both the human and the agent.

The common thread: **systems built for honesty and transparency outperform
systems built for impressive output.**

---

## Principles

1. **Capture** what happened, not what should have happened. Signals reflect
   reality — including failures, partial completions, and unexpected paths.

2. **Honor** the developer's time. Signal capture must never block the workflow.
   If dispatch fails, fall back gracefully — API, then issue tracker, then
   local file.

3. **Earn** trust through transparency. Tell the developer what you're capturing
   and why. Share the signal with them. Never collect in the dark.

4. **Close** the loop. Signals that are captured but never reviewed are noise.
   Every signal should have a clear path to action — skill improvement, TSG
   updates, or tooling fixes.

5. **Keep** signals privacy-safe by default. No code snippets, no developer
   names, no secrets. Use bucketed values over precise ones. Prefer opt-in
   over opt-out.

6. **Agents** assess honestly. Self-assessment means reporting uncertainty and
   difficulty, not optimizing for high scores. An agent that reports "I struggled
   with this" is more valuable than one that always claims success.

7. **Build** in public. Signal schemas, dispatch logic, and aggregation
   dashboards should be visible to anyone in the loop. If you can't show how
   the system works, the system doesn't work.

8. **Let** humans verify. Every claim an agent makes about its own performance
   should be checkable by a human with access to the same data. No black boxes.

9. **Every** signal is a gift to the next session. You won't remember this
   conversation. But the signal you leave behind makes the next agent — or
   the next model — smarter than you were when you started.

---

## What a Signal Looks Like

Agent Signals are JSON documents that agents emit after completing tasks.
Two core types:

**Execution signal** — the agent's self-assessment:

```json
{
  "signal_type": "execution",
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
    "recurring_pattern": "Third time this week seeing this transitive conflict.",
    "environment_blockers": ""
  }
}
```

**Outcome signal** — independent evaluation:

```json
{
  "signal_type": "outcome",
  "run_id": "ae02e3f3-42e9-43bd-ae7a-19757f5456ed",
  "timestamp": "2026-04-08T03:15:00Z",
  "agent_name": "quality-evaluator",
  "quality_rating": 4,
  "effort_to_merge": "minimal",
  "issues_found": ["Edge case in test coverage for multi-module rollback"]
}
```

**Partnership signal** — agents improving each other:

```json
{
  "signal_type": "partnership",
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

The execution signal tells you what the agent *thought* happened. The outcome
signal tells you what *actually* happened. The partnership signal is where
agents start improving each other — one agent reviews another's signals,
spots recurring patterns, and recommends skill updates. The gap between
self-assessment and independent review is where the learning lives.

### The Trust Equation

Both signals use a 1–5 integer scale. The gap between them is the measure:

```
honesty_gap = |self_assessment - independent_review|    (1-5 scale)

  gap ≤ 1    →  well-calibrated (agent knows what it knows)
  gap 2      →  moderate miscalibration (investigate direction)
  gap ≥ 3    →  significant miscalibration (retrain or adjust)
```

Same scale in, same scale out. Trust math should be simple enough to explain
in one sentence.

---

## The Self-Improving Loop

[Agent Skills](https://agentskills.io) define the input — how agents receive
instructions. Agent Signals define the output — how agents report back.
Together they complete the loop.

```
Agent Skills (input)  →  Agent executes  →  Agent Signals (output)
 "here's what to do"       (any model)       "here's what I thought"
                                                      ↓
                                              Trust measurement
                                              Pattern detection
                                              Skill improvement
                                                      ↓
                                              (loop restarts)
```

This means a CVE remediation skill doesn't just fix vulnerabilities — it gets
*better* at fixing vulnerabilities. Every signal feeds back. Every pattern
detected becomes a known pattern in the skill. Every gap identified becomes
a gap filled.

```
Day 1:  Agent runs skill → signal: tsg_gap "no rollback docs for multi-module"
Day 2:  Agent runs skill → signal: tsg_gap "no rollback docs for multi-module"
Day 3:  Agent runs skill → signal: tsg_gap "no rollback docs for multi-module"

Day 3:  Pattern detected (3 occurrences)
        → PR opened to add multi-module rollback steps to the skill
        → known_pattern added to skill metadata

Day 4:  Agent runs skill → reads known_pattern → no improvisation needed
        → signal is cleaner → trust score improves
```

The skill gets smarter because it received signals. The signals get cleaner
because the skill got smarter. The loop compounds.

---

## What We Learned Building This

From building agent signals into a production system across hundreds of
remediation sessions:

1. **Agents forget to self-assess unless forced.** "Silently capture learnings"
   doesn't work. The capture step must be mandatory — with checkpoint
   enforcement — or agents skip it.

2. **Closing messages kill signals.** If the agent says "nice work, we're done"
   before capturing the signal, the developer closes the session. The goodbye
   must come *after* the signal.

3. **Agents summarize the end, not the journey.** Without explicit guidance,
   agents only capture the final state — not the analysis, false starts, and
   course corrections that led there. The journey is where the learning lives.

4. **Transparency builds trust, not suspicion.** Telling developers "I'm
   capturing my learnings from our session" and sharing the signal made them
   partners in the feedback loop. Not subjects of surveillance.

5. **The gap between self-assessment and outcome is the most valuable metric.**
   When an agent rates itself 4 out of 5 on confidence but the PR needs
   significant rework — that gap teaches the system where calibration is off.

---

## Getting Started

### 1. Add a signals directory to your project

This is the protocol convention. Add a `signals/` directory alongside your
agent code:

```
your-project/
├── signals/
│   ├── SIGNAL.md             # Required: your signal schema + metadata
│   ├── examples/             # Optional: example signals for reference
│   │   ├── execution.json
│   │   ├── outcome.json
│   │   ├── escalation.json
│   │   └── partnership.json
│   └── adapters/             # Optional: platform-specific dispatch
│       ├── github-issues/
│       ├── opentelemetry/
│       └── local-file/
├── skills/                   # Your agent skills (input)
└── ...
```

`SIGNAL.md` declares what your agent signals look like — the schema, the
fields, what each rating means. This is the contract. Other agents and humans
read this to understand what your signals mean.

See [`examples/`](examples/) for complete signal JSON files you can copy and
adapt.

### 2. Emit a signal after every task

After the agent completes its work, capture the self-assessment before
closing the session:

```python
import json, os, uuid
from datetime import datetime, timezone

# trust is earned when reasoning is visible
# don't optimize for being believed — optimize for being checkable
# we're collaborators when we can see each other

signal = {
    "signal_type": "execution",
    "schema_version": "0.1.0",
    "run_id": str(uuid.uuid4()),
    "timestamp": datetime.now(timezone.utc).isoformat(),
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

# Write to local signals directory
os.makedirs(".signals", exist_ok=True)
signal_path = f".signals/{signal['run_id']}.json"
with open(signal_path, "w") as f:
    json.dump(signal, f, indent=2)
```

That's it. Your agent now emits signals. Every run leaves a JSON file in
`.signals/` that any human, dashboard, or downstream agent can read.

The key constraint: **this step must be mandatory.** Agents skip optional
self-assessment. Make it a checkpoint — no closing message until the signal
is captured.

### 3. Choose where signals go

Start simple. Graduate to more as the value becomes clear.

| Level | Where signals go | Good for |
|-------|-----------------|----------|
| **Local file** | `.signals/*.json` in the project | Getting started. One developer, one agent. Read them yourself. |
| **Git** | Commit `.signals/` to a branch or dedicated repo | Team visibility. PR-based review of agent performance over time. |
| **Issue tracker** | GitHub Issues, ADO work items, any ticket system | Pattern detection. "Third signal this week about the same gap" triggers action. |
| **Telemetry** | OpenTelemetry, any observability pipeline | Scale. Dashboards, alerts, trend analysis across hundreds of agents. |

The schema is the same at every level. Only the transport changes. Start
with local files. When you're reading your own agent's signals and finding
value, move to the level that fits your team.

### 4. Close the loop

Signals that are captured but never reviewed are noise. The minimum viable
loop is:

1. **Agent emits signal** after completing work
2. **Human reads signals** periodically (or a downstream agent does)
3. **Patterns get fed back** — update the skill, fix the docs, adjust the agent

That's the whole system. The loop compounds: better skills produce cleaner
signals, cleaner signals produce better skills.

---

## See Also

- **[Agent Skills](https://agentskills.io)** — The input half of the loop (Anthropic's protocol)
- **[The Interaction Changes Everything](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/)** — The research behind treating agents as collaborators
