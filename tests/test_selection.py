"""Workflow選定時に原典を消さず、公開元の指標を誤読しないためのテスト。"""
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gwp.discovery import record_file
from gwp.registry import load_registry
from gwp.select import select_workflows
from gwp.state import empty_catalog


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = empty_catalog()
        self.registry = load_registry()
        for repo, name, complete in [
            ("example/popular", "3d/mesh-to-glb.json", True),
            ("example/new", "3d/trellis-image-model.json", True),
            ("example/uninspected", "3d/unknown.json", False),
            ("example/unrelated", "podcast/tts.json", True),
        ]:
            record_file(self.catalog, repo, "a" * 40, {
                "path": name, "sha": "b" * 40, "size": 100,
            }, "2026-11-01T00:00:00Z")
            row = self.catalog["artifacts"]["github:" + repo + ":" + name]
            if complete:
                row.update({"format": "workflow-ui", "inspection": "complete",
                            "node_types": ["SaveAudio" if repo == "example/unrelated" else "SaveGLB"]})
        self.metadata = {
            "example/popular": {"stargazers_count": 100,
                                "pushed_at": "2026-06-01T00:00:00Z"},
            "example/new": {"stargazers_count": 9,
                            "pushed_at": "2026-11-03T00:00:00Z"},
            "example/uninspected": {"stargazers_count": None,
                                    "pushed_at": None},
            "example/unrelated": {"stargazers_count": 999,
                                  "pushed_at": "2026-11-03T00:00:00Z"},
        }
        self.now = datetime(2026, 11, 4, tzinfo=timezone.utc)

    def test_selection_is_read_only_and_popularity_belongs_to_repository(self):
        before = json.dumps(self.catalog, sort_keys=True)
        selected = select_workflows(self.catalog, self.registry, "3d-models",
                                    self.metadata, sort="popular", inspected_only=True,
                                    now=self.now)
        self.assertEqual([x["repository"] for x in selected],
                         ["example/popular", "example/new"])
        self.assertEqual(selected[0]["repository_stars"], 100)
        self.assertEqual(json.dumps(self.catalog, sort_keys=True), before)

    def test_latest_and_explicit_filters_do_not_invent_missing_metrics(self):
        selected = select_workflows(
            self.catalog, self.registry, "3d-models", self.metadata,
            sort="latest", updated_within_days=30, min_stars=1,
            inspected_only=True, now=self.now)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["repository"], "example/new")
        all_rows = select_workflows(
            self.catalog, self.registry, "3d-models", self.metadata,
            now=self.now)
        self.assertTrue(any(x["inspection"] == "registry-only" for x in all_rows))
        self.assertTrue(any(x["inspection"] == "pending" for x in all_rows))
        self.assertFalse(any(x["repository"] == "example/unrelated" for x in all_rows))


if __name__ == "__main__":
    unittest.main()
