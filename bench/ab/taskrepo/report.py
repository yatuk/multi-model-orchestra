"""Order report. Works, but is one long function."""


def summarize(orders):
    # orders: list of dicts with keys customer, amount (cents, int), status
    lines = []
    totals = {}
    counts = {}
    for o in orders:
        if o["status"] == "cancelled":
            continue
        if o["status"] == "refunded":
            if o["customer"] in totals:
                totals[o["customer"]] = totals[o["customer"]] - o["amount"]
            else:
                totals[o["customer"]] = 0 - o["amount"]
            if o["customer"] in counts:
                counts[o["customer"]] = counts[o["customer"]] + 1
            else:
                counts[o["customer"]] = 1
            continue
        if o["customer"] in totals:
            totals[o["customer"]] = totals[o["customer"]] + o["amount"]
        else:
            totals[o["customer"]] = o["amount"]
        if o["customer"] in counts:
            counts[o["customer"]] = counts[o["customer"]] + 1
        else:
            counts[o["customer"]] = 1
    names = list(totals.keys())
    for i in range(len(names)):
        for j in range(len(names) - 1 - i):
            a, b = names[j], names[j + 1]
            if totals[a] < totals[b] or (totals[a] == totals[b] and a > b):
                names[j], names[j + 1] = names[j + 1], names[j]
    grand = 0
    for n in names:
        t = totals[n]
        grand = grand + t
        sign = "-" if t < 0 else ""
        t = abs(t)
        lines.append(n + ": " + sign + str(t // 100) + "." + str(t % 100).zfill(2) + " (" + str(counts[n]) + " orders)")
    sign = "-" if grand < 0 else ""
    g = abs(grand)
    lines.append("TOTAL: " + sign + str(g // 100) + "." + str(g % 100).zfill(2))
    return "\n".join(lines)
