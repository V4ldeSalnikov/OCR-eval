from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from models.model_interface import OCRModel


@dataclass(frozen=True)
class ModelMeta:
    loader: Callable[..., "OCRModel"]
    name: str
    supported_tasks: tuple[str, ...]
    loader_kwargs: Mapping[str, Any] = field(default_factory=dict)

    family: str | None = None
    languages: Iterable[str] | None = None
    license: str | None = None
    reference: str | None = None
    notes: str | None = None

    def validate_task(self, task: str) -> None:
        if task not in self.supported_tasks:
            supported = ", ".join(self.supported_tasks)
            raise ValueError(
                f"Model '{self.name}' does not support task '{task}'. "
                f"Supported tasks: {supported}"
            )

    def load(self, task: str, **overrides: Any) -> OCRModel:
        self.validate_task(task)
        loader_kwargs = dict(self.loader_kwargs)
        loader_kwargs.update(overrides)
        loader_kwargs["task"] = task
        return self.loader(**loader_kwargs)
