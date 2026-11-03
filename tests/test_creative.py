"""作品構成の依存関係と変更影響を検査する。"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.creative import impact, validate
from gwp.registry import load_registry


PLAN = {
    "schema_version": 1,
    "project_id": "project-001",
    "title": "複数領域の制作",
    "missions": ["podcast", "youtube"],
    "continuity": {"voice": "両媒体で同じ発話内容を使う"},
    "units": [
        {"id": "script", "kind": "direction", "purpose": "構成",
         "deliverables": ["台本"]},
        {"id": "audio", "kind": "sound", "purpose": "音声",
         "requires": ["script"], "continuity_refs": ["voice"],
         "deliverables": ["収録データ"]},
        {"id": "video", "kind": "edit", "purpose": "映像",
         "requires": ["script", "audio"], "deliverables": ["映像ファイル"]},
    ],
    "releases": [
        {"id": "episode", "mission": "podcast", "requires": ["audio"]},
        {"id": "short", "mission": "youtube", "requires": ["video"]},
    ],
}

    
def registry_for_plan():
    registry = copy.deepcopy(load_registry())
    registry["projects"]["project-001"] = {
        "title": "複数領域の作品", "tags": ["制作", "音声"],
        "mission_ids": ["podcast", "youtube"],
        "workflow_ids": []
    }
    return registry


class CreativeTests(unittest.TestCase):
    def test_dependencies_and_impacts_across_missions(self):
        order = validate(PLAN, registry_for_plan())
        self.assertLess(order.index("script"), order.index("video"))
        changed = impact(PLAN, "audio", registry_for_plan())
        self.assertEqual(set(changed["affected_units"]), {"audio", "video"})
        self.assertEqual(set(changed["affected_releases"]), {"episode", "short"})

    def test_invalid_references_and_cycle(self):
        plan = copy.deepcopy(PLAN)
        plan["units"][1]["continuity_refs"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "共有表現"):
            validate(plan, registry_for_plan())
        plan = copy.deepcopy(PLAN)
        plan["units"][0]["requires"] = ["video"]
        with self.assertRaisesRegex(ValueError, "循環"):
            validate(plan)
        plan = copy.deepcopy(PLAN)
        plan["releases"][0]["mission"] = "games"
        with self.assertRaisesRegex(ValueError, "missions"):
            validate(plan)


if __name__ == "__main__":
    unittest.main()
