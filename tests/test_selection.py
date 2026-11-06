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

    def test_evaluation_timestamp_reproduces_freshness_scores(self):
        from gwp.evaluate import report

        first = report(self.catalog, self.registry, now=self.now)
        repeated = report(self.catalog, self.registry, now=self.now)
        later = report(self.catalog, self.registry,
                       now=datetime(2026, 12, 4, tzinfo=timezone.utc))
        self.assertEqual(first, repeated)
        self.assertEqual(first["evaluated_at"], "2026-11-04T00:00:00Z")
        self.assertNotEqual(first["evaluated_at"], later["evaluated_at"])
        def score(result):
            return next(x["score_components"]["freshness"] for x in result["ranked"]
                        if x["id"].startswith("github:example/new:"))
        self.assertGreater(score(first), score(later))
        with self.assertRaises(ValueError):
            report(self.catalog, self.registry, now=datetime(2026, 11, 4))

    def test_assignment_score_uses_its_own_mission_fit(self):
        from gwp.evaluate import report

        catalog = empty_catalog()
        name = "podcast/video-and-audio.json"
        record_file(catalog, "example/mixed", "a" * 40,
                    {"path": name, "sha": "1" * 40, "size": 100},
                    "2026-11-01T00:00:00Z")
        row = catalog["artifacts"]["github:example/mixed:" + name]
        row.update({"inspection": "complete", "format": "workflow-ui",
                    "node_types": ["SaveVideo", "SaveAudio"],
                    "mission_ids": ["youtube"]})
        catalog["repositories"]["example/mixed"] = {
            "stargazers_count": 10, "pushed_at": "2026-11-03T00:00:00Z"}
        result = report(catalog, self.registry, now=self.now)
        ranked = next(x for x in result["ranked"] if x["id"] == row["id"])
        self.assertNotEqual(ranked["mission_scores"]["youtube"],
                            ranked["mission_scores"]["podcast"])
        for mission in ("youtube", "podcast"):
            assignment = next(x for x in result["assignments"][mission]
                              if x["workflow_id"] == row["id"])
            components = ranked["score_components"]
            expected = round(sum(x for x in (components["popularity"], components["freshness"])
                                 if x is not None) + ranked["mission_scores"][mission], 2)
            self.assertEqual(assignment["score"], expected)

    def test_assignment_ranking_uses_weighted_total_not_fit_first(self):
        from gwp.evaluate import report

        catalog = empty_catalog()
        examples = [
            ("example/high-fit", "generic/high-fit.json", "1" * 40, ["3d-models"], 0, "2025-01-01T00:00:00Z"),
            ("example/high-total", "3d/mesh.json", "2" * 40, [], 10000, "2026-11-04T00:00:00Z"),
        ]
        for repo, path, blob, missions, stars, pushed in examples:
            record_file(catalog, repo, "a" * 40,
                        {"path": path, "sha": blob, "size": 100},
                        "2026-11-01T00:00:00Z")
            row = catalog["artifacts"]["github:" + repo + ":" + path]
            row.update({"inspection": "complete", "format": "workflow-ui",
                        "node_types": ["SaveGLB"], "mission_ids": missions})
            catalog["repositories"][repo] = {
                "stargazers_count": stars, "pushed_at": pushed,
            }
        assignments = report(catalog, self.registry, now=self.now)["assignments"]["3d-models"]
        ranked = [x for x in assignments if x["workflow_id"].startswith("github:example/")]
        self.assertEqual(len(ranked), 2)
        self.assertGreater(ranked[0]["score"], ranked[1]["score"])
        self.assertIn("example/high-total", ranked[0]["workflow_id"])
        self.assertLess(ranked[0]["mission_fit"], ranked[1]["mission_fit"])

    def test_report_does_not_merge_different_content_with_same_nodes(self):
        from gwp.evaluate import report

        catalog = empty_catalog()
        for repo, blob in [("example/first", "1" * 40), ("example/second", "2" * 40)]:
            name = "3d/same-nodes.json"
            record_file(catalog, repo, "a" * 40, {
                "path": name, "sha": blob, "size": 100,
            }, "2026-11-01T00:00:00Z")
            row = catalog["artifacts"]["github:" + repo + ":" + name]
            row.update({"inspection": "complete", "format": "workflow-ui",
                        "node_types": ["LoadImage", "SaveGLB"],
                        "model_references": ["same-model"], "mission_ids": ["3d-models"]})
        before = json.dumps(catalog, sort_keys=True)
        evaluated = report(catalog, self.registry, now=self.now)
        # The registry also contributes 14 independent, uninspected source rows.
        self.assertEqual(evaluated["groups"], evaluated["candidates"])
        self.assertEqual(len([row for row in evaluated["ranked"]
                              if row["id"].startswith("github:example/")]), 2)
        self.assertEqual(json.dumps(catalog, sort_keys=True), before)

        # Identical blob contents may be grouped, but both provenance IDs survive.
        rows = list(catalog["artifacts"].values())
        rows[1]["blob_sha"] = rows[0]["blob_sha"]
        grouped = report(catalog, self.registry, now=self.now)
        self.assertEqual(grouped["groups"], grouped["candidates"] - 1)
        merged = [row for row in grouped["ranked"]
                  if row["id"].startswith("github:example/")]
        self.assertEqual(len(merged), 1)
        self.assertEqual(len(merged[0]["similar_candidates"]), 1)



if __name__ == "__main__":
    unittest.main()
