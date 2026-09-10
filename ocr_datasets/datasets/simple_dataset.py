from collections.abc import Iterable
from pathlib import Path

from PIL import Image

from ocr_datasets.dataset_interface import LineDatasetSource, LineSample


class SimpleDataset(LineDatasetSource):
    id = "simple_dataset"
    languages = ["da"]

    def __init__(self, image_dir: Path | str | None = None):
        if image_dir is None:
            root = Path(__file__).resolve().parents[2]
            self.image_dir = root / "test_images"
        else:
            self.image_dir = Path(image_dir)

    def load_lines(self) -> Iterable[LineSample]:
        yield LineSample(
            name="first_case",
            image=Image.open(self.image_dir / "test_image_1.jpg"),
            text="Stå af og træk cyklen",
            metadata={"difficulty": "easy"},
        )
        yield LineSample(
            name="second_case",
            image=Image.open(self.image_dir / "test_image_2.jpg"),
            text="Knallert forbudt",
            metadata={"difficulty": "easy"},
        )
