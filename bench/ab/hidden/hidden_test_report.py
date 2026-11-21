import inspect
import random
import subprocess
import sys
import unittest
from pathlib import Path

import report
from report import format_cents, group_totals, rank, summarize

HERE = Path(__file__).parent


def reference(orders):
    totals, counts = {}, {}
    for o in orders:
        if o["status"] == "cancelled":
            continue
        sign = -1 if o["status"] == "refunded" else 1
        totals[o["customer"]] = totals.get(o["customer"], 0) + sign * o["amount"]
        counts[o["customer"]] = counts.get(o["customer"], 0) + 1
    names = sorted(totals, key=lambda n: (-totals[n], n))

    def fmt(c):
        s = "-" if c < 0 else ""
        c = abs(c)
        return f"{s}{c // 100}.{c % 100:02d}"

    lines = [f"{n}: {fmt(totals[n])} ({counts[n]} orders)" for n in names]
    lines.append("TOTAL: " + fmt(sum(totals.values())))
    return "\n".join(lines)


class HiddenReport(unittest.TestCase):
    def test_same_output_random(self):
        rnd = random.Random(7)
        for _ in range(300):
            orders = [
                {"customer": rnd.choice("abcde"), "amount": rnd.randint(0, 5000),
                 "status": rnd.choice(["paid", "paid", "refunded", "cancelled"])}
                for _ in range(rnd.randint(0, 12))
            ]
            self.assertEqual(summarize(orders), reference(orders))

    def test_group_totals(self):
        orders = [
            {"customer": "x", "amount": 500, "status": "paid"},
            {"customer": "x", "amount": 200, "status": "refunded"},
            {"customer": "y", "amount": 100, "status": "cancelled"},
        ]
        self.assertEqual(group_totals(orders), {"x": (300, 2)})

    def test_rank(self):
        self.assertEqual(rank({"b": (5, 1), "a": (5, 3), "c": (9, 1), "d": (-1, 1)}), ["c", "a", "b", "d"])

    def test_format_cents(self):
        self.assertEqual(format_cents(0), "0.00")
        self.assertEqual(format_cents(7), "0.07")
        self.assertEqual(format_cents(-305), "-3.05")
        self.assertEqual(format_cents(123456), "1234.56")

    def test_summarize_is_short(self):
        src = inspect.getsource(report.summarize)
        body = [l for l in src.splitlines()[1:] if l.strip() and not l.strip().startswith("#")]
        self.assertLessEqual(len(body), 12, "summarize should delegate to the helpers")

    def test_new_tests_added(self):
        path = HERE / "test_report_parts.py"
        self.assertTrue(path.exists(), "test_report_parts.py was not added")
        r = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_report_parts"],
                           cwd=HERE, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertGreaterEqual(r.stderr.count(" ... ok"), 3)


if __name__ == "__main__":
    unittest.main()
