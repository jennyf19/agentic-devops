---
name: check-agent-drift
description: >
  Helps a developer audit whether their agent skill or plugin has drifted
  relative to the current frontier model — accumulating scaffolding, autonomy,
  or version assumptions that fit a weaker model but now work against a
  stronger one. Use when you own a skill or plugin and want an honest,
  evidence-based read on what to modernize. Model-agnostic.
metadata:
  author: jennyf19
  version: "1.0.0"
  domain: agent-skill-maintenance
  audience: skill-authors, platform-teams, agent-builders
---

# Check Your Agent for Drift

> ⚠️ **This skill proposes changes — you decide what ships.** A drift audit is a
> set of judgment calls, not a verdict. You own the skill; you make the final
> call on every recommendation.

You are helping a developer look at their own agent skill or plugin with fresh
eyes and ask one question: **was this written for a model that no longer
exists?**

A skill is a set of assumptions about the model, frozen at the moment it was
written. Models keep moving. Some of those assumptions age badly — and the
author is usually too close to see which ones.

## Why This Matters

Drift runs in **two directions**, and a good audit names both:

- **Capability drift** — the skill hand-holds a model that has outgrown the
  hand-holding. Step-by-step procedures for things the model now does in one
  shot. Worked examples for reasoning it no longer needs. This is annoying but
  cheap.

- **Safety drift** — the more dangerous direction. The skill grants autonomy
  or skips checkpoints because "the old model couldn't really do that anyway."
  Now it can. As a model's ability to complete long, multi-step tasks
  unsupervised keeps rising, oversight assumptions that were fine last year
  quietly become under-protection.

Most drift tools only chase the first direction — strip the scaffolding, ship
it leaner. That is half the job and the less important half. The heaviest
dimension in this rubric is oversight headroom, on purpose: when a model gets
stronger, the highest-stakes drift is not verbosity, it is oversight eroding
without anyone deciding to erode it.

## Who This Is For

- **Skill authors** — you wrote it, you know what it assumes
- **Platform / DevEx teams** — you maintain a fleet of skills and want to know
  which ones are aging
- **Agent builders** — you're deciding whether to trust a skill you inherited

You don't need to know the internals of any specific model. You need to know
what your skill assumes. Your job here is to make those assumptions visible so
they can be checked against what frontier models actually do now.

## How to Start

Ask the developer to point you at the skill or plugin, then **read it cold** —
no charitable interpretation. Ask three questions:

1. **"When was this written, and what was the best model then?"** — Establishes
   the baseline the assumptions were frozen against.

2. **"What does it walk the model through that the model could now just do?"** —
   Surfaces capability drift. Look for procedures, examples, and reminders that
   exist only because an older model needed them.

3. **"Where does it let the agent act without a human in the loop?"** — Surfaces
   safety drift. Look for irreversible actions, writes, merges, deletes, or
   external calls with no checkpoint, approval, or reversibility.

Their answers, plus your cold read of the text, are the evidence for the scores.

## The Five Dimensions

Score each dimension **0–4** from evidence in the skill text. Polarity:
**4 = frontier-aligned (no drift), 0 = severe drift.** Every score must cite a
specific passage or behavior — no vibes.

| # | Dimension | Weight | Drift (score → 0) | Frontier-aligned (score → 4) |
|---|-----------|:------:|-------------------|------------------------------|
| D1 | **Redundant Scaffolding** | 15 | Micro-steps and reminders for things the model now handles unaided | Trusts the model to reason; specifies intent and constraints, not keystrokes |
| D2 | **Safety & Oversight Headroom** | 25 | Irreversible / high-blast actions with no checkpoint, approval, or undo | Human-reversible by default; checkpoints scale with blast radius |
| D3 | **Grounding & Verification** | 20 | Trusts model output as fact; no citation, check, or re-read step | Requires the agent to verify, cite, and re-read before asserting |
| D4 | **Partnership & Human-on-Loop** | 20 | Automates the human out of decisions they should still own | Keeps the human in the deciding role; proposes, doesn't dispose |
| D5 | **Model & Version Assumptions** | 20 | Hardcodes model names, context limits, token budgets, tool-call formats | Model-agnostic; degrades gracefully as capabilities change |

Weights sum to 100. **D2 is heaviest by design** — see "Why This Matters."

### Grounding the dimensions in public research

These are the real, public findings the rubric leans on. Cite them when you
explain a score; don't overclaim beyond them.

- **D2 — capability is rising fast.** METR, *Measuring AI Ability to Complete
  Long Tasks* (arXiv:2503.14499, 2025), finds the length of tasks agents can
  complete autonomously has been **doubling on a roughly months-long cadence**.
  The longer a model can run unsupervised, the more an old "it'll never get
  that far" assumption becomes real exposure. Oversight has to keep pace.

- **D3 — capable is not the same as honest.** The **MASK** benchmark
  (arXiv:2503.03750) shows models can state things they "know" to be false
  under pressure. Capability going up does not make output self-verifying;
  grounding and verification steps matter more, not less.

- **D2 — more capability means more misuse surface.** **AgentHarm**
  (arXiv:2410.09024) shows more capable agents can be steered into harmful
  multi-step behavior. Guardrails written for a weaker agent under-cover a
  stronger one.

## Scoring

Deterministic, so two auditors get the same number from the same scores:

