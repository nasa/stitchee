# Versioning System

## Overview

This project uses automated semantic versioning with Git Flow. Version numbers follow the format `MAJOR.MINOR.PATCH[PRE_LABEL][PRE_NUMBER]` (e.g., `1.11.0`, `1.11.0a5`, `1.11.0rc2`).

**Key principle:** Developers focus on code, CI manages all version numbers automatically.

## Visual Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Automatic Versioning Flow                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

develop:     1.11.0a1 → 1.11.0a2 → 1.11.0a3 → 1.11.0a4 → 1.11.0a5 → 1.11.0a6
               ↑         ↑         ↑         ↑         ↑         ↑
          feature1   feature2  feature3  feature4  feature5  feature6
           merged    merged    merged    merged    merged    merged

                                                                    ↓
                                                        (create release/1.11.0)
                                                                    ↓
                                                    ┌───────────────┴─────┐
                                                    ↓                     ↓
release/1.11.0:                                1.11.0rc1              (auto!)
develop:                                       1.12.0a1 ←─────────────────┘
                                                  ↓
                                              1.12.0a2 ← new feature merged
                                                  ↓
release/1.11.0: 1.11.0rc1 → 1.11.0rc2 → 1.11.0rc3 (bug fixes during testing)
                                            ↓
                                    (merge to main)
                                            ↓
main:                                   1.11.0 ← stripped, tagged v1.11.0
                                            ↓
                                      (hotfix needed)
                                            ↓
hotfix/1.11.1:                         1.11.1 ← patch bump, tagged v1.11.1
                                            ↓
                                    (merge back to develop)
                                            ↓
develop:                               1.12.0a3 ← alpha increment

Timeline: 1.11.0 < 1.11.1 < 1.12.0a3 < 1.12.0rc1 < 1.12.0 ✓
```

## What CI Does Automatically

| Branch Pattern | Action | Version Change | Publishing |
|----------------|--------|----------------|------------|
| `develop` | Feature merged | 1.11.0a5 → 1.11.0a6 | Test PyPI (optional) |
| `release/X.Y.Z` (first push) | Create release | 1.11.0a6 → 1.11.0rc1<br>develop: 1.12.0a1 | Test PyPI |
| `release/X.Y.Z` (later) | Bug fixes | 1.11.0rc1 → 1.11.0rc2 | Test PyPI |
| `main` | Release merge | 1.11.0rc2 → 1.11.0 | PyPI + git tag |
| `hotfix/X.Y.Z` | Hotfix merge | 1.11.0 → 1.11.1 | PyPI + git tag |

## Complete Workflows

### 🚀 Feature Development

```bash
# 1. Create feature branch
git checkout develop
git checkout -b feature/cool-new-thing

# 2. Develop and test
# ... write code ...
git add .
git commit -m "Add cool new feature"
git push

# 3. Create and merge PR
gh pr create --base develop --title "Add cool new feature"
gh pr merge

# ✅ Result: CI automatically bumps develop (1.11.0a5 → 1.11.0a6)
```

### 🎯 Creating a Release

```bash
# 1. Start release from develop
git checkout develop
git pull
git checkout -b release/1.11.0
git push

# ✅ CI automatically:
#   - Bumps release: 1.11.0a6 → 1.11.0rc1
#   - Bumps develop: 1.11.0a6 → 1.12.0a1 (prevents hotfix collisions!)
```

### 🔧 Testing and Fixing Release

```bash
# 2. Test the release candidate
# If bugs found, fix them on release branch:

git checkout release/1.11.0
# ... fix bugs ...
git add .
git commit -m "Fix widget crash"
git push

# ✅ CI automatically: 1.11.0rc1 → 1.11.0rc2

# Repeat until release is stable
```

### 🎉 Shipping to Production

```bash
# 3. Merge release to main
gh pr create --base main --title "Release 1.11.0"
gh pr merge

# ✅ CI automatically:
#   - Strips pre-release: 1.11.0rc3 → 1.11.0
#   - Creates git tag: v1.11.0
#   - Publishes to PyPI
```

### 🚨 Emergency Hotfix

```bash
# 1. Create hotfix from current production (main)
git checkout main
git pull
git checkout -b hotfix/1.11.1

# 2. Fix the critical bug
# ... make emergency fix ...
git add .
git commit -m "Fix critical security issue"
git push

# 3. Deploy hotfix
gh pr create --base main --title "Hotfix: Critical security issue"
gh pr merge

# ✅ CI automatically:
#   - Bumps patch: 1.11.0 → 1.11.1
#   - Creates git tag: v1.11.1
#   - Publishes to PyPI

# 4. Merge hotfix back to develop (important!)
git checkout develop
git pull
git merge main -m "Merge hotfix 1.11.1"
git push

