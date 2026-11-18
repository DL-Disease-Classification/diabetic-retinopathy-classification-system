# 2 · Data exploration & audit

**Goal:** understand the raw dataset *before* changing anything. We look at what's really in it, where each image came from, and what's wrong with it.

## Notebooks (run in order, in Google Colab, CPU runtime)

> ⏳ **Status:** Steps 1–4 were run in Colab and still need to be saved here (Colab: *File → Save a copy in GitHub*). If they're saved as a single notebook, update this table to match.

| Notebook | What it does | Main outputs |
|---|---|---|
| `01_download_and_index.ipynb` | Downloads the dataset with kagglehub, shows the folder layout, and builds a table with one row per image (split, grade, filename, path) | `index.csv` |
| `02_filename_audit.ipynb` | Decodes each filename into source, original photo ID and augmentation code. Measures how many real photos each grade has, checks for train/val/test leakage, conflicting grades and patient leakage | `index.csv` (with extra columns), `photos.csv` |
| `03_image_audit.ipynb` *(next)* | Image-level checks: unreadable files, resolution, quality, and pixel-level duplicates that the filename check can't see | TBD |

## Key findings

See the "Known issues" section in [`../1_datasets/README.md`](../1_datasets/README.md).

## Notes

- Outputs (`.csv`) are small enough to commit. **Images are never committed.**
- Each notebook downloads the data itself, so it runs from a fresh Colab session.
