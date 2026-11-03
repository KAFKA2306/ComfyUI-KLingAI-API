"""制作台帳での権利・二重送信・公開済み誤判定を防ぐ最小回帰テスト。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gwp.discovery import record_file
from gwp.ledger import lineage, put, query, validate_record
from gwp.state import empty_catalog, merge_catalog


class LedgerTests(unittest.TestCase):
    def test_adoption_is_pinned_to_observed_revision(self):
        c = empty_catalog()
        record_file(c, "a/repo", "1" * 40,
                    {"path": "flow.json", "sha": "2" * 40}, "2026-11-01")
        flow = {"artifact_id": "github:a/repo:flow.json",
                "blob_sha": "2" * 40, "commit_sha": "1" * 40,
                "project_id": "cafe", "mission_ids": ["vrchat-world"]}
        self.assertIsNotNone(put(c, "adoptions", "cup", flow))
        self.assertEqual(put(c, "adoptions", "cup", flow), None)
        invalid = dict(flow, blob_sha="3" * 40)
        with self.assertRaises(ValueError):
            validate_record(c, "adoptions", "other", invalid)

    def test_publication_requires_verifiable_claim(self):
        c = empty_catalog()
        base = {"project_id": "cafe", "platform": "VRChat",
                "state": "verified", "url": "https://vrchat.com/home/world/wrld_1"}
        with self.assertRaises(ValueError):
            put(c, "publications", "world", base)
        ready = {**base, "verified_at": "2026-11-03T00:00:00Z",
                 "verification_method": "公開ページをブラウザで確認",
                 "evidence_urls": ["https://vrchat.com/home/world/wrld_1"]}
        self.assertIsNotNone(put(c, "publications", "world", ready))

    def test_job_uses_same_client_id_and_valid_transition(self):
        c = empty_catalog()
        job = {"state": "planned", "target": "cafe", "client_id": "fixed-request",
               "workflow_sha256": "a" * 64}
        put(c, "jobs", "job1", job)
        with self.assertRaises(ValueError):
            put(c, "jobs", "job1", {**job, "state": "succeeded"},
                change_kind="correction")
        put(c, "jobs", "job1", {**job, "state": "submission_unknown"},
            change_kind="correction")
        with self.assertRaises(ValueError):
            put(c, "jobs", "job1", {**job, "client_id": "new"},
                change_kind="correction")

    def test_lineage_traces_downstream_publication(self):
        c = empty_catalog()
        c["artifacts"]["source"] = {"id": "source"}
        c["assets"]["mesh"] = {"depends_on": ["artifacts:source"]}
        c["projects"]["cafe"] = {"depends_on": ["assets:mesh"]}
        c["publications"]["vrchat"] = {"project_id": "cafe"}
        trace = lineage(c, "artifacts:source")
        self.assertIn("publications:vrchat", trace["affected"])

    def test_two_device_corrections_preserve_both_events(self):
        left, right = empty_catalog(), empty_catalog()
        one = {"project_id": "cafe", "platform": "VRChat", "state": "draft"}
        two = {"project_id": "cafe", "platform": "VRChat", "state": "reported"}
        put(left, "publications", "world", one)
        put(right, "publications", "world", two)
        merged = merge_catalog(left, right)
        self.assertEqual(len(merged["events"]), 2)
        self.assertIn(merged["publications"]["world"]["state"], ("draft", "reported"))

    def test_tags_are_nonexclusive(self):
        c = empty_catalog()
        c["assets"]["texture"] = {"tags": ["VRChat", "BOOTH"],
                                    "mission_ids": ["vrchat-world", "booth"]}
        self.assertEqual(len(query(c, "assets", tags=["VRChat"],
                                   missions=["booth"])), 1)


if __name__ == "__main__":
    unittest.main()
