from datasets import load_dataset
from pydantic_evals import Case, Dataset

from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset


class SwedishFrakturLines(OCRDataset):
    id = "swedish-fraktur-lines"
    languages = ["swe"]
    default_evaluator = StandardEvaluator()

    def __init__(self, max_examples: int | None = None, streaming: bool = False):
        self.max_examples = max_examples
        self.streaming = streaming

    def load_dataset(self) -> Dataset:
        hf = load_dataset(
            "Riksarkivet/swedish_fraktur",
            split="train",
            streaming=self.streaming,
        )

        cases = []
        for index, example in enumerate(hf):
            if self.max_examples is not None and index >= self.max_examples:
                break

            cases.append(
                Case(
                    name=f"swedish-fraktur-train-{index}",
                    inputs=OCRInput(image=example["image"]),
                    expected_output=example["text"],
                    metadata={
                        "source": "Riksarkivet/swedish_fraktur",
                        "split": "train",
                        "lang": "swe",
                    },
                )
            )

        return Dataset(name=self.id, cases=cases, evaluators=[self.default_evaluator])
