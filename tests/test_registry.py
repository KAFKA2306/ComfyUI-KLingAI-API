import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.registry import load_registry, validate_registry


class RegistryTests(unittest.TestCase):
    def test_single_registry_contains_all_missions_and_selected_workflows(self):
        data = load_registry()
        self.assertEqual(len(data["missions"]), 8)
        self.assertEqual(len(data["projects"]["vrchat-cafe"]["workflows"]), 3)
        self.assertTrue(data["github_repos"])
        self.assertEqual(len({x["source_key"] for x in data["projects"]["vrchat-cafe"]["workflows"]}), 3)

    def test_broken_references_and_duplicate_ids_fail(self):
        data = load_registry()
        broken = copy.deepcopy(data)
        broken["projects"]["vrchat-cafe"]["workflows"][0]["source_key"] = "wrong"
        with self.assertRaises(ValueError):
            validate_registry(broken)
        duplicate = copy.deepcopy(data)
        flows = duplicate["projects"]["vrchat-cafe"]["workflows"]
        flows[1]["id"] = flows[0]["id"]
        with self.assertRaises(ValueError):
            validate_registry(duplicate)


if __name__ == "__main__":
    unittest.main()
