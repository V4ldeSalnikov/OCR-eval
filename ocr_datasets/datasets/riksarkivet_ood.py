from collections.abc import Iterable

from datasets import load_dataset

from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class RiksarkivetOODLines(LineDatasetSource):
    id = "riksarkivet-ood-lines"
    languages = ["swe"]

    def __init__(self, streaming: bool = False):
        self.streaming = streaming

    def load_lines(self) -> Iterable[LineSample]:
        lines = load_dataset(
            "Riksarkivet/eval_htr_out_of_domain_lines",
            split="test",
            streaming=self.streaming,
        )

        for index, example in enumerate(lines):
            yield LineSample(
                name=f"riksarkivet-ood-test-{index}",
                image=example["image"],
                text=example["transcription"],
                metadata={
                    "source": "Riksarkivet/eval_htr_out_of_domain_lines",
                    "split": "test",
                    "lang": "swe",
                },
            )
