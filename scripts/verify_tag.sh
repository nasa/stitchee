#!/usr/bin/env bash
set -euo pipefail

# Get the git tag, handling case where no tags exist
if ! git_tag=$(git describe --tags --abbrev=0 2>/dev/null); then
  echo "❌ No git tags found"
  exit 1
fi

# Strip 'v' prefix if present (e.g., v1.10.0 -> 1.10.0)
git_tag="${git_tag#v}"

current_version=$(grep -E '^version = ' pyproject.toml | head -n1 | cut -d'"' -f2)

if [ -z "$current_version" ]; then
  echo "❌ Could not extract version from pyproject.toml"
  exit 1
fi

echo "Git tag: ${git_tag} | pyproject.toml version: ${current_version}"

if [ "$current_version" == "$git_tag" ]; then
  echo "✅ Version matches git tag"
else
  echo "❌ Version mismatch! pyproject.toml: ${current_version} vs Tag: ${git_tag}"
  exit 1
fi
