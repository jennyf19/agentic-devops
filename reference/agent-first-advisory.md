# Agent-First Advisory Guide

> **For:** Library maintainers, security teams, and anyone who writes vulnerability fix documentation
> **The idea:** Your advisory IS the skill. Structure it right and agents execute from it directly.

---

## The Problem

Today, a CVE drops and two things happen:

1. **You** (the library maintainer or security team) write an advisory: "Upgrade to version X. If you were using the old API, here's what changed."

2. **Someone else** (maybe months later) reads your advisory and writes an agent skill — a structured set of instructions an agent can follow to actually do the fix.

Step 2 shouldn't exist. If the advisory were structured right, the agent could read it directly.

---

## What "Agent-First" Means

Agent-first doesn't mean "add some YAML to your existing advisory." It means writing with the agent as the primary reader and humans as secondary.

Think about the difference:

**Human-first advisory:**
> "Users should upgrade to version 2.0. Note that the API for creating sessions has changed — see the migration guide for details."

An agent reading this has to: figure out what "upgrade" means in practice (which file? which line?), find the migration guide, parse the migration guide, figure out what code to change, and hope nothing was left out.

**Agent-first advisory:**

```markdown
## Detection
Search for `com.example:session-lib` in pom.xml files.
If version < 2.0.0, this advisory applies.

## Fix
### Step 1: Update version
Change `<session-lib.version>1.x.x</session-lib.version>` to `2.0.0`

### Step 2: Update API calls
BEFORE:
  Session s = SessionFactory.create(config);
AFTER:
  Session s = SessionFactory.builder().config(config).build();

## Validate
mvn compile — should succeed.
Search for `SessionFactory.create` — should return zero results.
```

Same information. Structured so an agent can act on it without interpretation.

---

## The 6 Sections

Every agent-first advisory needs these. They map to what an agent needs to do its job:

### 1. Metadata

```yaml
---
advisory-id: CVE-2024-XXXXX
library: com.example:session-lib
affected-versions: "< 2.0.0"
fixed-version: "2.0.0"
severity: high
ecosystem: java-maven
fix-type: version-bump-plus-code-change
---
```

**Why:** The agent (or an orchestrator) uses this to decide whether to attempt the fix and how to prioritize it. Without metadata, the agent has to read the whole document to figure out if it even applies.

### 2. Scope — What's affected and what's not

```markdown
## Scope

**Applies to:** Maven projects that directly depend on `com.example:session-lib` < 2.0.0.
**Does NOT apply to:** Projects that depend on session-lib transitively through
`com.example:session-framework` (that library handles the migration internally).

**How to check:**
- Search for `com.example:session-lib` in `pom.xml` files
- If the dependency is direct and version < 2.0.0 → this advisory applies
- If the dependency is transitive → check the parent library instead
```

**Why:** Agents waste time (and developer trust) when they attempt fixes on repos that aren't affected. A clear scope section lets the agent skip early.

### 3. Detection — How to find the problem

