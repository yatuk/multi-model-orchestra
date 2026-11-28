"""Tests for roombook. Run: python -m unittest test_roombook

Every test runs the command line against a fresh database in a temporary folder, with the
clock frozen on Monday 2030-01-07 08:00.
"""
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest import mock

from roombook import clock
from roombook.cli.main import main

NOW = datetime(2030, 1, 7, 8, 0)
TUE = "2030-01-08"


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="rb-")
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.db = os.path.join(self.dir, "rb.sqlite3")
        self.ini = os.path.join(self.dir, "rb.ini")
        self.write_ini("")
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        for key in [k for k in os.environ if k.startswith("ROOMBOOK_")]:
            del os.environ[key]
        clock.freeze(NOW)
        self.addCleanup(clock.unfreeze)
        self.ok("rooms", "add", "A", "--name", "Atlas", "--capacity", "8", user="root")
        self.ok("rooms", "add", "B", "--capacity", "4", user="root")

    def write_ini(self, extra):
        with open(self.ini, "w", encoding="utf-8") as f:
            f.write("[people]\nadmin = root\ndesk = dana\n" + extra)

    def run_cli(self, *argv, user="alice"):
        out, err = io.StringIO(), io.StringIO()
        code = main(["--db", self.db, "--config", self.ini, "--user", user, *argv], out, err)
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv, user="alice"):
        code, out, err = self.run_cli(*argv, user=user)
        self.assertEqual(code, 0, f"{argv} failed: {out}{err}")
        return out


class Booking(Base):
    def test_book_and_show(self):
        out = self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Planning")
        self.assertEqual(out.strip(), f"booked B0001: A {TUE} 09:00-10:00")
        shown = self.ok("show", "B0001")
        self.assertIn("owner:     alice", shown)
        self.assertIn("title:     Planning", shown)

    def test_conflict_is_refused(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        code, out, err = self.run_cli("book", "A", f"{TUE} 09:30", "1h", user="bob")
        self.assertEqual(code, 1)
        self.assertIn("overlaps B0001", err)


class Listing(Base):
    def test_day_listing_text(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Planning")
        self.ok("book", "B", f"{TUE} 08:30", "30m", "--title", "Standup", user="bob")
        out = self.ok("list", "--day", TUE)
        self.assertEqual(out.splitlines(), [
            "Tue 2030-01-08",
            "  08:30-09:00  B      B0002  bob        Standup",
            "  09:00-10:00  A      B0001  alice      Planning",
        ])

    def test_tsv_listing_for_scripts(self):
        # The door screens and the cleaning rota read this; its shape does not change.
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Planning")
        self.ok("book", "A", f"{TUE} 11:00", "30m", "--title", "Review", user="bob")
        self.ok("book", "B", f"{TUE} 10:00", "1h", "--title", "1:1")
        self.ok("cancel", "B0002", user="bob")
        out = self.ok("list", "--day", TUE, "--format", "tsv")
        self.assertEqual(out.splitlines(), [
            "id\troom\tstart\tend\towner\ttitle",
            "B0001\tA\t2030-01-08 09:00\t2030-01-08 10:00\talice\tPlanning",
            "B0003\tB\t2030-01-08 10:00\t2030-01-08 11:00\talice\t1:1",
        ])


class Cancel(Base):
    def test_cancelled_slot_can_be_booked_again(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("cancel", "B0001")
        self.ok("book", "A", f"{TUE} 09:00", "1h", user="bob")

    def test_show_says_cancelled_with_reason(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Planning")
        self.ok("cancel", "B0001", "--reason", "Team offsite")
        shown = self.ok("show", "B0001")
        self.assertIn("cancelled", shown)
        self.assertIn("Team offsite", shown)

    def test_listing_marks_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Planning")
        self.ok("cancel", "B0001")
        lines = [l for l in self.ok("list", "--day", TUE).splitlines() if "B0001" in l]
        self.assertEqual(len(lines), 1)
        self.assertIn("[cancelled]", lines[0])


class Import(Base):
    def test_import_happy_path(self):
        path = os.path.join(self.dir, "facilities.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Room;Date;From;To;Organiser;Subject;People\n"
                    "A;08.01.2030;09:00;10:30;erin;Board;6\n"
                    "B;09.01.2030;14:00;15:00;frank;Interview;2\n")
        out = self.ok("import", path, user="dana")
        self.assertEqual(out.splitlines()[0], "imported 2, skipped 0")
        listing = self.ok("list", "--from", TUE, "--to", "2030-01-09", "--format", "tsv")
        self.assertIn("Board", listing)
        self.assertIn("Interview", listing)


class Free(Base):
    def test_free_windows(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        out = self.ok("free", "A", "--day", TUE, "--length", "1h")
        self.assertEqual(out.splitlines(), ["07:00-09:00", "10:00-20:00"])


class Usage(Base):
    def test_usage_counts_hours(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "A", f"{TUE} 13:00", "30m")
        out = self.ok("usage", "2030-01", "--format", "tsv").splitlines()
        header = out[0].split("\t")
        rows = {l.split("\t")[0]: dict(zip(header, l.split("\t"))) for l in out[1:]}
        self.assertEqual(rows["A"]["bookings"], "2")
        self.assertEqual(rows["A"]["hours"], "1.5")
        self.assertEqual(rows["B"]["bookings"], "0")


if __name__ == "__main__":
    unittest.main()
