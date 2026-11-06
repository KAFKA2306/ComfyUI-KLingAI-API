"""自律改善の実行間メモリを検証する最小テスト。"""
import copy
import unittest

from gwp.agent_memory import validate


def sample():
    return {
        "schema_version": 1,
        "scope": "KAFKA2306/comfyui-workflows-factory",
        "baseline": {
            "observed_main_sha": "a" * 40,
            "observed_on": "2026-11-07",
            "source_url": "https://github.com/example/commit/" + "a" * 40,
        },
        "verified_lessons": [
            {"id": "rule-one", "finding": "実測した事実", "evidence_url": "https://example.com/fact", "checked_on": "2026-11-07"}
        ],
        "hypotheses": [
            {"id": "hypothesis-one", "hypothesis": "検証前の仮説", "basis_url": "https://example.com/code",
             "checked_on": "2026-11-07", "status": "unverified", "proposed_test": "反例を作る",
             "next_action": "差分を計測する"}
        ],
        "blocked_attempts": [],
    }


class AgentMemoryTest(unittest.TestCase):
    def test_valid_evidence_separated_from_hypotheses(self):
        self.assertEqual(validate(sample()), [])

    def test_invalid_or_missing_evidence_is_rejected(self):
        data = sample()
        data["verified_lessons"][0]["evidence_url"] = "file:///no-source"
        self.assertTrue(any("HTTPS" in error for error in validate(data)))
        data = sample()
        del data["hypotheses"][0]["proposed_test"]
        self.assertTrue(any("proposed_test" in error for error in validate(data)))

    def test_cross_section_duplicate_ids_are_rejected(self):
        data = sample()
        data["hypotheses"][0]["id"] = "rule-one"
        self.assertTrue(any("重複" in error for error in validate(data)))

    def test_verified_hypothesis_cannot_remain_unchecked(self):
        data = copy.deepcopy(sample())
        data["hypotheses"][0]["status"] = "verified"
        self.assertTrue(any("verified_lessons" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()
