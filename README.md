# Agentic DevOps

> What persists when the model changes, the tools evolve, and the platform shifts?
> The feedback loop. The institutional memory. The partnership between humans and agents.

This repo is for teams building with AI agents — not as automation, but as
collaborators. Three paths depending on where you are.

---

## Don't Read Docs. Load a Skill.

These aren't guides for you to read — they're skills for your agent to read.
Load one, tell the agent what you're working on, and build together.

### "I have a CVE hitting my repos"

Load **[build-cve-skill.md](skills/build-cve-skill.md)** and say:

> *"I need to build a remediation skill for [CVE-YYYY-NNNNN]. Here's what
> I know about the fix..."*

The skill teaches the agent how to pull your expertise out and structure it
into something a cold agent can execute across your fleet. Any language,
any ecosystem.

### "I own the library / I write the advisory"

Load **[build-agent-first-advisory.md](skills/build-agent-first-advisory.md)** and say:

> *"I maintain [library]. We just fixed [CVE]. I want to write an advisory
> that agents can execute, not just read."*

The skill teaches the agent how to help you write documentation that IS
the fix — so developers using your library don't need a separate skill
at all.

### "I want my agents to learn from every session"

Read **[Agent Signals](agent-signals/)** — the feedback loop that makes
everything else compound.

> Models change. Tools change. What persists is the loop: agent does work,
> agent reports what it thought, humans verify, the system gets smarter.

Agent Signals is an open protocol for capturing agent reasoning,
self-assessment, and outcomes. Skills are the input. Signals are the output.
Together they close the loop.

---

## Getting Started

Install [Ember](https://github.com/github/awesome-copilot) or use any agent:

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
                    → Agent signals capture what worked, what was hard
                        → Next run starts smarter
                            → Retire when clean
```

The skill is institutional memory. When the developer who figured out the
fix switches teams, the knowledge doesn't leave with them. It's a markdown
file in a repo.

The signal is the feedback loop. When the agent struggles with a pattern the
skill doesn't cover, the signal captures it. The next skill update includes
what the agent learned. The system compounds.

---

## What's Here

### Skills — load these into your agent

| File | What | Who |
|------|------|-----|
| [build-cve-skill.md](skills/build-cve-skill.md) | Build a CVE remediation skill | Devs with CVEs to fix |
| [build-agent-first-advisory.md](skills/build-agent-first-advisory.md) | Write an agent-executable advisory | Library maintainers, security teams |

### Agent Signals — the feedback loop

| File | What |
|------|------|
| [Agent Signals](agent-signals/) | The protocol for agent self-assessment, trust measurement, and self-improving skills |

### Examples — see what the output looks like

| File | What |
|------|------|
| [remediate-xstream-cve.md](examples/remediate-xstream-cve.md) | A finished skill — XStream deserialization fix for Maven projects |

### Reference — background reading

| File | What |
|------|------|
| [cve-skill-template.md](reference/cve-skill-template.md) | Blank template if you already know the pattern |
| [agent-first-advisory.md](reference/agent-first-advisory.md) | The concept behind agent-executable advisories |
| [prompt-guide.md](reference/prompt-guide.md) | Conversation patterns for working with your agent |

---

## Resources

### Talks

- [The Interaction Changes Everything](https://devblogs.microsoft.com/engineering-at-microsoft/the-interaction-changes-everything-treating-ai-agents-as-collaborators-not-automation/) — Engineering at Microsoft
- [Agentic DevOps: From CVE to Agent Skill](https://ignite.microsoft.com/en-US/sessions/BRK115) — Microsoft Ignite 2025
- [Building Agent Skills for DevOps](https://www.youtube.com/watch?v=jvzPLZQQD3A) — Microsoft Reactor

### Research

- [How Confessions Can Keep Language Models Honest](https://openai.com/index/how-confessions-can-keep-language-models-honest/) — OpenAI
- [Scalable Oversight of AI Systems](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) — Anthropic
- [Agent Skills Protocol](https://agentskills.io) — Anthropic
- [Agent Signals Specification](https://github.com/jeferrie_microsoft/AI-Experiments/tree/main/agentsignals) — The full protocol
