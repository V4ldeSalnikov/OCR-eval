from abc import ABC, abstractmethod

from pydantic_evals import Dataset

from ocr_datasets.dataset_interface import OCRDataset


class OCRTask(ABC):
    id: str

    @abstractmethod
    def build_dataset(self, source: OCRDataset) -> Dataset:
        ...
