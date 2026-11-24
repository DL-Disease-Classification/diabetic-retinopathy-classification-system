# Near-duplicate matcher: how we built and checked it

The matcher in [`src/duplicates.py`](../../src/duplicates.py) finds **the same photo stored under different names**, even when it was resized, re-compressed, cropped a little, squeezed into a square, flipped, turned by 90° or recoloured. Notebook [`03_near_duplicates.ipynb`](../03_near_duplicates.ipynb) uses it on our dataset. This page explains how we built it, what failed on the way, and what it can and can't do. Decision: D-015 in [`notes/decision_log.md`](../../notes/decision_log.md).

## Why we developed it on another dataset

- **Iterating on our own data was too slow.** Building the matcher took several rounds of change → measure → fix. One full run on the Kaggle dataset (45,327 files) takes about an hour on a Colab CPU.
- **We needed pairs with a known answer.** [DeepDRiD](https://github.com/deepdrdoc/DeepDRiD) (ISBI 2020, public) has **two photos of each eye** of 400 patients: 1,600 photos in its training and validation sets. That gives the hard cases (the other eye of the same patient, photos from the same camera), and we can make copies of every photo ourselves, the way the Kaggle copies were made.
- **DeepDRiD only prepared the method; it decides nothing.** The threshold and the pass / fail verdict come from **our** dataset, with the rule fixed in D-014 before the run (notebook 03, Steps 3–4).

## How we tested each version

For every DeepDRiD photo we made five versions with a known answer:

| Version | How it was made | Like |
|---|---|---|
| Copy, family A | 600 × 600, a random flip / 90° turn, JPEG quality 90 | `FF`, `BF` |
| Copy, family B | as A, plus a random hue shift | `HB`, `HF`, `ALL`… |
| Copy, family C | as A, darker (×0.83) and more saturated (×1.47) | `FS`, `SF` |
| Copy, family D | as A, brighter (×1.6) | `FA` |
| Re-saved | resized to 40–80%, cropped 2–5% on every side, JPEG quality 60–85 | renamed copies |

We then measured:
- **same photo:** each version's score against its original, and whether the quick search finds the original among the 10 closest photos;
- **different eyes:** the left vs right eye of every patient (1,589 pairs), and each photo vs its closest photo of another patient (1,600 pairs);
- **same eye, other photo:** photo 1 vs photo 2 of each eye (792 pairs), for information.

The script is [`evaluate_on_deepdrid.py`](evaluate_on_deepdrid.py); its docstring says how to download DeepDRiD and run it (about 6 minutes).

## The versions, and what each one fixed

A score of about 1 means the same photo. The numbers come from the full DeepDRiD test of each version.

| Round | What the matcher did | What went wrong | Key numbers |
|---|---|---|---|
| 1 | Green channel, fine detail relative to the local brightness, only the dark detail kept | **Different eyes looked alike:** a dark ring along the edge of every photo, and halos around the camera's reflections (in the same place on every photo) | Different eyes up to **0.86**; recoloured copies found **84%** |
| 2 | **Black top-hat** (keeps only *thin* dark lines, i.e. vessels; ignores shading and reflections); outside the field filled with the nearest inside pixel, so the edge is no line | Different eyes fixed; but **recoloured copies** are missed by the green channel, and the brightest channel (HSV value, unchanged by hue shifts) fails on **brightened** copies | Different eyes max **0.67**. Green: recoloured found 85%. Value: recoloured 99.9%, brightened 87% |
| 3 | **Both channels**, keep the better match. Background colour read from the corners (DeepDRiD has **white-background** photos). An **oval** fitted to the field's edge, to undo squeezing | Squeezed copies of the wide photos still scored low: our oval fit was rejected by a sign error | Squeezed wide photos **0.34–0.45** |
| 4 | Sign error fixed | A few dark photos: parts of the retina as dark as the background cut "bites" into the field's edge and bent the oval | Plain copies: lowest **0.16**, 1st percentile 0.89 |
| 5 | Lower background threshold; field **filled to its convex outline**; oval **refitted** without the edge points that lie inside it. Faster scoring: only the 2 best of the 16 channel × flip / turn combinations are aligned in full (scores identical on 800 copies; 4 ms per pair) | — | See the final results |

## Final results on DeepDRiD

Threshold by the D-014 rule (at most 0.1% false matches in both different-eye sets): **0.669**.

| Set | Pairs | Lowest | 1st percentile | Median | At or above threshold | Search finds it |
|---|---|---|---|---|---|---|
| Copy, family A | 1,600 | 0.775 | 0.906 | 0.967 | 100.00% | 100.00% |
| Copy, family B | 1,600 | 0.721 | 0.851 | 0.947 | 100.00% | 100.00% |
| Copy, family C | 1,600 | 0.678 | 0.884 | 0.961 | 100.00% | 100.00% |
| Copy, family D | 1,600 | 0.280 | 0.787 | 0.963 | 99.44% | 99.69% |
| Re-saved | 1,600 | 0.429 | 0.832 | 0.976 | 99.81% | 99.94% |

| Different eyes | Pairs | 99.9th percentile | Highest | False matches |
|---|---|---|---|---|
| Other eye, same patient | 1,589 | 0.650 | 0.782 | 1 (0.06%) |
| Closest other patient | 1,600 | 0.639 | 0.648 | 0 |

- The one false match is patient 46: two eyes that look almost like mirror images. The camera's notch is in the same corner in both, so it isn't a digital copy.
- The lowest copy scores come from a few very poor photos (e.g. very dark, almost no visible vessels) and from brightened copies whose colours are clipped.

## What it can't do

- **It finds the same *photo*, not every photo of the same eye.** Of the 792 pairs of two photos of one eye:
  - 33 score above 0.9: DeepDRiD's own near-identical second photos (mean pixel difference 0.4 / 255);
  - 29 score between the threshold and 0.9: photos taken moments apart, with almost the same framing;
  - 730 score below the threshold: photos with different framing.
- **Consequence for the split (issue #4):**
  - **EyePACS:** both eyes of a patient are kept together through the patient number in the file name.
  - **APTOS and DDR:** the files carry **no patient IDs**, so two different photos of the same eye there can't be detected. This is a limitation of the data, stated in the report.
- **Very poor photos** (nearly black, or no visible vessels) can't be matched reliably. They are listed as "no usable field of view" when the field can't be found at all.

## The final method in short

1. **Field of view:** pixels that differ from the background colour (from the corners), filled to the convex outline. An oval is fitted to the edge where it isn't cut off by the image border, then refitted twice.
2. **Vessel maps:** the oval is mapped onto a 256 × 256 square. A black top-hat (11 px) gives the relative depth of thin dark lines. It is computed from the green channel and the brightest channel, reduced to 128 × 128, blurred slightly, and normalised. The rim (outer 10%) is left out.
3. **Search:** 32 × 32 versions of the maps, compared under the 8 flips / 90° turns and both channels; the 10 closest photos are candidates.
4. **Score:** for each candidate pair, the 2 most promising channel × flip / turn combinations are aligned (shifts up to 6 px) and correlated. The best correlation is the score.
