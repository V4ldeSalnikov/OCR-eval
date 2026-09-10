from ocr_datasets.dataset_interface import OCRDatasetSource
from ocr_datasets.datasets.danish_typewritten import DanishTypewrittenLines
from ocr_datasets.datasets.historical_danish_handwriting import DanishHistoricalHandwriting
from ocr_datasets.datasets.modern_danish_handwriting import ModernDanishHandwriting
from ocr_datasets.datasets.nasjonalt_vitenarkiv import NasjonaltVitenarkiv
from ocr_datasets.datasets.norhand import Norhand
from ocr_datasets.datasets.oj4ocrmt import OJ4OCRMT
from ocr_datasets.datasets.riksarkivet_ood import RiksarkivetOODLines
from ocr_datasets.datasets.simple_dataset import SimpleDataset
from ocr_datasets.datasets.swedish_fraktur import SwedishFrakturLines


def create_simple_dataset() -> OCRDatasetSource:
    return SimpleDataset()


def create_norhand_dataset() -> OCRDatasetSource:
    return Norhand(streaming=True)


def create_historical_danish_dataset() -> OCRDatasetSource:
    return DanishHistoricalHandwriting(streaming=True)


def create_modern_danish_dataset() -> OCRDatasetSource:
    return ModernDanishHandwriting(streaming=True)


def create_danish_typewritten_dataset() -> OCRDatasetSource:
    return DanishTypewrittenLines(streaming=True)


def create_riksarkivet_ood_dataset() -> OCRDatasetSource:
    return RiksarkivetOODLines(streaming=True)


def create_swedish_fraktur_dataset() -> OCRDatasetSource:
    return SwedishFrakturLines(streaming=True)


def create_oj4ocrmt_danish_dataset() -> OCRDatasetSource:
    return OJ4OCRMT(language="da")


def create_oj4ocrmt_swedish_dataset() -> OCRDatasetSource:
    return OJ4OCRMT(language="sv")


def create_nasjonalt_vitenarkiv_dataset() -> OCRDatasetSource:
    return NasjonaltVitenarkiv(streaming=True)


DATASET_REGISTRY = {
    "simple": create_simple_dataset,
    "norhand": create_norhand_dataset,
    "historical-danish": create_historical_danish_dataset,
    "modern-danish": create_modern_danish_dataset,
    "danish-typewritten": create_danish_typewritten_dataset,
    "riksarkivet-ood": create_riksarkivet_ood_dataset,
    "swedish-fraktur": create_swedish_fraktur_dataset,
    "oj4ocrmt-danish": create_oj4ocrmt_danish_dataset,
    "oj4ocrmt-swedish": create_oj4ocrmt_swedish_dataset,
    "nasjonalt-vitenarkiv": create_nasjonalt_vitenarkiv_dataset,
}


def get_dataset(name: str) -> OCRDatasetSource:
    return DATASET_REGISTRY[name]()
