# Diabetic Retinopathy Grading with Explainable AI

> Graduation project — Palestine Technical University - Kadoorie, Information Technology and Artificial Intelligence department, 2026-2027
>
> Team: Malak Battatt (lead), Mayar Battat, Hassan Sheikh Qasim · Supervisor: Dr. Samer Sweileh

## Overview

Diabetic retinopathy (DR) is a complication of diabetes that damages the retina and is a leading cause of preventable blindness. Screening means a specialist examines photos of the back of the eye (fundus photos) and grades the disease. There aren't enough specialists to do this for everyone.

This project builds a model that **grades DR severity from a fundus photo** on the 5-level international (ICDR) scale:

| Grade | Name |
|---|---|
| 0 | No DR |
| 1 | Mild non-proliferative DR |
| 2 | Moderate non-proliferative DR |
| 3 | Severe non-proliferative DR |
| 4 | Proliferative DR |

The model also **explains its prediction**: it highlights the regions of the image that drove the decision. Everything is delivered through a **web application** for doctors and patients.

## Project status

| Stage | Folder | Status |
|---|---|---|
| Domain study | `0_domain_study/` | 🟡 |
| Dataset selection | `1_datasets/` | 🟡 |
| Data exploration & audit | `2_data_exploration/` | 🟡 |
| Data preparation | `3_data_preparation/` | ⬜ |
| Modeling | `4_modeling/` | ⬜ |
| Evaluation | `5_evaluation/` | ⬜ |
| Explainability | `6_explainability/` | ⬜ |
| Web app | `7_web_app/` | ⬜ |
| Final report & presentation | `8_final_presentation/` | ⬜ |

⬜ not started · 🟡 in progress · ✅ done

## Key findings so far

- The Kaggle dataset we started from has **heavy train/test leakage**. Augmented copies of the same photo appear in train, validation and test: 46.5% of test files are versions of a training photo, rising to 95% for the Severe grade.
- We will therefore **rebuild the split ourselves**. We also plan to evaluate on an **independent external dataset** (Messidor-2, pending supervisor approval). See [`1_datasets/README.md`](1_datasets/README.md) and [`notes/decision_log.md`](notes/decision_log.md).

## Results

| Test set | QWK | Accuracy | Severe recall | Referable-DR AUC |
|---|---|---|---|---|
| Internal test (our clean split) | – | – | – | – |
| External test (Messidor-2) | – | – | – | – |

## Repository structure

```
0_domain_study/        DR background, grading scale, literature review
1_datasets/            dataset cards and download instructions (no images)
2_data_exploration/    auditing the raw data
3_data_preparation/    cleaning, de-duplication, leak-free split
4_modeling/            training notebooks and experiment log
5_evaluation/          metrics, external testing, error analysis
6_explainability/      Grad-CAM and other explanation methods
7_web_app/             backend (model API) and frontend
8_final_presentation/  report, slides, figures
src/                   shared Python code used by the notebooks
collaboration/         roles, team norms, meeting notes
notes/                 decision log and working notes
```

## Getting started

We work in **Google Colab**.

1. Open a notebook from this repo in Colab: **File → Open notebook → GitHub**. The first time, when Colab asks to authorise GitHub, **grant access to the `DL-Disease-Classification` organisation**, or the repo won't appear.
2. Get a Kaggle API token (kaggle.com → Settings → API → *Generate New Token*). Add it to Colab **Secrets** (🔑 icon) as `KAGGLE_API_TOKEN` with notebook access on.
3. Run the notebook's first cell, which clones this repo so the shared code in `src/` can be imported:

```python
# First cell of every notebook: get the repo's shared code (src/) into Colab
REPO = "diabetic-retinopathy-classification-system"
!git clone -q https://github.com/DL-Disease-Classification/{REPO}.git
import sys; sys.path.append(f"/content/{REPO}")
```

If the repo is **private**, create a read-only GitHub token (GitHub → Settings → Developer settings → *Fine-grained tokens*, access to this repo only, permission *Contents: Read*). Add it to Colab Secrets as `GITHUB_TOKEN`, and clone with:

```python
from google.colab import userdata
token = userdata.get("GITHUB_TOKEN")
!git clone -q https://x-access-token:{token}@github.com/DL-Disease-Classification/{REPO}.git
```

4. Run the notebooks in folder order. Each notebook downloads the data it needs. Download instructions are in [`1_datasets/README.md`](1_datasets/README.md).

New to the tools? Start with the team's learning plan: [`0_domain_study/study_plan.md`](0_domain_study/study_plan.md).

Images and model weights are **not stored in this repo**. They're too large, and the datasets have their own licences.

## Team workflow

See [`CONTRIBUTING.md`](CONTRIBUTING.md). In short:
- Real tasks get a GitHub Issue, and the branch is named after it (`12-duplicate-threshold`).
- Small changes (typos, docs tidy-ups) skip the issue and use a descriptive branch name.
- Everything merges through a pull request reviewed by another team member.

## Disclaimer

This is a student research project. It is **not a medical device** and must not be used for diagnosis or treatment decisions.

## Acknowledgements

The original datasets, citations and licence terms are listed in [`1_datasets/README.md`](1_datasets/README.md).

## License

See [`LICENSE`](LICENSE). It covers our code only, not the datasets.
