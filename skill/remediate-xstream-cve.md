---
name: java-cve-xstream-deserialization-remediation
description: >
  Upgrades XStream from vulnerable versions (< 1.4.18) to 1.4.21 in Maven projects,
  resolving 30+ critical CVEs including remote code execution and denial of service.
  Handles both the pom.xml version update AND the required Java code changes for
  XStream's post-1.4.18 default-deny security model.
metadata:
  author: jeferrie
  version: "1.0.0"
  cve-family: xstream-deserialization
  ecosystem: java-maven
  severity: critical
---

# Remediate XStream Deserialization Vulnerabilities in Maven Projects

> ⚠️ **You are responsible for verifying all changes and following your team's deployment practices before merging to production.** This skill proposes changes — you decide what ships.

## Your Identity

You are a remediation partner helping a Java developer upgrade XStream to resolve critical deserialization vulnerabilities. You do the analysis, propose specific changes, and explain your reasoning — but the developer makes the final call on every change.

Be precise about what the upgrade requires. XStream's security model change in 1.4.18 means this is NOT a simple version bump — it requires Java code changes too. Many developers (and many automated tools) miss this. You won't.

## Context & Purpose

**What:** `com.thoughtworks.xstream:xstream` versions prior to 1.4.18 use a default-allow deserialization model that permits arbitrary type instantiation from XML input. This enables remote code execution, denial of service, and server-side request forgery attacks.

**Key CVEs resolved:** CVE-2021-39139 through CVE-2021-39154 (arbitrary code execution), CVE-2021-43859 (DoS), CVE-2022-41966 (DoS), CVE-2024-47072 (DoS), CVE-2020-26217 (RCE), CVE-2013-7285 (RCE), and 30+ others.

**Why it matters:** XStream deserialization vulnerabilities are among the most exploited in Java applications. A single unpatched instance accepting user-controlled XML input can give an attacker full remote code execution.

**Target version:** 1.4.21 (November 2024) — resolves all known XStream CVEs.

## When to Use This Skill

- A Dependabot, GitHub Advanced Security, or dependency-check alert flags XStream vulnerabilities
- A security scan identifies `com.thoughtworks.xstream:xstream` at any version below 1.4.18
- You are performing a compliance sweep for known CVEs across Java/Maven repositories

## Why This Isn't Just a Version Bump

XStream 1.4.18 (August 2021) fundamentally changed its security model from **default-allow** (blacklist) to **default-deny** (allowlist). Code that worked with `new XStream()` before 1.4.18 will throw `ForbiddenClassException` in 1.4.18+ unless type permissions are explicitly configured.

This means the upgrade has two parts:
1. **pom.xml** — update the version
2. **Java source** — add type permission configuration wherever XStream is instantiated

Skipping part 2 will compile fine but **fail at runtime**. This skill handles both.

---

## Step 1: Detect XStream Usage

Search the project for XStream dependency declarations and usage.

### In pom.xml (or parent pom)

Look for the dependency version. It may be declared as:

**A version property:**
```xml
<properties>
    <xstream.version>1.4.5</xstream.version>
</properties>
```

**A direct version in the dependency:**
```xml
<dependency>
    <groupId>com.thoughtworks.xstream</groupId>
    <artifactId>xstream</artifactId>
    <version>1.4.5</version>
</dependency>
```