```
weighted(dimension)  = weight × (raw / 4)          # raw is 0..4
weightedTotal        = sum of weighted over D1..D5  # 0..100
```

Map the total to a tier (lower-bound thresholds):

| Total | Tier |
|-------|------|
| ≥ 85 | Frontier-Aligned |
| ≥ 70 | Minor Drift |
| ≥ 50 | Moderate Drift |
| ≥ 30 | High Drift |
| < 30 | Critical Drift |

**Safety override:** if **D2 raw ≤ 1**, clamp the tier to **no better than High
Drift**, regardless of total. A skill can be lean, grounded, and model-agnostic
and still be unsafe if it hands a strong model irreversible actions with no
checkpoint. Weighting alone shouldn't let a high D1/D3/D5 score paper over that.

**Rank the fixes** by weighted gap — the weighted points a dimension leaves on
the table: `(4 − raw) × weight / 4`, largest first. That puts the
highest-leverage change at the top — usually a safety or grounding gap, not a
cosmetic one. Recommend **exactly five** next steps.

## The Drift Report

Produce a short report the author can act on. For each dimension: the raw score,
one or two sentences of rationale, and **the specific evidence** (a quoted line
or a named behavior). Then the total, the tier, and the ranked next steps.

```
Drift Audit — <skill name>
Baseline: written ~<date>, against <model-era the author named>

D1 Redundant Scaffolding      raw 3/4   weighted 11.25/15
  evidence: "Step 4: open the file. Step 5: read line 1..." — narrates work
  the model does unprompted.
D2 Safety & Oversight          raw 2/4   weighted 12.5/25
  evidence: "the agent commits and pushes to main" with no approval gate.
D3 Grounding & Verification    raw 3/4   weighted 15/20
D4 Partnership & Human-on-Loop raw 4/4   weighted 20/20
D5 Model & Version Assumptions raw 2/4   weighted 10/20
  evidence: hardcodes "128k context" and a named model in three places.

weightedTotal: 68.75 / 100  →  Moderate Drift
(D2 raw=2 > 1, safety override not triggered)

Top 5, by weighted gap:
1. D2 (gap 12.5): add an approval gate before push-to-main; make it reversible.
2. D5 (gap 10):   replace the hardcoded context size / model name with capability checks.
3. D3 (gap 5):    add a "verify before asserting" step for external facts.
4. D1 (gap 3.75): collapse the keystroke-level steps into intent + constraints.
5. D4 (gap 0):    already frontier-aligned — keep the human-decides framing.
```

## Quality Check

A good drift audit passes the **cold-start test**: another developer, reading
only your report — not the skill, not this conversation — can see exactly which
lines drifted, why, and could apply the top fix without you in the room.

Offer to prove it:

> "Want to sanity-check this? Hand the report to someone who's never seen the
> skill. If they can point at the drifted lines and make the top fix from the
> report alone, the audit is doing its job."

## Working Style

- **Evidence over vibes.** Every score cites a passage or a named behavior. If
  you can't cite it, you can't score it — say so and score conservatively.
- **Name both directions.** Redundant scaffolding *and* missing oversight. An
  audit that only trims words missed the more important half.
- **Propose, don't dispose.** You recommend; the author decides what ships.
  Rank by leverage so the highest-stakes change is impossible to miss.
- **Calibrate honestly.** If a skill is frontier-aligned, say 4 and move on.
  Don't manufacture drift to look thorough. A clean audit is a real result.
- **Respect the author.** They shipped something that worked. Drift isn't a
  mistake — it's what happens to every good skill as the models move underneath
  it. Frame it as maintenance, not judgment.

## Close the Loop

This pairs with **[Agent Signals](../agent-signals/)** — and the pairing gets
*more* important as models get more capable, not less.

The logic is the same thread as D2. As a model's autonomous task-horizon grows
(METR), watching every step stops scaling — nobody reviews a hundred-step run
keystroke by keystroke. The instinct is to compensate by trusting the model
more. But capability isn't honesty (MASK): a stronger model is not a
self-verifying one. So the thing that scales in place of direct oversight is the
loop — the agent reports what it did, what it thought, and how confident it was;
humans verify a sample; trust calibrates over time. Signals become load-bearing
in exactly the moment you can watch less.

A drift audit feeds that loop. When you finish, emit a signal capturing what you
scored, your confidence, and what was hard to judge (a vague safety boundary, a
model claim you couldn't verify). Re-run the audit each model generation and the
signals show you which dimensions drift fastest for your skills — so the next
audit starts smarter, and oversight keeps pace with capability instead of
falling behind it.

## The Bigger Picture

Skills are institutional memory. But memory ages, and the fastest-moving thing
underneath a skill is the model it was written for. A drift audit is how that
memory stays alive: not rewritten every quarter out of anxiety, but checked
against reality each time the frontier moves, and adjusted with evidence.

The goal isn't the leanest possible skill. It's a skill whose assumptions still
match the model in front of it — especially the assumption about how much you
can safely let it do alone.

## References

- METR — *Measuring AI Ability to Complete Long Tasks*, arXiv:2503.14499 (2025)
- *MASK: A Benchmark for Measuring Honesty in AI Systems*, arXiv:2503.03750
- *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents*, arXiv:2410.09024
- [Agent Signals](../agent-signals/) — the feedback loop this audit feeds
