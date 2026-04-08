# Building a CVE Skill with Ember

You have a CVE hitting multiple repos. You want a skill that fixes it everywhere. Here's how to work with Ember to build one.

---

## What to Bring

- **The CVE ID** (or just the dependency and vulnerable version)
- **One affected repo** you can test against
- **10 minutes** for the first pass. 30-60 for a polished skill.

You don't need to know how to "prompt AI." You know the fix. That's the prompt.

---

## Opening the Conversation

Don't overthink this. Ember isn't a chatbot — it's a partner. Talk to it like a colleague.

### If you know the fix well

> "I need to build an agent skill for CVE-2024-47072. It's an XStream DoS vulnerability. The fix is upgrading to 1.4.21, but it's not just a version bump — XStream changed its security model in 1.4.18. I've done this manually a few times. Help me turn what I know into a skill."

This is the best opening. You're the expert. Ember helps you structure what you already know.

### If you know the CVE but not the full fix

> "I have CVE-2021-44228 (Log4Shell) hitting 30 repos. I know the basics — upgrade log4j — but I'm not sure about all the edge cases. Help me research the full fix and build a skill for it."

Ember will research alongside you. You'll both learn the fix, and the skill captures it.

### If you just have Dependabot alerts

> "I have 47 Dependabot alerts for commons-collections across my org. I want to build a skill to fix them all. Here's what one of the alerts looks like: [paste alert]"

Start with what you have. Ember will help you figure out what the fix actually requires.

---

## The Arc of Building

Here's what typically happens:

**1. Figure out the fix (5-15 min)**
You and Ember research the CVE, understand what changes, identify the gotchas. If you already know the fix, this is fast — you're just articulating what's in your head.

**2. Structure it as a skill (10-20 min)**
Ember helps you organize the fix into steps an agent can follow. Detection → Fix → Validate. The [template](cve-skill-template.md) gives you the skeleton.

**3. Test it cold (5-10 min)**
Point a fresh agent at your repo with just the skill loaded. If it produces the right fix, the skill is good. If not, the skill is missing something — fix it and try again.

**4. Ship it**
Same skill, every repo. Review the PRs. Done.

---

## What Makes Skills Great vs. Mediocre

Lessons from building 60+ of these internally:

### Spend your words on the hard part

The XStream skill is 300 lines. Step 3 (permissions) takes up 40% of it. That's where Dependabot fails. That's where your skill earns its keep.

Don't distribute words evenly. Put them where the complexity lives.

### Include before/after code

Agents produce better output when they can see the target state. Don't just describe the change — show it.

```
BEFORE (vulnerable):
  XStream xstream = new XStream();

AFTER (secure):
  XStream xstream = new XStream();
  xstream.addPermission(AnyTypePermission.ANY);
```

### Describe the decision, not just the action

"Add `AnyTypePermission`" is an action. "Use fine-grained allowlisting for production code, broad permissions for test and educational apps" is a decision. Agents with decisions produce better code than agents with instructions.

### Say what NOT to do

Edge cases, gotchas, common mistakes. The skill should warn: "If you see X, don't do Y — do Z instead." Negative examples prevent the most common failures.

### Test with a cold agent

This is the quality bar. If a fresh agent with zero context about your repo can execute the skill correctly, it's good. If it can't, the skill is missing something.

---

## Conversation Patterns That Work

Once you're building, these prompts help:

| When you want to... | Say something like... |
|---|---|
| Start from an alert | "Here's the Dependabot alert. What's the full fix?" |
| Capture what you know | "I've fixed this manually. Let me walk you through what I do. Turn it into a skill." |
| Handle edge cases | "What happens when the dependency is transitive? When it's in a parent pom?" |
| Test the skill | "Pretend you've never seen this repo. Use only the skill. Fix the CVE." |
| Improve after testing | "The agent missed the test files. What do we need to add to the skill?" |
| Add a new variant | "Same CVE but Gradle instead of Maven. Add Gradle support to the skill." |

---

## After the Conference

The skill you build today is real. It works. You can run it tomorrow against your repos.

When you find edge cases in production, update the skill. It's markdown — you edit it and the next run picks up the change. No redeployment. No pipeline. Just better prose.

And if you build something good — share it. The skill you write for one CVE might save hundreds of developers the same work.
