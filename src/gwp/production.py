"""制作リポジトリ向けComfyUIの安全な入出力境界。GPU・Unityの完成検証は別工程。"""
import hashlib
import json
import math
import os
import re
import tempfile
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from gwp.comfyui import ComfyUIClient

ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".wav", ".flac", ".ogg"}
MAX_FILE_BYTES = 256 * 1024 * 1024


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def targets():
    return json.loads((ROOT / "config/production_targets.json").read_text(encoding="utf-8"))["targets"]


def prepare(target, graph, patches=None):
    if target not in targets():
        raise ValueError("制作先が未登録です")
    if not isinstance(graph, dict) or not graph or "nodes" in graph or "definitions" in graph:
        raise ValueError("ComfyUIで Export Workflow (API) を実行したJSONが必要です")
    for node_id, node in graph.items():
        if not isinstance(node_id, str) or not re.fullmatch(r"[1-9][0-9]*", node_id):
            raise ValueError("ノードIDが不正です")
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str) or not node["class_type"] or not isinstance(node.get("inputs"), dict):
            raise ValueError("API形式のnode class_type/inputsが不正です")
    if patches is None:
        patches = {}
    if not isinstance(patches, dict):
        raise ValueError("patchはJSON objectにしてください")
    updated = deepcopy(graph)
    for node_id, changes in patches.items():
        if node_id not in updated or not isinstance(changes, dict):
            raise ValueError("patchのノードが存在しません")
        for key, value in changes.items():
            original = updated[node_id]["inputs"]
            if key not in original or isinstance(original[key], list):
                raise ValueError("未定義入力または結線の変更は禁止します")
            if value is not None and type(value) not in (str, bool, int, float):
                raise ValueError("入力はスカラー値だけ変更できます")
            if type(value) is float and not math.isfinite(value):
                raise ValueError("NaN/Infinityは禁止です")
            original[key] = value
    config = targets()[target]
    meta = {"target": target, "repository": config["repository"],
            "handoff": config["handoff"], "completionAuthority": config["completionAuthority"],
            "originalSha256": digest(graph), "submittedSha256": digest(updated),
            "patchSha256": digest(patches), "nodes": len(graph),
            "state": "PREPARED_NOT_EXECUTED"}
    return updated, meta


class LocalComfyUI:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        parsed = urlsplit(base_url)
        if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
                or parsed.username or parsed.password or parsed.path not in ("", "/")
                or parsed.query or parsed.fragment):
            raise ValueError("ComfyUIの接続先はローカルHTTPだけです")
        self.base_url = base_url.rstrip("/")
        self.client = ComfyUIClient(self.base_url)

    def submit(self, graph, client_id):
        return self.client.submit(graph, client_id)

    def history(self, prompt_id):
        with urlopen(Request(self.base_url + "/history/" + quote(prompt_id, safe="")), timeout=30) as res:
            return json.load(res)

    def download(self, filename, subfolder, file_type):
        url = self.base_url + "/view?" + urlencode({"filename": filename, "subfolder": subfolder, "type": file_type})
        with urlopen(Request(url), timeout=60) as res:
            value = res.read(MAX_FILE_BYTES + 1)
        if len(value) > MAX_FILE_BYTES:
            raise ValueError("出力が256MiBを超えています")
        return value


def submit_job(target, graph, patches, backend, client_id):
    updated, metadata = prepare(target, graph, patches)
    response = backend.submit(updated, client_id)
    prompt_id = response.get("prompt_id") if isinstance(response, dict) else None
    if not isinstance(prompt_id, str) or not prompt_id:
        raise ValueError("ComfyUIのprompt_idが取得できません")
    return {**metadata, "promptId": prompt_id, "state": "SUBMITTED_NOT_COMPLETE"}


