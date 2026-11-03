import base64
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects/vrchat-cafe"))
from cafe_pipeline import download_snapshot, inspect_glb, manifest_entries, snapshot, verify_snapshots


class CafePipelineTests(unittest.TestCase):
    def sample_project(self, root):
        folder = root / "projects/vrchat-cafe"
        folder.mkdir(parents=True)
        (folder / "workflows.json").write_text(json.dumps({"workflows": [
            {"id": "cup-shape", "repository": "Comfy-Org/workflow_templates", "path": "templates/cup.json"}
        ]}), encoding="utf-8")

    def fake_api(self, path):
        if path.endswith("/commits/main"):
            return {"sha": "a" * 40}
        if path.endswith("/contents/templates/cup.json?ref=" + "a" * 40):
            raw = json.dumps({"nodes": [{"type": "Test"}]}).encode()
            return {"encoding": "base64", "type": "file", "size": len(raw),
                    "sha": "b" * 40, "content": base64.b64encode(raw).decode()}
        if path.endswith("/workflow_templates"):
            return {"default_branch": "main"}
        raise AssertionError(path)

    def test_snapshot_provenance_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.sample_project(root)
            self.assertEqual(snapshot(root, self.fake_api)[0]["execution"], "not-run")
            self.assertEqual(verify_snapshots(root)[0]["status"], "intact")
            json_path = root / "projects/vrchat-cafe/upstream/cup-shape.json"
            json_path.write_text('{"nodes": []}')
            self.assertEqual(verify_snapshots(root)[0]["status"], "mismatch")

    def test_manifest_rejects_path_traversal_and_duplicate_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.sample_project(root)
            path = root / "projects/vrchat-cafe/workflows.json"
            path.write_text(json.dumps({"workflows": [{"id": "cup-shape", "repository": "a/b", "path": "templates/../etc.json"}]}))
            with self.assertRaises(ValueError):
                manifest_entries(root)

    def test_real_glb_header_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cup.glb"
            body = json.dumps({"asset": {"version": "2.0"}, "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}], "accessors": [{"count": 12}]}).encode()
            body += b" " * ((-len(body)) % 4)
            path.write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(body)) + struct.pack("<I4s", len(body), b"JSON") + body)
            result = inspect_glb(path)
            self.assertEqual(result["triangles_estimated"], 4)
            path.write_bytes(path.read_bytes()[:-2])
            with self.assertRaisesRegex(ValueError, "length mismatch"):
                inspect_glb(path)


if __name__ == "__main__":
    unittest.main()
