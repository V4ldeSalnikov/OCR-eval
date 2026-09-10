from collections.abc import Iterable
from itertools import islice

from pydantic_evals import Case, Dataset

from metrics.metrics import cer, wer
from models.model_interface import OCRInput
from ocr_datasets.dataset_interface import OCRDatasetSource, PageDatasetSource
from tasks.task_interface import OCRTask


class PageTranscriptionTask(OCRTask):
    id = "page-transcription"
    metrics = {"cer": cer, "wer": wer}

    def build_dataset(
        self,
        source: OCRDatasetSource,
        max_examples: int | None = None,
    ) -> Dataset:
        if not isinstance(source, PageDatasetSource):
            raise TypeError(
                f"Task '{self.id}' requires a page dataset source: {source.id}"
            )

        cases = self._build_cases(source)
        if max_examples is not None:
            cases = islice(cases, max_examples)

        return Dataset(
            name=source.id,
            cases=list(cases),
        )

    def _build_cases(self, source: PageDatasetSource) -> Iterable[Case]:
        for document in source.load_documents():
            for page in document.pages:
                yield Case(
                    name=page.name,
                    inputs=OCRInput(image=page.image),
                    expected_output=page.text,
                    metadata={**document.metadata, **page.metadata},
                )
