"""Find the same photo stored under different names, including near copies.

Exact copies (identical bytes or pixels) are found with fingerprints in
``2_data_exploration/02_image_audit.ipynb``, steps 5-6. Near copies are the same photo
resized, re-compressed, cropped a little, squeezed into a square, flipped, turned by
90 degrees, brightened, darkened or recoloured. They are found by comparing the photos'
**vessel patterns**:

1. ``field_of_view``: the round (or, after squeezing, oval) field of view, found by its
   difference from the background colour, so black and white backgrounds both work.
   An oval is fitted to its edge, ignoring edges cut off by the image border.
2. ``vessel_maps``: the field is mapped onto a fixed square, and a *black top-hat* keeps
   only thin dark structures, i.e. vessels, relative to the local brightness. Broad
   shading, the darker rim, bright reflections and brightness changes don't count.
   Two maps are made, from two channels:
   - green: the strongest vessel contrast;
   - value (the brightest channel): unchanged by hue shifts.
3. ``search``: each photo's closest candidates, from small, blurred versions of the maps,
   compared under all 8 flips / 90-degree turns.
4. ``pair_score``: for a candidate pair, the best correlation of the full maps over the
   two channels, the 8 flips / turns and small shifts. About 1 = the same photo.

The threshold is NOT set here. It is chosen from pairs with a known answer, as fixed in
``notes/decision_log.md``, D-014.

How it was built and checked: ``2_data_exploration/matcher_development/README.md``. In short,
on 1,600 photos of the public DeepDRiD dataset, with copies made like this dataset's: at the
threshold the D-014 rule gives there (0.669), 99.4-100% of every kind of copy scored at or above
it, with 1 false match in 3,189 different-eye pairs. It finds the same *photo*: two photos of one
eye taken with different framing usually score low.
"""
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image

MAP_SIZE = 128          # side of a vessel map; the field of view fills it
COARSE_SIZE = 32        # side of the small map used for the candidate search
BG_DIFF = 10            # a pixel is part of the field if it differs from the background colour by more
RIM = 0.90              # keep the inner 90% of the field's radius (drops the notch and edge glare)
TOPHAT = 11             # black top-hat element (pixels, at twice the map size): wider than a vessel
MAX_SHIFT = 6           # largest shift (pixels of the map) tried when lining two maps up
MIN_VALID = 0.25        # a map needs at least this share of the square to be valid
CHANNELS = ("green", "value")

# the 8 flips / 90-degree turns of a square image
DIHEDRAL = [lambda a: a, lambda a: np.rot90(a, 1), lambda a: np.rot90(a, 2), lambda a: np.rot90(a, 3),
            lambda a: a[:, ::-1], lambda a: np.rot90(a[:, ::-1], 1),
            lambda a: np.rot90(a[:, ::-1], 2), lambda a: np.rot90(a[:, ::-1], 3)]


def load_rgb(path, max_side=1024):
    """Read an image as RGB, shrunk so its longer side is at most ``max_side`` (fast for JPEGs)."""
    im = Image.open(path)
    im.draft("RGB", (max_side, max_side))
    im = im.convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.BILINEAR)
    return np.asarray(im)


def background_colour(rgb):
    """Colour of the background, from the four corners: the corner colour that at least two
    corners share (black or white backgrounds). Black if the corners disagree."""
    h, w = rgb.shape[:2]
    p = max(4, int(0.03 * min(h, w)))
    corners = [rgb[:p, :p], rgb[:p, -p:], rgb[-p:, :p], rgb[-p:, -p:]]
    meds = [np.median(c.reshape(-1, 3), axis=0) for c in corners]
    for i, m in enumerate(meds):
        if sum(np.abs(m - o).max() < BG_DIFF for o in meds) >= 2:
            return m
    return np.zeros(3)


