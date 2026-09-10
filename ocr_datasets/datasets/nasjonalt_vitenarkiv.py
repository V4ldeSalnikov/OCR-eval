from collections.abc import Iterable

import pypdfium2 as pdfium
from datasets import Pdf, load_dataset

from ocr_datasets.dataset_interface import (
    OCRDocument,
    PageAnnotation,
    PageDatasetSource,
)


class NasjonaltVitenarkiv(PageDatasetSource):
    id = "nasjonalt-vitenarkiv"
    languages = ["nob", "nno", "nor"]
    source = "danish-foundation-models/nasjonalt-vitenarkiv"
    revision = "5db862bd176c960d891ce1779cf18d05785cdab5"
    pdf_ids = {
        "698566db-b621-4af2-b33e-819d589eae33",
        "2e628ee1-d60a-4e2b-8349-69cb0b30e185",
        "08c30d7d-5e27-4d6b-86f4-e91f638dc541",
        "996afa1c-9d32-4caa-a712-6b048a2f6081",
        "63a14955-b0c1-43eb-9308-4abd495f7602",
        "d4e01f1d-4d73-471e-809a-5db01435e82c",
        "fcc210ed-e297-4952-8a80-18b14b96c9ef",
        "ab8119d5-4baa-4023-bbef-632fbdee78bf",
        "dc078c8e-4cf3-4bda-8d80-c60159158ee2",
        "886fc4fb-2b66-48fa-978d-b7986827f416",
        "d6d88c13-dac3-4546-b75e-a0a878adbeaa",
        "fba8f1d6-e2e6-4e2a-818f-db91a1777ec2",
        "8a03d469-e21e-4ab6-935a-35d4a6cb527c",
        "ee746cfd-2bba-484e-92c4-5ba934334017",
        "0e98590e-2251-4b99-8fb4-90718f34f7a3",
        "8822ae70-99fc-41c2-aaac-5de6acace8dc",
        "ccd57e74-440e-4ee2-896c-3ceccaa5dc5e",
        "a488274c-5130-480b-bc17-519f45efe8ef",
        "2c9c3c5f-61d2-491e-916d-460e79744582",
    }

    def __init__(
        self,
        streaming: bool = False,
        dpi: int = 300,
    ):
        self.streaming = streaming
        self.dpi = dpi

    def load_documents(self) -> Iterable[OCRDocument]:
        documents = load_dataset(
            self.source,
            split="train",
            streaming=self.streaming,
            revision=self.revision,
            columns=[
                "id",
                "publication_identifier",
                "url",
                "handle",
                "title",
                "year",
                "language",
                "license",
                "pdf",
            ],
        ).cast_column("pdf", Pdf(decode=False))

        for document in documents:
            if document["id"] not in self.pdf_ids:
                continue

            yield OCRDocument(
                id=document["id"],
                pages=self._load_pages(document),
                metadata={
                    "source": self.source,
                    "revision": self.revision,
                    "split": "train",
                    "pdf_id": document["id"],
                    "publication_id": document["publication_identifier"],
                    "url": document["url"],
                    "handle": document["handle"],
                    "title": document["title"],
                    "year": document["year"],
                    "lang": document["language"],
                    "license": document["license"],
                },
            )

    def _load_pages(self, document: dict) -> Iterable[PageAnnotation]:
        with pdfium.PdfDocument(document["pdf"]["bytes"]) as pdf:
            for page_index in range(len(pdf)):
                page = pdf[page_index]
                text_page = page.get_textpage()
                text = text_page.get_text_range().replace("\r\n", "\n").strip()
                text_page.close()

                if not text:
                    page.close()
                    continue

                bitmap = page.render(scale=self.dpi / 72)
                image = bitmap.to_pil().copy()
                bitmap.close()
                page.close()

                page_number = page_index + 1
                yield PageAnnotation(
                    name=f"nva-{document['id']}-p{page_number}",
                    image=image,
                    text=text,
                    metadata={
                        "page": page_number,
                        "dpi": self.dpi,
                        "reference_type": "pdf_text",
                        "reference_tool": "pdfium",
                    },
                )