# ✅ CI automatically: 1.12.0a1 → 1.12.0a2 (includes hotfix)
```

## Version Types Explained

### Alpha Releases (`X.Y.ZaN`)

**Purpose:** Ongoing development versions
**Example:** `1.11.0a1`, `1.11.0a2`, `1.11.0a3`
**When:** Every feature merge to develop
**Stability:** Unstable, for testing only

### Release Candidates (`X.Y.ZrcN`)

**Purpose:** Pre-release testing versions
**Example:** `1.11.0rc1`, `1.11.0rc2`
**When:** Testing releases before production
**Stability:** Should be stable, final testing

### Final Releases (`X.Y.Z`)

**Purpose:** Production-ready stable releases
**Example:** `1.11.0`, `1.12.0`
**When:** Approved releases deployed to production
**Stability:** Stable, supported

### Patch Releases (`X.Y.Z+1`)

**Purpose:** Bug fixes for current release
**Example:** `1.11.1`, `1.11.2`
**When:** Critical fixes needed in production
**Stability:** Stable, backward compatible

## Why This System Works

### 🛡️ Collision-Proof Design

The key innovation: **develop auto-bumps to next minor when release is created**.

```
Before release creation:
  main: 1.10.0
  develop: 1.11.0a6

After creating release/1.11.0:
  main: 1.10.0
  release/1.11.0: 1.11.0rc1
  develop: 1.12.0a1  ← Auto-bumped!

Now hotfixes are safe:
  hotfix: 1.10.1, 1.10.2, etc.
  All < 1.12.0a1, so no collision possible! ✓
```

### 📊 Proper Version Ordering

PEP 440 ensures correct version ordering:
```
1.10.0 < 1.10.1 < 1.10.2 < 1.11.0a1 < 1.11.0a2 < 1.11.0rc1 < 1.11.0 < 1.12.0a1
```

This means:
- ✅ Hotfix `1.11.1` < next release `1.12.0a1`
- ✅ Users get updates in correct order
- ✅ Dependency resolution works correctly

### 🔄 Clean Git History

```
main:     v1.10.0 ──── v1.11.0 ──── v1.11.1 ──── v1.12.0
             │           │           │           │
develop:     │      (1.12.0a1) ─ (1.12.0a2) ─ (1.12.0a3) ─ 1.13.0a1
             │           │           │           │
features:    │           │       feature/X ──── │
             │           │           │           │
release:     │       release/1.11.0 ─────────── │
             │                                   │
hotfix:      │                   hotfix/1.11.1 ─│
```

Every commit to main is a tagged release. Clean and traceable.

## Configuration

### pyproject.toml

```toml
[tool.bumpversion]
current_version = "1.10.0a2"
parse = "(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)((?P<pre_label>a|rc)(?P<pre_number>\\d+))?"
serialize = [
    "{major}.{minor}.{patch}{pre_label}{pre_number}",
    "{major}.{minor}.{patch}",
]

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'

[tool.bumpversion.parts.pre_label]
optional_value = "final"
values = ["a", "rc", "final"]

[tool.bumpversion.parts.pre_number]
first_value = 1
```

### GitHub Secrets

Required for publishing:
- `PYPI_API_TOKEN` - Token for PyPI publishing
- `TEST_PYPI_API_TOKEN` - Token for Test PyPI publishing

### Branch Protection

Recommended settings:
- **develop**: Require PR reviews, allow stitchee-bot to push
- **main**: Require PR reviews + status checks, allow stitchee-bot to push
- **release/\***: Allow direct pushes for CI version bumps

## Local Commands

### Check Version Information

```bash
# Show current version
bump-my-version show current_version

# Show what would change (dry-run)
bump-my-version bump --dry-run --verbose pre_number

# Show all version parts
bump-my-version show-bump
```

### Manual Bumping (Rarely Needed)

```bash
# Increment alpha: 1.11.0a5 → 1.11.0a6
bump-my-version bump pre_number

# Alpha to RC: 1.11.0a5 → 1.11.0rc1
bump-my-version bump pre_label

# RC to final: 1.11.0rc2 → 1.11.0
bump-my-version bump pre_label

# Bump minor: 1.11.0a5 → 1.12.0a1
bump-my-version bump minor

# Set specific version
bump-my-version bump --new-version 2.0.0a1 major
```

### Install bump-my-version Locally

```bash
# Using uv (recommended)
uv pip install bump-my-version

