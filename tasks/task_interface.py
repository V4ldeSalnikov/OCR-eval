from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic_evals import Dataset

from ocr_datasets.dataset_interface import OCRDatasetSource


MetricInput = str | list[str]
OCRMetric = Callable[[MetricInput, MetricInput], float]


class OCRTask(ABC):
    id: str
    metrics: dict[str, OCRMetric]

    def calculate_metrics(
        self,
        model_output: MetricInput,
        ground_truth: MetricInput,
    ) -> dict[str, float]:
        return {
            name: metric(model_output, ground_truth)
            for name, metric in self.metrics.items()
        }

    @abstractmethod
    def build_dataset(
        self,
        source: OCRDatasetSource,
        max_examples: int | None = None,
    ) -> Dataset:
        ...
