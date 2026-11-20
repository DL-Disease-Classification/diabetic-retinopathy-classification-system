# 3 · Data preparation

**Goal:** turn the raw pool into a clean, leak-free dataset (see D-004 in [`../notes/decision_log.md`](../notes/decision_log.md)).

## Starting point (from issue #5, the data audit)

Don't re-implement the cleaning. Use the shared code, which applies selection rule v3 (D-007):

```python
from src.dataset_index import build_index, CLASS_NAMES
from src.selection import add_look_stats, select_clean_photos

df = add_look_stats(build_index(DATA_DIR))   # DATA_DIR = .../split_dataset; reads every image (a few minutes)
clean = select_clean_photos(df)              # 23,755 rows: one per photo (base 20,150 + family B 3,605)
```

## Rules for the split (`01_make_split.ipynb`, issue #4)

1. **Split by `patient`, never by file.** Both eyes of an EyePACS patient go to the same split.
2. **`train_only` rows go to train**: every kept copy (family A **or** B), plus the other eye of their patient. Split the *full* selection once, so validation and test stay identical whether or not family B copies are used (D-009).
3. Split the remaining photos **70 / 15 / 15**, stratified by grade. That gives roughly 160 Severe photos each in validation and test.
4. **Validation and test contain originals only** (`is_copy == False`).
5. Use a fixed random seed and record it.
6. Save `split_v1.csv` with `base_id`, `patient`, `source`, `label`, `split`, `aug`, `family`, `is_copy` and the file path **relative to `split_dataset/`** (e.g. `train/3/xxx.jpg`), since absolute paths change between runtimes.
7. Print class counts per split, for the base set and with family B, as a sanity check, and confirm no `patient` appears in two splits.
8. ⏳ Wait for the pixel-level duplicate check (`2_data_exploration/02_image_audit.ipynb`). Duplicate photos under different names must be grouped too.

## Notebooks (planned)
| Notebook | What it does | Main outputs |
|---|---|---|
| `01_make_split.ipynb` | Patient-grouped, stratified split following the rules above | `split_v1.csv` |

Small `.csv` outputs are committed. Images are not.