def _fit_oval(x, y, h, w):
    """Axis-aligned oval ``(cx, cy, ax, ay)`` through edge points; a circle if no plausible oval."""
    cx, cy, c = np.linalg.lstsq(np.c_[2 * x, 2 * y, np.ones_like(x)], x * x + y * y, rcond=None)[0]
    r = float(np.sqrt(max(c + cx * cx + cy * cy, 1.0)))
    fit = (float(cx), float(cy), r, r)
    try:      # A x^2 + B y^2 + C x + D y = 1 (a photo squeezed into a square)
        A, B, C, D = np.linalg.lstsq(np.c_[x * x, y * y, x, y], np.ones_like(x), rcond=None)[0]
        G = 1 + C * C / (4 * A) + D * D / (4 * B)
        if A * B > 0 and G / A > 0 and G / B > 0:      # an oval (the signs may all be flipped)
            ax, ay = np.sqrt(G / A), np.sqrt(G / B)
            if 0.6 < ax / ay < 1.6 and abs(ax / ay - 1) > 0.03 and 0.25 * max(h, w) < max(ax, ay) < 1.5 * max(h, w):
                fit = (float(-C / (2 * A)), float(-D / (2 * B)), float(ax), float(ay))
    except (np.linalg.LinAlgError, ZeroDivisionError, FloatingPointError):
        pass
    return fit


def field_of_view(rgb):
    """``(mask, oval)`` of the field of view.

    ``mask``: uint8, 1 inside the field, filled out to its convex outline (so very dark parts
    of the retina at the edge still count). ``oval``: ``(cx, cy, ax, ay)``, centre and the two
    semi-axes in pixels, fitted to the field's edge where it is not cut off by the image
    border. Edge points well inside the first fit are dropped and the oval refitted twice.
    A circle if no plausible oval fits; the image centre and half its longer side if no edge
    is visible.
    """
    h, w = rgb.shape[:2]
    whole = (w / 2.0, h / 2.0, max(h, w) / 2.0, max(h, w) / 2.0)
    bg = background_colour(rgb)
    m = (np.abs(rgb.astype(np.int16) - bg.astype(np.int16)).max(axis=2) > BG_DIFF).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 1:
        return np.ones((h, w), np.uint8), whole
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    contours, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(max(contours, key=len))
    filled = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(filled, hull, 1)
    contours, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pts = max(contours, key=len)[:, 0, :].astype(np.float64)
    pts = pts[(pts[:, 0] > 2) & (pts[:, 0] < w - 3) & (pts[:, 1] > 2) & (pts[:, 1] < h - 3)]
    if len(pts) < 50:
        return filled, whole
    oval = _fit_oval(pts[:, 0], pts[:, 1], h, w)
    for _ in range(2):        # drop points well inside the fit (straight chords across dark bites), refit
        cx, cy, ax, ay = oval
        rho = np.sqrt(((pts[:, 0] - cx) / ax) ** 2 + ((pts[:, 1] - cy) / ay) ** 2)
        keep = rho > 0.97
        if keep.sum() < 50:
            break
        oval = _fit_oval(pts[keep, 0], pts[keep, 1], h, w)
    return filled, oval


def _channel(rgb, name):
    if name == "value":                    # HSV value = brightest channel: a hue shift leaves it unchanged
        return rgb.max(axis=2).astype(np.float32)
    return rgb[..., 1].astype(np.float32)  # green: the strongest vessel contrast