```markdown
## Detection

**In the build file:**
Search pom.xml for:
- `<groupId>com.example</groupId>` + `<artifactId>session-lib</artifactId>`
- Check version: if < 2.0.0, affected

**In source code:**
Search for usage sites that need code changes:
- `import com.example.session.SessionFactory`
- `SessionFactory.create(` — this API was removed in 2.0.0
```

**Why:** This is the #1 gap between advisories agents can use and advisories they can't. Detection logic tells the agent exactly what to look for. Without it, the agent guesses.

### 4. Remediation — The actual fix

This is the heart of the advisory. Structure it as ordered steps with code blocks.

```markdown
## Fix

**Step 1: Update version** (no dependencies)
Change the version property or inline version to 2.0.0:
BEFORE: <session-lib.version>1.4.3</session-lib.version>
AFTER:  <session-lib.version>2.0.0</session-lib.version>

**Step 2: Update API calls** (depends on Step 1)
The `SessionFactory.create()` method was replaced with a builder pattern.

BEFORE:
  Session s = SessionFactory.create(config);
AFTER:
  Session s = SessionFactory.builder().config(config).build();

For calls with options:
BEFORE:
  Session s = SessionFactory.create(config, options);
AFTER:
  Session s = SessionFactory.builder()
      .config(config)
      .options(options)
      .build();

**Step 3: Update tests** (depends on Step 2)
Test files need the same API changes. Additionally, tests that mock
SessionFactory.create() need to mock SessionFactory.builder() instead.
```

**Key principles:**
- **Before/after code** for every change. Don't describe it — show it.
- **Multiple variants** when the change differs by context (production vs test, simple vs complex).
- **Dependencies between steps** — tell the agent what order matters.
- **The decision, not just the action** — "Use the builder pattern for new code. For test code, the shorthand `Session.forTesting(config)` is also acceptable."

### 5. Validation — How to verify the fix

```markdown
## Validation

1. `mvn compile` — must succeed
2. `mvn test` — all tests must pass
3. Search for `SessionFactory.create(` — should return 0 results
4. Search for `session-lib` version — should show 2.0.0 only

**Common failures:**
| Symptom | Cause | Fix |
|---------|-------|-----|
| `NoSuchMethodError: create()` | Missed a call site in Step 2 | Search again, update the missed site |
| Test fails on mock setup | Mock targets old API | Update mock to use builder pattern |
```

**Why:** Without validation, the agent can't close the loop. It makes changes and hopes. With validation, it makes changes and proves they work.

### 6. Edge Cases — What trips people up

```markdown
## Edge Cases

| Scenario | What happens | What to do |
|----------|-------------|------------|
| Transitive dependency | Parent library may override | Check parent's version management |
| Multi-module project | Version in parent pom | Update parent, not child modules |
| Custom SessionFactory wrapper | Wrapper hides the direct API | Update the wrapper, not callers |

**Common mistakes:**
- Upgrading to 2.0.0 without updating `create()` calls — compiles fine, fails at runtime
- Forgetting test files — tests use SessionFactory too
- Leaving old version in dependency management section of parent pom
```

**Why:** Every developer who's fixed this CVE by hand knows the gotchas. Write them down. The agent avoids them. The next 200 developers avoid them.

---

## The Worked Example

Look at the [XStream CVE skill](../examples/remediate-xstream-cve.md) from the demo. It follows this exact structure:

| Section | How XStream does it |
|---------|-------------------|
| Metadata | YAML frontmatter with CVE family, ecosystem, severity |
| Scope | "When to Use This Skill" — which alerts trigger it |
| Detection | Step 1 — find version in pom.xml, find all `new XStream()` call sites |
| Remediation | Steps 2-5 — version bump, permissions (the hard part), tests, suppressions |
| Validation | Step 6 — compile, test, grep for misses, common failure table |
| Edge cases | "Scope and Limitations" — what it handles, what it doesn't |

The XStream skill scores high because it spends 40% of its words on Step 3 (permissions) — the part where every automated tool fails. That's the pattern: spend your words where the complexity lives.

---

## Starting From What You Have

You probably already have an advisory, a changelog entry, or a migration guide. You don't need to start from scratch.

### "I have a changelog"

Changelogs list what changed. Agent-first advisories show how to adapt. Take your changelog and for each breaking change, add:
- Detection: how to find code that uses the old behavior
- Before/after: what the code looks like before and after
- Validation: how to verify the migration worked

### "I have a migration guide"

Migration guides are often 80% of the way there. What's usually missing:
- Detection logic (the guide assumes the reader knows they're affected)
- Machine-parseable code blocks (prose descriptions instead of copy-paste code)
- Validation commands (the guide says "verify it works" but not how)

### "I have nothing — just a CVE ID"

Start with Ember:

> "I maintain [library]. CVE-XXXX-XXXXX was just published. Help me write an agent-first advisory for it."

Ember will research the CVE, help you structure the fix, and produce a document in this format. You bring the domain knowledge. Ember brings the structure.

---

## Why This Matters

Every CVE that has an agent-first advisory is a CVE that never needs a dedicated skill. The advisory is the skill.

For library maintainers: your users don't have to wait for someone to write a remediation skill. They point an agent at your advisory and it does the work.

For security teams: you write one document. It serves humans (who can read it normally) AND agents (who execute from it). One source of truth.

For the ecosystem: the number of fixable CVEs scales with the number of good advisories, not the number of skill authors.
