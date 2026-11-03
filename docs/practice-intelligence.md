# ComfyUI Community Practice Intelligence

Goal: continuously learn from real-world ComfyUI work by official maintainers and
independent creators. The canonical asset is evidence of an actual implementation,
not a copy of upstream code.

## Discovery flow (every six hours)

1. Fetch every public Comfy-Org repository, including archived projects.
2. Search public community projects for workflows, subgraphs, blueprints, custom nodes,
   and 3D workflows, while retaining curated sources.
3. Scan selected Git trees to discover JSON examples. Record paths, exact commit SHAs,
   content-based blob hashes, first seen and last changed timestamps.
4. Detect duplicates by Git blob SHA. Rank by search signals only.
5. Run unit tests and catalog validation; automatically merge metadata changes through
   a GitHub PR, or push validated metadata directly if Actions cannot create PRs.

## Canonical data and lifecycle

- config/practice-sources.json: discovery configuration
- registry/official.json: complete official repository inventory
- registry/community.json: independent creator inventory
- registry/practices.json: candidate workflow/blueprint paths and provenance
- registry/decisions.json: independent adoption decisions
- dependencies/sources.lock.json: observed latest upstream commits, NOT deployed versions

The discovery process never downloads executable dependencies, installs custom nodes,
imports JSON into ComfyUI, or deploys a runtime. File extensions and popularity are not
proof of working output. All entries are explicitly unverified.

## Qualification to adopt an implementation

Discovery -> original license verification -> review model and custom node requirements ->
normalize input/output contracts -> validate node types -> pin exact model and node
revisions -> reproduce on RTX 3060 12 GB -> score image/video/3D quality, time and peak VRAM ->
promote versioned workflow/blueprint and keep rollback.

GPU runtime promotion is not automated here: no compatible self-hosted GPU runner has been
verified. An external revision update must not silently change a running environment.

## Source links

https://github.com/orgs/Comfy-Org/repositories
https://github.com/Comfy-Org/workflow_templates
https://github.com/Comfy-Org/workflows
https://github.com/comfyanonymous/ComfyUI_examples
https://github.com/ZHO-ZHO-ZHO/ComfyUI-Workflows-ZHO
https://github.com/cubiq/ComfyUI_Workflows
https://registry.comfy.org/
