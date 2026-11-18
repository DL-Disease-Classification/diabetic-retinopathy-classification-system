# Study plan

All three of us are new to machine learning. This plan lists **what each of us needs to learn, in the order the project needs it**, with free resources. We learn each topic *just before* we use it, by applying it straight away in the repo.

> **How to use this file**
> - Tick topics off (`[x]`) as you finish them, and commit the change.
> - Fill in the **Target** dates together with the supervisor's milestones.
> - If a resource is bad or a better one turns up, replace it and note why.

## Roles

Everyone covers the **core track**. After that, each person leads one area and becomes the team's "go-to" for it. Leading means owning it, not doing it alone.

| Area | Lead | Main folders |
|---|---|---|
| Data & evaluation | [name] | `1_datasets/`, `2_data_exploration/`, `3_data_preparation/`, `5_evaluation/` |
| Modeling & explainability | [name] | `4_modeling/`, `6_explainability/` |
| Web app | [name] | `7_web_app/` |

Malak (team lead) also coordinates issues, reviews and supervisor meetings (`collaboration/`).

---

## Phases

| Phase | What we build | What we learn | Target |
|---|---|---|---|
| 1 | Data audit, cleaning and leak-free split | Core track A–C | [date] |
| 2 | First baseline model | Core track D–E | [date] |
| 3 | Better model + full evaluation | Track: modeling, evaluation | [date] |
| 4 | Explanations (Grad-CAM) + sanity checks | Track: explainability | [date] |
| 5 | Web app | Track: web app | [date] |
| 6 | Report, model card, presentation | Writing & presenting | [date] |

---

## Core track (everyone)

### A. The medical problem
- [ ] What diabetic retinopathy is, and its lesions: microaneurysms, haemorrhages, hard exudates, cotton-wool spots, neovascularisation
- [ ] The 5-grade ICDR scale, and what separates each grade (Wilkinson et al., *Ophthalmology*, 2003)
- [ ] What "referable DR" means and why screening programmes use it
- [ ] The landmark deep-learning DR paper: Gulshan et al., *JAMA*, 2016
- **Output:** write `dr_basics.md` and `icdr_grading_scale.md` in this folder, in your own words.

### B. Tools
- [ ] Git & GitHub flow: issues, branches, pull requests, reviews (see [`../CONTRIBUTING.md`](../CONTRIBUTING.md))
- [ ] Google Colab: runtimes, Secrets, saving notebooks to GitHub
- [ ] Python refresher: functions, lists/dicts, f-strings: [Kaggle Learn: Python](https://www.kaggle.com/learn/python)

### C. Working with data
- [ ] pandas: DataFrames, filtering, `groupby`, `crosstab`, merging: [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas)
- [ ] Plotting with matplotlib (bar charts, histograms, image grids)
- [ ] Data leakage, and why we split by photo/patient: [Kaggle Learn: Intermediate ML, "Data Leakage"](https://www.kaggle.com/learn/intermediate-machine-learning)
- **Output:** each person reproduces one part of the data audit notebook and explains it to the others.

### D. Deep learning basics
- [ ] What a neural network is, training vs validation vs test, overfitting: [fast.ai, *Practical Deep Learning for Coders*](https://course.fast.ai), lessons 1–3
- [ ] Convolutional neural networks (CNNs): [Stanford CS231n notes](https://cs231n.github.io)
- [ ] Transfer learning: fine-tuning a pretrained model
- [ ] PyTorch basics: tensors, `Dataset`/`DataLoader`, a training loop: [PyTorch tutorials](https://pytorch.org/tutorials/)

### E. Evaluating a classifier
- [ ] Confusion matrix, precision, recall, F1, accuracy and why it misleads on imbalanced data
- [ ] Quadratic weighted kappa (QWK)
- [ ] ROC curve and AUC, sensitivity and specificity

---

## Specialist tracks

### Modeling (lead + whoever is free)
- [ ] Pretrained models with [timm](https://huggingface.co/docs/timm): EfficientNet, ConvNeXt
- [ ] Data augmentation during training (flips, rotations, colour jitter)
- [ ] Handling class imbalance: class weights, weighted sampling
- [ ] Treating DR grading as ordinal: regression + tuned thresholds
- [ ] Learning-rate schedules, early stopping, mixed precision on Colab GPUs
- [ ] Keeping the experiment log ([`../4_modeling/experiments.md`](../4_modeling/experiments.md))

### Evaluation
- [ ] Internal vs external test sets, and why the external one matters
- [ ] Error analysis: looking at the images the model gets wrong
- [ ] Confidence intervals for metrics (bootstrapping)

### Explainability
- [ ] Grad-CAM: Selvaraju et al., *Grad-CAM: Visual Explanations from Deep Networks*, ICCV 2017 ([arXiv:1610.02391](https://arxiv.org/abs/1610.02391))
- [ ] The [pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam) library
- [ ] Sanity checks for saliency maps: Adebayo et al., *Sanity Checks for Saliency Maps*, NeurIPS 2018
- [ ] Comparing heatmaps with lesion annotations (IDRiD has lesion masks)

### Web app
- [ ] HTTP and REST APIs basics
- [ ] Serving a PyTorch model with [FastAPI](https://fastapi.tiangolo.com)
- [ ] Frontend basics (HTML/CSS/JavaScript, or a framework the team agrees on)
- [ ] Deploying a demo (e.g. Hugging Face Spaces)
- [ ] Handling medical images responsibly: no storage without consent, clear disclaimers

### Writing & presenting (everyone, phase 6)
- [ ] Writing a model card
- [ ] Turning the decision log into the report's method and discussion sections
- [ ] Presenting results honestly: what works, what doesn't, limitations

---

## Weekly routine (suggested)
- **Weekly meeting (30 min):** what each of us learned and built, blockers, next tasks. Notes go in `../collaboration/meetings/`.
- **Teach-back:** whoever learned a topic first explains it to the others in 10 minutes.
- **Keep it applied:** every topic should end in a commit (a notebook, a README section or a log entry).
