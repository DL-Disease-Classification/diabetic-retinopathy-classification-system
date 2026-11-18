# Datasets

This folder documents the data we use: where it comes from, how to get it, and its known problems.
**No images are stored in this repository.**

---

## 1. Main training pool: "Fundus (APTOS, DDR, IDRiD, EyePACS, Messidor)"

| | |
|---|---|
| **Source** | Kaggle: [`sehastrajits/fundus-aptosddridirdeyepacsmessidor`](https://www.kaggle.com/datasets/sehastrajits/fundus-aptosddridirdeyepacsmessidor) |
| **What it is** | A re-packaging of five public DR datasets into one folder structure |
| **Size** | 45,327 image files (jpg/png). Many filenames contain `-600`, which suggests resizing to ~600 px. **To verify in the image audit**, since the APTOS `.png` files are likely full size |
| **Labels** | 5 grades (0–4), given by the folder name |
| **Licence** | TODO: check the Kaggle page. The original datasets' licences also apply (section 4) |
| **How we use it** | Training and validation **only**, after cleaning and re-splitting (see `3_data_preparation/`) |

### How to download (Colab)

```python
import os, kagglehub
from google.colab import userdata
os.environ['KAGGLE_API_TOKEN'] = userdata.get('KAGGLE_API_TOKEN')
DATA_ROOT = kagglehub.dataset_download("sehastrajits/fundus-aptosddridirdeyepacsmessidor")
DATA_DIR = os.path.join(DATA_ROOT, "split_dataset")
```

### Folder layout

```
split_dataset/
├── train/{0,1,2,3,4}/
├── val/{0,1,2,3,4}/
└── test/{0,1,2,3,4}/
```

### Files per split, as provided

| split | No DR | Mild | Moderate | Severe | Proliferative | Total |
|---|---|---|---|---|---|---|
| train | 5,968 | 5,968 | 5,968 | 5,968 | 5,968 | 29,840 |
| val | 1,520 | 1,305 | 1,399 | 1,278 | 1,294 | 6,796 |
| test | 2,650 | 1,430 | 1,965 | 1,280 | 1,366 | 8,691 |

### Where each image comes from (identified from filenames)

| Filename pattern | Example | Source |
|---|---|---|
| `<number>_left/right-600` | `19109_left-600.jpg` | EyePACS (Kaggle 2015) |
| 12 hex characters | `a963ac561580.png` | APTOS 2019 |
| `GF` in the name | `9b093fe95d6b-GF-600-FF.jpg` | APTOS, Gaussian-filtered version |
| 17-digit timestamp | `20170612163236281.jpg` | probably DDR (TODO: confirm) |
| `nnn-nnnn-ggg` | `007-1590-000.jpg` | unknown (TODO: confirm). Last 3 digits look like a grade code |
| `YYYYMMDD_nnnnn_nnnn_PP` | `20051020_53178_0100_PP.png` | Messidor (the `0100` is part of the ID, **not** a grade) |
| `IM000xxx` | `IM000319.JPG` | Messidor-2 extension |
| `IDRiD_nnn` | `IDRiD_006.jpg` | IDRiD |

### Augmentation codes in filenames

Suffixes like `-HB`, `-HFF`, `-FA`, `-FS`, `-ALL`, `-SF`, `-HF`, `-BF`, `-FF` and `-HBF` mark **augmented copies** (flips, brightness changes, etc.) of an original photo. TODO: decode each code visually.

### ⚠️ Known issues (found in our audit, `2_data_exploration/`)

1. **Balancing was done with copies.** 22,756 of the 45,327 files are augmented copies. No DR has 0% copies; Severe has about 81%.
2. **Train/val/test leakage.** The whole pool was augmented *before* being split, so copies of the same photo are spread across all three splits:
   - 4,676 original photos appear in more than one split.
   - **54% of val** and **46.5% of test** files are versions of a photo that is also in train.
   - By grade in test: Severe 95%, Proliferative 87%, Mild 76%, Moderate 25%, No DR 2%.
   - ➜ **The provided split cannot be used for evaluation.**
3. **Far fewer real images than files.** Train Severe has 5,968 files but only 1,157 distinct photos.
4. **Label conflicts.** 22 photos appear under more than one grade.
5. **Possible label changes.** For `nnn-nnnn-ggg` files, the grade code in the name often differs from the folder label. Still to be verified.
6. **Patient leakage.** For 3,581 EyePACS patients, the left and right eye sit in different splits.
7. **Mixed preprocessing.** Some APTOS photos are present both as the original and as a Gaussian-filtered version.

How we handle each issue is recorded in [`../notes/decision_log.md`](../notes/decision_log.md).

---

## 2. External test set: Messidor-2 (planned)

| | |
|---|---|
| **Images** | 1,748 macula-centred fundus photos (874 examinations, two eyes each), from French hospitals |
| **Labels** | DR grades adjudicated by a panel of 3 retina specialists (Krause et al., 2018), on Kaggle as [`google-brain/messidor2-dr-grades`](https://www.kaggle.com/datasets/google-brain/messidor2-dr-grades) |
| **Get the images** | Request from ADCIS: https://www.adcis.net/en/third-party/messidor2/ (free for academic use) |
| **How we use it** | **Final external test only.** Every Messidor image is removed from the training pool first |
| **Required acknowledgement** | "Kindly provided by the Messidor program partners (see https://www.adcis.net/en/third-party/messidor/)." |

## 3. Optional second external test: IDRiD

TODO: fill in if we decide to use it. Again, all IDRiD images must be removed from the training pool first.

---

## 4. Original datasets: citations and licences

TODO: add the full citation and verify the licence of each before the final report.

| Dataset | Citation | Licence / terms |
|---|---|---|
| EyePACS (Kaggle 2015) | TODO | Kaggle competition rules (TODO: check) |
| APTOS 2019 | TODO | Kaggle competition rules (TODO: check) |
| DDR | Li et al., *Information Sciences*, 2019 | CC BY 4.0 |
| IDRiD | Porwal et al., 2018 | TODO |
| Messidor / Messidor-2 | Decencière et al., 2014; grades: Krause et al., *Ophthalmology*, 2018 | Academic use; acknowledgement required (above) |
