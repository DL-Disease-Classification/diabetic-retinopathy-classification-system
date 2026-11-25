# Experiment log

Log **every** training run here, including failed ones, right after it finishes.
If it isn't in this table, it didn't happen. 🙂

## Rules
- **Give each run an ID** (`EXP-001`, `EXP-002`, …). Use the same ID in the notebook filename or the saved-model name.
- **Use only validation scores here.** The test sets are used **once**, at the end, and recorded in `5_evaluation/`.
- **Change one thing at a time** when comparing runs, and say in *Notes* what changed.
- **Write the data split version** (e.g. `split_v1`) so results stay comparable if the split changes.

## Runs

| ID | Date | Who | Split | Model | Img size | Epochs | Batch | LR | Loss / imbalance handling | Augmentation | Val QWK | Val acc | Val Severe recall | Notes | Weights saved at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | 2026-11-24 | Hassan | split_v1 (SHA256 deduplicated, patient-aware; 5,261 train / 1,125 val) | EfficientNet-B0 (ImageNet) | 224 | 6 (best @ ep 5) | 32 | 3e-4 (CosineAnnealingLR -> 1e-6, AdamW wd=1e-2) | CrossEntropyLoss + inverse-freq class weights `[0.461, 2.441, 0.675, 3.531, 1.521]` | RandomHorizontalFlip (p=0.5), RandomRotation (±15°) | 0.8874 | 0.7760 | 0.612 (Grade 3) / 0.855 (Grades 3+4) | Baseline run (`baseline_training.03.ipynb`). Val Macro F1 = `0.6888`. Val loss hit min at ep 4 (`0.7141`) then rose slightly (`0.7238` @ ep 5, `0.7324` @ ep 6). Strong on Grade 0 (`F1=0.919`) & Grade 4 (`F1=0.811`), weaker on Grade 1 (`F1=0.484`) & Grade 3 (`F1=0.532`). | `/content/drive/MyDrive/dr_project_artifacts/checkpoints/best_baseline_effnet_b0.pt` |

## Best model so far

| ID | Val QWK | Why it's the best | Link |
|---|---|---|---|
| EXP-001 | 0.8874 | Only baseline model trained so far; strong overall ordinal agreement (`QWK = 0.8874`) and high Grade 0/4 separation, serving as the reference benchmark before resolution/architecture upgrades. | `/content/drive/MyDrive/dr_project_artifacts/checkpoints/best_baseline_effnet_b0.pt` |

## Lessons learned

What worked, what didn't, and ideas to try next. Add these as you go; they become the "Discussion" section of the report.

- **What worked:** Patient-aware SHA256 deduplicated splitting prevented data leakage and produced a solid baseline (`Val QWK = 0.8874`, `Val Acc = 0.7760`) with `EfficientNet-B0` at `224x224` using AMP (`~370s/epoch` on Tesla T4).
- **What didn't:**
  - Low input resolution (`224x224`) blurs fine retinal lesions (microaneurysms, small exudates), hurting mid-grade discrimination (`Grade 1 F1 = 0.484`, `Grade 3 F1 = 0.532`) where `Grade 2` heavily overlaps with adjacent grades.
  - Aggressive inverse-frequency class weights (`3.531` for Grade 3, `2.441` for Grade 1) boosted recall at the cost of low precision (`0.409` for Grade 1, `0.471` for Grade 3).
  - Noticeable domain shift on external validation (`Messidor-2`), where `Grade 0` images frequently drifted into `Grade 2` predictions due to camera/illumination differences.
- **Ideas to try next (`experiments_04.ipynb` / `EXP-002+`):**
  - Increase input resolution (`300x300` or `384x384`) while keeping model/loss fixed (one change at a time) to capture fine lesions.
  - Test smoother class weighting (e.g., square-root inverse frequency) or ordinal/regression loss (`SmoothL1` / `MSE` + optimized thresholds) to reduce adjacent-grade confusion.
  - Add light photometric/illumination normalization or mild color/contrast augmentation to improve cross-domain generalization on `Messidor-2`.
  - Evaluate stronger backbones (`EfficientNet-B2/B3`, `ConvNeXt-Tiny`) once resolution and loss baselines are established.
