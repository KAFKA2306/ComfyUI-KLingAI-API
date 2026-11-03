import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.contracts import GenerationRequest
from gwp.registry import load_workflow


class ContractTests(unittest.TestCase):
    def test_request_rejects_missing_workflow(self):
        with self.assertRaises(ValueError):
            GenerationRequest("", {})

    def test_registry_blocks_path_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                load_workflow(Path(folder), "..", "v1")

    def test_registry_loads_versioned_graph(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "sample"
            p.mkdir()
            (p / "v1.json").write_text(json.dumps({"1": {"class_type": "Test"}}), encoding="utf-8")
            self.assertIn("1", load_workflow(Path(folder), "sample", "v1"))


if __name__ == "__main__":
    unittest.main()
