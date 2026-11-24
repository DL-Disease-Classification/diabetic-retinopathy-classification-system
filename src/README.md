# src · Shared code

Reusable Python functions used by several notebooks (e.g. `parse_name`). Write a function here once and import it, so a fix applies everywhere.

## Using it in Colab

A notebook opened from GitHub doesn't include the rest of the repo, so clone it first. In VS Code with the Colab extension, the runtime can't see your laptop's files either, so clone there too. **Push your changes first**, because the runtime clones from GitHub.

```python
REPO = "diabetic-retinopathy-classification-system"
!git clone -q https://github.com/DL-Disease-Classification/{REPO}.git
import sys; sys.path.append(f"/content/{REPO}")

from src.dataset_index import build_index, parse_name, CLASS_NAMES
from src.selection import add_look_stats, select_clean_photos
import src.duplicates as dup
```

To use code from a branch that isn't merged yet, add `-b <branch-name>` to the `git clone` line.

If the repo is private, see *Getting started* in the [main README](../README.md) for cloning with a token.

## Modules

| Module | What it does |
|---|---|
| [`dataset_index.py`](dataset_index.py) | `build_index(data_dir)`: one row per image file. `parse_name(fname)`: decode a filename into source, original photo ID (`base_id`), augmentation code, GF flag |
| [`selection.py`](selection.py) | `add_look_stats(df)`: brightness/colour measures and the grey "processed" flag (reads every image). `select_clean_photos(df)`: selection rule v3, with one file per photo plus `family`, `is_copy`, `patient`, `train_only`. Base training set: `family` in `original`, `A_geometry` |
| [`duplicates.py`](duplicates.py) | Near-duplicate photos under different names, by their vessel patterns. `representatives(df)`: one least-altered file per photo. `features_many(paths)`: vessel maps. `search(...)`: closest candidates over flips / 90° turns. `score_pairs(...)`: pair scores (about 1 = same photo). `threshold_for(...)`: the D-014 threshold rule. `groups(...)`: join matches into groups. Used in `2_data_exploration/03_near_duplicates.ipynb` |
