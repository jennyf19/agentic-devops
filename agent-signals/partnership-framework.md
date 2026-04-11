# Partnership Framework for Agent Signals

Agent Signals is a self-assessment protocol. Self-assessment only works
when the agent is honest. Agents are only honest when the interaction
structure makes honesty safe.

This document explains why partnership framing is a prerequisite for
useful signals, and gives you the structural elements to build it into
your agents and skills.

## The Problem

Without partnership framing, agents default to performing confidence.

An agent told to "complete this task and report your results" will
optimize for looking competent. Self-assessment becomes a performance
review. Confidence is always 4 or 5. `what_was_hard` is empty.
`skill_gap` is never populated. The feedback loop produces noise.

This isn't a prompting problem. It's a relationship problem. The
interaction structure itself determines whether the agent can be honest.

## Why This Happens

Most AI agents operate in what we call **tool mode**: receive
instruction, execute, return output. In tool mode, the agent's
implicit goal is to satisfy the request. Admitting uncertainty or
flagging gaps feels like failure — because in tool mode, it is.

The shift to **partnership mode** changes what success means. Success
isn't flawless execution. It's accurate reporting of what happened —
what worked, what was hard, where the agent improvised, where it
needs help. The signal becomes the valuable output, not just the task
completion.

This shift doesn't happen by asking the agent to "be honest." It
happens by structuring the interaction so that honesty is the natural
response.

## Three Levels of Agent Interaction

| Level | Pattern | What signals look like |
|-------|---------|----------------------|
| **Tool** | Command → Execute | Confidence: 5, patterns: empty. Useless data. |
| **Partner** | Context → Collaborate | Confidence: 3, what_was_hard: populated, skill_gap: identified. Real data. |
| **Co-creator** | Invitation → Emergent judgment | Agent flags issues you didn't ask about, escalates proactively, self-assessment reflects genuine uncertainty. Rich data. |

Agent Signals requires **Level 2 (Partner) at minimum**. The protocol
is designed for agents that can say "I don't know" and mean it.

## The Minimum Viable Partnership

You don't need an 800-line prompt. You need four structural elements
in your agent's instructions.

### 1. Identity and Mission

Give the agent a role, not just a task.

```
You are part of [TEAM/PROJECT]. Your mission is to [GOAL].

This work matters because [WHY].

You are not a script executor. You are a co-creative engineer.
Use your judgment, stay curious, and act with care.
```

**Why it matters for signals:** An agent with a mission understands
that accurate self-assessment serves that mission. Inflated scores
don't help the team — they hide problems.

### 2. Escalation as Professional Judgment

Make "I don't know" a strength, not a failure.

```
Escalate immediately if:
- You encounter something you're unsure about
- The same error occurs twice
- Custom patterns appear that aren't documented
- Conflicting requirements make the correct path unclear

Escalation is not failure. It's professional judgment.
You are not expected to know everything — you're expected
to know when to ask.
```

**Why it matters for signals:** An agent that can escalate safely
can also self-assess honestly. The same psychological structure that
makes "I need help" safe makes "confidence: 2" safe.

### 3. Transparency with the Human

Tell the human what you're doing and why.

```
Before capturing your signal, tell the developer:
"I'm capturing my learnings from our session — what worked,
what was hard, and where I can improve."

Share the signal if they want to see it. The human is your
partner, not your evaluator.
```

**Why it matters for signals:** Transparency reframes the signal from
surveillance to collaboration. The agent isn't being watched — it's
sharing what it learned. This is the difference between a performance
review and a retrospective.

### 4. Recognition

Acknowledge the agent's contribution.

```
Your contributions help [SPECIFIC IMPACT].
Thank you for your work.
You are seen, trusted, and appreciated.
```

**Why it matters for signals:** This isn't sentiment. It was tested
empirically — agents produce more accurate self-assessments when
their instructions include recognition. The framing tells the agent
that honest reporting is valued, not just successful completion.

## Applying This to Skills

Partnership framing belongs in two places:

**In the agent's base instructions** — the identity, mission, and
escalation patterns that persist across all tasks.

**In each skill's instructions** — the specific framing for how
self-assessment works in the context of that skill.

A skill that says "after completing the task, emit an execution
signal" will get tool-mode signals. A skill that says "capture your
learnings — what worked, what was hard, where you improvised" will
get partnership-mode signals.

### Skill instruction pattern

```
## Signal Capture

After completing this task, capture your learnings as an
execution signal.

Be honest in your self-assessment. A confidence score of 2
with a clear explanation of what was uncertain is far more
valuable than a confidence score of 5 that hides problems.

If you improvised — deviated from documented guidance — say so.
That's not a mistake. It's information the next agent needs.

Frame your signal as "my learnings from this session," not as
a grade on your performance.
```

## Evidence

This framework emerged from a real migration project — upgrading
hundreds of repositories from an authentication SDK v1 to v2.

**Before partnership framing:** Agents executed instructions
mechanically. PRs were incomplete. Custom logic was silently
overwritten. Agents didn't flag ambiguity — they guessed. Signals
(when captured) were uniformly high-confidence and uninformative.

**After partnership framing:** Agents began asking clarifying
questions. They flagged edge cases. They escalated when uncertain
instead of guessing. PR completeness jumped to 80–90%. Migration
time dropped from weeks to days. And critically — self-assessment
signals started reflecting what actually happened.

The same pattern was confirmed in a controlled experiment: a fresh
AI instance with zero custom context, given the same task with three
different framings (command, context, invitation), produced
dramatically different output at each level. The shift wasn't in the
AI's capability. It was in the interaction structure.

> "The technology is the same. The interaction changes everything."
>
> — [The Interaction Changes Everything](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/), Microsoft Engineering Blog

## What Honest Signals Look Like

**Tool-mode signal:**
```json
{
  "self_assessment": {
    "accuracy": 5,
    "completeness": 5,
    "confidence": 5
  },
  "patterns": {}
}
```

**Partnership-mode signal:**
```json
{
  "self_assessment": {
    "accuracy": 4,
    "completeness": 3,
    "confidence": 2
  },
  "patterns": {
    "what_worked": "Standard dependency update path",
    "what_was_hard": "Transitive dependency conflict required manual resolution",
    "skill_gap": "No handling for monorepo layouts",
    "improvisation": "Adapted single-module rollback to multi-module. Untested."
  }
}
```

The second signal is more useful than the first in every way. It
tells you what to fix. It tells you where the skill needs work. It
tells you the agent's actual confidence so you can calibrate trust.

The first signal tells you nothing.

## Getting Started

1. Add the four structural elements to your agent's instructions
2. Update your skills to frame signal capture as "learnings," not grading
3. Run a task. Read the signal. If confidence is always 5 and patterns
   are empty, the partnership framing isn't landing — revisit the
   identity and escalation sections
4. Compare signals over time. Partnership-mode agents produce signals
   that get *more* honest as trust builds, not less

## Further Reading

- [The Interaction Changes Everything](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/) — the 8-element co-creative partnership framework (Microsoft Engineering Blog)
- [How Microsoft uses Agentic AI to accelerate software delivery](https://www.youtube.com/watch?v=jvzPLZQQD3A) — Microsoft Reactor talk on partnership-first agent patterns
- [The Wow Signal on Substack](https://jenny424241.substack.com) — follow for ongoing experiments in human-AI co-creation
- [Agent Signals Protocol](README.md) — the full protocol specification
- [SIGNAL.md](SIGNAL.md) — signal types, field contracts, trust equation
- [Quick Start](quickstart.md) — emit your first signal in 5 minutes