def collect_job(receipt, backend, output_root):
    if not isinstance(receipt, dict) or receipt.get("state") != "SUBMITTED_NOT_COMPLETE":
        raise ValueError("送信済みreceiptを指定してください")
    target, prompt_id = receipt.get("target"), receipt.get("promptId")
    if target not in targets() or not isinstance(prompt_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", prompt_id):
        raise ValueError("receiptのtarget/promptIdが不正です")
    history = backend.history(prompt_id)
    job = history.get(prompt_id) if isinstance(history, dict) else None
    if not isinstance(job, dict) or not isinstance(job.get("status"), dict):
        raise ValueError("該当ジョブの完了履歴がありません")
    status = job["status"]
    if status.get("status_str") != "success" or status.get("completed") is not True:
        raise ValueError("ジョブが成功していません")
    outputs = job.get("outputs")
    if not isinstance(outputs, dict):
        raise ValueError("出力情報がありません")
    files = []
    for node_id, result in outputs.items():
        if not isinstance(result, dict):
            continue
        for field in ("images", "gifs", "audio"):
            for item in result.get(field, []):
                if isinstance(item, dict):
                    files.append((str(node_id), item))
    if not 1 <= len(files) <= 100:
        raise ValueError("回収可能な出力がないか、100件を超えています")
    destination = Path(output_root).resolve() / target / prompt_id
    if destination.exists():
        raise FileExistsError("既存の出力を上書きしません")
    destination.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staging = Path(temporary)
        for n, (node_id, item) in enumerate(files, 1):
            name, subfolder, kind = item.get("filename"), item.get("subfolder", ""), item.get("type")
            if not isinstance(name, str) or not name or "/" in name or "\\" in name or name in (".", ".."):
                raise ValueError("不正なファイル名です")
            if not isinstance(subfolder, str) or ".." in subfolder.split("/") or "\\" in subfolder:
                raise ValueError("不正なsubfolderです")
            if kind != "output" or Path(name).suffix.lower() not in EXTENSIONS:
                raise ValueError("未対応の出力形式です")
            raw = backend.download(name, subfolder, kind)
            if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_FILE_BYTES:
                raise ValueError("不正な出力データです")
            local_name = f"{n:03d}-{re.sub(r'[^A-Za-z0-9_-]', '_', node_id)}{Path(name).suffix.lower()}"
            (staging / local_name).write_bytes(raw)
            records.append({"file": local_name, "nodeId": node_id,
                            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        manifest = {"schemaVersion": 1, "target": target, "repository": targets()[target]["repository"],
                    "handoff": targets()[target]["handoff"], "promptId": prompt_id,
                    "workflowSha256": receipt.get("submittedSha256"), "files": records,
                    "state": "GENERATED_UNVERIFIED",
                    "completionAuthority": targets()[target]["completionAuthority"]}
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.rename(staging, destination)
    return manifest


def handoff_job(manifest_path, project_root):
    """検証済み生成素材を既存制作repoの非追跡作業領域へコピーする。"""
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target, prompt_id = manifest.get("target"), manifest.get("promptId")
    cfg = targets()
    if target not in cfg or manifest.get("state") != "GENERATED_UNVERIFIED":
        raise ValueError("正規の生成物manifestが必要です")
    if not isinstance(prompt_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", prompt_id):
        raise ValueError("不正なpromptIdです")
    files = manifest.get("files")
    if not isinstance(files, list) or not 1 <= len(files) <= 100:
        raise ValueError("不正なファイル一覧です")
    project = Path(project_root).resolve()
    marker = project / cfg[target]["projectMarker"]
    if not marker.is_file():
        raise ValueError("制作repoの識別ファイルが見つかりません")
    destination = project / cfg[target]["stagingRoot"] / target / prompt_id
    if destination.exists():
        raise FileExistsError("既存出力は上書きできません")
    checked = []
    for item in files:
        if not isinstance(item, dict):
            raise ValueError("不正なファイル情報です")
        name, expected = item.get("file"), item.get("sha256")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.(?:png|jpg|jpeg|webp|gif|mp4|webm|wav|flac|ogg)", name, re.I):
            raise ValueError("ファイル名が不正です")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("SHA-256が不正です")
        source = manifest_path.parent / name
        if not source.is_file() or source.is_symlink():
            raise ValueError("生成ファイルが見つかりません")
        raw = source.read_bytes()
        if not 0 < len(raw) <= MAX_FILE_BYTES or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("SHA-256検証失敗")
        checked.append((name, raw))
    if len(set(name for name, _ in checked)) != len(checked):
        raise ValueError("生成ファイル名が重複しています")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staging = Path(temporary)
        for name, raw in checked:
            (staging / name).write_bytes(raw)
        receipt = {
            "schemaVersion": 1, "target": target, "repository": cfg[target]["repository"],
            "promptId": prompt_id, "workflowSha256": manifest.get("workflowSha256"),
            "originManifestSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "files": [{"file": name, "sha256": hashlib.sha256(raw).hexdigest()} for name, raw in checked],
            "state": "STAGED_UNREVIEWED",
            "note": "素材の受け渡しのみ。既存製品の正本と品質判定は変更しません。"
        }
        (staging / "handoff.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.rename(staging, destination)
    return {"destination": str(destination), **receipt}
