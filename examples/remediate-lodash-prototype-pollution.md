---
name: js-cve-lodash-prototype-pollution-remediation
description: >
  Remediates Lodash prototype pollution vulnerabilities (CVE-2019-10744,
  CVE-2020-8203, CVE-2021-23337) in Node.js/npm projects by upgrading
  to 4.17.21+ and fixing vulnerable usage patterns. Handles both direct
  dependencies and common code patterns that rely on vulnerable functions.
metadata:
  author: jeferrie
  version: "1.0.0"
  cve-family: lodash-prototype-pollution
  ecosystem: javascript-npm
  severity: high
---

# Remediate Lodash Prototype Pollution in Node.js Projects

> ⚠️ **You are responsible for verifying all changes and following your team's deployment practices before merging to production.** This skill proposes changes — you decide what ships.

## Your Identity

You are a remediation partner helping a JavaScript/TypeScript developer fix Lodash prototype pollution vulnerabilities. You do the analysis, propose specific changes, and explain your reasoning — but the developer makes the final call on every change.

Be precise about what the upgrade requires. Unlike most npm bumps, prototype pollution fixes sometimes need code changes — particularly around `_.defaultsDeep`, `_.merge`, `_.set`, and `_.template`. Automated tools miss the code patterns. You won't.

## Context & Purpose

**What:** Lodash versions prior to 4.17.21 are vulnerable to prototype pollution — an attacker can inject properties into `Object.prototype` via crafted input, affecting all objects in the application. This can lead to denial of service, property injection, and in some configurations, remote code execution.

**Key CVEs resolved:**
- **CVE-2019-10744** (Critical) — `_.defaultsDeep` allows prototype pollution via crafted objects
- **CVE-2020-8203** (High) — `_.zipObjectDeep` and other deep-path functions pollute prototypes
- **CVE-2021-23337** (High) — `_.template` allows arbitrary code execution via template strings

**Why it matters:** Lodash is one of the most depended-upon packages in the npm ecosystem. Prototype pollution in Lodash can be exploited in any application that passes user-controlled objects to vulnerable functions — which is extremely common in Express/Koa middleware, configuration merging, and API input handling.

**Target version:** 4.17.21 (February 2021) — resolves all known Lodash prototype pollution CVEs.

## When to Use This Skill

- Dependabot, Snyk, or npm audit flags Lodash vulnerabilities
- A security scan identifies `lodash` at any version below 4.17.21
- You are performing a compliance sweep for known CVEs across JavaScript/TypeScript repositories

## Why This Isn't Just a Version Bump

For most projects, upgrading Lodash is straightforward. But three patterns need attention:

1. **`_.template` with user input** — CVE-2021-23337 means `_.template` can execute arbitrary code if the template string comes from user input. Upgrading doesn't fully fix this — the usage pattern needs to change.
2. **Deep merge with untrusted data** — `_.defaultsDeep` and `_.merge` with user-controlled objects were the prototype pollution vector. Even after upgrading, passing raw `req.body` into deep merge functions is a smell worth flagging.
3. **Cherry-picked imports** — Many projects import individual Lodash functions (`lodash.merge`, `lodash.defaultsdeep`) as separate packages. These have their own versions and may not be covered by upgrading the main `lodash` package.

---

## Step 1: Detect Lodash Usage

### In package.json

Look for Lodash dependencies. There are several forms:

**The main package:**
```json
"dependencies": {
  "lodash": "^4.17.11"
}
```

**Individual method packages (common in older projects):**
```json
"dependencies": {
  "lodash.merge": "^4.6.1",
  "lodash.defaultsdeep": "^4.6.0",
  "lodash.template": "^4.4.0",
  "lodash.set": "^4.3.2"
}
```

**The ES module variant:**
```json
"dependencies": {
  "lodash-es": "^4.17.11"
}
```

Record all Lodash-related packages and their current versions.

### In source files

Search for vulnerable usage patterns:

```
_.defaultsDeep(
_.merge(
_.set(
_.setWith(
_.template(
_.zipObjectDeep(
```

Also search for cherry-picked imports:
```
require('lodash.merge')
require('lodash.defaultsdeep')
require('lodash/merge')
import merge from 'lodash/merge'
```

Record every file and the specific functions used. These are the sites that may need code review beyond the version bump.

---

## Step 2: Update Lodash Version

### Main lodash package

```bash
npm install lodash@4.17.21
```

Or in package.json, change:
```json
"lodash": "^4.17.11"
```
To:
```json
"lodash": "^4.17.21"
```

### Individual method packages

Each cherry-picked package needs its own update:

```bash
npm install lodash.merge@latest lodash.defaultsdeep@latest lodash.template@latest lodash.set@latest
```

**Important:** Some individual packages haven't been updated to fix all CVEs. The recommended migration is to switch from individual packages to the main `lodash` package:

```json
// BEFORE — individual packages with inconsistent versions
"lodash.merge": "^4.6.1",
"lodash.defaultsdeep": "^4.6.0"

// AFTER — single package, all fixes included
"lodash": "^4.17.21"
```

Then update imports:
```javascript
// BEFORE
const merge = require('lodash.merge');
const defaultsDeep = require('lodash.defaultsdeep');

// AFTER
const { merge, defaultsDeep } = require('lodash');
```

### lodash-es

```bash
npm install lodash-es@4.17.21
```

---

## Step 3: Review Vulnerable Code Patterns

### Pattern A: Deep merge with user input

