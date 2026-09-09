from ocr_datasets.dataset_interface import OCRDataset
from ocr_datasets.datasets.danish_typewritten import DanishTypewrittenLines
from ocr_datasets.datasets.historical_danish_handwriting import DanishHistoricalHandwriting
from ocr_datasets.datasets.modern_danish_handwriting import ModernDanishHandwriting
from ocr_datasets.datasets.norhand import Norhand
from ocr_datasets.datasets.riksarkivet_ood import RiksarkivetOODLines
from ocr_datasets.datasets.simple_dataset import SimpleDataset
from ocr_datasets.datasets.swedish_fraktur import SwedishFrakturLines


def create_simple_dataset(max_examples: int | None) -> OCRDataset:
    return SimpleDataset(max_examples=max_examples)


def create_norhand_dataset(max_examples: int | None) -> OCRDataset:
    return Norhand(max_examples=max_examples, streaming=True)


def create_historical_danish_dataset(max_examples: int | None) -> OCRDataset:
    return DanishHistoricalHandwriting(max_examples=max_examples, streaming=True)


def create_modern_danish_dataset(max_examples: int | None) -> OCRDataset:
    return ModernDanishHandwriting(max_examples=max_examples, streaming=True)


def create_danish_typewritten_dataset(max_examples: int | None) -> OCRDataset:
    return DanishTypewrittenLines(max_examples=max_examples, streaming=True)


def create_riksarkivet_ood_dataset(max_examples: int | None) -> OCRDataset:
    return RiksarkivetOODLines(max_examples=max_examples, streaming=True)


def create_swedish_fraktur_dataset(max_examples: int | None) -> OCRDataset:
    return SwedishFrakturLines(max_examples=max_examples, streaming=True)


DATASET_REGISTRY = {
    "simple": create_simple_dataset,
    "norhand": create_norhand_dataset,
    "historical-danish": create_historical_danish_dataset,
    "modern-danish": create_modern_danish_dataset,
    "danish-typewritten": create_danish_typewritten_dataset,
    "riksarkivet-ood": create_riksarkivet_ood_dataset,
    "swedish-fraktur": create_swedish_fraktur_dataset,
}


def get_dataset(name: str, max_examples: int | None = None) -> OCRDataset:
    return DATASET_REGISTRY[name](max_examples)
