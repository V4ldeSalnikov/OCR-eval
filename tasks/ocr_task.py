from itertools import batched

from pydantic_evals import Case, Dataset

from models.model_interface import OCRInput, OCROutput, OCRModel


def default_ocr_task(model: OCRModel):
    def task(inpt: OCRInput) -> str:
        return model(inpt).text

    return task


def run_batch_ocr(
    model: OCRModel,
    dataset: Dataset,
    batch_size: int,
) -> list[tuple[Case, OCROutput]]:
    results = []

    for cases in batched(dataset.cases, batch_size):
        outputs = model.batch_call([case.inputs for case in cases])
        results.extend(zip(cases, outputs, strict=True))

    return results
