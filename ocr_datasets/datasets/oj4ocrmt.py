from collections import defaultdict
from collections.abc import Iterable
from io import BytesIO

from huggingface_hub import HfFileSystem
from PIL import Image

from ocr_datasets.dataset_interface import (
    OCRDocument,
    PageAnnotation,
    PageDatasetSource,
)


class OJ4OCRMT(PageDatasetSource):
    source = "hltcoe/OJ4OCRMT"
    language_names = {"da": "danish", "sv": "swedish"}

    def __init__(
        self,
        language: str,
        split: str = "test",
        page_type: str = "regular",
        dpi: int = 300,
    ):
        self.language = language
        self.languages = [language]
        self.id = f"oj4ocrmt-{self.language_names[language]}"
        self.split = split
        self.page_type = page_type
        self.dpi = dpi
        self.files = HfFileSystem()
        self.root = f"datasets/{self.source}"

    def load_documents(self) -> Iterable[OCRDocument]:
        documents = self._load_split()

        for doc_id, page_numbers in documents.items():
            yield OCRDocument(
                id=doc_id,
                pages=self._load_pages(doc_id, page_numbers),
                metadata={
                    "source": self.source,
                    "split": self.split,
                    "page_type": self.page_type,
                    "doc_id": doc_id,
                    "license": "CC-BY-4.0",
                },
            )

    def _load_split(self) -> dict[str, list[int]]:
        documents = defaultdict(list)
        split_path = f"{self.root}/splitfiles/{self.split}.{self.page_type}.txt"

        with self.files.open(split_path, "r", encoding="utf-8") as split_file:
            for row in split_file:
                doc_id, page_number = row.rstrip().split("\t")
                documents[doc_id].append(int(page_number))

        return dict(documents)

    def _load_pages(
        self,
        doc_id: str,
        page_numbers: list[int],
    ) -> Iterable[PageAnnotation]:
        for page_number in page_numbers:
            filename = f"{doc_id}:FULL.{self.language}.p-{page_number}"
            document_path = f"{self.root}/{self.split}/{doc_id}"
            text_path = f"{document_path}/raw/{filename}.txt"
            image_path = f"{document_path}/png{self.dpi}/{filename}.png"

            with self.files.open(text_path, "r", encoding="utf-8") as text_file:
                text = text_file.read().strip()

            with self.files.open(image_path, "rb") as image_file:
                image = Image.open(BytesIO(image_file.read())).convert("RGB")

            yield PageAnnotation(
                name=f"oj4ocrmt-{self.language}-{doc_id}-p{page_number}",
                image=image,
                text=text,
                metadata={
                    "page": page_number,
                    "dpi": self.dpi,
                    "lang": self.language,
                    "reference_type": "pdf_text",
                    "reference_tool": "pdftotext",
                },
            )
