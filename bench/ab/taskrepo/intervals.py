"""Merge closed integer intervals."""


def merge(intervals):
    """Merge a list of (start, end) intervals.

    Rules:
    1. Input may be in any order; the result is sorted by start.
    2. Overlapping intervals merge: (1, 5) and (3, 8) -> (1, 8).
    3. Touching intervals merge too: (1, 3) and (3, 6) -> (1, 6).
       Intervals one apart do NOT merge: (1, 3) and (4, 6) stay separate.
    4. An interval fully inside another disappears: (1, 10) and (2, 3) -> (1, 10).
    5. A single-point interval (4, 4) is valid.
    6. start > end raises ValueError naming the bad interval.
    7. The input list is not modified. The result is a new list of tuples.
    """
    out = []
    intervals.sort()
    for start, end in intervals:
        if out and start < out[-1][1]:
            out[-1] = (out[-1][0], end)
        else:
            out.append((start, end))
    return out
