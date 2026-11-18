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
| EXP-000 | YYYY-MM-DD | name | split_v1 | e.g. EfficientNet-B0 (ImageNet) | 512 | 20 | 32 | 3e-4 | e.g. MSE regression + tuned thresholds / class weights | flips, rotation, brightness | – | – | – | template row: delete me | HF Hub link |

## Best model so far

| ID | Val QWK | Why it's the best | Link |
|---|---|---|---|
| – | – | – | – |

## Lessons learned

What worked, what didn't, and ideas to try next. Add these as you go; they become the "Discussion" section of the report.

- ...
