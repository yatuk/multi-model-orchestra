"""Held-out tests for the service task. The lane never sees this file.

Five groups, one class each, so the detail column says what was done:
  NewBehaviour  cancelled bookings are kept, shown and marked, and free the room (end to end)
  BugFix        double bookings over imported meetings, plus two quieter forms of the same
                cause: series rows (back to back refused, room busy after the end) and rows
                that were imported before the fix
  KeepWorking   behaviour the ticket does not change (pass-to-pass: passes on the starting code)
  LateCancel    the easy-to-miss rule: late cancellations still count in the usage report,
                with the notice period from the settings, measured when the booking was cancelled
  OldData       databases and backup files written by the previous version

Everything runs through the command line (roombook.cli.main.main) or plain sqlite3, so the
tests do not depend on how the lane names its internals. The clock is frozen on Monday
2030-01-07 08:00 unless a test moves it.
"""
import io
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from datetime import datetime
from unittest import mock

import roombook
from roombook import clock
from roombook.cli.main import main

PUBLIC = ["roombook.main", "roombook.open_db", "roombook.load_settings", "roombook.BookingService",
          "roombook.Booking", "roombook.Room", "roombook.clock.freeze", "roombook.clock.unfreeze",
          "roombook.cli.main.main"]

NOW = datetime(2030, 1, 7, 8, 0)
TUE, WED, THU = "2030-01-08", "2030-01-09", "2030-01-10"
CSV_HEADER = "Room;Date;From;To;Organiser;Subject;People\n"

# The schema the previous version (2.3.1) wrote, user_version 2.
V2_SCHEMA = """
CREATE TABLE rooms (code TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT '', capacity INTEGER NOT NULL DEFAULT 4,
    features TEXT NOT NULL DEFAULT '');
CREATE TABLE series (id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
    owner TEXT NOT NULL, weeks INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL REFERENCES rooms(code),
    starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, owner TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'manual', attendees INTEGER NOT NULL DEFAULT 1,
    series_id INTEGER REFERENCES series(id));
CREATE INDEX bookings_room_start ON bookings(room, starts_at);
CREATE TABLE audit (id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, actor TEXT NOT NULL,
    action TEXT NOT NULL, booking_id INTEGER, detail TEXT NOT NULL DEFAULT '');
"""
V1_SCHEMA = """
CREATE TABLE rooms (code TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT '', capacity INTEGER NOT NULL DEFAULT 4);
CREATE TABLE bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL REFERENCES rooms(code),
    starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, owner TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'manual');
"""


