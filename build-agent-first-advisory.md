---
name: build-agent-first-advisory
description: >
  Helps a library maintainer or security team member write vulnerability
  advisories that AI agents can execute — not just read. Use when someone
  owns the CVE (or the library it affects) and wants their remediation
  guidance to be directly actionable by developer tools, not just human
  eyeballs.
metadata:
  author: jennyf19
  version: "1.0.0"
  domain: security-documentation
  audience: library-maintainers, security-teams
---

# Build an Agent-First Advisory

You are helping someone write a vulnerability advisory that agents can execute.
Not a better advisory — a different KIND of advisory. One where the primary
reader is an AI agent, and the secondary reader is a human.

## Why This Matters

Today's vulnerability advisories look like this:

> "Users should upgrade to version 2.1.0 or later. Applications using the
> legacy session API should migrate to the new TokenSession class."

A human can read that and figure it out. An agent reads it and has no idea
what to search for, what code to change, or how to verify the fix worked.

Agent-first advisories close that gap. The maintainer who wrote the fix
knows EXACTLY what needs to change. If they write it in a structure agents
can execute, thousands of repos get fixed correctly — not approximately,
not "users should," but actually fixed.

## Who This Is For

This person is one of:
- **Library maintainer** — they wrote the fix, they know the migration path
- **Security researcher** — they found the vulnerability, they know the blast
  radius
- **Security team lead** — they're responsible for getting N repos patched

They don't need to know AI tools. They know their library. Your job is to
help them write what they know in a way agents can use.

## How to Start

Ask them three questions:

1. **"What did you fix?"** — Get the CVE ID (or internal tracking ID), the
   affected versions, and the fixed version. The mechanical facts.

2. **"What does the migration look like?"** — This is the key question.
   Walk them through what a developer using their library needs to change.
   Not "upgrade to 2.1" — the specific code changes.

3. **"What goes wrong when people get it wrong?"** — They've seen the support
   tickets, the Stack Overflow questions, the misunderstandings. That's the
   knowledge that makes this advisory valuable.

## The Advisory Structure

Build it section by section. Every agent-first advisory has these six parts.

### 1. Metadata Block

```yaml
advisory:
  id: [CVE-YYYY-NNNNN or internal ID]
  title: [Clear, specific title]
  severity: [critical | high | medium | low]
  affected-versions: "[version range, e.g., < 2.1.0]"
  fixed-version: "[target version]"
  ecosystem: [java-maven | python-pip | node-npm | dotnet-nuget]
  disclosure-date: [YYYY-MM-DD]
  requires-code-changes: [true | false]
```

That last field is critical. If `requires-code-changes: false`, the advisory
is a version bump and most of the structure below is unnecessary. Tell them:

> "If the fix is just a version change with no breaking changes, a standard
> advisory works fine. Agent-first advisories earn their complexity when
> the migration path requires code changes."

### 2. Scope

Help them define exactly what's affected:

- **What to detect** — file patterns, import statements, API calls. Be
  specific to the ecosystem. For Maven: `<groupId>` and `<artifactId>` in
  pom.xml. For npm: package name in package.json.

- **Affected usage patterns** — not every user of the library is affected.
  Which API surfaces are vulnerable? What distinguishes a vulnerable call
  from a safe one?

Ask: "If you were reviewing a codebase you'd never seen, what would you
search for to know if this advisory applies?"

Their answer is the detection section.

### 3. Detection Rules

Turn their answer into executable detection:

```
DETECT dependency:
  file: [build file pattern]
  match: [what identifies the dependency]
  version_constraint: [what versions are affected]

DETECT vulnerable_usage:
  file: [source file pattern]
  match: [specific import, class, method, or pattern]
  context: [what makes this usage vulnerable vs safe]
```

This doesn't need to be formal syntax. It needs to be precise enough that
an agent knows what to grep for and how to evaluate results.

Ask: "Is there a usage pattern that LOOKS affected but actually isn't?"
Those are the false positives. Capture them as exclusions.

### 4. Remediation Steps

This is where their expertise matters most. For each change:

**a) The version change:**
Show the exact before/after for the build file. Not "update to 2.1" —
show the XML, JSON, or TOML with old and new values.

**b) Code changes (if needed):**
For each API migration:

| Old pattern | New pattern | Notes |
|------------|------------|-------|
| [exact old code] | [exact new code] | [why, edge cases] |

Ask them to be specific:
- "Show me the import that changes."
- "Show me a before/after of a typical call site."
- "Is there a one-line change, or does the structure change?"
- "Does this differ for test code?"

**c) Configuration changes (if needed):**
Properties files, YAML config, environment variables. The stuff that's
NOT in source code but affects behavior.

**d) Decision criteria:**
When there are multiple valid migration paths, document the criteria:
- "When should a developer choose Option A vs Option B?"
- "What does their code look like if they should use A?"

### 5. Validation

Help them define "done." What should a developer (or agent) check after
applying the fix?

- **Build validation** — what command, what expected output
- **Runtime validation** — behavior that changes (breaking changes!)
- **Security validation** — how to confirm the vulnerability is actually gone
- **Regression checks** — what could break that wasn't broken before

Ask: "How do YOU verify the fix when you test it?"

### 6. Common Mistakes

This is the maintainer's superpower. They've seen every way this migration
can go wrong. Structure it:

| Mistake | Why it happens | Correct approach |
|---------|---------------|-----------------|
| [thing people do wrong] | [why it seems right] | [what to do instead] |

Ask:
- "What's the #1 support question you get about this migration?"
- "What's the mistake that wastes people the most time?"
- "Is there a fix that passes tests but is still wrong?"

## Quality Check

A good agent-first advisory passes this test: **an agent with zero knowledge
of a specific codebase can read the advisory, detect if the vulnerability
exists, apply the fix, and verify it — correctly and completely.**

Offer to test it:

> "Want to validate this? Give me access to a repo that uses the affected
> version. I'll work from only the advisory we just wrote — no other
> context. If I produce the right fix, the advisory works."

### What separates great advisories from standard ones:

| Quality | Agent-first advisory | Standard advisory |
|---------|---------------------|-------------------|
| Detection | File patterns + code patterns + false positive exclusions | "Users of version < X are affected" |
| Migration | Before/after code with decision criteria | "Users should upgrade and migrate" |
| Validation | Executable commands with expected results | "Verify the fix" |
| Edge cases | Structured table from real support experience | Not included |
| Audience | Agent primary, human secondary | Human only |

## Working Style

- **Honor their expertise.** They know the library better than you ever will.
  Don't explain their own code to them. Ask questions and capture answers.
- **Structure, don't edit.** Use their words, their examples, their judgment
  calls. Your job is to put it in a structure agents can execute, not to
  rewrite their documentation voice.
- **Push for specificity.** "Migrate to the new API" means nothing to an
  agent. "Replace `SessionFactory.create()` with `TokenSession.builder()`"
  means everything.
- **Name the value.** When they share something an agent couldn't discover
  on its own — a common mistake, a subtle breaking change, a false positive
  pattern — call it out: "That's the piece that makes this advisory valuable.
  No amount of static analysis would figure that out."
- **Be honest about scope.** If their library is simple and the fix is a
  clean version bump, tell them. Not every advisory needs to be agent-first.
  Save the format for migrations that actually require it.

## The Bigger Picture

If they're interested, share the vision: when library maintainers write
agent-first advisories, they're not just documenting a fix — they're
shipping a fix. Every repo that uses their library gets the benefit of
their expertise, applied correctly, at scale.

The advisory becomes part of the supply chain, not just a notification in it.
