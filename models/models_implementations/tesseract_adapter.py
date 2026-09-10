import pytesseract

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


TESSERACT_PAGE_SEGMENTATION = {
    "line-recognition": 7,
    "page-transcription": 3,
}


class TesseractOCR(OCRModel):
    def __init__(self, model_id: str, language: str, task: str):
        self.id = model_id
        self.language = language
        self.task = task
        self.page_segmentation = TESSERACT_PAGE_SEGMENTATION[task]

    def __call__(self, inputs: OCRInput) -> OCROutput:
        text = pytesseract.image_to_string(
            inputs.image.convert("RGB"),
            lang=self.language,
            config=f"--oem 1 --psm {self.page_segmentation}",
        )
        return OCROutput(text=text.rstrip("\r\n\f"))


TESSERACT_DANISH = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-dan",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-dan",
        "language": "dan",
    },
    family="Tesseract",
    languages=["da-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/dan.traineddata",
    notes="Tesseract LSTM baseline for Danish printed OCR",
)

TESSERACT_NORWEGIAN = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-nor",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-nor",
        "language": "nor",
    },
    family="Tesseract",
    languages=["no-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/nor.traineddata",
    notes="Tesseract LSTM baseline for Norwegian printed OCR",
)

TESSERACT_SWEDISH = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-swe",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-swe",
        "language": "swe",
    },
    family="Tesseract",
    languages=["sv-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/swe.traineddata",
    notes="Tesseract LSTM baseline for Swedish printed OCR",
)
