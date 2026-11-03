"""作品構成の参照と変更影響を検査する。"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gwp.creative import impact, validate


class CreativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "projects/vrchat-cafe/creative.json").read_text(encoding="utf-8"))

    def test_dependencies_and_impacts(self):
        order = validate(self.plan)
        self.assertLess(order.index("architecture"), order.index("world-assembly"))
        changed = impact(self.plan, "cup")
        self.assertIn("world-assembly", changed["affected_units"])
        self.assertIn("vrchat-public-world", changed["affected_releases"])
        self.assertNotIn("furniture", changed["affected_units"])

    def test_broken_reference_and_cycle(self):
        plan = copy.deepcopy(self.plan)
        plan["units"][0]["continuity_refs"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "共有表現"):
            validate(plan)
        plan = copy.deepcopy(self.plan)
        plan["units"][0]["requires"] = ["world-package"]
        with self.assertRaisesRegex(ValueError, "循環"):
            validate(plan)

    def test_mission_invariants(self):
        plan = copy.deepcopy(self.plan)
        plan["releases"][0]["mission"] = "games"
        with self.assertRaisesRegex(ValueError, "missions"):
            validate(plan)


if __name__ == "__main__":
    unittest.main()
