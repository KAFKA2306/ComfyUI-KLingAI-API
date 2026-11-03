import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_catalog import render


class CatalogTests(unittest.TestCase):
    def test_no_candidates_are_discarded_and_tags_are_exploratory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "config").mkdir()
            (root / "registry").mkdir()
            (root / "config/use-cases.json").write_text(json.dumps({
                "categories": [
                    {"id": "vrchat", "title": "VRChat", "keywords": ["vrchat"]},
                    {"id": "movies", "title": "Movies", "keywords": ["video"]},
                ]
            }))
            assets = []
            for name in ("vrchat-world", "video", "unmatched"):
                assets.append({
                    "id": "author/repo:" + name + ".json",
                    "source_repository": "author/repo",
                    "path": name + ".json",
                    "url": "https://github.com/author/repo/blob/a/" + name + ".json",
                    "source_commit": "a" * 40, "blob_sha": "b" * 40,
                    "kind": "workflow_candidate", "license": "UNKNOWN",
                })
            (root / "registry/practices.json").write_text(json.dumps({"assets": assets}))
            (root / "registry/insights.json").write_text(json.dumps({"inspected": [
                {"id": assets[1]["id"], "blob_sha": "b" * 40,
                 "format": "comfyui_ui", "node_count": 3, "node_types": ["VideoCombine"]}
            ]}))
            out = render(root)
            self.assertEqual(out["all"], 3)
            self.assertEqual(out["other"], 1)
            with (root / "catalog/all-workflows.csv").open(encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 3)
            self.assertEqual({r["id"] for r in rows}, {a["id"] for a in assets})
            by_usecase = json.loads((root / "catalog/by-usecase.json").read_text())
            self.assertEqual(by_usecase["categories"]["vrchat"]["count"], 1)
            self.assertEqual(by_usecase["categories"]["movies"]["count"], 1)
            self.assertIn("unmatched.json", (root / "catalog/index.md").read_text())
            # An unchanged snapshot must produce deterministic indexed output.
            original = (root / "catalog/all-workflows.csv").read_bytes()
            render(root)
            self.assertEqual(original, (root / "catalog/all-workflows.csv").read_bytes())
