# 7 · Web app

**Goal:** let doctors and patients upload a fundus photo and get a grade plus an explanation heatmap.

## Layout (planned)
```
backend/   model API (loads weights from Hugging Face Hub / GitHub Release)
frontend/  user interface
```
Model weights are **never** committed here.

## Planned features (to agree with the supervisor)

Our supervisor asked for features **beyond image classification**. Candidate ideas:

| Feature | For | Notes |
|---|---|---|
| DR grade + confidence | doctors, patients | Core output |
| Explanation heatmap (Grad-CAM) | doctors | Overlay on the uploaded photo |
| Refer / don't refer recommendation | patients, doctors | Based on referable DR (grade ≥ 2) |
| Image quality check | everyone | Warn if the photo is too dark, blurry or not a fundus photo |
| Downloadable PDF report | doctors, patients | Grade, heatmap, date, disclaimer |
| Plain-language explanation of each grade | patients | What the grade means and next steps |
| Separate doctor / patient views | both | More detail for doctors, simpler language for patients |
| Upload history | doctors | Track a patient over time (needs secure storage, so maybe out of scope) |

Always show the disclaimer: research project, **not a medical device**.
