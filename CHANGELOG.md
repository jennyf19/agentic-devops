# Changelog

All notable changes to Agentic DevOps will be documented here.

## [0.3.0] — 2026-04-14

### Added
- agent-signals/closing-the-loop.md — Signal-consuming agent pattern specification: how a dedicated agent reads accumulated signals, detects recurring patterns, and opens PRs to improve skills

### Changed
- agent-signals/README.md — Added "Closing the Loop" to See Also section and linked from step 4

## [0.2.0] — 2026-04-11

### Added
- MIT LICENSE
- CONTRIBUTING.md — contribution guide with Ember as recommended tool
- agent-signals/SIGNAL.md — protocol contract file
- agent-signals/quickstart.md — 5-minute quick start guide
- CHANGELOG.md
- Second worked example: Lodash prototype pollution (Node.js/npm)

### Changed
- Prompt guide: removed conference-specific language, added CONTRIBUTING link

## [0.1.0] — 2026-04-08

### Added
- Initial release
- skills/build-cve-skill.md — how to build a CVE remediation skill
- skills/build-agent-first-advisory.md — agent-first advisory concept
- agent-signals/ — Agent Signals protocol with execution, outcome, escalation, and partnership signal types
- agent-signals/examples/ — JSON examples for all four signal types
- examples/remediate-xstream-cve.md — XStream CVE remediation worked example (Java/Maven)
- reference/prompt-guide.md — prompt engineering guide for agent skills
- reference/cve-skill-template.md — CVE skill template
- reference/agent-first-advisory.md — agent-first advisory reference
- _config.yml — GitHub Pages with minimal theme
