"""Merging several logs, for example one per server."""
from .reader import parse_events, resolve


def merge(sources, options=None):
    """Merge several logs into one list of (source_index, Event), ordered by event time.

    sources is a sequence of logs (each one what parse_events accepts). Events with the
    same time keep source order, then input order. A source does not have to be in time
    order itself, which is why this one keeps every event and sorts: a streaming merge
    (heapq.merge) would give a different order for such sources.
    """
    opts = resolve(options)
    tagged = []
    for index, source in enumerate(sources):
        for event in parse_events(source, opts):
            tagged.append((index, event))
    tagged.sort(key=lambda pair: pair[1].time)
    return tagged
