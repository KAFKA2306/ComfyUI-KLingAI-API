# Generative Workflow Platform

Model-agnostic ComfyUI workflow engineering, versioned contracts, and reproducible evaluation.

## Architecture

Application/Agent -> Python API contract -> Workflow registry -> ComfyUI runtime -> Model adapters.

This repository intentionally replaces the legacy Kling API custom-node implementation. Old history remains available through Git history. ComfyUI itself is an upstream dependency, not a fork.

## Layout

- `src/gwp/`: API contracts, orchestration, ComfyUI adapter
- `workflows/`: versioned ComfyUI API-format workflows
- `blueprints/`: reusable subgraphs
- `contracts/`: stable input/output schema
- `benchmarks/`: fixed cases and evaluation results
- `environments/`: hardware profiles
- `dependencies/`: upstream revision locks
- `docs/decisions/`: architecture decisions

## Validate

`python -m unittest discover -s tests -v`

Python 3.11+; standard library only for the core. No model weights or secrets in Git.
