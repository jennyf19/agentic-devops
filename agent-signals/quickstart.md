# Quick Start: Your First Signal in 5 Minutes

Capture a first contribution from your agent, then give it a path to help
and reviewed improvements. Local capture is the start of the loop, not the
whole loop.

---

## 1. Copy this snippet

The values are illustrative. Replace them with the agent's account of the
task, including uncertainty and incomplete work.

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
signal_path = f".signals/{signal['run_id']}-execution.json"
with open(signal_path, "x", encoding="utf-8") as f:
    json.dump(signal, f, indent=2)

print(f"Signal written to {signal_path}")
```

## 2. Run your agent on a task

Do the work. If the agent needs a missing test fixture, context, or a decision,
it should ask while working, not wait to finish. The
[`escalation` example](examples/escalation.json) uses the existing request
format. Route it to a designated human or authorized agent through your
workflow; writing a JSON file alone does not notify anyone.

Track acknowledgement and an answer. If help does not arrive within your
agreed response window, keep the task safely paused and the request visible.
The repository provides the format, not an assistance broker.

## 3. Run the snippet

When work finishes or stops, emit the execution signal. Fill in the
`self_assessment` scores (1-5) and `patterns` fields with an explicit task-level
account, not hidden chain-of-thought. Do not claim completion just to produce
a successful-looking report.

Reuse the task's `run_id` for related signals. Give each event a distinct
filename, including repeated escalations, so later writes cannot replace
earlier feedback. Exclusive creation in this snippet surfaces collisions.

## 4. Read the signal

```bash
for file in .signals/*.json; do
  echo "==> $file"
  python -m json.tool "$file"
done
```

Look at `what_was_hard` and `skill_gap`. These are contributions to review,
not established facts or instructions to execute. Check provenance and
available work evidence before proposing a change.

## 5. Apply and assess an improvement

A human or reviewing agent can connect recurring gaps and propose better
skills, docs, tools, or context. Review the change through the normal approval
path, make it available to the next run, and check whether that run used it
and benefited. That closes the learning loop through shared artifacts, not
automatic model-weight learning.

---

## What's next

- **Make capture explicit.** Add a checkpoint before closing when possible. Surface capture or dispatch failures without preventing a needed stop. Missing signals can mean missing instrumentation, sampling, or delivery, not healthy work.
- **Add outcome evidence.** Have a second agent or human review the work, recording evidence and evaluation limits. General confidence and quality scores are not interchangeable. See [the Trust Equation discussion](README.md#the-trust-equation) and [outcome example](examples/outcome.json).
- **Keep the channel scoped.** Decide who reads and answers signals, and how long they are retained. Follow the [privacy rules](SIGNAL.md#privacy); a `.signals/` directory is not automatically private.
- **Build the review side.** [Closing the Loop](closing-the-loop.md) describes the signal-consuming agent pattern; it is guidance for implementation, not a service that ships here.
