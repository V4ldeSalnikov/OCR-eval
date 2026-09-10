from collections.abc import Iterable

from datasets import load_dataset

from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class Norhand(LineDatasetSource):
    id = "NorHand-v2-line"
    languages = ["nob"]

    def __init__(self, split: str = "test", streaming: bool = False):
        self.split = split
        self.streaming = streaming

    def load_lines(self) -> Iterable[LineSample]:
        lines = load_dataset(
            "Teklia/NorHand-v2-line",
            split=self.split,
            streaming=self.streaming,
        )

        for index, example in enumerate(lines):
            yield LineSample(
                name=f"norhand-{self.split}-{index}",
                image=example["image"],
                text=example["text"],
                metadata={
                    "source": "Teklia/NorHand-v2-line",
                    "split": self.split,
                    "lang": "nob",
                },
            )
