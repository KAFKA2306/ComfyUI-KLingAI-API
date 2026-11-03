# ADR-0001: Replace legacy Kling plugin with a model-agnostic platform

Status: accepted (2026-11-03)

Decision: fully replace the repository working tree. Preserve history via Git; do not carry forward legacy Kling-specific API clients, custom nodes, or frontend assets. Use ComfyUI as an external runtime, version workflow contracts, and isolate model adapters.

Rationale: avoid tying the architecture to a vendor API or custom-node version. Changes to external models must not require changes to the public application contract.