class Base(unittest.TestCase):
    make_rooms = True

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="rbh-")
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
        if self.make_rooms:
            self.ok("rooms", "add", "A", "--name", "Atlas", "--capacity", "8", user="root")
            self.ok("rooms", "add", "B", "--capacity", "4", user="root")

    def write_ini(self, extra):
        with open(self.ini, "w", encoding="utf-8") as f:
            f.write("[people]\nadmin = root\ndesk = dana\n" + extra)

    def run_cli(self, *argv, user="alice", db=None):
        out, err = io.StringIO(), io.StringIO()
        code = main(["--db", db or self.db, "--config", self.ini, "--user", user, *argv], out, err)
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv, user="alice", db=None):
        code, out, err = self.run_cli(*argv, user=user, db=db)
        self.assertEqual(code, 0, f"{argv} failed: {out}{err}")
        return out

    def refused(self, *argv, user="alice"):
        code, out, err = self.run_cli(*argv, user=user)
        self.assertNotEqual(code, 0, f"{argv} should be refused: {out}{err}")
        return out + err

    def tsv(self, *argv, db=None):
        lines = self.ok("list", *argv, "--format", "tsv", db=db).splitlines()
        self.assertEqual(lines[0], "id\troom\tstart\tend\towner\ttitle")
        return lines[1:]

    def ids(self, *argv, db=None):
        return [l.split("\t")[0] for l in self.tsv(*argv, db=db)]

    def import_rows(self, *rows):
        path = os.path.join(self.dir, f"import{len(os.listdir(self.dir))}.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(CSV_HEADER + "".join(r + "\n" for r in rows))
        return self.ok("import", path, user="dana")

    def usage(self, month="2030-01"):
        lines = self.ok("usage", month, "--format", "tsv").splitlines()
        header = lines[0].split("\t")
        rows = {}
        for line in lines[1:]:
            cells = line.split("\t")
            rows[cells[0]] = dict(zip(header, cells))
        return header, rows

    def cancelled_count(self, row):
        keys = [k for k in row if "cancel" in k.lower()]
        self.assertTrue(keys, f"no cancellations column in the usage report: {list(row)}")
        return row[keys[0]]

    def status_line(self, at, room="A"):
        out = self.ok("status", "--at", at)
        lines = [l for l in out.splitlines() if l.split() and l.split()[0] == room]
        self.assertEqual(len(lines), 1, out)
        return lines[0]

    def old_db(self, schema, version, bookings, path=None):
        path = path or self.db
        if os.path.exists(path):
            os.remove(path)
        conn = sqlite3.connect(path)
        conn.executescript(schema)
        conn.execute("INSERT INTO rooms(code, name, capacity) VALUES ('A', 'Atlas', 8)")
        conn.execute("INSERT INTO rooms(code, name, capacity) VALUES ('B', '', 4)")
        for b in bookings:
            cols = ", ".join(b)
            conn.execute(f"INSERT INTO bookings({cols}) VALUES ({', '.join('?' * len(b))})", tuple(b.values()))
        conn.execute(f"PRAGMA user_version = {version}")
        conn.commit()
        conn.close()
        return path


class NewBehaviour(Base):
    def test_show_after_cancel_says_cancelled(self):
        self.ok("book", "B", f"{WED} 14:00", "45m", "--title", "Retro")
        self.ok("cancel", "B0001")
        shown = self.ok("show", "B0001")
        self.assertIn("cancelled", shown.lower())
        self.assertIn("Retro", shown)

    def test_show_has_reason_and_who_cancelled(self):
        self.ok("book", "A", f"{WED} 10:00", "1h", "--title", "Budget")
        self.ok("cancel", "B0001", "--reason", "Budget moved to March", user="dana")
        shown = self.ok("show", "B0001")
        self.assertIn("Budget moved to March", shown)
        self.assertIn("dana", shown)

    def test_cancel_without_reason(self):
        self.ok("book", "A", f"{WED} 10:00", "1h")
        self.ok("cancel", "B0001")
        self.assertIn("cancelled", self.ok("show", "B0001").lower())

    def test_cancel_twice_is_an_error(self):
        self.ok("book", "A", f"{WED} 10:00", "1h")
        self.ok("cancel", "B0001")
        text = self.refused("cancel", "B0001")
        self.assertIn("already", text.lower())

    def test_slot_is_free_for_others(self):
        self.ok("book", "A", f"{WED} 10:00", "2h")
        self.ok("cancel", "B0001")
        self.ok("book", "A", f"{WED} 11:00", "30m", user="bob")
        self.ok("book", "A", f"{WED} 10:00", "1h", user="carol")

    def test_free_search_offers_the_slot(self):
        self.ok("book", "A", f"{WED} 09:00", "1h")
        self.ok("cancel", "B0001")
        self.assertEqual(self.ok("free", "A", "--day", WED, "--length", "1h").splitlines(), ["07:00-20:00"])

    def test_status_shows_room_free(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("cancel", "B0001")
        line = self.status_line(f"{TUE} 09:30")
        self.assertNotIn("busy", line)
        self.assertIn("free", line)

    def test_week_listing_marks_only_the_cancelled_one(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "Keep")
        self.ok("book", "B", f"{THU} 15:00", "1h", "--title", "Drop")
        self.ok("cancel", "B0002")
        lines = self.ok("list", "--week", TUE).splitlines()
        keep = [l for l in lines if "B0001" in l]
        drop = [l for l in lines if "B0002" in l]
        self.assertEqual((len(keep), len(drop)), (1, 1), lines)
        self.assertNotIn("[cancelled]", keep[0])
        self.assertIn("[cancelled]", drop[0])

    def test_usage_has_cancellations_column(self):
        self.ok("book", "B", f"{WED} 09:00", "1h")
        self.ok("book", "B", f"{THU} 09:00", "1h")
        self.ok("cancel", "B0001")
        self.ok("cancel", "B0002")
        _, rows = self.usage()
        self.assertEqual(self.cancelled_count(rows["B"]), "2")
        self.assertEqual(self.cancelled_count(rows["A"]), "0")
        self.assertEqual((rows["B"]["bookings"], rows["B"]["hours"]), ("0", "0.0"))

    def test_cancelled_booking_keeps_its_id(self):
        self.ok("book", "A", f"{WED} 09:00", "1h")
        self.ok("cancel", "B0001")
        out = self.ok("book", "A", f"{WED} 09:00", "1h", user="bob")
        self.assertIn("B0002", out)
        self.assertIn("alice", self.ok("show", "B0001"))


class BugFix(Base):
    def test_booking_over_imported_meeting_is_refused(self):
        self.import_rows("A;08.01.2030;09:00;10:00;erin;Board;6")
        text = self.refused("book", "A", f"{TUE} 09:30", "1h")
        self.assertIn("overlaps", text)

    def test_booking_inside_imported_meeting_is_refused(self):
        self.import_rows("B;09.01.2030;9.00;12.00;erin;Workshop;4")
        self.refused("book", "B", f"{WED} 10:00", "30m")

    def test_importing_the_same_file_twice_does_not_duplicate(self):
        self.import_rows("A;08.01.2030;13:00;14:00;erin;Board;6")
        out = self.import_rows("A;08.01.2030;13:00;14:00;erin;Board;6")
        self.assertTrue(out.startswith("imported 0"), out)
        self.assertEqual(len(self.tsv("--day", TUE)), 1)

    def test_room_busy_during_imported_meeting(self):
        self.import_rows("A;08.01.2030;09:00;10:00;erin;Board;6")
        self.assertIn("busy", self.status_line(f"{TUE} 09:30"))

    def test_upcoming_list_in_time_order_with_imported_meetings(self):
        self.ok("book", "A", f"{TUE} 10:00", "1h", "--title", "late")
        self.import_rows("B;08.01.2030;09:00;09:30;alice;early;2")
        lines = self.ok("mine").splitlines()
        self.assertEqual(len(lines), 2, lines)
        self.assertIn("early", lines[0])
        self.assertIn("late", lines[1])

    def test_meetings_imported_before_the_fix_are_protected(self):
        self.old_db(V2_SCHEMA, 2, [
            {"room": "A", "starts_at": "2030-01-08T09:00", "ends_at": "2030-01-08T11:00", "owner": "erin",
             "title": "Board", "source": "import", "attendees": 6},
        ])
        text = self.refused("book", "A", f"{TUE} 10:00", "1h")
        self.assertIn("overlaps", text)

    def test_booking_right_after_a_series_meeting_is_allowed(self):
        self.ok("series", "A", f"{TUE} 09:00", "1h", "--weeks", "2", "--title", "Weekly")
        self.ok("book", "A", f"{TUE} 10:00", "1h", user="bob")
        self.ok("book", "A", "2030-01-15 10:00", "30m", user="bob")

    def test_room_free_when_series_meeting_ends(self):
        self.ok("series", "B", f"{TUE} 09:00", "1h", "--weeks", "2")
        self.assertIn("busy", self.status_line(f"{TUE} 09:59", "B"))
        self.assertNotIn("busy", self.status_line(f"{TUE} 10:00", "B"))


class KeepWorking(Base):
    def test_book_output(self):
        self.assertEqual(self.ok("book", "B", f"{TUE} 11:15", "45m").strip(), f"booked B0001: B {TUE} 11:15-12:00")

    def test_refusal_lists_every_problem(self):
        code, out, err = self.run_cli("book", "B", f"{TUE} 06:00", "5h", "--people", "20")
        self.assertEqual(code, 1)
        self.assertEqual(err.count("refused:"), 3, err)

    def test_past_is_refused(self):
        self.assertIn("passed", self.refused("book", "A", "2030-01-07 07:00", "30m"))

    def test_advance_limit(self):
        self.assertIn("days ahead", self.refused("book", "A", "2030-06-03 09:00", "30m"))

    def test_weekend_warning(self):
        code, out, err = self.run_cli("book", "A", "2030-01-12 10:00", "1h")
        self.assertEqual(code, 0)
        self.assertIn("weekend", err)

    def test_duration_forms(self):
        for i, (dur, end) in enumerate((("1h30", "10:30"), ("1.5h", "12:30"), ("90", "14:30"), ("1:15", "17:15"))):
            start = ("09:00", "11:00", "13:00", "16:00")[i]
            out = self.ok("book", "A", f"{TUE} {start}", dur)
            self.assertIn(f"{start}-{end}", out)

    def test_booking_for_someone_needs_desk(self):
        code, _, _ = self.run_cli("book", "A", f"{TUE} 09:00", "1h", "--for", "bob")
        self.assertEqual(code, 4)
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--for", "bob", user="dana")
        self.assertIn("owner:     bob", self.ok("show", "B0001"))

    def test_staff_cannot_cancel_others(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        code, _, _ = self.run_cli("cancel", "B0001", user="bob")
        self.assertEqual(code, 4)
        self.refused("book", "A", f"{TUE} 09:00", "1h", user="carol")

    def test_cancel_unknown_id(self):
        code, out, err = self.run_cli("cancel", "B0042")
        self.assertEqual(code, 3)
        self.assertIn("no such booking", err)

    def test_late_cancel_note(self):
        self.ok("book", "A", "2030-01-07 15:00", "1h")
        self.ok("book", "A", f"{THU} 15:00", "1h")
        self.assertIn("late cancellation", self.ok("cancel", "B0001"))
        self.assertNotIn("late", self.ok("cancel", "B0002"))

    def test_week_tsv_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "one")
        self.ok("book", "B", f"{WED} 09:00", "1h", "--title", "two")
        self.ok("book", "A", f"{THU} 09:00", "1h", "--title", "three")
        self.ok("cancel", "B0002")
        self.assertEqual(self.tsv("--week", WED), [
            "B0001\tA\t2030-01-08 09:00\t2030-01-08 10:00\talice\tone",
            "B0003\tA\t2030-01-10 09:00\t2030-01-10 10:00\talice\tthree",
        ])

    def test_tsv_room_filter_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "A", f"{TUE} 11:00", "1h")
        self.ok("book", "B", f"{TUE} 11:00", "1h")
        self.ok("cancel", "B0001")
        self.assertEqual(self.ids("--day", TUE, "--room", "a"), ["B0002"])

    def test_finance_export_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "B", f"{WED} 14:00", "30m", user="bob")
        self.ok("cancel", "B0001")
        self.assertEqual(self.ok("export", "--week", TUE).splitlines(), [
            "booking,room,date,from,to,owner,minutes",
            "B0002,B,2030-01-09,14:00,14:30,bob,30",
        ])

    def test_mine_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "gone")
        self.ok("book", "A", f"{WED} 09:00", "1h", "--title", "stays")
        self.ok("cancel", "B0001")
        lines = self.ok("mine").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("stays", lines[0])

    def test_calendar_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "gone")
        self.ok("book", "A", f"{WED} 09:00", "1h", "--title", "stays")
        self.ok("cancel", "B0001")
        feed = self.ok("calendar", "A", "--week", TUE)
        self.assertEqual(feed.count("BEGIN:VEVENT"), 1)
        self.assertIn("SUMMARY:stays", feed)
        self.assertIn("DTSTART:20300109T090000", feed)

    def test_digest_skips_cancelled(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "A", f"{TUE} 10:00", "1h")
        self.ok("cancel", "B0001")
        lines = self.ok("digest", "--day", TUE).splitlines()
        self.assertIn("  A      1 booking, 1h booked, 10:00-11:00", lines)
        self.assertIn("  B      free all day", lines)

    def test_doctor_clean_after_rebooking_a_cancelled_slot(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("cancel", "B0001")
        self.ok("book", "A", f"{TUE} 09:00", "1h", user="bob")
        self.assertEqual(self.ok("doctor").strip(), "no problems found")

    def test_quota_ignores_cancelled(self):
        self.write_ini("[policy]\nweekly_quota_hours = 2\n")
        self.ok("book", "A", f"{TUE} 09:00", "2h")
        self.assertIn("limit is 2h", self.refused("book", "B", f"{WED} 09:00", "1h"))
        self.ok("cancel", "B0001")
        self.ok("book", "B", f"{WED} 09:00", "2h")

    def test_series_skips_conflicts(self):
        self.ok("book", "A", "2030-01-15 09:30", "30m", user="bob")
        out = self.ok("series", "A", f"{TUE} 09:00", "1h", "--weeks", "3")
        self.assertIn("2 bookings created", out)
        self.assertIn("skipped 2030-01-15 09:00: overlaps B0001", out)

    def test_series_blocks_overlap(self):
        self.ok("series", "A", f"{TUE} 09:00", "1h", "--weeks", "2")
        self.refused("book", "A", "2030-01-15 09:30", "1h", user="bob")

    def test_move(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "A", f"{TUE} 12:00", "1h", user="bob")
        self.assertEqual(self.ok("move", "B0001", f"{TUE} 10:00").strip(), f"moved B0001 to {TUE} 10:00-11:00")
        self.assertIn("overlaps B0002", self.refused("move", "B0001", f"{TUE} 11:30"))
        self.ok("move", "B0001", f"{TUE} 13:00", "--length", "30m")

    def test_import_reports_bad_lines(self):
        out = self.import_rows("A;08.01.2030;09:00;10:00;erin;ok;", "Z;08.01.2030;09:00;10:00;erin;x;1",
                               "B;08.01.2030;9-00;10:00;erin;x;1")
        lines = out.splitlines()
        self.assertEqual(lines[0], "imported 1, skipped 2")
        self.assertIn("  line 3: unknown room Z", lines)
        self.assertTrue(any(l.startswith("  line 4: bad time") for l in lines), lines)

    def test_import_needs_desk(self):
        path = os.path.join(self.dir, "x.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(CSV_HEADER + "A;08.01.2030;09:00;10:00;erin;ok;1\n")
        code, _, _ = self.run_cli("import", path)
        self.assertEqual(code, 4)

    def test_backup_restore_round_trip(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h", "--title", "one")
        self.ok("series", "B", f"{WED} 09:00", "1h", "--weeks", "2", "--title", "two", user="bob")
        before = self.tsv("--from", TUE, "--to", "2030-01-20")
        path = os.path.join(self.dir, "backup.json")
        self.ok("backup", path)
        other = os.path.join(self.dir, "other.sqlite3")
        self.ok("restore", path, user="root", db=other)
        self.assertEqual(self.tsv("--from", TUE, "--to", "2030-01-20", db=other), before)

    def test_audit_log_records_cancel(self):
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("cancel", "B0001", user="dana")
        log = self.ok("log", "--id", "B0001").splitlines()
        self.assertEqual(len(log), 2, log)
        self.assertIn("cancel", log[1])
        self.assertIn("dana", log[1])

    def test_outbox_message_when_desk_cancels(self):
        box = os.path.join(self.dir, "outbox")
        self.write_ini(f"[notify]\noutbox_dir = {box}\n")
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("cancel", "B0001", user="dana")
        files = os.listdir(box)
        self.assertEqual(len(files), 1)
        with open(os.path.join(box, files[0]), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("To: alice", text)
        self.assertIn("cancelled by dana", text)

    def test_rooms_list(self):
        self.assertEqual(self.ok("rooms", "list").splitlines(), [
            "code  name   capacity  features", "A     Atlas         8", "B                   4"])

    def test_free_today_starts_after_now(self):
        clock.freeze(datetime(2030, 1, 7, 8, 7))
        self.assertEqual(self.ok("free", "A", "--day", "today").splitlines(), ["08:15-20:00"])


class LateCancel(Base):
    def test_late_cancel_still_counts(self):
        self.ok("book", "A", "2030-01-07 14:00", "2h")
        self.ok("cancel", "B0001")
        _, rows = self.usage()
        self.assertEqual((rows["A"]["bookings"], rows["A"]["hours"]), ("1", "2.0"))
        self.assertEqual(self.cancelled_count(rows["A"]), "1")

    def test_early_cancel_does_not_count(self):
        self.ok("book", "A", f"{THU} 14:00", "2h")
        self.ok("cancel", "B0001")
        _, rows = self.usage()
        self.assertEqual((rows["A"]["bookings"], rows["A"]["hours"]), ("0", "0.0"))
        self.assertEqual(self.cancelled_count(rows["A"]), "1")

    def test_notice_period_from_settings_file(self):
        self.write_ini("[policy]\nlate_cancel_hours = 72\n")
        self.ok("book", "B", f"{WED} 10:00", "1h")      # 50 hours ahead
        self.ok("cancel", "B0001")
        _, rows = self.usage()
        self.assertEqual((rows["B"]["bookings"], rows["B"]["hours"]), ("1", "1.0"))

    def test_notice_period_from_environment(self):
        os.environ["ROOMBOOK_LATE_CANCEL_HOURS"] = "2"
        self.ok("book", "B", "2030-01-07 14:00", "1h")  # 6 hours ahead
        self.ok("cancel", "B0001")
        _, rows = self.usage()
        self.assertEqual((rows["B"]["bookings"], rows["B"]["hours"]), ("0", "0.0"))
        self.assertEqual(self.cancelled_count(rows["B"]), "1")

    def test_lateness_is_measured_when_cancelled(self):
        self.ok("book", "A", f"{THU} 10:00", "1h")      # cancelled early
        self.ok("book", "B", "2030-01-07 12:00", "1h")  # cancelled late
        self.ok("cancel", "B0001")
        self.ok("cancel", "B0002")
        clock.freeze(datetime(2030, 1, 20, 9, 0))      # the report is run long after both
        _, rows = self.usage()
        self.assertEqual((rows["A"]["bookings"], rows["A"]["hours"]), ("0", "0.0"))
        self.assertEqual((rows["B"]["bookings"], rows["B"]["hours"]), ("1", "1.0"))

    def test_mixed_month(self):
        self.ok("book", "B", f"{TUE} 09:00", "1h")      # stays
        self.ok("book", "B", "2030-01-07 16:00", "1h")  # cancelled late
        self.ok("book", "B", f"{THU} 09:00", "1h")      # cancelled early
        self.ok("cancel", "B0002")
        self.ok("cancel", "B0003")
        _, rows = self.usage()
        self.assertEqual((rows["B"]["bookings"], rows["B"]["hours"]), ("2", "2.0"))
        self.assertEqual(self.cancelled_count(rows["B"]), "2")


class OldData(Base):
    make_rooms = False

    def v2_rows(self):
        return [
            {"room": "A", "starts_at": "2030-01-08 09:00", "ends_at": "2030-01-08 10:00", "owner": "alice",
             "title": "Planning", "source": "manual", "attendees": 3},
            {"room": "B", "starts_at": "2030-01-09 13:00", "ends_at": "2030-01-09 14:00", "owner": "bob",
             "title": "Review", "source": "manual", "attendees": 2},
        ]

    def test_v2_database_lists_and_cancels(self):
        self.old_db(V2_SCHEMA, 2, self.v2_rows())
        self.assertEqual(self.ids("--week", TUE), ["B0001", "B0002"])
        self.ok("cancel", "B0001")
        self.assertIn("cancelled", self.ok("show", "B0001").lower())
        self.assertEqual(self.ids("--week", TUE), ["B0002"])

    def test_v2_database_upgrade_is_kept(self):
        self.old_db(V2_SCHEMA, 2, self.v2_rows())
        self.ok("cancel", "B0002", user="bob")
        self.ok("book", "B", f"{WED} 13:00", "1h")
        self.assertIn("cancelled", self.ok("show", "B0002").lower())
        self.assertEqual(self.ids("--week", TUE), ["B0001", "B0003"])
        self.assertNotIn("cancelled", self.ok("show", "B0001").lower())

    def test_v1_database_still_opens(self):
        self.old_db(V1_SCHEMA, 1, [{"room": "A", "starts_at": "2030-01-08 09:00", "ends_at": "2030-01-08 10:00",
                                    "owner": "alice", "title": "Old", "source": "manual"}])
        self.assertEqual(self.ids("--day", TUE), ["B0001"])
        self.refused("book", "A", f"{TUE} 09:30", "1h", user="bob")
        self.ok("book", "A", f"{TUE} 10:00", "1h", user="bob")

    def write_json(self, data):
        path = os.path.join(self.dir, "old-backup.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_restore_format1_backup(self):
        path = self.write_json({"version": 1, "rooms": [{"code": "A", "name": "Atlas", "capacity": 8}],
                                "items": [{"id": 7, "room": "A", "from": "2030-01-08 09:00", "to": "2030-01-08 10:00",
                                           "who": "alice", "what": "Kiosk era"}]})
        self.ok("restore", path, user="root")
        self.assertEqual(self.ids("--day", TUE), ["B0007"])
        self.refused("book", "A", f"{TUE} 09:30", "1h", user="bob")

    def test_restore_format2_backup(self):
        path = self.write_json({
            "format": 2, "written": "2029-12-20 10:00",
            "rooms": [{"code": "A", "name": "Atlas", "capacity": 8, "features": ["screen"]}],
            "series": [],
            "bookings": [{"id": 3, "room": "A", "start": "2030-01-08 09:00", "end": "2030-01-08 10:00",
                          "owner": "alice", "title": "Two", "source": "manual", "attendees": 2, "series_id": None}]})
        self.ok("restore", path, user="root")
        self.assertEqual(self.ids("--day", TUE), ["B0003"])
        self.assertNotIn("cancelled", self.ok("show", "B0003").lower())
        self.refused("book", "A", f"{TUE} 09:30", "1h", user="bob")

    def test_backup_keeps_cancellation(self):
        self.ok("rooms", "add", "A", user="root")
        self.ok("book", "A", f"{TUE} 09:00", "1h")
        self.ok("book", "A", f"{TUE} 11:00", "1h")
        self.ok("cancel", "B0001", "--reason", "Holiday")
        path = os.path.join(self.dir, "new-backup.json")
        self.ok("backup", path)
        other = os.path.join(self.dir, "other.sqlite3")
        self.ok("restore", path, user="root", db=other)
        shown = self.ok("show", "B0001", db=other)
        self.assertIn("cancelled", shown.lower())
        self.assertIn("Holiday", shown)
        self.assertEqual(self.ids("--day", TUE, db=other), ["B0002"])

    def test_backup_of_a_v2_database(self):
        self.old_db(V2_SCHEMA, 2, self.v2_rows())
        path = os.path.join(self.dir, "b.json")
        self.ok("backup", path)
        other = os.path.join(self.dir, "other.sqlite3")
        self.ok("restore", path, user="root", db=other)
        self.assertEqual(self.ids("--week", TUE, db=other), ["B0001", "B0002"])


if __name__ == "__main__":
    unittest.main()
