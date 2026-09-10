from pydantic_evals import Dataset

from ocr_datasets.dataset_interface import OCRDataset
from tasks.task_interface import OCRTask


class LineRecognitionTask(OCRTask):
    id = "line-recognition"

    def build_dataset(self, source: OCRDataset) -> Dataset:
        return source.load_dataset()
