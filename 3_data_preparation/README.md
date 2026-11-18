# 3 · Data preparation

**Goal:** turn the raw pool into a clean, leak-free dataset (see D-004 in [`../notes/decision_log.md`](../notes/decision_log.md)).

## Notebooks (planned, run in order)
| Notebook | What it does | Main outputs |
|---|---|---|
| `01_clean_and_deduplicate.ipynb` | Keep one un-augmented file per photo, drop conflicting labels, pixel-level duplicate check | `clean_index.csv` |
| `02_make_split.ipynb` | Group split by photo / patient, remove Messidor & IDRiD | `split_v1.csv` |

Small `.csv` outputs are committed. Images are not.
