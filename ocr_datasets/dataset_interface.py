from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field

from PIL import Image


@dataclass
class LineAnnotation:
    bbox: tuple[int, int, int, int]
    text: str


@dataclass
class PageAnnotation:
    name: str
    image: Image.Image
    text: str
    metadata: dict
    lines: list[LineAnnotation] = field(default_factory=list)


@dataclass
class OCRDocument:
    id: str
    pages: Iterable[PageAnnotation]
    metadata: dict


@dataclass
class LineSample:
    name: str
    image: Image.Image
    text: str
    metadata: dict


class OCRDatasetSource(ABC):
    id: str
    languages: list[str]


class LineDatasetSource(OCRDatasetSource):
    @abstractmethod
    def load_lines(self) -> Iterable[LineSample]:
        ...


class PageDatasetSource(OCRDatasetSource):
    @abstractmethod
    def load_documents(self) -> Iterable[OCRDocument]:
        ...


class LineAnnotatedPageDatasetSource(PageDatasetSource):
    pass
