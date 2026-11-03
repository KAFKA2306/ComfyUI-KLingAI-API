import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from practice_registry import candidate_json, official_repositories, collect_assets, discover
from validate_registry import validate

def repo(name):
    return {"full_name": "Comfy-Org/" + name, "name": name, "default_branch": "main",
            "description": "Example", "archived": False, "fork": False,
            "stargazers_count": 42, "license": {"spdx_id": "MIT"}}

class RegistryTests(unittest.TestCase):
    def test_pagination(self):
        def fetch(path):
            return [repo(str(i)) for i in range(100)] if path.endswith("&page=1") else [repo("last")]
        self.assertEqual(len(official_repositories(fetch, "Comfy-Org")), 101)

    def test_path_filter(self):
        self.assertTrue(candidate_json("blueprints/x.json", True))
        self.assertTrue(candidate_json("basic/basic_workflow.json"))
        self.assertFalse(candidate_json("package.json"))
        self.assertFalse(candidate_json("tests/sample.json"))

    def test_identical_assets_detected_without_execution(self):
        row = {"repository": "Comfy-Org/workflow_templates", "default_branch": "main",
               "archived": False, "license": "MIT", "stars": 100, "kind": "official"}
        def fetch(path):
            if "/commits/" in path:
                return {"sha": "a" * 40}
            return {"truncated": False, "tree": [
                {"type": "blob", "path": "blueprints/a.json", "sha": "b" * 40, "size": 9},
                {"type": "blob", "path": "templates/b.json", "sha": "b" * 40, "size": 9}]}
        assets, scans, heads = collect_assets(fetch, [row], [row["repository"]], {}, "2026-11-03")
        self.assertEqual(2, len(assets))
        self.assertEqual(1, sum("same_content_as" in a for a in assets))
        self.assertEqual("a" * 40, heads[row["repository"]])

    def test_end_to_end_repeatable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "config").mkdir()
            (root / "registry").mkdir()
            (root / "config/practice-sources.json").write_text(json.dumps({
                "organization":"Comfy-Org", "searches":[], "per_query":2, "curated":[],
                "scan_repositories":["Comfy-Org/workflow_templates"],
                "track_upstreams":["workflow_templates"]}))
            (root / "registry/decisions.json").write_text('{"schema_version":1,"decisions":[]}')
            def fetch(path):
                if "/orgs/" in path: return [repo("workflow_templates")]
                if "/commits/" in path: return {"sha":"a" * 40}
                if "/git/trees/" in path: return {"truncated":False, "tree":[
                    {"type":"blob","path":"templates/demo.json","sha":"b"*40,"size":100}]}
                raise AssertionError(path)
            self.assertEqual(1, discover(root, fetch, "2026-11-03")["practices"])
            validate(root)
            previous = (root / "registry/practices.json").read_text()
            discover(root, fetch, "2026-11-04")
            self.assertEqual(previous, (root / "registry/practices.json").read_text())

    def test_truncated_tree_rejected(self):
        row = {"repository": "Comfy-Org/workflow_templates", "default_branch": "main",
               "archived": False, "license": "MIT", "stars": 1, "kind": "official"}
        def fetch(path):
            return {"sha":"a"*40} if "/commits/" in path else {"truncated":True}
        with self.assertRaisesRegex(ValueError, "incomplete"):
            collect_assets(fetch, [row], [row["repository"]], {}, "2026-11-03")
