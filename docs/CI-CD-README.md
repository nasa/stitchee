# CI/CD and Branching Strategy

A developer's guide to working with the stitchee repository's automated build, test, and deployment pipeline.

---

## Branch Structure and Flow

```
                    Production
                    ┌──────────────────────┐
                    │   main (ops)         │
                    │   Version: 1.11.0    │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
         ┌──────────▼────────┐  ┌────────▼──────────┐
         │  release/1.11.0   │  │  hotfix/1.11.1    │
         │  (uat)            │  │  (ops)            │
         │  1.11.0rc1        │  │  1.11.1           │
         └──────────┬────────┘  └───────────────────┘
                    │                     │
                    │                     │ backport
         ┌──────────▼─────────────────────▼──────┐
         │        develop (sit)                   │
         │        Version: 1.12.0a1               │
         └──────────┬────────────────────────────┘
                    │
         ┌──────────┼──────────┬─────────────┐
         │          │          │             │
    ┌────▼───┐ ┌───▼────┐ ┌───▼──────┐ ┌───▼──────┐
    │feature/│ │issue/  │ │docs/     │ │feature/  │
    │algo    │ │bug-123 │ │readme    │ │netcdf    │
    │(dev)   │ │(dev)   │ │(dev)     │ │(dev)     │
    └────────┘ └────────┘ └──────────┘ └──────────┘
         │          │          │             │
         └──────────┴──────────┴─────────────┘
                    │
                    │ All PRs go to develop
                    ▼
```

### Branch Purpose Table

| Branch Pattern | Purpose | Version Example | Environment | Protected |
|----------------|---------|-----------------|-------------|-----------|
| `main` | Production releases | `1.11.0` | Production (ops) | ✅ Yes |
| `release/X.Y.0` | Release candidates | `1.11.0rc1` | UAT (uat) | ✅ Yes |
| `hotfix/X.Y.Z` | Emergency production fixes | `1.11.1` | Production (ops) | ✅ Yes |
| `develop` | Integration & testing | `1.11.0a5` | SIT (sit) | ✅ Yes |
| `feature/*` | New features | (no bump) | Not deployed | ❌ No |
| `issue/*` | Bug fixes | (no bump) | Not deployed | ❌ No |
| `docs/*` | Documentation | (no bump) | Not deployed | ❌ No |

---

## Publishing Environments

The stitchee project uses different publishing targets based on the branch and stage:

### Python Package Publishing

| Branch/Event | Target Registry | Version Example | Purpose |
|-------------|----------------|-----------------|----------|
| `develop` | ❌ Not published | `1.11.0a5` | Development/SIT testing |
| `release/*` | 🧪 **test.pypi.org** | `1.11.0rc2` | Pre-release validation |
| `main` (via GitHub Release) | ✅ **pypi.org** | `1.11.0` | Production release |

