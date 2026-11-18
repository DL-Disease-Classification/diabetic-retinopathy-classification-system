# Contributing

## Workflow
1. **One GitHub Issue per task** (e.g. "Step 5: decide duplicate threshold"). Assign yourself.
2. **One branch per task**, named after the issue: `12-duplicate-threshold`.
3. Commit small, clear changes.
4. Open a **pull request** that links the issue (`Closes #12`). **Another team member reviews** before merging.
5. Never push directly to `main`.

## Naming
- Folders and files use `snake_case`.
- Notebooks start with a number so their order is obvious: `02_filename_audit.ipynb`.

## Notebooks from Colab
- **File → Save a copy in GitHub**, then pick the repo, your branch and the path (e.g. `2_data_exploration/02_filename_audit.ipynb`).
- Clear bulky outputs (big image grids) before saving.

## Never commit
Images, datasets, model weights, `kaggle.json`, `.env` or any token. See `.gitignore`.

## Documentation habits
- Important choice → add an entry to [`notes/decision_log.md`](notes/decision_log.md).
- Training run → add a row to [`4_modeling/experiments.md`](4_modeling/experiments.md).
- New folder → a 5-line README: what's in it, how to run it, what it produces.
