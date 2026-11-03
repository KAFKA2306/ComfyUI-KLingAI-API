"""消失、競合、故障時にデータを守れることを検証する。"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gwp.state import atomic_save, empty_catalog, health, load_catalog, merge_catalog, restore
from gwp.discovery import extract_png_workflow, record_file, discover_github


class CatalogDurabilityTests(unittest.TestCase):
    def test_atomic_update_backup_corruption_restore(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "registry.json"
            original = empty_catalog()
            original["artifacts"]["id-a"] = {"id": "id-a", "revisions": []}
            atomic_save(file, original)
            changed = load_catalog(file)
            changed["artifacts"]["id-b"] = {"id": "id-b", "revisions": []}
            atomic_save(file, changed)
            backup = Path(str(file) + ".bak")
            self.assertTrue(backup.exists())
            self.assertEqual(len(load_catalog(backup)["artifacts"]), 1)
            file.write_bytes(b'{"broken"')
            with self.assertRaises(ValueError):
                load_catalog(file)
            # 破損した本体を上書きできないなら、まず破損を隔離して復旧する。
            corrupt = file.with_suffix(".corrupt")
            file.rename(corrupt)
            Path(str(file) + ".sha256").unlink()
            restore(file, backup)
            self.assertEqual(set(load_catalog(file)["artifacts"]), {"id-a"})

    def test_optimistic_conflict_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "registry.json"
            atomic_save(file, empty_catalog())
            with self.assertRaises(RuntimeError):
                atomic_save(file, empty_catalog(), expected_sha256="a" * 64)

    def test_multi_machine_merge_keeps_origins_revisions_and_counts(self):
        a, b = empty_catalog(), empty_catalog()
        record_file(a, "alice/workflows", "1" * 40,
                    {"path": "x.json", "sha": "a" * 40}, "2026-11-01")
        record_file(b, "alice/workflows", "2" * 40,
                    {"path": "x.json", "sha": "b" * 40}, "2026-11-02")
        record_file(b, "bob/workflows", "3" * 40,
                    {"path": "y.json", "sha": "b" * 40}, "2026-11-02")
        merged = merge_catalog(a, b)
        self.assertEqual(len(merged["artifacts"]), 2)
        item = merged["artifacts"]["github:alice/workflows:x.json"]
        self.assertEqual(item["blob_sha"], "b" * 40)
        self.assertEqual(len(item["revisions"]), 2)
        self.assertEqual(len(merged["content_index"]["b" * 40]), 2)
        self.assertEqual(health(merged, a)["status"], "ok")

    def test_concurrent_merge_keeps_success_timestamp_and_sha_together(self):
        older, newer = empty_catalog(), empty_catalog()
        older["repositories"]["a/b"] = {
            "repo": "a/b", "last_scanned_at": "2026-11-03T12:00:00Z",
            "last_success_at": "2026-11-03T12:00:00Z",
            "last_success_sha": "f" * 40}
        newer["repositories"]["a/b"] = {
            "repo": "a/b", "last_scanned_at": "2026-11-03T12:05:00Z",
            "last_success_at": "2026-11-03T12:05:00Z",
            "last_success_sha": "0" * 40}
        for first, second in ((older, newer), (newer, older)):
            merged = merge_catalog(first, second)["repositories"]["a/b"]
            self.assertEqual(
                (merged["last_success_at"], merged["last_success_sha"]),
                ("2026-11-03T12:05:00Z", "0" * 40))

    def test_concurrent_merge_keeps_both_search_overflow_warnings(self):
        left, right = empty_catalog(), empty_catalog()
        key = "github-search:comfyui"
        left["search_progress"][key] = {
            "overflows": ["created:2026-11-01"], "pending": []}
        right["search_progress"][key] = {
            "overflows": ["created:2026-11-02"], "pending": []}
        for first, second in ((left, right), (right, left)):
            merged = merge_catalog(first, second)
            self.assertEqual(
                set(merged["search_progress"][key]["overflows"]),
                {"created:2026-11-01", "created:2026-11-02"})

    def test_migrate_old_schema_without_removing_candidates(self):
        before = {"schema_version": 1, "artifacts": {"old": {"id": "old", "revisions": []}}}
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "registry.json"
            file.write_text(json.dumps(before), encoding="utf-8")
            loaded = load_catalog(file)
            self.assertEqual(loaded["schema_version"], 2)
            self.assertIn("old", loaded["artifacts"])
            self.assertIn("events", loaded)

    def test_missing_old_ids_detected(self):
        old = empty_catalog()
        old["artifacts"]["lost"] = {"id": "lost"}
        self.assertEqual(health(empty_catalog(), old)["status"], "data-loss-detected")


class DiscoveryRecoveryTests(unittest.TestCase):
    def test_png_workflow_metadata(self):
        import struct
        import zlib

        def chunk(kind, payload):
            packet = kind + payload
            return struct.pack(">I", len(payload)) + packet + struct.pack(">I", zlib.crc32(packet))
        payload = json.dumps({"nodes": [{"type": "KSampler"}]}).encode("utf-8")
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"tEXt", b"workflow\x00" + payload) + chunk(b"IEND", b"")
        self.assertEqual(extract_png_workflow(png)["nodes"][0]["type"], "KSampler")

    def test_search_1000_limit_partitions_and_resumes(self):
        catalog = empty_catalog()
        called = []

        class API:
            def json(self, url):
                called.append(url)
                if "2008-01-01" in url and ".." in url and "2026-" in url:
                    return {"total_count": 1001, "items": []}
                return {"total_count": 1, "items": [
                    {"full_name": "alice/one", "html_url": "https://github.com/alice/one"}]}

        discover_github(API(), catalog, ["comfyui workflow"], pages=2)
        state = catalog["search_progress"]["github-search:comfyui workflow"]
        self.assertGreaterEqual(len(called), 2)
        self.assertTrue(state["pending"])
        self.assertIn("alice/one", catalog["discoveries"])


if __name__ == "__main__":
    unittest.main()
