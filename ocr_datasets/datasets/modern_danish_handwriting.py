from datasets import load_dataset
from pydantic_evals import Case, Dataset

from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset
from ocr_datasets.utility_functions.XML_load_helper import crop, parse_page


class ModernDanishHandwriting(OCRDataset):
    id = "modern-danish-handwriting"
    languages = ["da"]
    default_evaluator = StandardEvaluator()

    def __init__(
        self,
        max_examples: int | None = None,
        streaming: bool = False,
        margin: int = 2,
    ):
        self.max_examples = max_examples
        self.streaming = streaming
        self.margin = margin

    def load_dataset(self) -> Dataset:
        pages = load_dataset(
            "RA-Data-Science/modern-danish-handwriting",
            split="train",
            streaming=self.streaming,
        )

        cases = []
        for page in pages:
            if self.max_examples is not None and len(cases) >= self.max_examples:
                break

            page_image = page["image"]
            doc_id = int(page["doc_id"])
            sequence = int(page["sequence"])

            for line_index, (x, y, width, height, text) in enumerate(
                parse_page(page["page"])
            ):
                if self.max_examples is not None and len(cases) >= self.max_examples:
                    break

                line_image = crop(
                    page_image,
                    x,
                    y,
                    width,
                    height,
                    margin=self.margin,
                )

                cases.append(
                    Case(
                        name=f"modern-danish-{doc_id}-{sequence}-{line_index}",
                        inputs=OCRInput(image=line_image),
                        expected_output=text,
                        metadata={
                            "source": "RA-Data-Science/modern-danish-handwriting",
                            "split": "train",
                            "doc_id": doc_id,
                            "sequence": sequence,
                            "line_bbox": [x, y, width, height],
                            "xml": "PAGE",
                            "lang": "da",
                        },
                    )
                )

        return Dataset(name=self.id, cases=cases, evaluators=[self.default_evaluator])
