"""HTTP boundary for a local ComfyUI instance; no third-party dependencies."""
import json
from urllib.request import Request, urlopen
from urllib.parse import urlsplit


class ComfyUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8188") -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an HTTP(S) URL")
        self.base_url = base_url.rstrip("/")

    def submit(self, api_workflow: dict, client_id: str) -> dict:
        if not api_workflow or not isinstance(api_workflow, dict):
            raise ValueError("api_workflow must be a nonempty dict")
        payload = json.dumps({"prompt": api_workflow, "client_id": client_id}).encode("utf-8")
        req = Request(self.base_url + "/prompt", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=30) as response:
            return json.load(response)
