import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.production import LocalComfyUI, collect_job, prepare, submit_job

GRAPH = {"1": {"class_type": "TextNode", "inputs": {"text": "before", "link": ["2", 0]}},
         "2": {"class_type": "SaveImage", "inputs": {"filename_prefix": "demo"}}}


class FakeBackend:
    def submit(self, graph, client_id):
        self.received = graph
        return {"prompt_id": "test-123"}

    def history(self, prompt_id):
        return {prompt_id: {"status": {"status_str": "success", "completed": True},
                            "outputs": {"2": {"images": [{"filename": "demo.png", "subfolder": "", "type": "output"}]}}}}

    def download(self, filename, subfolder, file_type):
        return b"image-bytes"


class ProductionTests(unittest.TestCase):
    def test_patch_only_changes_declared_scalar(self):
        graph, meta = prepare("image2outfit", GRAPH, {"1": {"text": "after"}})
        self.assertEqual(graph["1"]["inputs"]["text"], "after")
        self.assertEqual(GRAPH["1"]["inputs"]["text"], "before")
        self.assertEqual(meta["state"], "PREPARED_NOT_EXECUTED")

    def test_ui_json_wrong_node_or_link_change_rejected(self):
        for graph, patch in (({"nodes": []}, {}), (GRAPH, {"9": {"text": "bad"}}),
                             (GRAPH, {"1": {"link": "replace"}})):
            with self.assertRaises(ValueError):
                prepare("image2outfit", graph, patch)

    def test_remote_and_credentialed_urls_rejected(self):
        for url in ("https://example.org", "http://169.254.169.254", "http://user:pass@localhost:8188"):
            with self.assertRaises(ValueError):
                LocalComfyUI(url)

    def test_submitted_result_remains_unverified_and_never_overwrites(self):
        backend = FakeBackend()
        receipt = submit_job("vrmine-cafe", GRAPH, {"1": {"text": "cafe"}}, backend, "test")
        self.assertEqual(backend.received["1"]["inputs"]["text"], "cafe")
        with tempfile.TemporaryDirectory() as directory:
            manifest = collect_job(receipt, backend, Path(directory))
            self.assertEqual(manifest["state"], "GENERATED_UNVERIFIED")
            self.assertEqual(manifest["files"][0]["sha256"], hashlib.sha256(b"image-bytes").hexdigest())
            self.assertTrue((Path(directory) / "vrmine-cafe" / "test-123" / "manifest.json").is_file())
            with self.assertRaises(FileExistsError):
                collect_job(receipt, backend, Path(directory))

    def test_incomplete_history_cannot_write(self):
        class Incomplete(FakeBackend):
            def history(self, prompt_id):
                return {prompt_id: {"status": {"status_str": "running", "completed": False}, "outputs": {}}}
        backend = Incomplete()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                collect_job(submit_job("tripo-3d", GRAPH, {}, backend, "test"), backend, Path(directory))
            self.assertFalse(list(Path(directory).iterdir()))

    def test_malicious_filename_rejected(self):
        class Malicious(FakeBackend):
            def history(self, prompt_id):
                data = super().history(prompt_id)
                data[prompt_id]["outputs"]["2"]["images"][0]["filename"] = "../secret.png"
                return data
        backend = Malicious()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                collect_job(submit_job("image2outfit", GRAPH, {}, backend, "test"), backend, Path(directory))


    def test_handoff_copies_only_hash_verified_assets(self):
        from gwp.production import handoff_job
        backend = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            output = directory / "outputs"
            receipt = submit_job("vrmine-cafe", GRAPH, {}, backend, "test")
            collect_job(receipt, backend, output)
            manifest_path = output / "vrmine-cafe" / "test-123" / "manifest.json"
            project = directory / "vrmine"
            (project / "config").mkdir(parents=True)
            (project / "config" / "quality-gates.json").write_text("{}")
            handoff = handoff_job(manifest_path, project)
            self.assertEqual(handoff["state"], "STAGED_UNREVIEWED")
            self.assertEqual((Path(handoff["destination"]) / "002-2.png").exists(), False)
            self.assertEqual((Path(handoff["destination"]) / "001-2.png").read_bytes(), b"image-bytes")
            with self.assertRaises(FileExistsError):
                handoff_job(manifest_path, project)

    def test_handoff_rejects_modified_source_bytes(self):
        from gwp.production import handoff_job
        backend = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            output = directory / "outputs"
            collect_job(submit_job("image2outfit", GRAPH, {}, backend, "test"), backend, output)
            manifest_path = output / "image2outfit" / "test-123" / "manifest.json"
            (manifest_path.parent / "001-2.png").write_bytes(b"tampered")
            project = directory / "image2outfit"
            (project / "config").mkdir(parents=True)
            (project / "config" / "genworks-handoff-policy.json").write_text("{}")
            with self.assertRaises(ValueError):
                handoff_job(manifest_path, project)

if __name__ == "__main__":
    unittest.main()
