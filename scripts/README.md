# Scripts

Automation scripts used by CI/CD workflows. Most are called automatically by GitHub Actions.

## version_bump.sh

Core version bumping logic used by CI. Handles all version transitions:
- `develop`: Alpha increments (1.11.0a5 → 1.11.0a6)
- `release/X.Y.Z`: Alpha to RC, then RC increments
- `main`: Strip pre-release (1.11.0rc3 → 1.11.0)
- `hotfix/X.Y.Z`: Patch increments (1.11.0 → 1.11.1)

**Called by:** `.github/workflows/version-and-build.yml`

**Manual usage** (rarely needed):
```bash
./scripts/version_bump.sh
```

## verify_tag.sh

Verifies git tags match the version in `pyproject.toml` before publishing to PyPI.

**Called by:** `.github/workflows/publish.yml`

## create-netrc

Creates `.netrc` file for EDL (Earthdata Login) authentication during integration tests.

**Called by:** `.github/workflows/integration-tests.yml`

**Requires:**
- `EDL_USERNAME` environment variable
- `EDL_PASSWORD` environment variable

---

**For complete CI/CD workflows:** See [.github/CI-CD-README.md](../.github/CI-CD-README.md)
