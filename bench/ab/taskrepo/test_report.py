import unittest

from report import summarize


ORDERS = [
    {"customer": "bo", "amount": 1250, "status": "paid"},
    {"customer": "al", "amount": 999, "status": "paid"},
    {"customer": "bo", "amount": 50, "status": "cancelled"},
    {"customer": "al", "amount": 300, "status": "refunded"},
]


class TestReport(unittest.TestCase):
    def test_summary(self):
        self.assertEqual(
            summarize(ORDERS),
            "bo: 12.50 (1 orders)\nal: 6.99 (2 orders)\nTOTAL: 19.49",
        )

    def test_empty(self):
        self.assertEqual(summarize([]), "TOTAL: 0.00")


if __name__ == "__main__":
    unittest.main()
