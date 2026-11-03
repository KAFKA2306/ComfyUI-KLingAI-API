import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_practices import static_inspection, pick_assets, highlights, infer_modality

class AuditTests(unittest.TestCase):
    def test_api_graph_extracts_nodes_and_models_without_prompts(self):
        graph = {"1":{"class_type":"CheckpointLoaderSimple",
                      "inputs":{"ckpt_name":"model.safetensors","text":"private prompt"}},
                 "2":{"class_type":"KSampler","inputs":{"seed":42}}}
        got = static_inspection(json.dumps(graph).encode())
        self.assertEqual(got["format"], "comfyui_api")
        self.assertEqual(got["node_count"], 2)
        self.assertEqual(got["models"], ["model.safetensors"])
        self.assertNotIn("private prompt", json.dumps(got))

    def test_ui_graph_is_supported(self):
        got = static_inspection(json.dumps({"nodes":[{"id":1,"type":"VAEDecode"}]}).encode())
        self.assertEqual(got["node_types"], ["VAEDecode"])
        self.assertEqual(got["format"], "comfyui_ui")

    def test_wrong_format_never_qualifies(self):
        self.assertEqual(static_inspection(b'{"foo":3}')["format"], "unknown")
        self.assertEqual(static_inspection(b"not-json")["format"], "not_json")

    def test_inspection_selection_excludes_existing_and_duplicates(self):
        rows = [
            {"id":"repo:a","source_repository":"repo","blob_sha":"a"*40,
             "signal_score":70,"path":"a.json"},
            {"id":"repo:b","source_repository":"repo","blob_sha":"a"*40,
             "signal_score":70,"path":"b.json","same_content_as":"repo:a"}]
        self.assertEqual(1, len(pick_assets(rows, [], 2)))
        self.assertEqual([], pick_assets(rows, [{"id":"repo:a","blob_sha":"a"*40}], 2))