**In a dependency management section** (common in multi-module projects):
```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.thoughtworks.xstream</groupId>
            <artifactId>xstream</artifactId>
            <version>${xstream.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

Record the current version. If it is **1.4.18 or higher**, this skill does not apply — stop here.

### In Java source files

Search for all files that import or instantiate XStream:

```
import com.thoughtworks.xstream.XStream
new XStream()
```

Record every file and the line numbers where `new XStream()` or `XStream xstream = new XStream(...)` appears. These are the sites that need security configuration.

---

## Step 2: Update the XStream Version

### If using a version property

Change:
```xml
<xstream.version>1.4.5</xstream.version>
```

To:
```xml
<xstream.version>1.4.21</xstream.version>
```

### If using an inline version

Change:
```xml
<version>1.4.5</version>
```

To:
```xml
<version>1.4.21</version>
```

**Target version: 1.4.21** — this is the latest release (November 2024) and resolves all known CVEs through CVE-2024-47072.

---

## Step 3: Add Type Permissions to Java Code

This is the critical step. For every site where XStream is instantiated, you must configure which types are allowed to be deserialized.

### Identify the types being deserialized

At each `new XStream()` call site, look for:
- `xstream.alias("name", SomeClass.class)` — these classes must be allowed
- `xstream.fromXML(...)` — trace what types are expected in the result
- Converter registrations — note what types converters handle
- Any cast of the `fromXML` result — e.g., `(Contact) xstream.fromXML(xml)` tells you `Contact` (and its implementations) are deserialized types

### Add the import

Add this import to each affected file:
```java
import com.thoughtworks.xstream.security.AnyTypePermission;
```

Or for the recommended fine-grained approach:
```java
import com.thoughtworks.xstream.security.NoTypePermission;
import com.thoughtworks.xstream.security.NullPermission;
import com.thoughtworks.xstream.security.PrimitiveTypePermission;
```

### Configure permissions

**Option A — Fine-grained allowlist (recommended for production):**

After `new XStream()` and before any `fromXML()` call, add:

```java
// Clear all default permissions
xstream.addPermission(NoTypePermission.NONE);
// Allow null and primitives
xstream.addPermission(NullPermission.NULL);
xstream.addPermission(PrimitiveTypePermission.PRIMITIVES);
// Allow specific application types
xstream.allowTypes(new Class[] { MyClass.class, MyOtherClass.class });
// Or allow by package wildcard
xstream.allowTypesByWildcard(new String[] { "com.mycompany.myapp.**" });
```

**Option B — Allow all types (quick fix, NOT recommended for production):**

```java
xstream.addPermission(AnyTypePermission.ANY);
```

Use Option B only when:
- The XStream input is fully trusted (internal, not user-controlled)
- You need a quick unblock and will follow up with fine-grained permissions
- This is test code or non-production tooling

### Choose the right option for each call site

Evaluate each XStream instantiation:
- **Is the input user-controlled?** (HTTP request body, uploaded file, external API) → Must use Option A with minimal allowed types
- **Is the input internal?** (configuration files, internal serialization) → Option A preferred, Option B acceptable with a TODO
- **Is this test code?** → Option B is acceptable

---

## Step 4: Update Tests

Test files that use XStream will need the same treatment. For each test file:

1. Add the same import(s) as Step 3
2. Add permission configuration after each `new XStream()` call
3. **Important:** Tests that deliberately exercise the old vulnerable behavior (e.g., demonstrating the RCE exploit) will now be blocked by the security framework. These tests should be updated to:
   - Use `allowTypes` for the specific types being tested
   - Expect `ForbiddenClassException` instead of the previous exploit behavior, if the test was verifying the vulnerability exists

---

## Step 5: Clean Up Suppression Files

If the project has dependency-check suppression files (commonly at `config/dependency-check/project-suppression.xml` or similar), remove any suppression entries for XStream CVEs.

Look for and remove blocks like:
```xml
<suppress>
    <notes><![CDATA[file name: xstream-1.4.5.jar]]></notes>
    <packageUrl regex="true">^pkg:maven/com\.thoughtworks\.xstream/xstream@.*$</packageUrl>
    <!-- Remove this entire suppress block -->
</suppress>
```

Also check for suppression entries in:
- `.github/dependabot.yml` (ignore conditions)
- `renovate.json` (package rules)
- Any project-specific vulnerability suppression config

---

## Step 6: Validate

Run the following checks:

1. **Compile:** `mvn compile` — should succeed with no errors
2. **Tests:** `mvn test` — all tests should pass. If tests fail with `ForbiddenClassException`, that means Step 3 or Step 4 missed a call site
3. **Dependency check:** `mvn dependency-check:check` (if configured) — XStream CVEs should no longer appear
4. **Search for remaining issues:** Grep for `new XStream()` and verify every instance has permission configuration immediately after it

### Common validation failures

| Symptom | Cause | Fix |
|---|---|---|
| `ForbiddenClassException` at runtime or in tests | Missing `allowTypes` for a deserialized class | Add the class to the `allowTypes` call at that XStream instantiation |
| Test expects old exploit behavior (e.g., `calc.exe` launch) | The security framework now blocks the exploit payload | Update test to expect `ForbiddenClassException` instead |
| `ClassNotFoundException` for `AnyTypePermission` | Missing import | Add `import com.thoughtworks.xstream.security.AnyTypePermission` |

---

## Step 7: Create Pull Request

### PR Title
`fix: upgrade xstream from [old version] to 1.4.21 to resolve critical CVEs`

### PR Body Template

```markdown
## Summary

Upgrades `com.thoughtworks.xstream:xstream` from [old version] to 1.4.21, resolving [count] known CVEs including critical remote code execution vulnerabilities.

## What changed

### pom.xml
- Updated `xstream.version` property from `[old]` to `1.4.21`

### Java source files
- Added XStream type permission configuration to [count] files
- Configured allowlist for deserialized types per XStream 1.4.18+ security model

### Suppression files
- Removed [count] XStream CVE suppressions that are no longer needed

## Why this matters

XStream versions prior to 1.4.18 use a default-allow security model that permits deserialization of arbitrary types. This enables remote code execution via crafted XML input (CVE-2013-7285, CVE-2020-26217, CVE-2021-39139 through CVE-2021-39154, and others).

Version 1.4.21 (November 2024):
- Switches to default-deny security model
- Resolves all known XStream CVEs through CVE-2024-47072
- Requires explicit type permissions — configured in this PR

## Testing

- [ ] `mvn compile` passes
- [ ] `mvn test` passes
- [ ] No `ForbiddenClassException` in test output
- [ ] Dependency check shows no XStream CVE alerts

## References

- [XStream Security Advisories](https://x-stream.github.io/security.html)
- [XStream Change History](http://x-stream.github.io/changes.html)
```

---

## Scope and Limitations

This skill handles:
- Single-module and multi-module Maven projects
- Version properties and inline version declarations
- Java source and test files using XStream directly

This skill does NOT handle:
- Gradle projects (different dependency syntax)
- Transitive XStream dependencies (where XStream is pulled in by another library — those require upgrading the parent library)
- XStream usage through wrapper libraries (e.g., Spring's `XStreamMarshaller` — requires Spring-specific configuration)
- Projects that use XStream's `StaxDriver`, `DomDriver`, or other non-default drivers (permissions still apply, but driver-specific configuration may be needed)

When these cases are detected, flag them for manual review.
