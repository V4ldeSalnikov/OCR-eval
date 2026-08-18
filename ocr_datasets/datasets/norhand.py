
from datasets import load_dataset
from pydantic_evals import Case, Dataset
from evaluators.standard_evaluator import StandardEvaluator
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDataset

class Norhand(OCRDataset):
    id = "NorHand-v2-line"
    languages = ["nob"]
    default_evaluator = StandardEvaluator()

    def __init__(self, split: str = "test", max_examples: int | None = None, streaming: bool = False):
        """
        split - which split is being used (train, validation or test)
        max_examples: maximum number of examples used for evaluation
        streaming: use HF streaming to avoid downloading complete dataset
        """
        self.split = split
        self.max_examples = max_examples
        self.streaming = streaming

    def load_dataset(self) -> Dataset:
        hf = load_dataset(
            "Teklia/NorHand-v2-line",
            split=self.split,
            streaming=self.streaming
        )


        iterator = hf if self.streaming else iter(hf)

        cases = []
        for i, test_case in enumerate(iterator):
            if self.max_examples is not None and i >= self.max_examples:
                break

            img = test_case["image"]
            gt_text = test_case["text"]

            cases.append(
                Case(
                    name=f"norhand-{self.split}-{i}",
                    inputs=OCRInput(image=img),
                    expected_output=gt_text,
                    metadata={
                        "source": "Teklia/NorHand-v2-line",
                        "split": self.split,
                        "lang": "nob"
                    },
                )
            )

        return Dataset(name=self.id, cases=cases, evaluators=[self.default_evaluator])


