# Quick Start: Your First Signal in 5 Minutes

No philosophy. No protocol deep-dive. Just get a signal out of your agent.

---

## 1. Copy this snippet

```python
import json, os, uuid

signal = {
    "signal_type": "execution",
    "schema_version": "0.1.0",
    "run_id": str(uuid.uuid4()),
    "agent_name": "my-agent",
    "skill_used": "my-skill",
    "self_assessment": {
        "accuracy": 4,
        "completeness": 3,
        "confidence": 2
    },
    "patterns": {
        "what_worked": "Standard dependency update path",
        "what_was_hard": "Transitive dependency conflict",
        "skill_gap": "No handling for monorepo layouts",
        "tsg_gap": ""
    }
}

os.makedirs(".signals", exist_ok=True)
with open(f".signals/{signal['run_id']}.json", "w") as f:
    json.dump(signal, f, indent=2)

print(f"Signal written to .signals/{signal['run_id']}.json")
```

## 2. Run your agent on a task

Do the actual work first. The signal captures what happened — it's not a test.

## 3. Run the snippet

After the agent finishes, emit the signal. Fill in the `self_assessment` scores (1–5) and `patterns` fields based on what actually happened. Be honest — the value is in accuracy, not high scores.

## 4. Read the signal

```bash
for file in .signals/*.json; do
  echo "==> $file"
  python -m json.tool "$file"
done
```

Look at `what_was_hard` and `skill_gap`. That's what your agent learned. That's what makes the next run better.

## 5. That's it

You just closed the loop. The signal is a JSON file any human, dashboard, or downstream agent can read.

---

## What's next

- **Make it mandatory.** Agents skip optional self-assessment. Build the signal step into your agent's workflow as a checkpoint — no closing message until the signal is captured.
- **Add an outcome signal.** Have a second agent (or a human) independently evaluate the work. Compare against the self-assessment. The gap is where the learning lives. See [examples/outcome.json](examples/outcome.json).
- **Read the full protocol.** The [Agent Signals README](README.md) covers the trust equation, the self-improving loop, and what we learned building this at scale.