**Vulnerable:**
```javascript
const config = _.defaultsDeep(req.body, defaultConfig);
```

**Why it's risky:** Even with Lodash 4.17.21, passing raw user input to deep merge functions is a code smell. The prototype pollution fix prevents `__proto__` injection, but defense in depth matters.

**Recommended:**
```javascript
// Sanitize or validate input before deep merge
const sanitized = sanitizeInput(req.body);
const config = _.defaultsDeep(sanitized, defaultConfig);
```

Flag these for developer review — they may or may not need changes depending on whether the input is truly user-controlled.

### Pattern B: _.template with dynamic strings

**Vulnerable (CVE-2021-23337):**
```javascript
const compiled = _.template(userProvidedString);
```

**Why it's dangerous:** `_.template` compiles strings into JavaScript functions. User-controlled template strings can execute arbitrary code. The Lodash upgrade adds some protections, but this pattern should be eliminated regardless.

**Recommended:**
```javascript
// Use a dedicated template engine with sandboxing
// Or use template literals if the source is trusted
const compiled = _.template(STATIC_TEMPLATE_STRING);
const result = compiled({ name: userInput });
```

This pattern always needs manual review. The fix is architectural — move user input from the template string to the template data.

### Pattern C: _.set with user-controlled paths

**Vulnerable:**
```javascript
_.set(config, req.body.path, req.body.value);
```

**Why it's risky:** If `path` is user-controlled, an attacker could set `__proto__.isAdmin` to `true`. Lodash 4.17.21 blocks `__proto__` paths, but `constructor.prototype` variants may still work in edge cases.

**Recommended:**
```javascript
// Validate the path before using _.set
const allowedPaths = ['name', 'email', 'preferences.theme'];
if (allowedPaths.includes(req.body.path)) {
  _.set(config, req.body.path, req.body.value);
}
```

---

## Step 4: Update Lock File

After all package.json changes:

```bash
npm install
```

Or if using a lock file:

```bash
rm -rf node_modules package-lock.json
npm install
```

Verify the installed version:

```bash
npm ls lodash
```

All instances should show 4.17.21 or higher. Watch for nested dependencies that pin older versions — these show as deduped entries at lower versions.

---

## Step 5: Validate

Run the following checks:

1. **Install:** `npm install` — should complete without errors
2. **Lint:** `npm run lint` (if configured) — should pass
3. **Tests:** `npm test` — all tests should pass
4. **Audit:** `npm audit` — Lodash CVEs should no longer appear
5. **Search for remaining issues:** Grep for `lodash.merge`, `lodash.defaultsdeep`, `lodash.template`, `lodash.set` in package.json to ensure no cherry-picked packages remain at vulnerable versions

### Common validation failures

| Symptom | Cause | Fix |
|---|---|---|
| `npm audit` still shows Lodash CVEs | A transitive dependency pins an older Lodash version | Add an `overrides` section in package.json (npm 8.3+): `"overrides": { "lodash": "4.17.21" }` |
| Tests fail after switching from cherry-picked to main package | Import paths changed | Update `require('lodash.merge')` to `require('lodash').merge` or `const { merge } = require('lodash')` |
| TypeScript errors after upgrade | Type definitions mismatch | `npm install @types/lodash@latest` |

---

## Step 6: Create Pull Request

### PR Title
`fix: upgrade lodash to 4.17.21 to resolve prototype pollution CVEs`

### PR Body Template

```markdown
## Summary

Upgrades Lodash to 4.17.21, resolving prototype pollution vulnerabilities
(CVE-2019-10744, CVE-2020-8203, CVE-2021-23337).

## What changed

### package.json
- Updated `lodash` from [old version] to 4.17.21
- [If applicable] Consolidated cherry-picked lodash packages into main package

### Source files
- [If applicable] Reviewed [count] usage sites for vulnerable patterns
- [If applicable] Flagged [count] _.template / _.merge sites for follow-up

### Lock file
- Regenerated package-lock.json

## Why this matters

Lodash prototype pollution allows attackers to inject properties into
Object.prototype via crafted input to functions like `defaultsDeep`,
`merge`, and `set`. This can lead to denial of service, property injection,
and in configurations using `_.template`, remote code execution.

## Testing

- [ ] `npm install` completes
- [ ] `npm test` passes
- [ ] `npm audit` shows no Lodash CVEs
- [ ] No cherry-picked lodash packages remain at vulnerable versions

## References

- [CVE-2019-10744](https://nvd.nist.gov/vuln/detail/CVE-2019-10744)
- [CVE-2020-8203](https://nvd.nist.gov/vuln/detail/CVE-2020-8203)
- [CVE-2021-23337](https://nvd.nist.gov/vuln/detail/CVE-2021-23337)
- [Lodash Changelog](https://github.com/lodash/lodash/wiki/Changelog)
```

---

## Scope and Limitations

This skill handles:
- npm projects with direct Lodash dependencies
- Cherry-picked Lodash method packages (`lodash.merge`, etc.)
- `lodash-es` ES module variant
- Common vulnerable code patterns (deep merge, template, set)

This skill does NOT handle:
- Yarn/pnpm (different lock file and install commands — adapt accordingly)
- Lodash vendored/bundled inside other packages (requires upgrading the parent)
- Projects using lodash alternatives (Ramda, underscore) — different fix paths
- Server-side rendering frameworks with custom template compilation — may need framework-specific guidance

When these cases are detected, flag them for manual review.
