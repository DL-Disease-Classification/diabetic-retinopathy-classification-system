# 2 · Data exploration & audit

**Goal:** understand the raw dataset *before* changing anything. We look at what's really in it, where each image came from, and what's wrong with it.

## Notebooks (run in order: Colab in the browser, or VS Code with the Colab extension; CPU runtime)

| Notebook | What it does |
|---|---|
| [`01_dataset_exploration.ipynb`](01_dataset_exploration.ipynb) | **Steps 1–2:** download with kagglehub, folder layout, one row per image. **Step 3:** decode filenames, leakage across splits. **Step 4:** distinct photos per source and grade, label conflicts. **Steps 5–7:** first look at augmentation codes, IDRiD check. **Step 8:** first selection rule. **Step 9:** measure **all** copy/original pairs against a pre-set envelope → 4 code families. **Step 10:** base dataset vs add-on; DDR name codes. **Steps 11–12:** verify every label against the original datasets' official label files |
| [`02_image_audit.ipynb`](02_image_audit.ipynb) | Pixel-level checks the filenames can't do. **Step 1:** checks that `src/` reproduces notebook 01. **Step 2:** can every file be opened (blank or nearly black files). **Step 3:** the selection compared with notebook 01. **Step 4:** real image sizes, and which APTOS file is kept. **Steps 5–6:** the exact same picture under different names, and the duplicate policy (preview) |
| [`03_near_duplicates.ipynb`](03_near_duplicates.ipynb) | The same photo under different names even when resized, re-compressed, squeezed, flipped or recoloured, using the vessel-pattern matcher in `src/duplicates.py`. The threshold comes from pairs with a known answer (D-014): a pass/fail table, a search of every photo, a visual check, and duplicate groups with the policy preview |

How the matcher was built and checked (on the public DeepDRiD dataset, with what failed on the way): [`matcher_development/README.md`](matcher_development/README.md).

The decoding and selection logic now lives in [`../src/`](../src/), so later notebooks reuse exactly the same rules.

## Key findings

- **The provided split leaks:** 46.5% of test files are versions of a training photo (95% for Severe).
- **24,916 distinct photos** behind 45,327 files. Severe has only **1,267**.
- **Labels are correct:** 100% agreement with the official labels of EyePACS, APTOS and DDR. IDRiD is the exception and is dropped.
- **Augmentation codes form 4 families** (measured on all ~14,100 pairs). Only geometry-only copies (family A) meet the pre-set criterion.
- **Base dataset: 20,150 photos**, plus 3,605 hue-shifted copies kept for an experiment.
- **Lesson:** two early conclusions, drawn from single examples and small samples, were wrong. Only full-population measurements and official label files were used for decisions.
- **Image audit (02):**
  - every file opens; 15 blank or nearly black files are excluded;
  - images are **not** all ~600 px, so the model input is at most **512 px**;
  - **135 photos are stored under two or more names**, 31 of them with different grades (APTOS's own labels). Duplicate policy: D-012.
- **APTOS:** the selection now always keeps the full-size original (D-007). The originals of No DR photos are smaller than those of the other grades: a shortcut risk to check in training (D-013).

Full details and tables: [`../1_datasets/README.md`](../1_datasets/README.md). Decisions: D-007 to D-015 in [`../notes/decision_log.md`](../notes/decision_log.md).

## Notes

- Files the notebook writes (`.csv`) stay on the Colab runtime and are regenerated on each run. **Images are never committed.**
- Each notebook downloads the data itself, so it runs from a fresh Colab session.
