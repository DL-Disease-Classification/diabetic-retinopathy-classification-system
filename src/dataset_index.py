"""Index the Kaggle "Fundus (APTOS, DDR, IDRiD, EyePACS, Messidor)" dataset.

Turns the folder tree into a table with one row per image file, and decodes each
filename into: source dataset, original photo ID (``base_id``), augmentation code and
Gaussian-filtered flag.

Findings behind these rules: ``2_data_exploration/01_dataset_exploration.ipynb``
and ``1_datasets/README.md``.
"""
import os
import re

import pandas as pd

CLASS_NAMES = {0: "No DR", 1: "Mild", 2: "Moderate", 3: "Severe", 4: "Proliferative"}
SPLITS = ("train", "val", "test")

# Filename patterns of the original datasets. Order matters: the first match wins.
# Every source and label was verified against the original datasets' official label files
# (EyePACS trainLabels + test solution, APTOS train.csv, DDR train/valid/test.txt): 100% agreement.
SOURCE_PATTERNS = [
    ("EyePACS",    r"^(\d+_(?:left|right))(?=$|-)"),          # 19109_left-600-HB
    ("Messidor-1", r"^(\d{8}_\d{5}_\d{4}_PP)(?=$|-)"),        # 20051020_53178_0100_PP (0100 is NOT a grade)
    ("Messidor-2", r"^(IM\d{6})(?=$|-)"),                     # IM000319
    ("IDRiD",      r"^(IDRiD_\d+)(?=$|-)"),                   # IDRiD_006
    ("DDR",        r"^(\d{14,})(?=$|-)"),                     # 20170612163236281 (DDR, timestamp-style name)
    ("APTOS",      r"^([0-9a-f]{12})(?=$|-)"),                # a963ac561580, 9b093fe95d6b-GF-600-FF
    ("DDR",        r"^(\d{3}-\d{4}-(\d{3}))(?=$|-)"),         # 007-1590-000 (DDR; the last number is NOT a grade)
]

# Tokens that are not augmentation codes: "600" = resized marker, "GF" = Gaussian-filtered APTOS version.
NON_AUG_TOKENS = {"600", "GF"}


def parse_name(fname):
    """Decode one filename.

    Returns ``(source, base_id, aug, gf, ddr_code)``:
    - ``source``: original dataset, or ``"other"`` if no pattern matches
    - ``base_id``: ID of the original photo (for DDR: the official DDR image name); all copies share it
    - ``aug``: augmentation code such as ``"HB"``, or ``"none"`` for a plain file
    - ``gf``: True for Gaussian-filtered (grey, heavily processed) APTOS files
    - ``ddr_code``: last number of ``nnn-nnnn-nnn`` DDR names. It is NOT a grade:
      it agrees with the official DDR label only ~70% of the time, and the folder label is the correct one.
    """
    stem = fname.rsplit(".", 1)[0]
    gf = False
    if stem.startswith("GF-"):                  # some APTOS files have GF at the start
        stem, gf = stem[3:], True
    for source, pattern in SOURCE_PATTERNS:
        m = re.match(pattern, stem)
        if m:
            base = m.group(1)
            ddr_code = int(m.group(2)) if m.re.groups >= 2 else None
            tokens = [t for t in stem[m.end():].split("-") if t]
            gf = gf or ("GF" in tokens)
            aug = [t for t in tokens if t not in NON_AUG_TOKENS]
            return source, base, ("-".join(aug) if aug else "none"), gf, ddr_code
    return "other", stem, "none", gf, None


def build_index(data_dir):
    """One row per image under ``data_dir/{train,val,test}/{0..4}/``.

    ``data_dir`` is the ``split_dataset`` folder of the Kaggle download.
    Columns: split, label, fname, path, source, base_id, aug, gf, ddr_code, is_aug.
    """
    rows = []
    for split in SPLITS:
        for label in CLASS_NAMES:
            folder = os.path.join(data_dir, split, str(label))
            for fname in sorted(os.listdir(folder)):
                rows.append({"split": split, "label": label, "fname": fname,
                             "path": os.path.join(folder, fname)})
    df = pd.DataFrame(rows)
    return add_parsed_columns(df)


def add_parsed_columns(df):
    """Add the decoded filename columns to a table that has an ``fname`` column."""
    parsed = pd.DataFrame(df["fname"].apply(parse_name).tolist(), index=df.index,
                          columns=["source", "base_id", "aug", "gf", "ddr_code"])
    df = pd.concat([df.drop(columns=parsed.columns, errors="ignore"), parsed], axis=1)
    df["is_aug"] = df["aug"] != "none"
    return df
