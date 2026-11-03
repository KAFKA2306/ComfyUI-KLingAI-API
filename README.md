# Comfy Workflow Atlas

Comfy Workflow Atlas is a source-preserving catalog of real-world ComfyUI workflows, subgraphs, blueprints, custom-node examples, model references, and public implementation evidence. The original Kling-specific implementation was replaced; its history remains available in Git.

**Workflow first. No proprietary quality scores, filtering, rankings, or execution of third-party workflows.** Every indexed candidate remains available with its origin and inspection state. Unsupported or inaccessible sources remain visible as unsynced references.

## Included
- Original ComfyUI API connection and versioned workflow contracts: `src/gwp/`
- GitHub workflow source registry: `config/workflow_sources.json`
- GitHub public-repository search + discovery queue + complete Git trees (including truncated-tree fallback)
- SHA-pinned workflow file references, revision history, basic node/model references, image-embedded-workflow candidates
- Public model-index discovery: Hugging Face and Civitai (metadata only)
- Issue-reference collection (recent 30 per scanned repo, repo-wide scope)
- UTC daily GitHub Actions collection, metadata commit to main, GitHub-hosted Python tests
- Local JSON catalog search without subjective rank or gate

## Run
```sh
python -m unittest discover -s tests -v
PYTHONPATH=src python -m gwp.discovery sync
PYTHONPATH=src python -m gwp.discovery stats
PYTHONPATH=src python -m gwp.discovery search --term flux
```

Uses Python 3.11+ standard library; no external runtime package or model weight. Optional `GITHUB_TOKEN` expands API rate allowance. GitHub Actions runs daily at 01:17 JST (16:17 UTC), with optional manual dispatch. The first full source ingestion occurs when the collector runs; a blank starting catalog does not claim that every source has already been indexed.

See [architecture and explicit collection gaps](docs/workflow-first-registry.md). ComfyUI workflows that come from a third party must be reviewed before running; this catalog never auto-adopts them.

## Existing platform components
- `src/gwp/comfyui.py`: local ComfyUI client
- `src/gwp/registry.py`: immutable versioned workflow loading
- `contracts/`, `workflows/`, `blueprints/`, `dependencies/`, `environments/`: prior platform structure
