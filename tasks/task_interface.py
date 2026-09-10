from abc import ABC, abstractmethod

from pydantic_evals import Dataset

from ocr_datasets.dataset_interface import OCRDatasetSource


class OCRTask(ABC):
    id: str

    @abstractmethod
    def build_dataset(
        self,
        source: OCRDatasetSource,
        max_examples: int | None = None,
    ) -> Dataset:
        ...
