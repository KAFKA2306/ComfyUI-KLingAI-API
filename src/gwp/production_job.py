"""任意の制作先でWorkflowを準備・投入・回収するCLI。"""
import argparse
import json
import os
import uuid
from pathlib import Path

from gwp.production import LocalComfyUI, collect_job, handoff_job, prepare, submit_job
from gwp.state import _durable_write


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("plan", "submit"):
        cmd = commands.add_parser(action)
        cmd.add_argument("--target", required=True, help="任意の制作先識別子（英小文字・数字・_-、最大64文字）")
        cmd.add_argument("--workflow", required=True, help="ComfyUIのExport Workflow (API)によるJSON")
        cmd.add_argument("--patch", help="ノードIDとスカラー入力値のJSON")
        if action == "submit":
            cmd.add_argument("--receipt", required=True)
            cmd.add_argument("--server", default="http://127.0.0.1:8188")
    cmd = commands.add_parser("status")
    cmd.add_argument("--receipt", required=True)
    cmd.add_argument("--server", default="http://127.0.0.1:8188")
    cmd = commands.add_parser("collect")
    cmd.add_argument("--receipt", required=True)
    cmd.add_argument("--output-root", required=True)
    cmd.add_argument("--server", default="http://127.0.0.1:8188")
    cmd = commands.add_parser("handoff")
    cmd.add_argument("--manifest", required=True)
    cmd.add_argument("--project-root", required=True)
    args = parser.parse_args()
    try:
        if args.action in ("plan", "submit"):
            graph = read_json(args.workflow)
            patch = read_json(args.patch) if args.patch else {}
            if args.action == "plan":
                result = prepare(args.target, graph, patch)[1]
            else:
                receipt_path = Path(args.receipt)
                if receipt_path.exists():
                    raise FileExistsError("receiptは上書きできません")
                # 送信より先に不確実な状態を確定させる。通信断でも再送しない。
                meta = prepare(args.target, graph, patch)[1]
                client_id = "gwp-" + uuid.uuid4().hex
                pending = {**meta, "clientId": client_id, "state": "SUBMISSION_UNKNOWN"}
                receipt_path.parent.mkdir(parents=True, exist_ok=True)
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                fd = os.open(receipt_path, flags, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as output:
                    output.write(json.dumps(pending, ensure_ascii=False, indent=2) + "\n")
                    output.flush()
                    os.fsync(output.fileno())
                result = submit_job(args.target, graph, patch, LocalComfyUI(args.server), client_id)
                result["clientId"] = client_id
                _durable_write(receipt_path, (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        elif args.action == "status":
            receipt_path = Path(args.receipt)
            receipt = read_json(receipt_path)
            backend = LocalComfyUI(args.server)
            if receipt.get("state") == "SUBMISSION_UNKNOWN":
                queue = backend.queue()
                matches = []
                for name in ("queue_running", "queue_pending"):
                    for row in queue.get(name, []):
                        if (isinstance(row, list) and len(row) > 3
                                and isinstance(row[3], dict)
                                and row[3].get("client_id") == receipt.get("clientId")):
                            matches.append(row[1])
                if len(set(matches)) == 1:
                    receipt["promptId"] = matches[0]
                    receipt["state"] = "SUBMITTED_NOT_COMPLETE"
                    _durable_write(receipt_path, (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            result = {"receipt_state": receipt.get("state"), "promptId": receipt.get("promptId"),
                      "may_resubmit": False}
            if receipt.get("promptId"):
                history = backend.history(receipt["promptId"])
                job = history.get(receipt["promptId"], {})
                result["comfyui_status"] = job.get("status", {}).get("status_str", "unknown")
        elif args.action == "collect":
            result = collect_job(read_json(args.receipt), LocalComfyUI(args.server), Path(args.output_root))
        else:
            result = handoff_job(args.manifest, args.project_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as error:
        parser.exit(2, f"失敗: {error}\n")


if __name__ == "__main__":
    main()
