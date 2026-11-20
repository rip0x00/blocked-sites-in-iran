"""Unit tests for tools/build_dist.py and the sanctions JSONL builder in
tools/update_lists.py (standard library only, no network).

Run: python3 -m unittest discover -s tests -v
"""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dist = load_module("build_dist", "tools/build_dist.py")
update = load_module("update_lists", "tools/update_lists.py")

GENERATED_AT = "2026-11-20T00:00:00Z"

FIXTURE_LISTS = {
    "list.txt": ["a.com", "b.org"],
    "blocked-from-outside.txt": ["c.ir", "d.ir"],
    "blocked-by-sanctions.txt": ["e.com", "f.net", "g.io"],
}

BASES = ["blocked-in-iran", "iran-hosted", "sanctions"]


def build_fixture():
    return dist.build_all(FIXTURE_LISTS, GENERATED_AT)


class BuildAllShapeTests(unittest.TestCase):
    def test_all_25_files_present(self):
        files = build_fixture()
        self.assertEqual(len(files), 25)  # 3 lists x 8 formats + manifest
        for base in BASES:
            for suffix in (
                "json", "csv", "adguard.txt", "dnsmasq.conf",
                "hosts", "clash.yaml", "surge.conf", "sing-box.json",
            ):
                self.assertIn(f"dist/{base}.{suffix}", files)
        self.assertIn("dist/manifest.json", files)

    def test_missing_list_raises(self):
        with self.assertRaises(ValueError):
            dist.build_all({"list.txt": ["a.com"]}, GENERATED_AT)


class FormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = build_fixture()

    def text(self, name):
        return self.files[f"dist/{name}"].decode("utf-8")

    def test_json_array(self):
        self.assertEqual(json.loads(self.text("blocked-in-iran.json")), ["a.com", "b.org"])

    def test_csv(self):
        self.assertEqual(self.text("blocked-in-iran.csv"), "domain\na.com\nb.org\n")

    def test_adguard(self):
        lines = self.text("blocked-in-iran.adguard.txt").splitlines()
        self.assertTrue(lines[0].startswith("! "))
        self.assertTrue(lines[1].startswith("! "))
        self.assertEqual(lines[2:], ["||a.com^", "||b.org^"])

    def test_dnsmasq(self):
        lines = self.text("blocked-in-iran.dnsmasq.conf").splitlines()
        self.assertTrue(lines[0].startswith("# "))
        self.assertTrue(lines[1].startswith("# "))
        self.assertEqual(lines[2:], ["server=/a.com/", "server=/b.org/"])

    def test_hosts(self):
        lines = self.text("blocked-in-iran.hosts").splitlines()
        self.assertTrue(lines[0].startswith("# "))
        self.assertEqual(lines[2:], ["0.0.0.0 a.com", "0.0.0.0 b.org"])

    def test_clash(self):
        lines = self.text("blocked-in-iran.clash.yaml").splitlines()
        self.assertEqual(lines[0], "payload:")
        self.assertEqual(
            lines[1:],
            ["  - 'DOMAIN-SUFFIX,a.com'", "  - 'DOMAIN-SUFFIX,b.org'"],
        )

    def test_surge(self):
        lines = self.text("blocked-in-iran.surge.conf").splitlines()
        self.assertTrue(lines[0].startswith("# "))
        self.assertEqual(lines[2:], ["DOMAIN-SUFFIX,a.com", "DOMAIN-SUFFIX,b.org"])

    def test_sing_box_structure(self):
        obj = json.loads(self.text("blocked-in-iran.sing-box.json"))
        self.assertEqual(obj["version"], 1)
        self.assertEqual(obj["rules"], [{"domain_suffix": ["a.com", "b.org"]}])

    def test_no_timestamps_in_payload_files(self):
        for name, data in self.files.items():
            if name == "dist/manifest.json":
                continue
            self.assertNotIn(GENERATED_AT.encode(), data, name)
            self.assertNotIn(b"2026", data, name)


class ManifestTests(unittest.TestCase):
    def test_manifest_entries_hashes_and_sizes(self):
        files = build_fixture()
        manifest = json.loads(files["dist/manifest.json"].decode("utf-8"))
        self.assertEqual(manifest["generated_at"], GENERATED_AT)
        self.assertEqual(manifest["generator"], "tools/build_dist.py")
        self.assertEqual(len(manifest["files"]), 24)
        self.assertNotIn("manifest.json", manifest["files"])
        for filename, info in manifest["files"].items():
            data = files[f"dist/{filename}"]
            self.assertEqual(info["sha256"], hashlib.sha256(data).hexdigest(), filename)
            self.assertEqual(info["bytes"], len(data), filename)
        self.assertEqual(manifest["files"]["blocked-in-iran.json"]["entries"], 2)
        self.assertEqual(manifest["files"]["sanctions.json"]["entries"], 3)


class DeterminismTests(unittest.TestCase):
    def test_same_inputs_same_bytes(self):
        self.assertEqual(build_fixture(), build_fixture())

    def test_only_manifest_depends_on_generated_at(self):
        a = build_fixture()
        b = dist.build_all(FIXTURE_LISTS, "2030-01-01T00:00:00Z")
        for name in a:
            if name == "dist/manifest.json":
                self.assertNotEqual(a[name], b[name])
            else:
                self.assertEqual(a[name], b[name], name)


class BuildDistOnDiskTests(unittest.TestCase):
    def test_writes_dist_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta_lists = []
            for name, domains in FIXTURE_LISTS.items():
                (root / name).write_text("\n".join(domains) + "\n", encoding="utf-8")
                meta_lists.append({"file": name, "entries": len(domains)})
            (root / "lists.json").write_text(
                json.dumps({"lists": meta_lists}), encoding="utf-8"
            )
            files = dist.build_dist(root, generated_at=GENERATED_AT)
            self.assertEqual(len(files), 25)
            for rel, data in files.items():
                on_disk = (root / rel).read_bytes()
                self.assertEqual(on_disk, data, rel)
            self.assertTrue((root / "dist" / "manifest.json").exists())

    def test_lists_json_count_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, domains in FIXTURE_LISTS.items():
                (root / name).write_text("\n".join(domains) + "\n", encoding="utf-8")
            (root / "lists.json").write_text(
                json.dumps({"lists": [{"file": "list.txt", "entries": 999}]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                dist.build_dist(root, generated_at=GENERATED_AT)


class SanctionsJsonlTests(unittest.TestCase):
    def test_record_shape(self):
        text = update.build_sanctions_jsonl(["a.com", "b.org"], GENERATED_AT)
        lines = text.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(text.endswith("\n"))
        obj = json.loads(lines[0])
        self.assertEqual(
            set(obj),
            {"domain", "list", "status", "direction", "source",
             "source_url", "confidence", "retrieved_at"},
        )
        self.assertEqual(obj["domain"], "a.com")
        self.assertEqual(obj["list"], "sanctions")
        self.assertEqual(obj["status"], "historical")
        self.assertEqual(obj["direction"], "foreign_to_iran")
        self.assertEqual(obj["source"], "freedomofdevelopers/fod")
        self.assertEqual(obj["source_url"], update.FOD_URL)
        self.assertEqual(obj["confidence"], "community-reported")
        self.assertEqual(obj["retrieved_at"], GENERATED_AT)


if __name__ == "__main__":
    unittest.main()
