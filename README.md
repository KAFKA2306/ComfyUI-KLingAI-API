# Comfy Workflow Atlas

Workflow-first 2026 discovery for **YouTube, VRChat, BOOTH, Podcast, 3D Models, Movies, Chill Worlds, Game Worlds, Avatars and game assets**. The former Kling-specific implementation was retired; its Git history remains accessible.

## Browse and reproduce

- [Use-case index](catalog/index.md): direct links to original, pinned Workflow JSON.
- [All candidates CSV](catalog/all-workflows.csv): complete index for Google Sheets / Excel, including unmatched entries.
- [Use-case JSON](catalog/by-usecase.json): machine-readable cross-category IDs.
- [Sources and limitations](docs/SOURCES.md)
- [Source-preserving registry design](docs/workflow-first-registry.md)

The catalog merges the prior official/community snapshot and the new `data/workflow_registry.json` provenance-first crawler. It **does not filter, score or rank creators**. Every candidate, including unknown formats and PNG/WebP, stays discoverable. Category tags are exploratory, not evidence that a workflow completes an entire published product.

## Automatic collection

`.github/workflows/workflow-discovery.yml` runs every 6 hours and on demand. It tracks independent and official sources and revisions, inspects JSON metadata without executing upstream code, regenerates the full category index, and commits metadata changes.

```sh
python -m unittest discover -s tests -v
PYTHONPATH=src python -m gwp.discovery sync
PYTHONPATH=src python -m gwp.discovery stats
PYTHONPATH=src python -m gwp.discovery search --term flux
python scripts/build_catalog.py
```

Python 3.11+, standard library. No paid model API. GPU execution, Unity/VRChat SDK integration and BOOTH commercial-license checks are separate production steps. Original versioned contracts and optional runtime adapter remain under `src/gwp/`.
