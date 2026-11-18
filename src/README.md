# src · Shared code

Reusable Python functions used by several notebooks (e.g. `parse_name`). Write a function here once and import it, so a fix applies everywhere.

## Using it in Colab

A notebook opened from GitHub doesn't include the rest of the repo, so clone it first:

```python
REPO = "diabetic-retinopathy-classification-system"
!git clone -q https://github.com/DL-Disease-Classification/{REPO}.git
import sys; sys.path.append(f"/content/{REPO}")

from src.filenames import parse_name   # src/filenames.py is planned, not written yet
```

If the repo is private, see *Getting started* in the [main README](../README.md) for cloning with a token.

## Planned modules
- `filenames.py`: decode filenames into source, original photo ID and augmentation code (`parse_name`)
