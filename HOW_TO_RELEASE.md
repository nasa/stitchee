# How to issue a release (and deploy) a new version of stitchee

1. Check that all development Pull Requests have been merged into `develop`

2. Create a new release branch (**from `develop`**), with the name pattern `release/<version number>`

3. Create a Pull Request from the `release/<version number>` branch to `main`

    1. Use previous Release PRs as a template for the description of the new release PR (Ensure *all* check boxes are unchecked, remove any previous issue links, and remove any ReadTheDocs preview.)
  
    2. Determine which issues were addressed in this release version, and add links to them using the `Closes #<issue number>` pattern in the Release PR's description

4. (Optional, if any new changes are desired, create PRs with target to release branch)

