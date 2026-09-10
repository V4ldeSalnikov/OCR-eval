from collections.abc import Iterable

from datasets import load_dataset

from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class SwedishFrakturLines(LineDatasetSource):
    id = "swedish-fraktur-lines"
    languages = ["swe"]

    def __init__(self, streaming: bool = False):
        self.streaming = streaming

    def load_lines(self) -> Iterable[LineSample]:
        lines = load_dataset(
            "Riksarkivet/swedish_fraktur",
            split="train",
            streaming=self.streaming,
        )

        for index, example in enumerate(lines):
            yield LineSample(
                name=f"swedish-fraktur-train-{index}",
                image=example["image"],
                text=example["text"],
                metadata={
                    "source": "Riksarkivet/swedish_fraktur",
                    "split": "train",
                    "lang": "swe",
                },
            )
