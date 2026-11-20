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
try:   # Colab in the browser: token stored in Colab Secrets
    from google.colab import userdata
    os.environ['KAGGLE_API_TOKEN'] = userdata.get('KAGGLE_API_TOKEN')
except Exception:   # VS Code + Colab extension: Secrets may not work, so type it in
    from getpass import getpass
    os.environ['KAGGLE_API_TOKEN'] = getpass('Paste your Kaggle API token: ')
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

Every one of the 45,327 filenames matches one of these patterns. Decoding is in [`../src/dataset_index.py`](../src/dataset_index.py).

| Filename pattern | Example | Source | Files | Distinct photos |
|---|---|---|---|---|
| `<number>_left/right-600` | `19109_left-600.jpg` | EyePACS (Kaggle 2015, train **and** test sets) | 30,189 | 16,501 |
| 12 hex characters (`GF` = Gaussian-filtered version) | `a963ac561580.png`, `9b093fe95d6b-GF-600-FF.jpg` | APTOS 2019 | 10,363 | 3,662 |
| `nnn-nnnn-nnn` | `007-1590-000.jpg` | DDR (the last number is **not** a grade) | 2,655 | 2,655 |
| 17-digit timestamp | `20170612163236281.jpg` | DDR | 1,361 | 1,361 |
| `YYYYMMDD_nnnnn_nnnn_PP` | `20051020_53178_0100_PP.png` | Messidor (the `0100` is part of the ID, **not** a grade) | 356 | 356 |
| `IM000xxx` | `IM000319.JPG` | Messidor-2 extension | 170 | 170 |
| `IDRiD_nnn` | `IDRiD_006.jpg` | IDRiD | 233 | 211 |
| **Total** | | | **45,327** | **24,916** |

### ✅ Labels verified against the original datasets

Every photo we train on was matched, by name, to its original dataset's **official label file**, and the folder label compared:

| Source | Official label file | Photos found | Folder label = official |
|---|---|---|---|
| EyePACS | `trainLabels.csv` + test-set `retinopathy_solution.csv` (Kaggle 2015 competition) | 16,501 / 16,501 | **100%** |
| APTOS 2019 | `train.csv` (Kaggle competition) | 3,662 / 3,662 | **100%** |
| DDR | `train.txt`, `valid.txt`, `test.txt` (two independent mirrors, 100% identical) | 4,016 / 4,016 | **100%** (none officially "ungradable") |

So the creator did **not** change any labels for these sources. (IDRiD is the exception, see issue 4. Messidor is reserved for the external test.) Notebook steps 11–12.

### Augmentation codes in filenames

Measured on **all** ~14,100 copies that still have their original (notebook step 9). The acceptance envelope was **fixed before** looking at the results: brightness/contrast/saturation ×0.80–1.25, red/green ×0.90–1.10, zoom ×0.95–1.05.

| Family | Codes | What it does (median [5th–95th percentile]) | Inside envelope | Use |
|---|---|---|---|---|
| **A: geometry only** | `FF`, `BF` | Random flips/rotation; colour unchanged (red/green 1.00 [1.00–1.01]) | 90% | ✅ Base dataset |
| **B: random hue shift** | `HB`, `HBF`, `HF`, `HFF`, `ALL` | Random flips + large random hue shift (red/green 0.99 [0.60–2.18]) | 22–26% | 🧪 Optional add-on, train only, tested in D-009 |
| **C: darker + oversaturated** | `FS`, `SF` | Darker (0.83), saturation +47%, redder | 12–14% | ❌ Never |
| **D: strong brightening** | `FA` | Brightness ×1.60 [1.41–2.53] | 0% | ❌ Never |

In every code: no crops or zoom (zoom 1.00), and no odd-angle rotations (alignment match ≥ 0.95 for 95% of pairs).

The grey, heavily processed look in some copies isn't caused by any code. Those copies were made **from the Gaussian-filtered (`GF`) APTOS images**: 100% of `GF` files look grey, versus 0.1% of plain files.

*Limitation:* brightness ratios exaggerate changes in very dark photos, so some family A copies fall outside the envelope only on brightness.

### ⚠️ Known issues (found in our audit, `2_data_exploration/`)

1. **Balancing was done with copies.** 22,756 of the 45,327 files are augmented copies. No DR has 0% copies; Severe has about 81%.
2. **Train/val/test leakage.** The whole pool was augmented *before* being split, so copies of the same photo are spread across all three splits:
   - 4,676 original photos appear in more than one split.
   - **54% of val** and **46.5% of test** files are versions of a photo that is also in train.
   - By grade in test: Severe 95%, Proliferative 87%, Mild 76%, Moderate 25%, No DR 2%.
   - ➜ **The provided split cannot be used for evaluation.**
3. **Far fewer real images than files.**
   - Only **24,916 distinct photos**: No DR 9,811 · Mild 3,704 · Moderate 7,561 · **Severe 1,267** · Proliferative 2,551.
   - Severe averages **6.7 files per photo**.
4. **IDRiD labels are unreliable.** 22 IDRiD files appear under two different grades, and each pair is the **byte-identical file**. Likely cause: IDRiD's train and test sets both number from `IDRiD_001`, and grades were matched by name. ➜ **All IDRiD files are dropped.**
5. ~~Possible label changes in DDR files~~. **Resolved:** the last number in DDR names is not a grade, and the folder labels match DDR's official labels 100%.
6. **Patient leakage.** For 3,581 EyePACS patients, the left and right eye sit in different splits.
7. **Mixed preprocessing.** APTOS photos appear both as originals and as Gaussian-filtered (`GF`) versions, and augmented copies were also made from the `GF` versions.
8. **4,020 photos exist only as augmented copies:** Mild 1,573, Moderate 2,130, Proliferative 313, Severe 4.

How we handle each issue is recorded in [`../notes/decision_log.md`](../notes/decision_log.md).

### ✅ Clean dataset (selection rule v3, D-007)

Built with [`../src/selection.py`](../src/selection.py):
- one file per photo;
- IDRiD and Messidor removed;
- no `GF`/grey files;
- copies only when no original exists, preferring family A over family B.

| | No DR | Mild | Moderate | Severe | Proliferative | Total |
|---|---|---|---|---|---|---|
| Originals | 9,561 | 2,007 | 5,296 | 1,119 | 2,165 | 20,148 |
| Family A copies | 0 | 0 | 0 | 2 | 0 | 2 |
| **Base dataset** | **9,561** | **2,007** | **5,296** | **1,121** | **2,165** | **20,150** |
| Family B copies (optional add-on, train only) | 0 | 1,177 | 2,130 | 0 | 298 | 3,605 |
| Free to split into train/val/test* | 9,491 | 1,806 | 4,903 | 1,089 | 1,996 | 19,285 |

\* Not a copy, and not the other eye of a patient who has a copy (those stay in train). The split is made once on the full selection, so validation and test are the same whether or not the add-on is used.

Dropped because no acceptable version exists: Mild 396, Proliferative 25, Severe 2, Moderate 1.

⏳ **Still to check before the split:** duplicate photos under *different* names (pixel-level check, `2_data_exploration/02_image_audit.ipynb`).

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
