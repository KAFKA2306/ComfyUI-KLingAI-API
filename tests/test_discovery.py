"""出典を失わずにWorkflow候補を収集するための最小限の回帰テスト。"""
import sys
import unittest
from pathlib import Path
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gwp.discovery import export_catalog, new_catalog, record_file, sync, walk_tree, workflow_details


class DiscoveryTests(unittest.TestCase):
    def test_origins_and_revisions_are_preserved(self):
        catalog = new_catalog()
        item = {"path": "flow.json", "sha": "a" * 40, "size": 20}
        self.assertTrue(record_file(catalog, "a/x", "1" * 40, item, "first"))
        self.assertTrue(record_file(catalog, "b/x", "1" * 40, item, "first"))
        self.assertFalse(record_file(catalog, "a/x", "1" * 40, item, "again"))
        self.assertTrue(record_file(catalog, "a/x", "2" * 40, {**item, "sha": "b" * 40}, "later"))
        self.assertEqual(len(catalog["artifacts"]), 2)
        self.assertEqual(len(catalog["artifacts"]["github:a/x:flow.json"]["revisions"]), 2)

    def test_truncated_tree_recovers_nested_files(self):
        prefix = "https://api.github.com/repos/a/b/git/trees/"
        pages = {
            prefix + "main?recursive=1": {"truncated": True, "tree": []},
            prefix + "main": {"tree": [{"type": "tree", "path": "nested", "sha": "child"}]},
            prefix + "child": {"tree": [{"type": "blob", "path": "flow.json", "sha": "blob"}]},
        }

        class API:
            def json(self, url):
                return pages[url]

        self.assertEqual([f["path"] for f in walk_tree(API(), "a/b", "main")], ["nested/flow.json"])

    def test_unclassified_candidates_are_not_discarded(self):
        catalog = new_catalog()
        for path in ("unknown.json", "vrchat/embedded.png"):
            self.assertTrue(record_file(catalog, "a/b", "1" * 40,
                                        {"path": path, "sha": "a" * 40}, "first"))
        self.assertEqual(len(catalog["artifacts"]), 2)
        self.assertEqual(workflow_details({"author": "someone"})["kind"], "json-unclassified")
        exported = export_catalog(catalog, [{"title": "VRChat", "keywords": ["vrchat"]}], "json")
        self.assertIn("unknown.json", exported)
        self.assertIn("vrchat/embedded.png", exported)


    def test_failed_repository_does_not_starve_unscanned_sources(self):
        catalog = new_catalog()
        for name in ("a/unavailable", "b/available"):
            catalog["discoveries"][name] = {
                "repo": name, "url": "https://github.com/" + name,
                "discovered_via": ["configured-seed"],
            }

        class API:
            def __init__(self):
                self.attempts = []

            def json(self, url):
                prefix = "https://api.github.com/repos/"
                if url == prefix + "a/unavailable":
                    self.attempts.append("a/unavailable")
                    raise URLError("一時的に取得できません")
                if url == prefix + "b/available":
                    self.attempts.append("b/available")
                    return {"default_branch": "main"}
                if url == prefix + "b/available/commits/main":
                    return {"sha": "a" * 40}
                if url == prefix + "b/available/git/trees/main?recursive=1":
                    return {"truncated": False, "tree": []}
                if url.startswith(prefix + "b/available/issues?"):
                    return []
                raise AssertionError("想定外のAPI呼び出し: " + url)

        api = API()
        sync(api, catalog, {}, max_repos=1, inspect_limit=0)
        sync(api, catalog, {}, max_repos=1, inspect_limit=0)

        self.assertEqual(api.attempts, ["a/unavailable", "b/available"])
        self.assertIn("last_attempted_at", catalog["repositories"]["a/unavailable"])
        self.assertIn("last_scanned_at", catalog["repositories"]["b/available"])


if __name__ == "__main__":
    unittest.main()
