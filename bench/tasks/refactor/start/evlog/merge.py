"""Merging several logs, for example one per server."""
from .reader import parse_events


def merge(sources, min_level="DEBUG", strict=False, utc_offset=0):
    """Merge several logs into one list of (source_index, Event), ordered by event time.

    sources is a sequence of logs (each one what parse_events accepts). Events with the
    same time keep source order, then input order. A source does not have to be in time
    order itself. Line numbers stay those of each source. The parse arguments mean what
    they mean for parse_events and apply to every source.
    """
    tagged = []
    for index, source in enumerate(sources):
        for event in parse_events(source, min_level, strict, utc_offset):
            tagged.append((index, event))
    tagged.sort(key=lambda pair: pair[1].time)
    return tagged
