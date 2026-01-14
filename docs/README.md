# Developer Documentation

## 🚀 Start Here

**[CI-CD-README.md](CI-CD-README.md)** - Complete guide to stitchee's CI/CD pipeline

Everything you need to know:
- 🌳 Branch structure and workflows (features, releases, hotfixes)
- ⚙️ CI/CD pipeline (PR checks, versioning, publishing)
- 📊 Version management (automatic semantic versioning)
- 🐛 Troubleshooting (common issues and fixes)
- 📚 Advanced scenarios (multiple hotfixes, version conflicts)

**[CI_CD_ARCHITECTURE_DIAGRAM.md](CI_CD_ARCHITECTURE_DIAGRAM.md)** - Visual workflow diagrams

Mermaid diagrams showing:
- Complete CI/CD flow
- Branching strategy
- Version bumping decision trees
- Security and testing flows

---

## ⚡ Quick Reference

### Feature Development
```bash
git checkout develop && git pull
git checkout -b feature/your-feature
# Write code, tests, update CHANGELOG.md
git push -u origin feature/your-feature
# Open PR → CI validates → Merge → Auto-version bump
```

### Creating a Release
```bash
git checkout -b release/X.Y.0  # Creates RC, auto-bumps develop
# Test in UAT, fix bugs via PRs
# Merge to main → Create GitHub Release → Published to PyPI
```

### Emergency Hotfix
```bash
git checkout main && git pull
git checkout -b hotfix/X.Y.Z
# Fix → PR to main → Merge → GitHub Release
# Backport to develop
```

### Version Examples
- **develop**: `1.11.0a1` → `1.11.0a2` (alpha increments)
- **release/1.11.0**: `1.11.0rc1` → `1.11.0rc2` (RC increments)
- **main**: `1.11.0rc3` → `1.11.0` (strips pre-release)
- **hotfix/1.11.1**: `1.11.0` → `1.11.1` (patch increment)

### Key Principles
- All version bumps are automatic on PR merge
- Only protected branches get version bumps
- Feature branches don't trigger version changes
- CI handles everything - just write code and merge

---

**For complete details, see [CI-CD-README.md](CI-CD-README.md)**
