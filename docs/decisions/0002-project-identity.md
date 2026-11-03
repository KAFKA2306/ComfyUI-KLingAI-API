# ADR-0002: Comfy Workflow Atlas project identity

Status: superseded by ADR-0003 (2026-11-03)

- Display name: **Comfy Workflow Atlas**
- GitHub repository slug: `comfy-workflow-atlas`
- Python distribution: `comfy-workflow-atlas`
- Python import path: `gwp` (kept stable for existing scripts and tests)

The canonical subject is a broad, source-preserving registry of real ComfyUI practices.
A workflow is the executable composition; subgraphs and blueprints are first-class
discoverable assets. Image, video, audio, 3D, VRChat, game worlds and other use cases
are not excluded by the project name.

The name does not imply subjective quality scoring or automatic adoption.
Collection, evidence, inspection and repeatability remain distinct.

GitHub repository rename requires administration access in GitHub Settings.
After the GitHub slug is changed, verify redirects, Actions permissions, connected
apps, badges, external links and clone URLs. Git history and PRs must be retained.
Do not delete or recreate the repository just to change its name.
