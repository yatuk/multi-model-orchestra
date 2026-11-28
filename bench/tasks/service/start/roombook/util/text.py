"""Small text helpers for the reports."""


def render_table(headers, rows, right=()):
    """Plain text table, columns two spaces apart. right: indexes of right-aligned columns."""
    cells = [list(map(str, headers))] + [[str(c) for c in r] for r in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    out = []
    for r in cells:
        parts = []
        for i, c in enumerate(r):
            parts.append(c.rjust(widths[i]) if i in right else c.ljust(widths[i]))
        out.append("  ".join(parts).rstrip())
    return out


def tsv_line(values):
    return "\t".join(clean_cell(v) for v in values)


def clean_cell(value):
    # Tabs and newlines would break the tsv for the scripts that read it.
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def shorten(text, width):
    text = text or ""
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def plural(n, word, many=None):
    if n == 1:
        return f"1 {word}"
    return f"{n} {many or word + 's'}"


def percent(part, whole):
    if not whole:
        return "0%"
    return f"{round(100 * part / whole)}%"
