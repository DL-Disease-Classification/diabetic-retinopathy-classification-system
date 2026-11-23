"""Pick one trustworthy file per original photo (selection rule v3).

Rule (``notes/decision_log.md``, D-007; D-008 for IDRiD):

1. Drop sources: IDRiD (labels unreliable in this dataset) and Messidor-1/2
   (reserved for the external test set).
2. Drop Gaussian-filtered (GF) files and any file with the grey "processed" look.
3. For each photo keep ONE file, preferring the original, then family A copies,
   then family B copies. Families C and D are never used. Among files of the same rank,
   prefer the full-size original over the uploader's resized "-600" copy (e.g. APTOS
   ``x.png`` over ``x-600.jpg``), then the file name, so the choice never depends on
   folder order (``02_image_audit.ipynb``, step 4).
4. Every kept copy, and every photo of the same EyePACS patient, is ``train_only``:
   validation and test contain real, untouched photos only.

Augmentation-code families, measured on ALL ~14,100 copy/original pairs (notebook step 9),
against an envelope fixed in advance (brightness/contrast/saturation 0.80-1.25,
red/green 0.90-1.10, zoom 0.95-1.05):

- A, geometry only (``FF``, ``BF``): colours untouched; 90% inside the envelope.
- B, random hue shift (``HB``, ``HBF``, ``HF``, ``HFF``, ``ALL``): red/green 0.60-2.18
  (5th-95th %); only ~25% inside. NOT part of the base dataset; kept and flagged so
  training can test with vs without them (D-009).
- C, darker + oversaturated (``FS``, ``SF``); D, strong brightening (``FA``): never used.

The split is made ONCE on the full selection, so validation and test are identical whether
or not family B copies are used for training. Base training set:
``clean[clean.family.isin(["original", "A_geometry"])]``.
"""
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from PIL import Image

FAMILY = {
    "none": "original",
    "FF": "A_geometry", "BF": "A_geometry",
    "HB": "B_hue", "HBF": "B_hue", "HF": "B_hue", "HFF": "B_hue", "ALL": "B_hue",
    "FS": "C_dark_saturated", "SF": "C_dark_saturated",
    "FA": "D_bright",
}
PRIORITY = ["none", "FF", "BF", "HFF", "HB", "HF", "HBF", "ALL"]   # first = most preferred
NEVER_USE = ["FS", "SF", "FA"]
BASE_FAMILIES = ["original", "A_geometry"]
EXCLUDED_SOURCES = ["IDRiD", "Messidor-1", "Messidor-2"]
PROCESSED_CORNER_THRESHOLD = 60   # mean corner brightness; black (~0) = normal photo, grey (~128) = processed


def look_stats(path):
    """Cheap appearance measures of one image: ``(corner_bg, saturation, red_green)``."""
    im = Image.open(path)
    im.draft("RGB", (256, 256))                      # fast partial decode for JPEGs
    im = im.convert("RGB").resize((128, 128))
    a = np.asarray(im, dtype=np.float32)
    gray = a.mean(2)
    corners = np.concatenate([gray[:10, :10].ravel(), gray[:10, -10:].ravel(),
                              gray[-10:, :10].ravel(), gray[-10:, -10:].ravel()])
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)[32:96, 32:96]
    centre = a[32:96, 32:96]
    return float(corners.mean()), float(hsv[..., 1].mean()), \
        float(centre[..., 0].mean() / (centre[..., 1].mean() + 1))


def add_look_stats(df, workers=8):
    """Add ``corner_bg``, ``saturation``, ``red_green`` and ``processed`` columns (reads every image)."""
    with ThreadPoolExecutor(workers) as ex:
        stats = list(ex.map(look_stats, df["path"]))
    df = df.copy()
    df[["corner_bg", "saturation", "red_green"]] = pd.DataFrame(stats, index=df.index)
    df["processed"] = df["corner_bg"] > PROCESSED_CORNER_THRESHOLD
    return df


def is_resized(fname, base_id):
    """True if the name carries the uploader's ``600`` resize marker, e.g. ``a963ac561580-600.jpg``.

    Only the part after the photo ID is checked, so a DDR name such as ``007-1590-600``,
    whose last number is part of the ID, is not mistaken for a resized copy.
    """
    stem = fname.rsplit(".", 1)[0]
    if stem.startswith("GF-"):
        stem = stem[3:]
    rest = stem[len(base_id):] if stem.startswith(base_id) else stem
    return "600" in rest.split("-")


def select_clean_photos(df):
    """Apply rule v3. ``df`` needs the columns from ``build_index`` and ``add_look_stats``.

    Returns one row per kept photo, with ``family``, ``is_copy``, ``patient`` and ``train_only``.
    """
    keep = (df["aug"].isin(PRIORITY) & ~df["gf"] & ~df["processed"]
            & ~df["source"].isin(EXCLUDED_SOURCES))
    cand = df[keep].copy()
    cand["rank"] = cand["aug"].map({code: i for i, code in enumerate(PRIORITY)})
    cand["resized"] = [is_resized(f, b) for f, b in zip(cand["fname"], cand["base_id"])]
    clean = (cand.sort_values(["base_id", "rank", "resized", "fname"])
                 .drop_duplicates("base_id")
                 .drop(columns=["rank", "resized"])
                 .reset_index(drop=True))
    clean["family"] = clean["aug"].map(FAMILY)
    clean["is_copy"] = clean["aug"] != "none"
    # EyePACS names carry a patient number (left + right eye); other sources: one photo = one group
    clean["patient"] = np.where(clean["source"] == "EyePACS",
                                "eyepacs_" + clean["base_id"].str.split("_").str[0],
                                clean["base_id"])
    copy_patients = set(clean.loc[clean["is_copy"], "patient"])
    clean["train_only"] = clean["patient"].isin(copy_patients)
    return clean
