"""Unit tests for tools/validate_lists.py (standard library only).

Run: python3 -m unittest discover -s tests -v
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate = load_module("validate_lists", "tools/validate_lists.py")


class ValidDomainTests(unittest.TestCase):
    def test_valid_domains(self):
        for name in ["example.com", "sub.example.co.uk", "a-b.example.org",
                     "xn--mgba3a4f16a.ir", "a.io"]:
            self.assertTrue(validate.valid_domain(name), name)

    def test_scheme_is_invalid(self):
        self.assertFalse(validate.valid_domain("https://example.com"))

    def test_path_is_invalid(self):
        self.assertFalse(validate.valid_domain("example.com/some/path"))

    def test_wildcard_is_invalid(self):
        self.assertFalse(validate.valid_domain("*.example.com"))

    def test_too_long_is_invalid(self):
        self.assertFalse(validate.valid_domain("a" * 250 + ".com"))  # 254 chars
        self.assertTrue(validate.valid_domain("a" * 249 + ".com"))   # 253 chars

    def test_uppercase_is_invalid(self):
        self.assertFalse(validate.valid_domain("Example.com"))

    def test_whitespace_is_invalid(self):
        self.assertFalse(validate.valid_domain(" example.com"))
        self.assertFalse(validate.valid_domain("example.com "))

    def test_bare_tld_is_invalid(self):
        self.assertFalse(validate.valid_domain("com"))


class CheckFileTests(unittest.TestCase):
    def check(self, text: str) -> list:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "list.txt"
            path.write_bytes(text.encode("utf-8"))
            return validate.check_file(path)

    def test_clean_file_passes(self):
        self.assertEqual(self.check("example.com\nexample.org\n"), [])

    def test_blank_line(self):
        errors = self.check("example.com\n\nexample.org\n")
        self.assertTrue(any("blank line" in e for e in errors), errors)

    def test_duplicate(self):
        errors = self.check("example.com\nexample.com\n")
        self.assertTrue(any("duplicate" in e for e in errors), errors)

    def test_unsorted(self):
        errors = self.check("example.org\nexample.com\n")
        self.assertTrue(any("alphabetical" in e for e in errors), errors)

    def test_missing_trailing_newline(self):
        errors = self.check("example.com")
        self.assertTrue(any("newline" in e for e in errors), errors)

    def test_uppercase_line(self):
        errors = self.check("Example.com\n")
        self.assertTrue(any("lowercase" in e for e in errors), errors)

    def test_leading_whitespace_line(self):
        errors = self.check(" example.com\n")
        self.assertTrue(any("whitespace" in e for e in errors), errors)

    def test_scheme_line(self):
        errors = self.check("https://example.com\n")
        self.assertTrue(any("not a valid bare domain" in e for e in errors), errors)

    def test_wildcard_line(self):
        errors = self.check("*.example.com\n")
        self.assertTrue(any("not a valid bare domain" in e for e in errors), errors)

    def test_empty_file(self):
        errors = self.check("")
        self.assertTrue(any("empty" in e for e in errors), errors)


class ListsJsonCountTests(unittest.TestCase):
    """The count check lives in validate_lists.main(); exercise it by
    pointing the module's ROOT at a scratch tree."""

    def run_main(self, declared_entries: int) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "list.txt").write_text("example.com\nexample.org\n", encoding="utf-8")
            (root / "blocked-from-outside.txt").write_text("example.ir\n", encoding="utf-8")
            (root / "blocked-by-sanctions.txt").write_text("example.net\n", encoding="utf-8")
            meta = {"lists": [
                {"file": "list.txt", "entries": declared_entries},
                {"file": "blocked-from-outside.txt", "entries": 1},
                {"file": "blocked-by-sanctions.txt", "entries": 1},
            ]}
            (root / "lists.json").write_text(json.dumps(meta), encoding="utf-8")
            old_root, old_argv = validate.ROOT, sys.argv
            try:
                validate.ROOT = root
                sys.argv = ["validate_lists.py"]
                return validate.main()
            finally:
                validate.ROOT, sys.argv = old_root, old_argv

    def test_matching_counts_pass(self):
        self.assertEqual(self.run_main(2), 0)

    def test_mismatched_count_fails(self):
        self.assertEqual(self.run_main(99), 1)


if __name__ == "__main__":
    unittest.main()
