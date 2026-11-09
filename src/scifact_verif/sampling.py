"""Stratified error sampling for RQ3 (standard library only)."""
import random


def allocate(counts, total):
    """Equal allocation of `total` slots across strata, capped at each stratum's size; unused slots are
    redistributed to strata with room, one at a time in sorted stratum order. Returns {stratum: n}.
    If sum(counts) <= total, every case is taken."""
    keys = sorted(counts)
    if sum(counts.values()) <= total:
        return dict(counts)
    take = {k: 0 for k in keys}
    left = total
    while left > 0:
        open_ = [k for k in keys if take[k] < counts[k]]
        if not open_:
            break
        share, extra = divmod(left, len(open_))
        for n, k in enumerate(open_):
            add = min(share + (1 if n < extra else 0), counts[k] - take[k])
            take[k] += add
            left -= add
    return take


def draw(ids_by_stratum, take, seed):
    """Seeded sample without replacement; ids are sorted first so the draw does not depend on input order."""
    rng = random.Random(seed)
    out = {}
    for k in sorted(ids_by_stratum):
        ids = sorted(ids_by_stratum[k])
        out[k] = sorted(rng.sample(ids, take[k]))
    return out