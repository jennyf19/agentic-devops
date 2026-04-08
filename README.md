# From CVE to Agent Skill

> **For:** Developers who want to stop fixing the same vulnerability by hand across dozens of repos
> **Works with:** [Ember](https://github.com/github/awesome-copilot), Copilot, or any AI agent that reads markdown

A CVE remediation skill is a markdown file that teaches an AI agent how to
fix a specific vulnerability — detect it, apply the fix, validate it, open
a PR. One developer writes it once. Then it runs everywhere.

---

## Don't Read Docs. Load a Skill.

These aren't guides for you to read — they're skills for your agent to read.
Load one, tell the agent what you're working on, and build together.

### "I have a CVE hitting my repos"

Load **[build-cve-skill.md](build-cve-skill.md)** and say:

> *"I need to build a remediation skill for [CVE-YYYY-NNNNN]. Here's what
> I know about the fix..."*

The skill teaches the agent how to pull your expertise out and structure it
into something a cold agent can execute across your fleet. Any language,
any ecosystem.

### "I own the library / I write the advisory"

Load **[build-agent-first-advisory.md](build-agent-first-advisory.md)** and say:

> *"I maintain [library]. We just fixed [CVE]. I want to write an advisory
> that agents can execute, not just read."*

The skill teaches the agent how to help you write documentation that IS
the fix — so developers using your library don't need a separate skill
at all.

---

## Getting Started

Install Ember or use any agent:

```
copilot plugin install ember@awesome-copilot
```

Or just point your agent at one of the skill files above. They're markdown —
they work anywhere.

---

## The Pattern

```
CVE drops
    → Developer who knows the fix writes a skill (30-60 min)
        → Test against one repo
            → Run across the fleet
                → Humans review and merge
                    → Retire when clean
```

The skill is institutional memory. When the developer who figured out the
fix switches teams, the knowledge doesn't leave with them. It's a markdown
file in a repo.

---

## What's Here

| File | What | Who |
|------|------|-----|
| [build-cve-skill.md](build-cve-skill.md) | **Skill:** Build a CVE remediation skill | Devs with CVEs to fix |
| [build-agent-first-advisory.md](build-agent-first-advisory.md) | **Skill:** Write an agent-executable advisory | Library maintainers, security teams |
| [cve-skill-template.md](cve-skill-template.md) | Blank template (reference) | Quick start if you know the pattern |

The first two are skills — load them into your agent. The template is
reference material if you already know the pattern and want a blank slate.
