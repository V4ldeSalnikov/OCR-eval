from ocr_datasets.dataset_interface import OCRDataset
from ocr_datasets.datasets.historical_danish_handwriting import DanishHistoricalHandwriting
from ocr_datasets.datasets.norhand import Norhand
from ocr_datasets.datasets.simple_dataset import SimpleDataset


def create_simple_dataset(max_examples: int | None) -> OCRDataset:
    return SimpleDataset(max_examples=max_examples)


def create_norhand_dataset(max_examples: int | None) -> OCRDataset:
    return Norhand(max_examples=max_examples, streaming=True)


def create_historical_danish_dataset(max_examples: int | None) -> OCRDataset:
    return DanishHistoricalHandwriting(max_examples=max_examples, streaming=True)


DATASET_REGISTRY = {
    "simple": create_simple_dataset,
    "norhand": create_norhand_dataset,
    "historical-danish": create_historical_danish_dataset,
}


def get_dataset(name: str, max_examples: int | None = None) -> OCRDataset:
    return DATASET_REGISTRY[name](max_examples)
