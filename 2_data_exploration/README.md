# 2 · Data exploration & audit

**Goal:** understand the raw dataset *before* changing anything. We look at what's really in it, where each image came from, and what's wrong with it.

## Notebooks (run in order: Colab in the browser, or VS Code with the Colab extension; CPU runtime)

| Notebook | What it does |
|---|---|
| [`01_dataset_exploration.ipynb`](01_dataset_exploration.ipynb) | **Steps 1–2:** download with kagglehub, folder layout, one row per image. **Step 3:** decode filenames, leakage across splits. **Step 4:** distinct photos per source and grade, label conflicts. **Steps 5–7:** first look at augmentation codes, IDRiD check. **Step 8:** first selection rule. **Step 9:** measure **all** copy/original pairs against a pre-set envelope → 4 code families. **Step 10:** base dataset vs add-on; DDR name codes. **Steps 11–12:** verify every label against the original datasets' official label files |
| `02_image_audit.ipynb` *(planned)* | Pixel-level checks the filenames can't do: duplicate photos under *different* names (e.g. across sources), unreadable files, image size and quality |

The decoding and selection logic now lives in [`../src/`](../src/), so later notebooks reuse exactly the same rules.

## Key findings

- **The provided split leaks:** 46.5% of test files are versions of a training photo (95% for Severe).
- **24,916 distinct photos** behind 45,327 files. Severe has only **1,267**.
- **Labels are correct:** 100% agreement with the official labels of EyePACS, APTOS and DDR. IDRiD is the exception and is dropped.
- **Augmentation codes form 4 families** (measured on all ~14,100 pairs). Only geometry-only copies (family A) meet the pre-set criterion.
- **Base dataset: 20,150 photos**, plus 3,605 hue-shifted copies kept for an experiment.
- **Lesson:** two early conclusions, drawn from single examples and small samples, were wrong. Only full-population measurements and official label files were used for decisions.

Full details and tables: [`../1_datasets/README.md`](../1_datasets/README.md). Decisions: D-007 to D-011 in [`../notes/decision_log.md`](../notes/decision_log.md).

## Notes

- Files the notebook writes (`.csv`) stay on the Colab runtime and are regenerated on each run. **Images are never committed.**
- Each notebook downloads the data itself, so it runs from a fresh Colab session.
