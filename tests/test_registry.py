"""設定台帳の参照整合性を検査する。"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.registry import load_registry, validate_registry


class RegistryTests(unittest.TestCase):
    def test_missions_and_workflows_are_independent_from_projects(self):
        data = load_registry()
        self.assertEqual(len(data["missions"]), 8)
        self.assertIsInstance(data["projects"], dict)
        self.assertTrue(data["github_repos"])
        self.assertEqual(len({row["id"] for row in data["workflows"]}), len(data["workflows"]))
        self.assertEqual(len({row["source_key"] for row in data["workflows"]}), len(data["workflows"]))

    def test_pipeline_inputs_and_references(self):
        data = load_registry()
        self.assertEqual(len(data["pipelines"]), 6)
        broken = copy.deepcopy(data)
        broken["pipelines"][0]["steps"][1]["requires"].append("missing.mp4")
        with self.assertRaisesRegex(ValueError, "未生成の入力"):
            validate_registry(broken)
        broken = copy.deepcopy(data)
        broken["projects"]["broken"] = {
            "title": "制作", "tags": ["映像"], "mission_ids": ["youtube"],
            "pipeline_ids": ["unknown"]
        }
        with self.assertRaisesRegex(ValueError, "制作パイプライン"):
            validate_registry(broken)

    def test_invalid_source_or_references_fail(self):
        data = load_registry()
        broken = copy.deepcopy(data)
        broken["workflows"][0]["source_key"] = "wrong"
        with self.assertRaises(ValueError):
            validate_registry(broken)
        missing = copy.deepcopy(data)
        missing["projects"]["project-001"] = {
            "title": "制作案件", "tags": ["制作", "検証"],
            "mission_ids": ["unknown"], "workflow_ids": []
        }
        with self.assertRaises(ValueError):
            validate_registry(missing)
        missing["projects"]["project-001"]["mission_ids"] = ["youtube"]
        missing["projects"]["project-001"]["workflow_ids"] = ["nonexistent"]
        with self.assertRaises(ValueError):
            validate_registry(missing)


if __name__ == "__main__":
    unittest.main()
