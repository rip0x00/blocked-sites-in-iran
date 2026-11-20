"""Unit tests for tools/update_lists.py (standard library only, no network).

The pure builder functions are fed small inline fixtures; fetch() and
main() are intentionally not exercised here.

Run: python3 -m unittest discover -s tests -v
"""
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


update = load_module("update_lists", "tools/update_lists.py")

CSV_HEADER = "month,country_code,country_name,domain,measurements,confirmed,anomaly,ok,failures,confirmed_rate"

MINI_CSV = "\n".join([
    CSV_HEADER,
    # older month: must be ignored even though it passes the thresholds
    "2026-09,IR,Iran,www.old-month.com,100,90,5,5,0,0.9",
    # newest month, passing; www. stripped
    "2026-10,IR,Iran,www.example.com,30,27,2,1,0,0.9",
    # same domain without www., fewer measurements: stats keep the 30-row
    "2026-10,IR,Iran,example.com,25,20,3,2,0,0.8",
    # below the measurement threshold
    "2026-10,IR,Iran,too-few.com,19,19,0,0,0,1.0",
    # below the confirmed-rate threshold
    "2026-10,IR,Iran,low-rate.com,40,10,10,20,0,0.25",
    # exactly at both thresholds: included
    "2026-10,IR,Iran,edge-case.org,20,10,5,5,0,0.5",
    # another country: ignored
    "2026-10,US,United States,other-country.com,100,99,0,1,0,0.99",
]) + "\n"

MINI_IR_TXT = "\n".join([
    "# clash rules in text format (comment line, ignored)",
    "+.example.com",
    "+.EXAMPLE.org",          # lowercased
    "example.net",            # no '+.' prefix: ignored
    "+.ir",                   # bare TLD (no dot after stripping): dropped
    "+.example.com",          # duplicate
    "+.sub.example.com",
]) + "\n"

MINI_FOD = "\n".join([
    ".example.com",
    ".example.org",
    "example.com",            # duplicate after dot-stripping
    "",
    ".sub.example.net",
]) + "\n"


class BuildBlockedInIranTests(unittest.TestCase):
    def test_thresholds_www_strip_and_month_selection(self):
        domains, period, stats = update.build_blocked_in_iran(MINI_CSV)
        self.assertEqual(domains, ["edge-case.org", "example.com"])
        self.assertEqual(period, "2026-10")

    def test_stats_keep_row_with_most_measurements(self):
        _, _, stats = update.build_blocked_in_iran(MINI_CSV)
        self.assertEqual(stats["example.com"], (30, 0.9))
        self.assertEqual(stats["edge-case.org"], (20, 0.5))

    def test_empty_source_raises(self):
        with self.assertRaises(update.SourceDataError):
            update.build_blocked_in_iran("")

    def test_no_ir_rows_raises(self):
        csv_text = CSV_HEADER + "\n2026-10,US,United States,x.com,50,50,0,0,0,1.0\n"
        with self.assertRaises(update.SourceDataError):
            update.build_blocked_in_iran(csv_text)

    def test_malformed_csv_missing_columns_raises(self):
        with self.assertRaises(update.SourceDataError):
            update.build_blocked_in_iran("a,b,c\n1,2,3\n")

    def test_malformed_csv_non_numeric_raises(self):
        csv_text = CSV_HEADER + "\n2026-10,IR,Iran,x.com,many,50,0,0,0,high\n"
        with self.assertRaises(update.SourceDataError):
            update.build_blocked_in_iran(csv_text)

    def test_idempotent(self):
        first = update.build_blocked_in_iran(MINI_CSV)
        second = update.build_blocked_in_iran(MINI_CSV)
        self.assertEqual(first, second)


class BuildFromOutsideTests(unittest.TestCase):
    def test_transform(self):
        self.assertEqual(
            update.build_from_outside(MINI_IR_TXT),
            ["example.com", "example.org", "sub.example.com"],
        )

    def test_empty_source(self):
        self.assertEqual(update.build_from_outside(""), [])


class BuildSanctionsTests(unittest.TestCase):
    def test_transform(self):
        self.assertEqual(
            update.build_sanctions(MINI_FOD),
            ["example.com", "example.org", "sub.example.net"],
        )

    def test_empty_source(self):
        self.assertEqual(update.build_sanctions(""), [])


class CheckDeltaTests(unittest.TestCase):
    def test_small_change_passes(self):
        old = [f"d{i}.com" for i in range(100)]
        new = old[:95] + [f"n{i}.com" for i in range(5)]  # 5 removed + 5 added = 10
        added, removed = update.check_delta(old, new)
        self.assertEqual(len(added), 5)
        self.assertEqual(len(removed), 5)

    def test_no_change_passes(self):
        old = ["a.com", "b.com"]
        self.assertEqual(update.check_delta(old, list(old)), ([], []))

    def test_large_change_raises(self):
        old = [f"d{i}.com" for i in range(100)]
        new = [f"x{i}.com" for i in range(40)]  # 100 removed + 40 added = 140 > 25
        with self.assertRaises(update.SourceDataError):
            update.check_delta(old, new)

    def test_large_change_allowed_with_force(self):
        old = [f"d{i}.com" for i in range(100)]
        new = [f"x{i}.com" for i in range(40)]
        added, removed = update.check_delta(old, new, force=True)
        self.assertEqual((len(added), len(removed)), (40, 100))

    def test_empty_old_list_never_raises(self):
        added, removed = update.check_delta([], ["a.com", "b.com"])
        self.assertEqual((len(added), len(removed)), (2, 0))


class DomainsJsonlTests(unittest.TestCase):
    def test_shape(self):
        stats = {"example.com": (30, 0.9)}
        text = update.build_domains_jsonl(stats, "2026-10", "2026-11-20T00:00:00Z")
        import json
        obj = json.loads(text.strip())
        self.assertEqual(obj["domain"], "example.com")
        self.assertEqual(obj["list"], "blocked-in-iran")
        self.assertEqual(obj["status"], "confirmed")
        self.assertEqual(obj["country"], "IR")
        self.assertEqual(obj["data_period"], "2026-10")
        self.assertEqual(obj["measurements"], 30)
        self.assertEqual(obj["confirmed_rate"], 0.9)
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