**Test PyPI Note:** Release candidates are automatically published to [Test PyPI](https://test.pypi.org/)
when PRs are merged to release branches. This allows final validation before production release.

To install from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ stitchee==1.11.0rc2
```

### Docker Image Publishing

| Branch | Target Registry | Tags | Purpose |
|--------|----------------|------|----------|
| `develop` | ghcr.io | `sit`, `1.11.0a5` | SIT environment |
| `release/*` | ghcr.io | `uat`, `1.11.0rc2` | UAT environment |
| `main` (via Release) | ghcr.io | `ops`, `latest`, `1.11.0` | Production |

### Venue Mapping

- **dev** - Feature branches (not deployed)
- **sit** (System Integration Test) - `develop` branch
- **uat** (User Acceptance Test) - `release/*` branches
- **ops** (Production) - `main` branch

---

## Complete CI/CD Pipeline

### 1. Pull Request Opened

```
┌──────────────────────────────────────────────────────────────┐
│  Developer opens PR: feature/my-feature → develop            │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │   pr-checks.yml           │
         │   (runs automatically)    │
         └───────────┬───────────────┘
                     │
         ┌───────────┴────────────┬─────────────┬──────────────┐
         │                        │             │              │
         ▼                        ▼             ▼              ▼
   ┌──────────┐           ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Security │           │  Linting │   │   Type   │   │   Unit   │
   │   Scan   │           │  (ruff)  │   │  Check   │   │  Tests   │
   │  (Snyk)  │           │          │   │ (mypy)   │   │ + Cov    │
   └────┬─────┘           └────┬─────┘   └────┬─────┘   └────┬─────┘
        │                      │              │              │
        │  High severity?      │  Style OK?   │  Types OK?   │  Pass?
        │                      │              │              │
        └──────────────────────┴──────────────┴──────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  CHANGELOG check    │
                    │  (develop/main/     │
                    │   release only)     │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │    PR Summary       │
                    │  (shows all status) │
                    └─────────────────────┘
                              │
                              ▼
               ✅ All checks pass → Ready for review
               ❌ Any check fails → Fix and push again
```

### 2. Push to Protected Branch

```
┌──────────────────────────────────────────────────────────────┐
│  Push to protected branch: develop, main, release/*, hotfix/* │
│  (Could be from PR merge OR direct push)                     │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  version-and-build.yml    │
         │  (runs automatically)     │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  Check commit message:    │
         │  "Merge pull request..."? │
         └───────────┬───────────────┘
                     │
         ┌───────────┴───────────┐
         │ Yes                   │ No
         │ (PR merge)            │ (Direct push)
         │                       │
         ▼                       ▼
┌─────────────────┐      ┌──────────────────┐
│ Version Bump    │      │ Skip version bump│
│ (automatic)     │      │ (use current)    │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  develop branch?       │
         │  or release branch?    │
         └────────┬───────────────┘
                  │
                  │ Yes
                  ▼
         ┌────────────────────────┐
         │  Integration Tests     │
         │  (with EDL creds)      │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  Build Python Package  │
         └────────┬───────────────┘
                  │
         ┌────────┴────────┬─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Create Tag  │   │ Build Docker│   │ Publish to  │
│ (dev/main/  │   │ (dev/rel    │   │ Test PyPI   │
│  release)   │   │  branches)  │   │ (rel branch)│
└─────────────┘   └─────────────┘   └─────────────┘
         │                 │                 │
         └─────────────────┴─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Snyk Monitor   │
                 │  (continuous    │
                 │   security)     │
                 └─────────────────┘
```

### 3. Production Release

```
┌──────────────────────────────────────────────────────────────┐
│  Maintainer creates GitHub Release with tag (e.g., v1.11.0)  │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │     publish.yml           │
         │     (runs automatically)  │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  Verify version matches   │
         │  git tag                  │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  Build Python Package     │
         └───────────┬───────────────┘
                     │
         ┌───────────┴───────────┬─────────────────┐
         │                       │                 │
         ▼                       ▼                 ▼
┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐
│ Publish to      │   │ Build & Push     │   │ Snyk Monitor │
│ PyPI (prod)     │   │ Docker Image     │   │ (production) │
│ pypi.org        │   │ ghcr.io          │   │              │
└─────────────────┘   └──────────────────┘   └──────────────┘
         │                       │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │   🚀 LIVE IN PRODUCTION   │
         └───────────────────────────┘
```

---

## Version Bumping Logic

### How Versions Change Per Branch

```
develop branch:
    PR merge #1: 1.11.0a1 → 1.11.0a2
    PR merge #2: 1.11.0a2 → 1.11.0a3
    PR merge #3: 1.11.0a3 → 1.11.0a4
    (continues incrementing alpha...)

release/1.11.0 branch:
    First commit:  1.11.0a4  → 1.11.0rc1  (alpha becomes rc)
                   + develop auto-bumps to 1.12.0a1
    PR merge #1:   1.11.0rc1 → 1.11.0rc2
    PR merge #2:   1.11.0rc2 → 1.11.0rc3
    (continues incrementing rc...)

main branch:
    Merge from release: 1.11.0rc3 → 1.11.0 (strips pre-release)

hotfix/1.11.1 branch:
    PR merge: 1.11.0 → 1.11.1 (increments patch)
```

### Version Format Explained

```
     1  .  11  .  0   rc   1
     │     │     │    │    │
     │     │     │    │    └─ Pre-release number
     │     │     │    └────── Pre-release label (a=alpha, rc=release candidate)
     │     │     └─────────── Patch version
     │     └───────────────── Minor version
     └─────────────────────── Major version
```

**Examples:**
- `1.11.0a5` - Alpha 5 (develop branch, SIT environment)
- `1.11.0rc2` - Release candidate 2 (release branch, UAT environment)
- `1.11.0` - Final release (main branch, Production)
- `1.11.1` - Patch release (hotfix)

---

## Understanding `[skip ci]` Commits

You'll see some commits in the repository history with `[skip ci]` in the message:

```
Bump version to 1.11.0a2 [skip ci]
Start 1.12.0a1 development [skip ci]
```

### Why `[skip ci]`?

The `[skip ci]` tag tells GitHub Actions to **skip running workflows** for that commit. This prevents infinite loops:

**Without `[skip ci]`:**
```
1. PR merged → version-and-build.yml runs
2. Version bumped → commit pushed
3. New commit pushed → version-and-build.yml runs again
4. Version bumped again → commit pushed
5. New commit pushed → version-and-build.yml runs again
6. ♾️ Infinite loop!
```

**With `[skip ci]`:**
```
1. PR merged → version-and-build.yml runs
2. Version bumped → commit with [skip ci]
3. Commit skips workflows ✅ Done!
```

### Other Skip Patterns

GitHub recognizes these patterns (case-insensitive):
- `[skip ci]`
- `[ci skip]`
- `[no ci]`
- `[skip actions]`
- `[actions skip]`

**When to use manually:** If you need to update documentation or make a minor fix that doesn't require CI to run, add `[skip ci]` to your commit message. However, for most development work, let CI run normally.

---

## Typical Development Workflow

### Scenario: Adding a New Feature

```
Step 1: Create Feature Branch
┌─────────────────────────────────────┐
│ $ git checkout develop              │
│ $ git pull                          │
│ $ git checkout -b feature/my-feat   │
└─────────────────────────────────────┘
                │
                ▼
Step 2: Develop & Push
┌─────────────────────────────────────┐
│ $ git add .                         │
│ $ git commit -m "Add feature"       │
│ $ git push -u origin feature/...    │
└─────────────────────────────────────┘
                │
                ▼
Step 3: Open PR on GitHub
┌─────────────────────────────────────┐
│ feature/my-feat → develop           │
│                                     │
│ ✓ Security scan                     │
│ ✓ Linting                           │
│ ✓ Type checking                     │
│ ✓ Unit tests                        │
│ ⚠ Update CHANGELOG.md               │
└─────────────────────────────────────┘
                │
                ▼
Step 4: Code Review & Approval
┌─────────────────────────────────────┐
│ Team reviews code                   │
│ Request changes OR approve          │
└─────────────────────────────────────┘
                │
                ▼
Step 5: Merge PR (automatic actions)
┌─────────────────────────────────────┐
│ Version: 1.11.0a4 → 1.11.0a5        │
│ Integration tests run               │
│ Docker image built (tag: sit)       │
│ Deployed to SIT environment         │
└─────────────────────────────────────┘
```

### Scenario: Creating a Release

```
Step 1: Create Release Branch
┌──────────────────────────────────────┐
│ From develop (at 1.11.0a5)           │
│ $ git checkout -b release/1.11.0     │
│ $ git push -u origin release/1.11.0  │
└──────────────────────────────────────┘
                │
                ▼
Step 1.5: auto-bump-develop.yml Triggers
┌──────────────────────────────────────┐
│ Automatically runs when branch       │
│ is created (on push)                 │
│ Bumps develop: 1.11.0a5 → 1.12.0a1   │
└──────────────────────────────────────┘
                │
                ▼
Step 2: First PR to Release Branch (automatic)
┌──────────────────────────────────────┐
│ Version: 1.11.0a5 → 1.11.0rc1        │
│ Published to Test PyPI               │
│ Docker image built (tag: uat)        │
└──────────────────────────────────────┘
                │
                ▼
Step 3: Test in UAT, Fix Bugs if Needed
┌──────────────────────────────────────┐
│ Create PRs to release/1.11.0         │
│ Each merge: rc1 → rc2 → rc3...       │
└──────────────────────────────────────┘
                │
                ▼
Step 4: Merge to Main
┌──────────────────────────────────────┐
│ PR: release/1.11.0 → main            │
│ Version: 1.11.0rc3 → 1.11.0          │
└──────────────────────────────────────┘
                │
                ▼
Step 5: Create GitHub Release
┌──────────────────────────────────────┐
│ Tag: v1.11.0                         │
│ Publishes to PyPI (production)       │
│ Docker: stitchee:1.11.0              │
│ Docker: stitchee:ops                 │
│ Docker: stitchee:latest              │
└──────────────────────────────────────┘
                │
                ▼
        🚀 Live in Production!
```

---

### 🔍 Understanding auto-bump-develop.yml Trigger

**When does it run?**
- ✅ Triggers: When you **create** a release branch (first push)
- ❌ Does NOT trigger: Subsequent pushes/PRs to existing release branch

**Example:**
```bash
# This WILL trigger auto-bump-develop.yml:
git checkout -b release/1.11.0
git push -u origin release/1.11.0

# These will NOT trigger it:
git push origin release/1.11.0  # Branch already exists
# Creating a PR to release/1.11.0  # Not a branch creation event
```

**GitHub's `on: create` trigger:**
- Fires once when a branch is created via push
- Does not fire when commits are pushed to existing branches
- Does not fire when PRs are opened/merged
- The workflow checks that it's a release branch before running

**What happens:**
1. GitHub detects a new branch starting with `release/`
2. `auto-bump-develop.yml` workflow triggers
3. It checks out `develop` branch
4. Compares develop's version with the release version
5. If they match (e.g., both are `1.11.0a5`), bumps develop to next minor (`1.12.0a1`)
6. Commits with `[skip ci]` to avoid triggering builds
7. Pushes to `develop`

**Manual Recovery:**

If `auto-bump-develop.yml` fails or doesn't run automatically:

1. Go to **Actions** → "Auto-bump develop after release branch created"
2. Click **"Run workflow"**
3. Select branch: `main` (the workflow will check out develop itself)
4. Enter the release version (e.g., `1.11.0`)
5. Click **"Run workflow"**

**Verification:**

To verify the auto-bump worked:
```bash
git fetch origin develop
git checkout develop
git log -1  # Should show "Start 1.12.0a1 development [skip ci]"
grep '^version = ' pyproject.toml  # Should show version = "1.12.0a1"
```

---

### Scenario: Emergency Hotfix

```
Step 1: Create Hotfix Branch
┌──────────────────────────────────────┐
│ From main (at 1.11.0)                │
│ $ git checkout -b hotfix/1.11.1      │
└──────────────────────────────────────┘
                │
                ▼
Step 2: Fix and PR to Main
┌──────────────────────────────────────┐
│ Make fix, create PR to main          │
│ CI checks run                        │
│ Get emergency approval                │
└──────────────────────────────────────┘
                │
                ▼
Step 3: Merge PR (automatic)
┌──────────────────────────────────────┐
│ Version: 1.11.0 → 1.11.1             │
│ Tag created automatically             │
└──────────────────────────────────────┘
                │
                ▼
Step 4: Create GitHub Release
┌──────────────────────────────────────┐
│ Tag: v1.11.1                         │
│ Publishes to PyPI                    │
└──────────────────────────────────────┘
                │
                ▼
Step 5: Backport to Develop
┌──────────────────────────────────────┐
│ Manual PR: hotfix/1.11.1 → develop   │
│ Keeps develop in sync                │
└──────────────────────────────────────┘
```

---

## External Contributors (Forks)

When someone outside the NASA organization contributes:

```
┌──────────────────────────────────────────────────────────────┐
│  External contributor forks repository                        │
│  Makes changes in their fork                                  │
│  Opens PR: contributor:feature → nasa/stitchee:develop        │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │ pull-request-received.yml │
         │ (detects fork PR)         │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  Run unit tests ONLY      │
         │  (no EDL credentials      │
         │   available to forks)     │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  Maintainer reviews       │
         │  Can manually trigger     │
         │  full tests if needed     │
         └───────────┬───────────────┘
                     │
                     ▼
              Merge follows
              normal workflow
```

---

## Quick Reference

### Developer Checklist

Before opening a PR:
- [ ] Branch created from `develop`
- [ ] Code changes tested locally
- [ ] Unit tests pass: `uv run pytest tests/unit`
- [ ] Linting passes: `uv run ruff check stitchee`
- [ ] `CHANGELOG.md` updated (for develop/main/release PRs)
- [ ] Branch pushed to GitHub
- [ ] PR opened with clear description

### Common Commands

```bash
# Check current version
grep '^version = ' pyproject.toml

# Run tests locally
uv run pytest tests/unit

# Run linting
uv run ruff check stitchee

# Run type checking
uv run mypy stitchee

# Update dependencies
uv sync --extra dev --extra harmony --frozen
```

### Branch Naming Convention

```bash
feature/<short-description>    # New functionality
issue/<bug-description>        # Bug fixes
docs/<what-changed>            # Documentation updates
release/<version>              # Release candidates (e.g., release/1.11.0)
hotfix/<version>               # Production fixes (e.g., hotfix/1.11.1)
```

---

## Key Insights

### Why Version Bumping Only on PR Merge?

**Problem:** If every push to `develop` bumped the version, you'd get commit spam:
```
Push 1: Bump version to 1.11.0a2 [skip ci]
Push 2: Bump version to 1.11.0a3 [skip ci]
Push 3: Bump version to 1.11.0a4 [skip ci]
```

**Solution:** Only bump on PR merge (clean, one commit per feature)
```
PR merge #1: Bump version to 1.11.0a2 [skip ci]
PR merge #2: Bump version to 1.11.0a3 [skip ci]
```

### Why Separate PR Checks and Post-Merge Actions?

**PR Stage:** Fast feedback for developers
- Security, linting, type checking, unit tests
- ~5-10 minutes
- Blocks merge if failing

**Post-Merge Stage:** Comprehensive validation
- Integration tests (with live APIs)
- Docker builds
- Publishing
- ~15-20 minutes
- Already approved code, so safe to deploy

### Why Integration Tests Only on develop/release?

**Feature branches:** Fast unit tests only
- Quick feedback loop
- No need for EDL credentials
- Encourages frequent commits

**Protected branches:** Full integration tests
- Tests against live NASA APIs
- Validates real-world scenarios
- Only after code review approval

---

## Troubleshooting

### Security Scan Failed

**Symptom:** PR blocked by Snyk with high severity vulnerabilities

**Solution:**
```bash
# Check which package is vulnerable
# (see Snyk output in GitHub Actions)

# Update the specific package
uv lock --upgrade-package vulnerable-package-name

# Or update all dependencies
uv lock --upgrade

# Commit and push
git add uv.lock
git commit -m "Update dependencies to fix CVE-XXXX-XXXX"
git push
```

### Version Wasn't Bumped

**Symptom:** PR merged but version didn't change

**Cause:** Direct push instead of PR merge

**Solution:**
```
1. Go to GitHub Actions
2. Find "Version and Build" workflow
3. Click "Run workflow"
4. Check "force_bump: true"
5. Click "Run workflow"
```

### Integration Tests Failing

**Symptom:** Post-merge workflow fails on integration tests

**Cause:** EDL credentials expired or invalid

**Solution:** Contact repository maintainer to update:
- `DEK_EDL_USER` secret
- `DEK_EDL_PASSWORD` secret

---

## Summary

The stitchee CI/CD pipeline handles:
- **Automated testing** on every PR
- **Automatic versioning** on every merge
- **Security scanning** continuously
- **Multi-environment deployment** (sit → uat → ops)
- **Package publishing** to PyPI
- **Docker image builds** for each environment

**Developer workflow:**
1. Create feature branch from `develop`
2. Write code & tests
3. Push and open PR
4. Wait for CI checks (automatic)
5. Get code review
6. Merge PR
7. Pipeline handles versioning, testing, and deployment
