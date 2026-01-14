#!/usr/bin/env bash
set -e

BRANCH="${1}"
CURRENT=$(bump-my-version show current_version)

echo "Processing branch: $BRANCH (current: $CURRENT)"

ALREADY_COMMITTED=false
PUBLISH=false  # Default: most branches don't publish

case "$BRANCH" in
  develop)
    echo "📦 Bumping develop alpha"
    bump-my-version bump pre_number
    VENUE=sit
    ;;

  release/*)
    echo "🎯 Bumping release"
    if [[ "$CURRENT" == *"a"* ]]; then
      echo "  Alpha → RC1"
      bump-my-version bump pre_label
      git commit -am "Bump to RC1 [skip ci]" && git push origin "$BRANCH"
      ALREADY_COMMITTED=true

      # Note: develop will be auto-bumped by auto-bump-develop.yml workflow
    else
      echo "  Incrementing RC"
      bump-my-version bump pre_number
    fi
    VENUE=uat
    PUBLISH=true
    ;;

  main)
    echo "🎉 Main branch"
    if [[ "$CURRENT" =~ (rc|a) ]]; then
      echo "  Stripping pre-release label"
      bump-my-version bump pre_label
    else
      echo "  Version already final: $CURRENT (no action needed)"
    fi
    VENUE=ops
    ;;

  hotfix/*)
    echo "🔧 Bumping hotfix patch"
    [[ "$CURRENT" =~ (rc|a) ]] && bump-my-version bump pre_label
    bump-my-version bump patch
    VENUE=ops
    ;;

  *)
    echo "🌟 Branch: no version bump"
    VENUE=dev
    ;;
esac

VERSION=$(bump-my-version show current_version)

# Output for GitHub Actions (with safety check for local testing)
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  {
    echo "version=$VERSION"
    echo "venue=$VENUE"
    echo "publish=$PUBLISH"
    echo "already_committed=$ALREADY_COMMITTED"
  } >> "$GITHUB_OUTPUT"
else
  echo "⚠️  GITHUB_OUTPUT not set (running locally?)"
  echo "   version=$VERSION"
  echo "   venue=$VENUE"
  echo "   publish=$PUBLISH"
  echo "   already_committed=$ALREADY_COMMITTED"
fi

echo "📌 Version: $VERSION | 📤 Publish: $PUBLISH | 🎯 Venue: $VENUE"
