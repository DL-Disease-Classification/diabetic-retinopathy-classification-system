"""Check the near-duplicate matcher (``src/duplicates.py``) on DeepDRiD, a public dataset.

DeepDRiD (ISBI 2020) has two photos of each eye of 400 patients in its training and validation
sets: 1,600 regular fundus photos. That gives realistic hard cases (the other eye of the same
patient, photos from the same camera) and lets us make copies of each photo the way the Kaggle
dataset's copies were made, so we know the right answer for every pair.

Get the photos (about 850 MB), from the repo root:

    git clone --filter=blob:none --no-checkout https://github.com/deepdrdoc/DeepDRiD.git ../DeepDRiD
    cd ../DeepDRiD
    git sparse-checkout set --no-cone 'regular_fundus_images/regular-fundus-training/*' \
        'regular_fundus_images/regular-fundus-validation/*'
    git checkout master

Run (takes about 5-10 minutes on 2 CPU cores):

    python 2_data_exploration/matcher_development/evaluate_on_deepdrid.py ../DeepDRiD/regular_fundus_images

What it measures (the same idea as D-014, on DeepDRiD):
- **Same photo:** every photo against copies of it, made like the Kaggle copies (600 x 600,
  a random flip / 90-degree turn, JPEG quality 90), plain (family A), with a random hue shift
  (B), darker + more saturated (C) or brighter (D), and a re-saved version (resized to 40-80%,
  cropped 2-5% on every side, JPEG quality 60-85). Score and whether the quick search finds it.
- **Different eyes:** the left vs the right eye of every patient (4 combinations), and every
  photo against its closest photo of another patient (by the quick search).
- **Same eye, other photo:** photo 1 vs photo 2 of the same eye (not calibrated; for information).
- The threshold by the D-014 rule (at most 0.1% false matches in both different-eye sets), and
  the share of each same-photo set at or above it.
"""
import glob, io, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import src.duplicates as dup  # noqa: E402


def jpeg(im, q):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def kaggle_copy(im, family, rng):
    """A copy made like the Kaggle dataset's: 600 x 600, a random flip / 90-degree turn, a colour change."""
    im = im.resize((600, 600), Image.BILINEAR)
    im = Image.fromarray(np.ascontiguousarray(dup.DIHEDRAL[rng.integers(8)](np.asarray(im))))
    if family == "B":                       # random hue shift
        h = np.asarray(im.convert("HSV")).copy()
        h[..., 0] = (h[..., 0].astype(int) + rng.integers(20, 236)) % 256
        im = Image.fromarray(h, "HSV").convert("RGB")
    elif family == "C":                     # darker, more saturated
        im = ImageEnhance.Color(ImageEnhance.Brightness(im).enhance(0.83)).enhance(1.47)
    elif family == "D":                     # strong brightening
        im = ImageEnhance.Brightness(im).enhance(1.6)
    return np.asarray(jpeg(im, 90))


def main(root):
    files = sorted(glob.glob(os.path.join(root, "*", "Images", "*", "*.jpg")))
    ids = [os.path.basename(f)[:-4] for f in files]
    idx = {k: i for i, k in enumerate(ids)}
    print(f"{len(files)} photos")
    t0 = time.time()

    def one(i):
        rng = np.random.default_rng(i)
        im = Image.open(files[i]).convert("RGB")
        im.thumbnail((1024, 1024))
        a = np.asarray(im)
        return (dup.features(a), {k: dup.features(kaggle_copy(im, k, rng)) for k in "ABCD"},
                dup.features(dup.resave(a, i)))

    with ThreadPoolExecutor(2) as ex:
        out = list(ex.map(one, range(len(files))))
    F = [o[0] for o in out]
    versions = {f"copy, family {k}": [o[1][k] for o in out] for k in "ABCD"}
    versions["re-saved"] = [o[2] for o in out]
    C = np.stack([f[2] for f in F])
    print(f"vessel maps: {time.time() - t0:.0f} s")

    # same photo
    same = {}
    for name, V in versions.items():
        s = np.array([dup.pair_score(F[i], V[i]) for i in range(len(files))], np.float32)
        I, _ = dup.search(np.stack([v[2] for v in V]), C, k=10)
        found = (I == np.arange(len(files))[:, None]).any(1)
        same[name] = (s, found)

    # different eyes, and the same eye
    lr, se = [], []
    for k in ids:
        p, e, n = re.match(r"(\d+)_([lr])(\d)", k).groups()
        if e == "l":
            lr += [(idx[k], idx[f"{p}_r{m}"]) for m in "12" if f"{p}_r{m}" in idx]
        if n == "1" and f"{p}_{e}2" in idx:
            se.append((idx[k], idx[f"{p}_{e}2"]))
    I, _ = dup.search(C, C, k=10, exclude_self=True)
    patient = [k.split("_")[0] for k in ids]
    nn = [(i, next(int(j) for j in I[i] if patient[j] != patient[i])) for i in range(len(files))]
    score = lambda pairs: np.array([dup.pair_score(F[i], F[j]) for i, j in pairs], np.float32)
    s_lr, s_nn, s_se = score(lr), score(nn), score(se)

    t = dup.threshold_for([s_lr, s_nn], 0.001)
    print(f"\nThreshold by the D-014 rule: {t:.3f}\n")
    print(f"{'set':28} {'n':>5} {'min':>6} {'1%':>6} {'median':>7} {'>= threshold':>13} {'search finds it':>16}")
    for name, (s, found) in same.items():
        ok = np.isfinite(s)
        print(f"{name:28} {ok.sum():5d} {np.nanmin(s):6.3f} {np.nanpercentile(s, 1):6.3f} {np.nanmedian(s):7.3f}"
              f" {np.mean(s[ok] >= t):13.2%} {found.mean():16.2%}")
    for name, s in [("other eye, same patient", s_lr), ("closest other patient", s_nn)]:
        s = s[np.isfinite(s)]
        print(f"{name:28} {len(s):5d}  p99.9 {np.percentile(s, 99.9):.3f}  max {s.max():.3f}"
              f"  false matches {np.mean(s >= t):.2%} ({int((s >= t).sum())})")
    s = s_se[np.isfinite(s_se)]
    print(f"{'same eye, other photo':28} {len(s):5d}  > 0.9: {(s > 0.9).sum()}   threshold-0.9: "
          f"{((s >= t) & (s <= 0.9)).sum()}   below threshold: {(s < t).sum()}")
    print(f"\ntotal {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main(sys.argv[1])
