# Decision log

Every important project decision goes here, **newest at the top**.
Write down what we decided, *why*, and what we rejected, so we (and the examiners) can follow our reasoning later.

**Status:** 🟡 Proposed · ✅ Accepted · ❌ Rejected · 🔁 Replaced by a later decision

### Template (copy for each new decision)

```markdown
## D-XXX: <short title>
- **Date:** YYYY-MM-DD
- **Status:** 🟡 Proposed
- **Decided by:** <names>
- **Context:** What problem or question led to this?
- **Decision:** What exactly did we decide?
- **Alternatives considered:** What else could we have done, and why not?
- **Consequences:** What does this change for the rest of the project?
- **Evidence / links:** notebook, issue, paper
```

---

## D-015: The near-duplicate matcher: method, development data and scope
- **Date:** 2026-11-24
- **Status:** ✅ Accepted (method and scope). Whether it passes on our data is decided by D-014's rule in notebook 03.
- **Decided by:** Malak (data audit, issue #5)
- **Context:**
  - Exact copies are found by fingerprints (D-012).
  - Near copies (resized, re-compressed, squeezed, flipped, recoloured) need a matcher.
  - Developing it directly on our dataset was too slow: one full run takes about an hour.
- **Decision:**
  1. **Method:** compare **vessel patterns** (`src/duplicates.py`).
     - The field of view is found and mapped onto a fixed square.
     - A black top-hat keeps the vessels, computed from the green and the brightest channel.
     - A quick search finds candidates over the 8 flips / 90° turns, and a full score is computed for each candidate.
  2. **Development data:** the method was built and checked on the public DeepDRiD dataset (1,600 photos, two of each eye), with copies made like ours. It only prepared the method; the threshold and the verdict come from our data (D-014).
  3. **D-014's rule made precise:**
     - the threshold is the lowest score at which both different-eye sets have at most 0.1% false matches;
     - a same-photo pair counts as found only if the quick search (10 candidates) finds it **and** its score reaches the threshold.
  4. **Scope:** the matcher finds the same **photo**, not every photo of the same eye.
     - EyePACS: both eyes of a patient are kept together in the split through the patient number (issue #4).
     - APTOS and DDR have **no patient IDs**, so two different photos of the same eye there can't be detected. This is stated as a limitation.
- **Alternatives considered:**
  - Perceptual hashes. Rejected: they mostly encode the shared bright-disc-on-black shape.
  - An earlier log-polar fingerprint. Rejected: on stand-in data its copies (0.29–0.70) and different eyes (up to 0.32) overlapped.
  - Developing on our own data. Rejected: about 1 h per round.
- **Evidence:** `2_data_exploration/matcher_development/README.md`, the DeepDRiD results:
  - threshold 0.669;
  - 99.4–100% of every kind of copy at or above it;
  - 1 false match in 3,189 different-eye pairs.

## D-014: How the near-duplicate threshold is chosen
- **Date:** 2026-11-21
- **Status:** ✅ Accepted (fixed before the matcher is run on the real data)
- **Decided by:** Malak (data audit, issue #5)
- **Context:**
  - Byte-identical copies are found exactly (D-012).
  - Copies that were resized, re-compressed, flipped or recoloured need a similarity score and a threshold.
  - Choosing the threshold by looking at a few pairs is the small-sample approach that misled us in notebook 01.
- **Decision:** the threshold is set from pairs whose answer is known, measured in full, before any unknown pair is looked at.
  - **Same photo:** all ~14,100 copy/original pairs known by name, and every base photo re-saved by code (resized, re-compressed, cropped a few %).
  - **Different eyes:** all EyePACS left/right pairs of the same patient, and each EyePACS photo's closest DDR photo (US vs China, so a real duplicate is implausible).
  - **Pass rule:** ≥ 99% found on both same-photo sets, and ≤ 0.1% false matches on both different-eye sets. If both can't be met, the matcher is improved, not the threshold.
  - **Visual check afterwards:** every accepted match across different names (a random sample per score band if there are hundreds), plus the band just below the threshold.
- **Limit:** there are no known examples of the same eye photographed twice, so the matcher can't be calibrated for that case. Those pairs are listed separately and judged by eye.
- **Alternatives considered:**
  - Choosing the threshold visually from side-by-side pairs. Rejected: small sample, subjective.
  - Reusing a threshold from earlier tests on stand-in data. Rejected: there, augmented copies and different eyes overlapped.

## D-013: Model input size at most 512 px
- **Date:** 2026-11-21
- **Status:** ✅ Accepted (rule fixed before measuring)
- **Decided by:** Malak (data audit, issue #5)
- **Context:** the docs assumed the images are ~600 px. Enlarging a small photo adds no detail.
- **Decision:**
  - Rule: the input size must not exceed the shorter side of 95% of base-dataset photos.
  - Measured: 99.8% have a shorter side of at least 512 px, so the input is **at most 512 px**.
  - The exact size is chosen with the baseline.
- **Evidence:** `2_data_exploration/02_image_audit.ipynb`, step 4.
  - EyePACS: all 600×600.
  - DDR: mostly 512×512 (3,224 of 4,016 files).
  - APTOS: originals 358–2,848 px; `-600` copies 600×600.
  - The "~600 px" assumption is not confirmed: only 63% of base photos have a shorter side of 550–650 px (measured after the D-007 tie-break of 2026-11-23).
- **Consequence: APTOS image size depends on the grade** (step 4, measured on the originals only):
  - median shorter side: No DR 1,050 px; Mild 1,736, Moderate 1,958, Severe 1,944, PDR 1,958;
  - APTOS seems to have photographed healthy and diseased eyes differently (likely different cameras or clinics);
  - resizing to one input size hides the size, but not necessarily the camera's look. The selection can't remove this;
  - check it during training: results per source, and Grad-CAM (does the model look at the retina or at the edges?).
  - (In the first run, the selected APTOS photos looked as if Severe photos were 600 px. That part came from the selection rule and is fixed in D-007.)

## D-012: Duplicate photos under different names
- **Date:** 2026-11-21
- **Status:** ✅ Accepted. Applied after the near-duplicate check (D-014), together with the near copies it finds.
- **Decided by:** Malak (data audit, issue #5)
- **Context:** `2_data_exploration/02_image_audit.ipynb`, steps 5–6.
  - 177 groups of byte-identical files carry different photo names. They form **135 duplicate photo groups** (275 photo IDs).
  - All are within one source: APTOS 123, DDR 9, Messidor-1 2, IDRiD 1.
  - **31 groups have conflicting grades** (30 APTOS, 1 IDRiD); 9 differ by 2 grades or more.
  - Our labels match APTOS's official `train.csv` 100%, so these conflicts are in APTOS's own labels.
- **Decision:**
  1. Same photo with **different grades** → drop all of its copies from the training pool. The true grade is unknown.
  2. Same photo with the **same grade** → keep one photo: the original, then family A, then family B.
  3. Any match with a **Messidor** photo → remove it from the training pool, so the external test stays untouched.
  4. Related (steps 2–3): a nearly black original (pixel std < 5) excludes that file only. The photo may still be used through one of its copies.
- **Effect (exact duplicates only):** 167 photos removed (62 with conflicting grades, 105 extra copies). Base dataset 20,145 → 19,978; Severe loses 16.
- **Alternatives considered:**
  - Keep one grade of a conflicting pair. Rejected: there is no way to know which is right.
  - Keep all duplicates. Rejected: the same photo would count twice and could leak across our own split.
  - For point 4, drop the whole photo when its original fails. Rejected by Malak on 2026-11-21.

## D-011: Trust the folder labels (verified)
- **Date:** 2026-11-20
- **Status:** ✅ Accepted
- **Decided by:** Malak (data audit, issue #5)
- **Context:** Several patterns made us doubt the labels: IDRiD conflicts, and DDR names whose last number disagreed with the folder 30% of the time.
- **Decision:** Keep the folder labels for EyePACS, APTOS and DDR.
- **Evidence:** every photo was matched to its original dataset's official label file, and agreement was **100%** for all three sources:
  - EyePACS: 16,501 photos, train + test labels;
  - APTOS: 3,662 photos;
  - DDR: 4,016 photos, two independent mirrors that agree 100%.
  - The DDR name number is not a grade. Notebook steps 11–12.
- **Alternatives considered:** Relabelling DDR from the name number. Rejected, since it would have introduced ~800 wrong labels.

## D-010: Work in VS Code with the Colab extension
- **Date:** 2026-11-19
- **Status:** ✅ Accepted
- **Decided by:** Malak
- **Context:** Moving notebooks between Colab in the browser and the repo is clumsy. The official Google Colab extension for VS Code runs a notebook stored in the repo on a Colab runtime, with the same resources and credits.
- **Decision:**
  - Notebooks live in the repo and run in VS Code on a Colab runtime.
  - Colab Secrets may not work there, so the Kaggle token is typed in with `getpass` (never saved in the notebook).
  - The runtime can't see local files, so shared code in `src/` is cloned from GitHub (push first).
- **Alternatives considered:** Colab in the browser + "Save a copy in GitHub". It still works, but is slower to keep in sync.
- **Consequences:** Files the runtime writes (CSVs) stay on the runtime. Anything we need again is regenerated by code.

## D-009: Test whether family B copies help, instead of guessing
- **Date:** 2026-11-19, revised 2026-11-20
- **Status:** 🟡 Proposed
- **Context:**
  - 3,605 photos exist only as family B copies (random, often large hue shifts).
  - They add data (Mild +59%, Moderate +40%), but their colours could act as a shortcut, and strong hue changes may hide colour cues that matter for DR.
- **Decision:**
  - Train the same baseline twice on the **same split**: (a) base dataset, (b) base + family B copies.
  - In run (b), apply hue augmentation of similar strength to **every** training image, so unusual colours carry no class information.
  - Keep whichever scores better on validation, which contains originals only.
- **Alternatives considered:** Always drop them (loses data in the hardest grades); always keep them (untested shortcut risk).
- **Consequences:** One extra training run. The result goes in `4_modeling/experiments.md` and becomes an ablation in the report.

## D-008: Drop all IDRiD images
- **Date:** 2026-11-19
- **Status:** ✅ Accepted
- **Decided by:** Malak (data audit, issue #5)
- **Context:** 22 IDRiD files appear under two different grades, and each pair is the byte-identical file. Likely cause: IDRiD's train and test sets both number from `IDRiD_001`, and grades were matched by name. So any IDRiD label in this dataset may be wrong.
- **Decision:** Remove all 233 IDRiD files from the training pool.
- **Alternatives considered:** Drop only the 22 conflicting photos. Rejected, because the other labels may be wrong in the same way without showing a conflict.
- **Consequences:** We lose about 211 photos (69 Severe). If we want IDRiD as a second external test, we use the original IDRiD release with its official labels.
- **Evidence:** `2_data_exploration/01_dataset_exploration.ipynb`, step 5c.

## D-007: Selection rule (v3): one trustworthy file per photo
- **Date:** 2026-11-19, revised 2026-11-20 and 2026-11-23
- **Status:** ✅ Accepted for *which file to keep per photo*. Final counts depend on the duplicate checks (D-012, D-014).
- **Decided by:** Malak (data audit, issue #5)
- **Context:**
  - 24,916 distinct photos sit behind 45,327 files.
  - v1 and v2 of this rule judged the augmentation codes from single examples and 20-pair samples, and those results changed when the notebook was re-run.
  - v3 rests on **all** ~14,100 copy/original pairs, measured against an envelope fixed **before** looking at the results.
- **Decision:**
  1. Drop IDRiD (D-008) and Messidor (external test, D-005).
  2. Drop `GF` files and grey-processed files.
  3. Keep **one file per photo**, preferring: original → family A (`FF`, `BF`) → family B (`HFF`, `HB`, `HF`, `HBF`, `ALL`). Never family C (`FS`, `SF`) or D (`FA`).
     - *Added 2026-11-23:* among files of the same rank, prefer the full-size original over the uploader's resized `-600` copy (e.g. APTOS `x.png` over `x-600.jpg`), then the file name.
     - Before this, the rule kept whichever file came first in folder order. For APTOS that meant the 600 px copy for 629 of 3,661 photos, strongly linked to the grade (No DR 7%, Severe 63%): a shortcut a model could learn (`02_image_audit.ipynb`, step 4).
     - The change affects which file is kept, not which photos, so the counts don't change.
  4. **Base dataset** = originals + family A (20,150 photos). Family B copies (3,605) are flagged and only used in the D-009 experiment.
  5. Every copy, and the other eye of the same EyePACS patient, is **train only**. The split is made once on the full selection, so validation and test are identical with or without family B.
- **Alternatives considered:**
  - v2 (keep family B in the base set). Rejected: 74–78% of family B copies fall outside the envelope, almost all because of their colour (red/green) shift.
  - Drop all copies. That's effectively the base dataset; family B is then tested, not assumed.
  - For the tie-break (2026-11-23): keep the folder-order choice. Rejected, because the file type would stay linked to the grade, and the choice would depend on an arbitrary order.
- **Consequences:** Implemented in `src/selection.py`.
- **Evidence:** `2_data_exploration/01_dataset_exploration.ipynb`, steps 5–10; `2_data_exploration/02_image_audit.ipynb`, step 4 (tie-break).

## D-006: Main evaluation metrics
- **Date:** 2026-11-17
- **Status:** 🟡 Proposed
- **Context:** The grades are imbalanced, so plain accuracy is misleading. A model that always says "No DR" can still look decent.
- **Decision:**
  - Primary metric: **quadratic weighted kappa (QWK)**. It is the standard for DR grading and was used in the Kaggle DR competitions.
  - Also report **per-grade recall**, **macro-F1**, **accuracy**, and **referable vs non-referable DR** (AUC, sensitivity, specificity).
- **Alternatives considered:** Accuracy only. Rejected because it hides failure on rare grades.
- **Consequences:** Model selection and threshold tuning use validation QWK.

## D-005: Use Messidor-2 as an external test set
- **Date:** 2026-11-17
- **Status:** 🟡 Proposed (confirm with supervisor)
- **Context:** We can't fully trust the labels and construction of the Kaggle re-packaged dataset. A test set from the same pool also overestimates real-world performance.
- **Decision:**
  - Use **Messidor-2 with Krause et al. adjudicated grades** as the final external test.
  - Remove **all** Messidor (and IDRiD) images from the training pool.
- **Alternatives considered:**
  - (a) Test only on our own re-split of the Kaggle data. Weaker evidence of generalisation.
  - (b) Rebuild everything from the original datasets. Cleaner, but much more work, and fewer Severe images without EyePACS.
- **Consequences:**
  - We expect lower scores on Messidor-2 than on the internal test. We report both and explain the gap.
  - Messidor-2 has only 75 Severe images, so its Severe scores are rough estimates. Report them with confidence intervals.

## D-004: Rebuild the train/val/test split ourselves
- **Date:** 2026-11-17
- **Status:** ✅ Accepted. Which files to keep: D-007 (v3); labels verified: D-011
- **Context:** See D-003.
- **Decision:**
  - Group files by **original photo** (`base_id`), and by **patient** for EyePACS.
  - Keep **one file per photo**: the original if it exists, otherwise the least-altered acceptable copy (D-007).
  - Drop sources with unreliable labels (IDRiD, D-008).
  - Split by group, so every version of a photo and both eyes of a patient land in the same split.
  - Do augmentation **on the fly, during training only**.
  - Handle class imbalance with class weights or balanced sampling, not stored copies.
- **Alternatives considered:** Keep the provided split. Rejected because of the leakage (D-003).
- **Consequences:**
  - The training set gets smaller but honest.
  - Rare grades (especially Severe) will have far fewer images.
  - We also need a pixel-level duplicate check for renamed copies.

## D-003: Do not use the provided train/val/test split
- **Date:** 2026-11-17
- **Status:** ✅ Accepted
- **Context:** The filename audit showed the dataset was augmented before splitting. 4,676 original photos appear in more than one split. 46.5% of test files (95% of Severe) are versions of a training photo.
- **Decision:** Never report results on the provided val/test splits.
- **Alternatives considered:** None viable. Any score on those splits is inflated.
- **Evidence:** `2_data_exploration/01_dataset_exploration.ipynb` (Step 3); `1_datasets/README.md` (Known issues).

## D-002: Don't connect Colab to Google Drive
- **Date:** 2026-11-17
- **Status:** ✅ Accepted
- **Context:** Team preference.
- **Decision:**
  - Download data fresh in each Colab session.
  - Keep small outputs by downloading them or committing them to this repo.
  - Store trained model weights on Hugging Face Hub or GitHub Releases.
- **Consequences:** Any notebook must be able to run from scratch in a new session.

## D-001: Use Google Colab as the main compute platform
- **Date:** 2026-11-17
- **Status:** ✅ Accepted
- **Context:** We need free or cheap GPU access, and Colab offers more credit capacity than Kaggle for our use.
- **Decision:**
  - Use a CPU runtime for data work and a GPU only for training.
  - Load data with `kagglehub`, with the token stored in Colab Secrets.
- **Consequences:** Disconnect runtimes when idle, to save credits.
