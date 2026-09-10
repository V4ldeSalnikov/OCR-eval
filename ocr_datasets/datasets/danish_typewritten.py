from collections.abc import Iterable

from datasets import load_dataset

from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class DanishTypewrittenLines(LineDatasetSource):
    id = "danish-typewritten-lines"
    languages = ["da"]

    def __init__(self, streaming: bool = False):
        self.streaming = streaming

    def load_lines(self) -> Iterable[LineSample]:
        lines = load_dataset(
            "V4ldeLund/ehri-danish-typewritten-lines",
            split="test",
            streaming=self.streaming,
        )

        for example in lines:
            yield LineSample(
                name=f"danish-typewritten-{example['id']}",
                image=example["image"],
                text=example["text"],
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
