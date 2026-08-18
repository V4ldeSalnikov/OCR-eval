# pip install datasets pillow

from datasets import load_dataset
from pydantic_evals import Case, Dataset
from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset

from PIL import Image
# your helpers (moved out)
from ocr_datasets.utility_functions.XML_load_helper import parse_alto,crop as crop_img

class DanishHistoricalHandwriting(OCRDataset):
    id = "historical-danish-handwriting"
    languages = ["da"]
    default_evaluator = StandardEvaluator()

    def __init__(self, max_examples: int | None = None, streaming: bool = False, margin: int = 2, max_pages : int = 1):
        self.max_examples = max_examples
        self.streaming = streaming
        self.margin = margin
        self.max_pages = max_pages

    def load_dataset(self) -> Dataset:

        ds = load_dataset(
            "aarhus-city-archives/historical-danish-handwriting",
            split="train",
            streaming=self.streaming
        )

        cases = []

        for id, ex in enumerate(ds):

            if id >= self.max_pages:
                break

            page_img: Image.Image = ex["image"]
            alto_xml: str | None = ex.get("alto")
            doc_id = ex.get("doc_id")
            seq = ex.get("sequence")

            if not alto_xml:
                continue

            for i, (x, y, w, h, gt_text) in enumerate(parse_alto(alto_xml)):

                if self.max_examples is not None and i >= self.max_examples:
                    break

                line_crop = crop_img(page_img, x, y, w, h, margin=self.margin)

                cases.append(
                    Case(
                        name=f"dkhist-{doc_id}-{i}",
                        inputs=OCRInput(image=line_crop),
                        expected_output=gt_text,
                        metadata={
                            "source": "aarhus-city-archives/historical-danish-handwriting",
                            "doc_id": int(doc_id) if doc_id is not None else None,
                            "sequence": int(seq) if seq is not None else None,
                            "line_bbox": [int(x), int(y), int(w), int(h)],
                            "xml": "ALTO",
                            "lang": "da",
                        },
                    )
                )




        return Dataset(name=self.id, cases=cases, evaluators=[self.default_evaluator])
