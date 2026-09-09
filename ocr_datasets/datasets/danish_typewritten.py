from datasets import load_dataset
from pydantic_evals import Case, Dataset

from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset


class DanishTypewrittenLines(OCRDataset):
    id = "danish-typewritten-lines"
    languages = ["da"]
    default_evaluator = StandardEvaluator()

    def __init__(self, max_examples: int | None = None, streaming: bool = False):
        self.max_examples = max_examples
        self.streaming = streaming

    def load_dataset(self) -> Dataset:
        hf = load_dataset(
            "V4ldeLund/ehri-danish-typewritten-lines",
            split="test",
            streaming=self.streaming,
        )

        cases = []
        for index, example in enumerate(hf):
            if self.max_examples is not None and index >= self.max_examples:
                break

            cases.append(
                Case(
                    name=f"danish-typewritten-{example['id']}",
                    inputs=OCRInput(image=example["image"]),
                    expected_output=example["text"],
                    metadata={
                        "source": "V4ldeLund/ehri-danish-typewritten-lines",
                        "split": "test",
                        "page_id": example["page_id"],
                        "line_id": example["line_id"],
                        "line_bbox": example["line_bbox"],
                        "source_image": example["source_image"],
                        "lang": "da",
                    },
                )
            )

        return Dataset(name=self.id, cases=cases, evaluators=[self.default_evaluator])
