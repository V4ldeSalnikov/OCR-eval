import pytesseract

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


class TesseractOCR(OCRModel):
    def __init__(self, model_id: str, language: str):
        self.id = model_id
        self.language = language

    def __call__(self, inputs: OCRInput) -> OCROutput:
        text = pytesseract.image_to_string(
            inputs.image.convert("RGB"),
            lang=self.language,
            config="--oem 1 --psm 7",
        )
        return OCROutput(text=text.rstrip("\r\n\f"))


TESSERACT_DANISH = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-dan",
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-dan",
        "language": "dan",
    },
    family="Tesseract",
    languages=["da-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/dan.traineddata",
    notes="Tesseract LSTM baseline for Danish printed line recognition",
)

TESSERACT_NORWEGIAN = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-nor",
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-nor",
        "language": "nor",
    },
    family="Tesseract",
    languages=["no-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/nor.traineddata",
    notes="Tesseract LSTM baseline for Norwegian printed line recognition",
)

TESSERACT_SWEDISH = ModelMeta(
    loader=TesseractOCR,
    name="Tesseract/tessdata_best-swe",
    loader_kwargs={
        "model_id": "Tesseract/tessdata_best-swe",
        "language": "swe",
    },
    family="Tesseract",
    languages=["sv-Latn"],
    license="apache-2.0",
    reference="https://github.com/tesseract-ocr/tessdata_best/blob/main/swe.traineddata",
    notes="Tesseract LSTM baseline for Swedish printed line recognition",
)
