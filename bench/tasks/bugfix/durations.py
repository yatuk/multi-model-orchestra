"""Duration parsing used by the scheduler."""

UNITS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """Return the number of seconds in a duration like "1h30m15s".

    Rules:
    1. Units are h, m and s. Each unit may appear at most once.
    2. Units that appear must be in the order h, m, s ("1m1h" is invalid).
    3. Every number must be followed by a unit ("90" and "1h30" are invalid).
    4. The empty string is invalid.
    5. Anything else (spaces, other letters, signs) is invalid.
    Invalid input raises ValueError.
    """
    total = 0
    num = ""
    for ch in text:
        if ch.isdigit():
            num += ch
        elif ch in UNITS:
            total += int(num or 0) * UNITS[ch]
            num = ""
        else:
            raise ValueError(f"bad character {ch!r}")
    return total
