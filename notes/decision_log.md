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
- **Consequences:** We expect lower scores on Messidor-2 than on the internal test. We report both and explain the gap.

## D-004: Rebuild the train/val/test split ourselves
- **Date:** 2026-11-17
- **Status:** 🟡 Proposed (final counts pending: `2_data_exploration/02_filename_audit.ipynb`, Step 4)
- **Context:** See D-003.
- **Decision:**
  - Group files by **original photo** (`base_id`), and by **patient** for EyePACS.
  - Keep **one un-augmented file per photo**. Drop the stored augmented copies.
  - Drop photos with conflicting grades.
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
- **Evidence:** `2_data_exploration/02_filename_audit.ipynb`; `1_datasets/README.md` (Known issues).

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
