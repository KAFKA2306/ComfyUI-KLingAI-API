"""Stable request contract, independent of any ComfyUI node schema."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GenerationRequest:
    workflow_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    request_id: str | None = None

    def __post_init__(self) -> None:
        if not self.workflow_id or not self.workflow_id.strip():
            raise ValueError("workflow_id is required")
        if not isinstance(self.inputs, dict):
            raise TypeError("inputs must be a dict")
