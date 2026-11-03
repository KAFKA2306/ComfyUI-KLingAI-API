# Workflow Atlas: sources and scope

This repository is a **source-preserving index**, not a replacement for ComfyUI, a custom-node installer, or a guarantee that generated assets are VRChat-ready.

## Upstreams
- Official full templates and blueprints: https://github.com/Comfy-Org/workflow_templates
- Official examples: https://github.com/comfyanonymous/ComfyUI_examples
- Comfy-Org organization: https://github.com/orgs/Comfy-Org/repositories
- Community video workflows: https://github.com/kijai/ComfyUI-WanVideoWrapper and https://github.com/pjecuacion/comfyui_workflows
- 3D workflows: https://github.com/Alex92908/image-to-3d-comfyui
- Audio/TTS workflows: https://github.com/skyiron/ComfyUI-TTS-Audio-Suite and https://github.com/wildminder/ComfyUI-Chatterbox
- VRChat-oriented integration: https://github.com/AEmotionStudio/ComfyUI-VRChat-Assets
- Community workflow catalogs: https://www.comfyworkflows.com/ , https://civitai.com/ , https://openart.ai/

The last three are **discovery surfaces**, not guaranteed sources of downloadable JSON. Their APIs, terms and permissions must be respected; no unsupported scraping is performed.

## Provenance, execution, and publication
- `registry/official.json`, `registry/community.json`: all discovered repository records.
- `registry/practices.json`: source-commit-pinned JSON candidate URLs, blob hashes, first/last observation.
- `registry/insights.json`: static inspection only; no user prompts stored.
- `catalog/all-workflows.csv`: every candidate preserved, even unmatched; importable in Google Sheets.
- `catalog/by-usecase.json`: cross-category IDs, never exclusive classifications.
- `catalog/index.md`: browseable category examples with links to the pinned original files.
- `config/use-cases.json`: editable keyword dictionary. Categorization is a search aid, never a quality rating.
- Production/BOOTH requires separate licensing verification. VRChat/world creation also requires Blender, Unity, VRChat SDK, rigging, performance checks and upload.

For the current collector run `PYTHONPATH=src python -m gwp.discovery sync`, followed by `python scripts/build_catalog.py`. The GitHub Action performs both automatically every six hours. The older `scripts/practice_registry.py` and `scripts/audit_practices.py` belong to a retired, signal-scored collector and are not part of the active scheduled pipeline.
