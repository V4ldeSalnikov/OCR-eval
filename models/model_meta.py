from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any, Mapping, Iterable

from models.model_interface import OCRModel

@dataclass(frozen=True)
class ModelMeta:
    loader: Callable[..., "OCRModel"]
    name: str
    loader_kwargs: Mapping[str, Any] = field(default_factory=dict)

    family: str | None = None
    languages: Iterable[str] | None = None
    license: str | None = None
    reference: str | None = None
    notes: str | None = None

    def load(self, **overrides):
        kw = dict(self.loader_kwargs)
        kw.update(overrides)
        return self.loader(**kw)