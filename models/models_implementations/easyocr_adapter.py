import easyocr
import numpy as np

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


class EasyOCRAdapter(OCRModel):
    def __init__(self, model_id: str, languages: list[str], task: str):
        self.id = model_id
        self.task = task
        self._reader = easyocr.Reader(languages, detector=False)

    def __call__(self, inputs: OCRInput) -> OCROutput:
        image = np.array(inputs.image.convert("L"))

        parts = self._reader.recognize(
            image,
            decoder="greedy",
            detail=0,
            paragraph=False,
        )

        return OCROutput(text=" ".join(parts))


EASYOCR_SCANDINAVIAN = ModelMeta(
    loader=EasyOCRAdapter,
    name="EasyOCR/Scandinavian",
    supported_tasks=("line-recognition",),
    loader_kwargs={
        "model_id": "EasyOCR/Scandinavian",
        "languages": ["da", "no", "sv"],
    },
    family="EasyOCR",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="apache-2.0",
    reference="https://github.com/JaidedAI/EasyOCR",
    notes="Conventional recognition-only baseline for pre-cropped lines",
)
