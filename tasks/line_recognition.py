from collections.abc import Iterable
from itertools import islice

from pydantic_evals import Case, Dataset

from metrics.metrics import cer, wer
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import (
    LineAnnotatedPageDatasetSource,
    LineDatasetSource,
    OCRDatasetSource,
)
from ocr_datasets.utility_functions.XML_load_helper import crop
from tasks.task_interface import OCRTask


class LineRecognitionTask(OCRTask):
    id = "line-recognition"
    metrics = {"cer": cer, "wer": wer}

    def __init__(self, margin: int = 2):
        self.margin = margin

    def build_dataset(
        self,
        source: OCRDatasetSource,
        max_examples: int | None = None,
    ) -> Dataset:
        cases = self._build_cases(source)
        if max_examples is not None:
            cases = islice(cases, max_examples)

        return Dataset(
            name=source.id,
            cases=list(cases),
        )

    def _build_cases(self, source: OCRDatasetSource) -> Iterable[Case]:
        if isinstance(source, LineDatasetSource):
            return self._line_cases(source)
        if isinstance(source, LineAnnotatedPageDatasetSource):
            return self._page_line_cases(source)
        raise TypeError(f"Task '{self.id}' requires line annotations: {source.id}")

    def _line_cases(self, source: LineDatasetSource) -> Iterable[Case]:
        for line in source.load_lines():
            yield Case(
                name=line.name,
                inputs=OCRInput(image=line.image),
                expected_output=line.text,
                metadata=line.metadata,
            )

    def _page_line_cases(
        self,
        source: LineAnnotatedPageDatasetSource,
    ) -> Iterable[Case]:
        for document in source.load_documents():
            for page in document.pages:
                for line_index, line in enumerate(page.lines):
                    yield Case(
                        name=f"{page.name}-{line_index}",
                        inputs=OCRInput(
                            image=crop(
                                page.image,
                                *line.bbox,
                                margin=self.margin,
                            )
                        ),
                        expected_output=line.text,
                        metadata={
                            **document.metadata,
                            **page.metadata,
                            "line_bbox": list(line.bbox),
                        },
                    )
