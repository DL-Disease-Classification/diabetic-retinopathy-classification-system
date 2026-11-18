# Contributing

## Workflow
1. **Real tasks get a GitHub Issue.** That means anything that takes more than one short session, or that someone else needs to know about (e.g. "Step 5: decide duplicate threshold"). Assign yourself.
   - Branch name: `<issue-number>-short-name`, e.g. `12-duplicate-threshold`.
   - The pull request links the issue: `Closes #12`.
2. **Small changes don't need an issue.** Examples: typos, documentation tidy-ups, small README updates.
   - Use a descriptive branch name, e.g. `fix-readme-typos`, `project-documentation`.
   - Describe the change clearly in the pull request instead.
3. **Every change still goes through a pull request.** Commit small, clear changes. **Another team member reviews** before merging.
4. Delete the branch after merging (GitHub does this automatically). Locally, switch to `main`, pull, and start the next task from a fresh branch.
5. Never push directly to `main`. *(Repo admin: enforce this with GitHub → Settings → Branches → add a branch protection rule for `main`, requiring a pull request with 1 approval.)*

## Naming
- Folders and files use `snake_case`.
- Notebooks start with a number so their order is obvious: `02_filename_audit.ipynb`.

## Notebooks from Colab
- **File → Save a copy in GitHub**, then pick the repo, your branch and the path (e.g. `2_data_exploration/02_filename_audit.ipynb`).
- The repo belongs to the `DL-Disease-Classification` organisation. When Colab asks to authorise GitHub, tick **Include private repos** if needed and **grant access to the organisation**. Otherwise the repo won't appear in Colab's list.
- The first cell of every notebook should clone the repo (see *Getting started* in the [README](README.md)) so `src/` can be imported.
- Clear bulky outputs (big image grids) before saving.

## Never commit
Images, datasets, model weights, `kaggle.json`, `.env` or any token. See `.gitignore`.

## Documentation habits
- Important choice → add an entry to [`notes/decision_log.md`](notes/decision_log.md).
- Training run → add a row to [`4_modeling/experiments.md`](4_modeling/experiments.md).
- New folder → a 5-line README: what's in it, how to run it, what it produces.
