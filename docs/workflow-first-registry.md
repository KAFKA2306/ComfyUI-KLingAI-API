# ComfyUI Workflows Factory: workflow-first source registry

## Contract
- Collect first. No proprietary score, ranking, popularity filter, quality gate, or workflow execution.
- Never infer that a discovered file is executable. Inspected JSON may still depend on unavailable models or nodes.
- Keep all discovered JSON, JSONC, PNG and WebP source references, including unclassified, invalid and as-yet-uninspected files.
- GitHub content is pinned by repository + commit SHA + file path + blob SHA, and revisions accumulate instead of overwriting history.
- Exact duplicates from different authors/repositories remain separate records. Blob equality is not proof of common authorship.
- Failed/unavailable upstream endpoints are recorded, not interpreted as empty results.
- Issue titles and URLs are evidence at repository scope, **not** established links to specific workflows.
- Workflow files are not downloaded, run, re-licensed, or redistributed by this catalog.
- External site links without verified APIs are tracked as source candidates, **not** falsely claimed to have been crawled.

## Layers
1. **Sources**: origin repo or external collection; discovery via GitHub topic search or configured source.
2. **Inventory**: file URLs + SHA-pinned paths, image candidates, non-workflow JSON, model metadata feeds.
3. **Inspection**: ComfyUI API/UI/Blueprint recognition, node class references and model path references, without a rejection decision.
4. **Lineage**: per-file revision records, upstream commit SHAs, independent repository identities.
5. **Evidence**: metadata-only issue references, and source-reported results/claims (future adapter).
6. **Access**: local JSON registry and case-insensitive text search.

## Commands
Pythonの実行には必ず `uv` を使います。最初に `uv sync --locked` を実行してください。
```sh
uv run --locked python -m gwp.discovery sync
uv run --locked python -m gwp.discovery stats
uv run --locked python -m gwp.discovery search --term KSampler
uv run --locked python -m unittest discover -s tests -v
```

GitHub Actions runs every six hours at minute 17 UTC (01:17, 07:17, 13:17 and 19:17 JST), and also permits manual dispatch. It commits reference-only catalog updates; it never runs third-party code or models. GitHub repository search API can expose at most 1,000 results per search query: coverage is limited and not presented as exhaustive. The configured maximum of 24 repositories per run is a **processing queue size**, not a rejection criterion; discovered repositories persist in `discoveries`.

## Known coverage gaps
- PNG/WebP may have embedded graph metadata. They are indexed as pending, not yet decoded.
- Civitai/Hugging Face collection currently records model-index metadata, not downloadable workflow bytes.
- RunningHub/Reddit/Comfy Registry/other unverified APIs are reference-only.
- GitHub Issues adapter indexes the latest 30 items per scanned repository, not the complete history.
- GitHub workflow metadata is indexed; GPU benchmarking, runtime reproducibility, licensing determinations and automatic adoption are **not claimed**.

## Security and reproducibility
- The GitHub API is called using GitHub Actions' short-lived token; no self-hosted runner or paid model API is required.
- Only known HTTPS API origins are accepted, never execute JSON as code. The catalog stores public identifiers rather than model weights.
- To independently verify a file, open `source_url` (commit-pinned) and compare `blob_sha`; never assume current main still has the same content.
