from collections.abc import Iterable
from itertools import groupby, islice

from datasets import load_dataset

from ocr_datasets.dataset_interface import (
    LineAnnotation,
    LineAnnotatedPageDatasetSource,
    OCRDocument,
    PageAnnotation,
)
from ocr_datasets.utility_functions.XML_load_helper import parse_alto


class DanishHistoricalHandwriting(LineAnnotatedPageDatasetSource):
    id = "historical-danish-handwriting"
    languages = ["da"]

    def __init__(
        self,
        streaming: bool = False,
        max_pages: int | None = None,
    ):
        self.streaming = streaming
        self.max_pages = max_pages

    def load_documents(self) -> Iterable[OCRDocument]:
        dataset = load_dataset(
            "aarhus-city-archives/historical-danish-handwriting",
            split="train",
            streaming=self.streaming,
        )

        indexed_pages = enumerate(dataset)
        if self.max_pages is not None:
            indexed_pages = islice(indexed_pages, self.max_pages)

        documents = groupby(
            indexed_pages,
            key=lambda indexed_page: indexed_page[1].get("doc_id"),
        )

        for doc_id, pages in documents:
            yield OCRDocument(
                id=str(doc_id),
                pages=self._load_pages(pages),
                metadata={
                    "source": "aarhus-city-archives/historical-danish-handwriting",
                    "doc_id": int(doc_id) if doc_id is not None else None,
                },
            )

    def _load_pages(
        self,
        pages: Iterable[tuple[int, dict]],
    ) -> Iterable[PageAnnotation]:
        for page_index, page in pages:
            alto_xml = page.get("alto")
            if not alto_xml:
                continue

            doc_id = page.get("doc_id")
            sequence = page.get("sequence")
            lines = [
                LineAnnotation(
                    bbox=(int(x), int(y), int(width), int(height)),
                    text=text,
                )
                for x, y, width, height, text in parse_alto(alto_xml)
            ]

            yield PageAnnotation(
                name=f"dkhist-{doc_id}-{page_index}",
                image=page["image"],
                text="\n".join(line.text for line in lines),
                metadata={
                    "sequence": int(sequence) if sequence is not None else None,
                    "xml": "ALTO",
                    "lang": "da",
                },
                lines=lines,
            )
