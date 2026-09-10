from collections.abc import Iterable

from datasets import load_dataset
from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class GothenburgPriceTag(LineDatasetSource):
    id = "gothenburg-price-tag"
    languages = ["swe"]

    def __init__(self, split: str = "test", streaming: bool = False):
        self.split = split
        self.streaming = streaming

    def load_lines(self) -> Iterable[LineSample]:
        hf = load_dataset(
            "fangsonglong/gothenburg-price-tag",
            split=self.split,
            streaming=self.streaming
        )

        for index, example in enumerate(hf):
            yield LineSample(
                name=f"norhand-{self.split}-{index}",
                image=example["image"],
                text=example["name"],
                metadata={
                    "source": "fangsonglong/gothenburg-price-tag",
                    "split": self.split,
                    "lang": "nob",
                },
            )


