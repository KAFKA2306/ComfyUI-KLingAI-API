"""制作先の自由指定と受け渡し安全性を検証する。"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.production import collect_job, handoff_job, prepare

GRAPH = {"1": {"class_type": "SaveImage", "inputs": {"filename_prefix": "test"}}}


class ProductionTests(unittest.TestCase):
    def test_any_project_label_is_accepted_but_path_traversal_is_not(self):
        for label in ("youtube-shorts", "podcast", "world", "new-project-2026"):
            with self.subTest(label=label):
                _, meta = prepare(label, GRAPH)
                self.assertEqual(meta["target"], label)
                self.assertNotIn("completionAuthority", meta)
        for label in ("../escape", "dir/name", ".hidden", "", "UPPER", "a" * 65):
            with self.subTest(label=label), self.assertRaises(ValueError):
                prepare(label, GRAPH)

    def test_handoff_without_repository_registration_checks_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "output"
            output.mkdir()
            (output / "001-1.png").write_bytes(b"image-bytes")
            manifest = output / "manifest.json"
            manifest.write_text(json.dumps({
                "target": "new-project", "promptId": "id-1", "state": "GENERATED_UNVERIFIED",
                "files": [{"file": "001-1.png",
                           "sha256": hashlib.sha256(b"image-bytes").hexdigest()}]
            }), encoding="utf-8")
            project = root / "project"
            project.mkdir()
            result = handoff_job(manifest, project)
            destination = Path(result["destination"])
            self.assertEqual(destination, project / ".artifacts/comfyui/new-project/id-1")
            self.assertEqual((destination / "001-1.png").read_bytes(), b"image-bytes")
            with self.assertRaises(FileExistsError):
                handoff_job(manifest, project)
            (output / "001-1.png").write_bytes(b"tampered")
            second = root / "another-project"
            second.mkdir()
            with self.assertRaises(ValueError):
                handoff_job(manifest, second)

    def test_glb_transfer_from_meshes_output(self):
        class Backend:
            def history(self, prompt_id):
                return {prompt_id: {"status": {"status_str": "success", "completed": True},
                                    "outputs": {"17": {"meshes": [{"filename": "cup.glb", "subfolder": "", "type": "output"}]}}}
            def download(self, filename, subfolder, file_type):
                return b"glTF-test-bytes"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = collect_job({"state": "SUBMITTED_NOT_COMPLETE", "target": "vrchat",
                                  "promptId": "job-1", "submittedSha256": "a"}, Backend(), root / "out")
            self.assertEqual(len(result["files"]), 1)
            project = root / "project"
            project.mkdir()
            receipt = handoff_job(root / "out/vrchat/job-1/manifest.json", project)
            self.assertTrue((Path(receipt["destination"]) / result["files"][0]["file"]).is_file())


if __name__ == "__main__":
    unittest.main()
