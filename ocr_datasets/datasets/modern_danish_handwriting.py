from collections.abc import Iterable
from itertools import groupby

from datasets import load_dataset

from ocr_datasets.dataset_interface import (
    LineAnnotation,
    OCRDocument,
    PageAnnotation,
    PageDatasetSource,
)
from ocr_datasets.utility_functions.XML_load_helper import parse_page


class ModernDanishHandwriting(PageDatasetSource):
    id = "modern-danish-handwriting"
    languages = ["da"]

    def __init__(self, streaming: bool = False):
        self.streaming = streaming

    def load_documents(self) -> Iterable[OCRDocument]:
        dataset = load_dataset(
            "RA-Data-Science/modern-danish-handwriting",
            split="train",
            streaming=self.streaming,
        )

        documents = groupby(dataset, key=lambda page: page["doc_id"])

        for doc_id, pages in documents:
            yield OCRDocument(
                id=str(doc_id),
                pages=self._load_pages(pages),
                metadata={
                    "source": "RA-Data-Science/modern-danish-handwriting",
                    "split": "train",
                    "doc_id": int(doc_id),
                },
            )

    def _load_pages(self, pages: Iterable[dict]) -> Iterable[PageAnnotation]:
        for page in pages:
            doc_id = int(page["doc_id"])
            sequence = int(page["sequence"])
            lines = [
                LineAnnotation(
                    bbox=(int(x), int(y), int(width), int(height)),
                    text=text,
                )
                for x, y, width, height, text in parse_page(page["page"])
            ]

            yield PageAnnotation(
                name=f"modern-danish-{doc_id}-{sequence}",
                image=page["image"],
                lines=lines,
                metadata={
                    "sequence": sequence,
                    "xml": "PAGE",
                    "lang": "da",
                },
            )
