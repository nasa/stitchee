# How to issue a release (and deploy) a new version of stitchee

1. Check that all development Pull Requests have been merged into `develop`

2. Create a new release branch (**from `develop`**), with the name pattern `release/<version number>`

   ```bash
   git checkout develop
   git pull
   git checkout -b release/1.11.0
   git push -u origin release/1.11.0
   ```

### What Happens Automatically When You Push the Release Branch?

When you run `git push -u origin release/1.11.0`, the following occurs automatically:

1. **`auto-bump-develop.yml` workflow triggers**
   - Detects that a release branch was created
   - Checks if `develop` is still on the version being released (e.g., `1.11.0a5`)
   - If yes, bumps `develop` to the next minor version (e.g., `1.11.0a5` → `1.12.0a1`)
   - Commits with `[skip ci]` to avoid triggering additional workflows
   - Pushes the change to `develop`

2. **You can verify this worked:**
   ```bash
   git fetch origin develop
   git checkout develop
   git log -1  # Should show "Start 1.12.0a1 development [skip ci]"
   grep '^version = ' pyproject.toml  # Should show version = "1.12.0a1"
   ```

3. **If auto-bump didn't run:**
   - Go to Actions → "Auto-bump develop after release branch created"
   - Click "Run workflow"
   - Enter the release version (e.g., `1.11.0`)
   - Click "Run workflow"
   - See [.github/CI-CD-README.md](.github/CI-CD-README.md#-understanding-auto-bump-developyml-trigger) for details

---

3. Update the changelog with the new release version, date, and reference link at the bottom (fix any issues with the changelog)
   - Commit the updated changelog to the release branch:
     ```bash
     git add CHANGELOG.md
     git commit -m "Update changelog for <version number>"
     git push
     ```

4. Create a Pull Request from the `release/<version number>` branch to `main`

    1. Use previous Release PRs as a template for the description of the new release PR (Ensure *all* check boxes are unchecked, remove any previous issue links, and remove any ReadTheDocs preview.)

    2. Determine which issues were addressed in this release version, and add links to them using the `Closes #<issue number>` pattern in the Release PR's description

5. Test in UAT (User Acceptance Testing)

    1. When satisfied with release candidate updates, deploy the release candidate Docker container (that's already in GHCR) to UAT using a `curl` command (requires token).

    2. Run any necessary tests on the new version in UAT.

6. (Optional, if any new changes are desired, create PRs with target to release branch)

7. Merge the Release PR into `main`

    - This triggers the final version bump (strips `rc` label)
    - Example: `1.11.0rc3` → `1.11.0`
    - A git tag is automatically created (e.g., `1.11.0`)
    - Builds Docker

8. Create and Publish a GitHub Release

    1. Navigate to: https://github.com/nasa/stitchee/releases/new

    2. Select the tag created by the merge (e.g., `1.11.0`)

    3. Set the release title (e.g., `1.11.0`)

    4. Generate and write release notes:
       - Summarize major changes
       - Link to closed issues
       - Highlight breaking changes if any

    5. Click **"Publish release"**

    6. This automatically triggers:
       - ✅ Publishing to PyPI (production)
       - ✅ Docker image build and push
       - ✅ Snyk security monitoring update

9. Deploy package to Production

    - Deploy the production release package/container to the Production environment.

10. Merge `main` back into `develop`

    - This ensures `develop` has the final release version
    - Do via a local merge:
      ```bash
      git checkout develop
      git pull
      git merge main
      git push
      ```
