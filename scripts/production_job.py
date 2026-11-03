"""制作対象別のWorkflowを準備・投入・回収するCLI。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gwp.production import LocalComfyUI, collect_job, prepare, submit_job, targets


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("targets", help="対応する制作プロジェクト")
    for action in ("plan", "submit"):
        cmd = commands.add_parser(action)
        cmd.add_argument("--target", required=True, choices=sorted(targets()))
        cmd.add_argument("--workflow", required=True, help="ComfyUIのExport Workflow (API)によるJSON")
        cmd.add_argument("--patch", help="ノードIDとスカラー入力値のJSON")
        if action == "submit":
            cmd.add_argument("--receipt", required=True)
            cmd.add_argument("--server", default="http://127.0.0.1:8188")
    cmd = commands.add_parser("collect")
    cmd.add_argument("--receipt", required=True)
    cmd.add_argument("--output-root", required=True)
    cmd.add_argument("--server", default="http://127.0.0.1:8188")
    args = parser.parse_args()
    try:
        if args.action == "targets":
            result = targets()
        elif args.action in ("plan", "submit"):
            graph = read_json(args.workflow)
            patch = read_json(args.patch) if args.patch else {}
            if args.action == "plan":
                result = prepare(args.target, graph, patch)[1]
            else:
                receipt_path = Path(args.receipt)
                if receipt_path.exists():
                    raise FileExistsError("receiptは上書きできません")
                result = submit_job(args.target, graph, patch, LocalComfyUI(args.server), "comfy-workflows-factory")
                receipt_path.parent.mkdir(parents=True, exist_ok=True)
                receipt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            result = collect_job(read_json(args.receipt), LocalComfyUI(args.server), Path(args.output_root))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as error:
        parser.exit(2, f"失敗: {error}\n")


if __name__ == "__main__":
    main()
