import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.discovery import (new_catalog, workflow_details, record_file,
                           walk_tree, atomic_save, load_catalog, search,
                           discover_organizations, export_catalog)


class FakeAPI:
    def __init__(self, pages):
        self.pages = pages

    def json(self, url):
        return self.pages[url]


class WorkflowDiscoveryTests(unittest.TestCase):
    def test_real_comfy_formats_and_nonworkflow_are_distinct(self):
        self.assertEqual(workflow_details({"nodes": [{"type": "KSampler"}]})["kind"], "workflow-ui")
        self.assertEqual(workflow_details({"7": {"class_type": "KSampler", "inputs": {"ckpt_name": "m.safetensors"}}})["kind"], "workflow-api")
        self.assertEqual(workflow_details({"definitions": {"subgraphs": []}})["kind"], "blueprint")
        self.assertEqual(workflow_details({"author": "someone"})["kind"], "json-unclassified")

    def test_same_blob_different_origin_kept_and_revision_not_dropped(self):
        c = new_catalog()
        f = {"path": "test.json", "sha": "a" * 40, "size": 20}
        self.assertTrue(record_file(c, "a/x", "1" * 40, f, "now"))
        self.assertTrue(record_file(c, "b/x", "1" * 40, f, "now"))
        self.assertEqual(len(c["artifacts"]), 2)
        self.assertFalse(record_file(c, "a/x", "1" * 40, f, "later"))
        self.assertTrue(record_file(c, "a/x", "2" * 40, {**f, "sha": "b" * 40}, "later"))
        self.assertEqual(len(next(iter(c["artifacts"].values()))["revisions"]), 2)

    def test_truncated_tree_recovers_nested_files(self):
        p = "https://api.github.com/repos/a/b/git/trees/"
        pages = {
            p + "main?recursive=1": {"truncated": True, "tree": []},
            p + "main": {"tree": [{"type": "tree", "path": "nested", "sha": "child"},
                                  {"type": "blob", "path": "root.json", "sha": "s"}]},
            p + "child": {"tree": [{"type": "blob", "path": "flow.json", "sha": "t"}]},
        }
        files = walk_tree(FakeAPI(pages), "a/b", "main")
        self.assertEqual({f["path"] for f in files}, {"nested/flow.json", "root.json"})

    def test_uninspected_media_and_unknown_json_not_excluded(self):
        c = new_catalog()
        for path in ("unknown.json", "embedded.png"):
            record_file(c, "a/b", "c" * 40, {"path": path, "sha": "d" * 40}, "now")
        self.assertEqual(len(c["artifacts"]), 2)
        self.assertEqual(len(list(search(c, "embedded"))), 1)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data" / "catalog.json"
            atomic_save(path, c)
            self.assertEqual(len(load_catalog(path)["artifacts"]), 2)


    def test_organization_listing_includes_all_repositories(self):
        c = new_catalog()
        url = "https://api.github.com/orgs/Comfy-Org/repos?per_page=100&page=1&type=public"
        discover_organizations(FakeAPI({url: [
            {"full_name": "Comfy-Org/workflows", "html_url": "https://github.com/Comfy-Org/workflows"},
            {"full_name": "Comfy-Org/ComfyUI", "html_url": "https://github.com/Comfy-Org/ComfyUI"},
        ]}), c, ["Comfy-Org"])
        self.assertEqual(len(c["discoveries"]), 2)

    def test_export_preserves_unknown_candidates(self):
        c = new_catalog()
        for path in ("vrchat/demo.json", "unknown.json"):
            record_file(c, "a/b", "c" * 40, {"path": path, "sha": "d" * 40}, "now")
        out = export_catalog(c, [{"title": "VRChat", "keywords": ["vrchat"]}])
        self.assertTrue(out.startswith("\ufeff"))
        self.assertEqual(out.count("\n"), 3)
        self.assertIn("VRChat", out)
        self.assertIn("未分類", out)


if __name__ == "__main__":
    unittest.main()