def vessel_maps(rgb, size=MAP_SIZE):
    """Vessel maps of one photo, one per channel in ``CHANNELS``, plus the mask where they are valid.

    Returns ``(maps, mask)``: ``maps`` is (len(CHANNELS), size, size), each with mean 0 and
    standard deviation 1 inside ``mask`` (size, size) and 0 outside it. If no usable field of
    view is found, the mask is empty.
    """
    work = 2 * size                                    # filter at twice the final resolution
    fov, (cx, cy, ax, ay) = field_of_view(rgb)
    pre = max(1.0, max(ax, ay) / work)                 # shrink first (anti-aliasing)
    if pre > 1.0:
        new = (max(1, int(round(rgb.shape[1] / pre))), max(1, int(round(rgb.shape[0] / pre))))
        rgb = cv2.resize(rgb, new, interpolation=cv2.INTER_AREA)
        fov = cv2.resize(fov, new, interpolation=cv2.INTER_NEAREST)
        cx, cy, ax, ay = cx / pre, cy / pre, ax / pre, ay / pre
    sx, sy = work / (2 * ax), work / (2 * ay)          # the oval becomes a circle filling the square
    M = np.float32([[sx, 0, -(cx - ax) * sx], [0, sy, -(cy - ay) * sy]])
    inside = cv2.warpAffine(fov, M, (work, work), flags=cv2.INTER_NEAREST) > 0
    yy, xx = np.mgrid[:work, :work]
    circle = (xx - work / 2 + 0.5) ** 2 + (yy - work / 2 + 0.5) ** 2 <= (RIM * work / 2) ** 2
    mask = (circle & inside).astype(np.uint8)
    empty = (np.zeros((len(CHANNELS), size, size), np.float32), np.zeros((size, size), np.float32))
    if mask.sum() < MIN_VALID * work * work:
        return empty
    # outside the mask: the nearest pixel inside it, so the edge itself is no "dark line"
    _, near = cv2.distanceTransformWithLabels(1 - mask, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (TOPHAT, TOPHAT))
    inner = cv2.erode(mask, np.ones((TOPHAT // 2, TOPHAT // 2), np.uint8))
    m = cv2.resize(inner.astype(np.float32), (size, size), interpolation=cv2.INTER_AREA) > 0.99
    if m.sum() < MIN_VALID * size * size:
        return empty
    maps = []
    for name in CHANNELS:
        g = cv2.warpAffine(_channel(rgb, name), M, (work, work), flags=cv2.INTER_LINEAR)
        lut = np.zeros(near.max() + 1, np.float32)
        lut[near[mask > 0]] = g[mask > 0]
        g = lut[near]
        closed = cv2.morphologyEx(g, cv2.MORPH_CLOSE, kernel)
        depth = (closed - g) / (closed + 1.0)          # relative depth of thin dark structures
        depth = cv2.resize(depth * inner, (size, size), interpolation=cv2.INTER_AREA)
        depth = cv2.GaussianBlur(depth, (0, 0), 1.0) * m
        vals = depth[m]
        d = np.clip((depth - vals.mean()) / (vals.std() + 1e-6) * m, -4, 4)
        maps.append(d.astype(np.float32))
    return np.stack(maps), m.astype(np.float32)


def coarse(vmap, mask, size=COARSE_SIZE):
    """Small, blurred, unit-length version of one map, for the candidate search."""
    num = cv2.resize(vmap, (size, size), interpolation=cv2.INTER_AREA)
    den = cv2.resize(mask, (size, size), interpolation=cv2.INTER_AREA)
    ok = den > 0.5
    v = np.where(ok, num / (den + 1e-6), 0).astype(np.float32)
    if ok.any():
        v[ok] -= v[ok].mean()
    v = v.ravel()
    return v / (np.linalg.norm(v) + 1e-6)


def features(path_or_rgb):
    """``(maps, mask, coarse)`` for one photo: a path, or an RGB array already in memory.

    ``coarse`` is (len(CHANNELS), COARSE_SIZE**2). A photo without a usable field of view
    has an empty mask and all-zero vectors; ``pair_score`` then returns NaN.
    """
    rgb = load_rgb(path_or_rgb) if isinstance(path_or_rgb, str) else path_or_rgb
    maps, mask = vessel_maps(rgb)
    return maps, mask, np.stack([coarse(v, mask) for v in maps])


def features_many(items, workers=8, chunk=2000, progress=None):
    """``features`` for many photos (paths, or callables returning an RGB array), filled into
    preallocated arrays: maps (n, c, s, s) float16, masks (n, s, s) uint8, coarse (n, c, s'**2)
    float32. Works in chunks so memory stays low. ``progress``: e.g. ``tqdm`` (optional)."""
    n = len(items)
    maps = np.zeros((n, len(CHANNELS), MAP_SIZE, MAP_SIZE), np.float16)
    masks = np.zeros((n, MAP_SIZE, MAP_SIZE), np.uint8)
    coarse_ = np.zeros((n, len(CHANNELS), COARSE_SIZE * COARSE_SIZE), np.float32)
    one = lambda it: features(it() if callable(it) else it)
    bar = progress(total=n) if progress else None
    with ThreadPoolExecutor(workers) as ex:
        for s in range(0, n, chunk):
            for i, (v, m, c) in enumerate(ex.map(one, items[s:s + chunk]), start=s):
                maps[i], masks[i], coarse_[i] = v, m, c
            if bar:
                bar.update(min(chunk, n - s))
    if bar:
        bar.close()
    return maps, masks, coarse_


def _dihedral_rows(c):
    a = c.reshape(COARSE_SIZE, COARSE_SIZE)
    return np.stack([np.ascontiguousarray(t(a)).ravel() for t in DIHEDRAL])


def search(query, database, k=10, batch=256, exclude_self=False):
    """For each query, the ``k`` most similar database photos (coarse maps, any channel, any of
    the 8 flips / turns).

    ``query`` (nq, c, n) and ``database`` (nd, c, n) are coarse vectors from ``features``.
    Returns ``(idx, sim)``, each (nq, k). With ``exclude_self``, query i is never matched to
    database i (use when query and database are the same set).
    """
    nq, nc, _ = query.shape
    idx = np.zeros((nq, k), np.int64)
    sim = np.zeros((nq, k), np.float32)
    dbT = [np.ascontiguousarray(database[:, c, :].T) for c in range(nc)]
    for s in range(0, nq, batch):
        q = query[s:s + batch]
        best = None
        for c in range(nc):
            qd = np.stack([_dihedral_rows(v) for v in q[:, c, :]])        # (b, 8, n)
            S = (qd.reshape(-1, qd.shape[2]) @ dbT[c]).reshape(len(q), 8, -1).max(1)
            best = S if best is None else np.maximum(best, S)
        if exclude_self:
            best[np.arange(len(q)), np.arange(s, s + len(q))] = -np.inf
        top = np.argpartition(-best, k, axis=1)[:, :k]
        order = np.argsort(-np.take_along_axis(best, top, 1), axis=1)
        top = np.take_along_axis(top, order, 1)
        idx[s:s + len(q)] = top
        sim[s:s + len(q)] = np.take_along_axis(best, top, 1)
    return idx, sim


def _ncc_shifted(a, ma, b, mb, max_shift=MAX_SHIFT):
    """Best correlation of a and b over shifts up to ``max_shift``, counted where both are valid."""
    n = a.shape[0]
    p = max_shift
    A = np.pad(a, p)
    MA = np.pad(ma, p)
    F = np.fft.fft2(a) * np.conj(np.fft.fft2(b))       # phase correlation proposes the shift
    r = np.fft.ifft2(F / (np.abs(F) + 1e-9)).real
    dy, dx = np.unravel_index(r.argmax(), r.shape)
    dy = dy - n if dy > n // 2 else dy
    dx = dx - n if dx > n // 2 else dx
    cands = {(0, 0)}
    if abs(dy) <= p and abs(dx) <= p:
        cands |= {(dy + i, dx + j) for i in (-1, 0, 1) for j in (-1, 0, 1)
                  if abs(dy + i) <= p and abs(dx + j) <= p}
    best = -1.0
    for sy, sx in cands:
        aa = A[p + sy:p + sy + n, p + sx:p + sx + n]
        mm = (MA[p + sy:p + sy + n, p + sx:p + sx + n] * mb) > 0
        if mm.sum() < MIN_VALID * n * n:
            continue
        x = aa[mm] - aa[mm].mean()
        y = b[mm] - b[mm].mean()
        best = max(best, float((x * y).sum() / (np.sqrt((x * x).sum() * (y * y).sum()) + 1e-9)))
    return best


def pair_score(fa, fb, top=2):
    """Similarity of two photos: the best correlation of their vessel maps over the channels,
    the 8 flips / turns and small shifts. About 1 = the same photo. NaN if either photo has no
    usable field of view.

    For speed, the 16 combinations of channel and flip / turn are first ranked with the small
    maps, and only the ``top`` best are lined up in full (``top=None``: all 16).
    """
    va, ma, ca = fa
    vb, mb, cb = fb
    ma = np.asarray(ma, np.float32)
    mb = np.asarray(mb, np.float32)
    if ma.sum() == 0 or mb.sum() == 0:
        return float("nan")
    combos = [(c, t) for t in range(len(DIHEDRAL)) for c in range(len(va))]
    if top is not None:
        quick = [float(ca[c] @ _dihedral_rows(cb[c])[t]) for c, t in combos]
        combos = [combos[i] for i in np.argsort(quick)[::-1][:top]]
    best = -1.0
    for c, t in combos:
        T = DIHEDRAL[t]
        best = max(best, _ncc_shifted(np.asarray(va[c], np.float32), ma,
                                      np.ascontiguousarray(T(np.asarray(vb[c], np.float32))),
                                      np.ascontiguousarray(T(mb))))
    return best


def score_pairs(A, B, pairs, workers=8, progress=None):
    """``pair_score`` for many pairs. ``A`` and ``B`` are ``(maps, masks, coarse)`` arrays from
    ``features_many``; ``pairs`` is a list of ``(i, j)``: row i of A against row j of B."""
    def one(p):
        i, j = p
        return pair_score((A[0][i], A[1][i], A[2][i]), (B[0][j], B[1][j], B[2][j]))
    out = np.empty(len(pairs), np.float32)
    bar = progress(total=len(pairs)) if progress else None
    with ThreadPoolExecutor(workers) as ex:
        for s in range(0, len(pairs), 5000):
            out[s:s + 5000] = list(ex.map(one, pairs[s:s + 5000]))
            if bar:
                bar.update(min(5000, len(pairs) - s))
    if bar:
        bar.close()
    return out


# --------------------------------------------------------------------------- calibration helpers

AUG_ORDER = ["none", "FF", "BF", "HFF", "HB", "HF", "HBF", "ALL", "FS", "SF", "FA"]   # least altered first


def representatives(df):
    """One file per photo (``base_id``), for every source: the least altered file.

    Not Gaussian-filtered first, then the augmentation code in ``AUG_ORDER`` (original first),
    then the full-size file over the resized ``-600`` copy, then the file name. ``df`` needs the
    columns of ``build_index``.
    """
    from src.selection import is_resized
    d = df.copy()
    d["_rank"] = d["aug"].map({a: i for i, a in enumerate(AUG_ORDER)}).fillna(len(AUG_ORDER))
    d["_resized"] = [is_resized(f, b) for f, b in zip(d["fname"], d["base_id"])]
    d = d.sort_values(["base_id", "gf", "_rank", "_resized", "fname"]).drop_duplicates("base_id")
    return d.drop(columns=["_rank", "_resized"]).reset_index(drop=True)


def resave(rgb, seed):
    """A re-saved version of a photo, as D-014 specifies: resized to 40-80%, cropped by 2-5% on
    every side, JPEG-compressed at quality 60-85. ``seed`` makes it reproducible."""
    import io
    rng = np.random.default_rng(seed)
    im = Image.fromarray(rgb)
    f = rng.uniform(0.4, 0.8)
    im = im.resize((max(8, int(im.width * f)), max(8, int(im.height * f))), Image.BILINEAR)
    c = rng.uniform(0.02, 0.05)
    im = im.crop((int(im.width * c), int(im.height * c), int(im.width * (1 - c)), int(im.height * (1 - c))))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=int(rng.integers(60, 86)))
    buf.seek(0)
    return np.asarray(Image.open(buf).convert("RGB"))


def threshold_for(negative_scores, max_rate=0.001):
    """The lowest threshold at which every set of different-eye scores has at most ``max_rate``
    false matches (score >= threshold). NaN scores are ignored."""
    t = np.float32(-np.inf)
    for s in negative_scores:
        s = np.asarray(s, np.float32)
        s = np.sort(s[np.isfinite(s)])[::-1]
        allowed = int(np.floor(max_rate * len(s)))
        if allowed < len(s):        # strictly above the (allowed+1)-th highest score, in float32 like the scores
            t = max(t, np.nextafter(s[allowed], np.float32(np.inf)))
    return float(t)


def groups(pairs, ids):
    """Join matched pairs into groups (connected components). ``pairs``: (i, j) indices into
    ``ids``. Returns a dict id -> group id (the smallest id in the group); unmatched ids are absent."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, j in pairs:
        a, b = find(ids[i]), find(ids[j])
        if a != b:
            parent[max(a, b)] = min(a, b)
    return {x: find(x) for x in parent}
