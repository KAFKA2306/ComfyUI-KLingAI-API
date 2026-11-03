# ComfyUI Workflows Factory architecture

## Boundaries

1. Application and agents call a stable request contract, not ComfyUI node IDs.
2. Orchestrator resolves workflow ID + immutable version.
3. Adapter maps named inputs to a validated ComfyUI API-format graph.
4. Runtime executes model-specific nodes; the adapter is replaceable.
5. Evaluation stores cases, provenance, output hashes, timing, VRAM and scores.

Do not put API keys, model binaries, generated media, or local paths in Git. No upstream repository is vendored. Pin all external revisions before production.