# Using pip
pip install bump-my-version
```

## Troubleshooting

### Version Didn't Bump in CI

**Check:**
1. Does commit message contain `[skip ci]`? (This is intentional for CI version commits)
2. Review CI logs for errors
3. Verify branch is in workflow triggers: `develop`, `main`, `release/**`, `hotfix/**`

**Fix:**
```bash
# Manually bump if needed
bump-my-version bump pre_number
git commit -am "Bump version [skip ci]"
git push
```

### Develop Didn't Auto-Bump

**Symptoms:** Created release branch but develop is still at same version

**Check:**
1. Review CI logs for `bump_develop_after_release.sh` errors
2. Verify script has execute permissions

**Fix:**
```bash
git checkout develop
bump-my-version bump minor
git commit -am "Bump develop to next minor [skip ci]"
git push
```

### Wrong Version After Mistake

**Fix:**
```bash
# Reset to correct version
bump-my-version bump --new-version 1.11.0a5 patch
git commit -am "Reset version [skip ci]"
git push
```

### CI Permission Errors

**Symptoms:** "Permission denied" when CI tries to push

**Fix:** Ensure GitHub Actions has write permissions:
```yaml
permissions:
  contents: write  # For commits and tags
  packages: write  # For publishing
```

### Release Failed to Publish

**Check:**
1. PyPI tokens are correctly set in GitHub Secrets
2. Package name doesn't conflict with existing PyPI package
3. Version number isn't already published

**Manual publish:**
```bash
git checkout v1.11.0  # Checkout the tagged version
uv build
uv publish  # With proper credentials
```

### Hotfix Conflicts

**Symptoms:** Merge conflicts when merging hotfix back to develop

**Fix:**
```bash
git checkout develop
git pull
git merge main
# Resolve conflicts manually
git add .
git commit -m "Merge hotfix with conflict resolution"
git push
```

## Advanced Scenarios

### Multiple Hotfixes

```bash
# First hotfix
git checkout main
git checkout -b hotfix/1.11.1
# ... fix ...
gh pr merge  # main: 1.11.0 → 1.11.1

# Second hotfix
git checkout main
git pull     # Now at 1.11.1
git checkout -b hotfix/1.11.2
# ... fix ...
gh pr merge  # main: 1.11.1 → 1.11.2
```

### Long-Running Release Branch

```bash
# Release branch can accumulate many RCs
release/1.11.0: rc1 → rc2 → rc3 → rc4 → rc5

# develop continues independently
develop: 1.12.0a1 → 1.12.0a2 → 1.12.0a3

# No conflicts - branches are independent
```

### Emergency Release

```bash
# Skip normal release process for urgent fix
git checkout main
git checkout -b hotfix/1.11.1
# ... critical fix ...
gh pr merge

# Result: Immediate production deployment
# Version: 1.11.0 → 1.11.1
# Tagged: v1.11.1
# Published: PyPI
```

## Files and Structure

```
├── .github/workflows/version-and-build.yml  # Main CI workflow
├── scripts/
│   ├── bump_develop_after_release.sh        # Auto-bump script
│   └── README.md                            # Script docs
├── pyproject.toml                           # Version config
└── docs/
    ├── VERSIONING.md                        # This file
    └── PATCH_VS_MINOR_RELEASES.md          # Git Flow concepts
```

## Quick Reference Cheat Sheet

### Branch → Version Behavior
```bash
develop          → bump pre_number    (1.11.0a5 → 1.11.0a6)
release/X.Y.Z    → bump pre_label     (1.11.0a6 → 1.11.0rc1)
                   + auto-bump develop (1.11.0a6 → 1.12.0a1)
release/X.Y.Z    → bump pre_number    (1.11.0rc1 → 1.11.0rc2)
main             → bump pre_label     (1.11.0rc2 → 1.11.0) + tag
hotfix/X.Y.Z     → bump patch         (1.11.0 → 1.11.1) + tag
```

### Common Commands
```bash
# Check version
bump-my-version show current_version

# Preview change
bump-my-version bump --dry-run pre_number

# Skip CI
git commit -m "Update docs [skip ci]"

# Manual version
bump-my-version bump --new-version 2.0.0a1 major
```

### Workflow Shortcuts
```bash
# Feature
git checkout -b feature/X → gh pr merge

# Release
git checkout -b release/X.Y.Z → push → test → gh pr merge to main

# Hotfix
git checkout -b hotfix/X.Y.Z → gh pr merge → git merge main to develop
```

### Version Examples
```
Alphas:     1.11.0a1, 1.11.0a2, 1.11.0a3
RCs:        1.11.0rc1, 1.11.0rc2
Final:      1.11.0
Patches:    1.11.1, 1.11.2
Next minor: 1.12.0a1, 1.12.0a2
```

---

**Remember:** The system handles version numbers automatically. Focus on writing code and following Git Flow - CI does the rest! 🎉
