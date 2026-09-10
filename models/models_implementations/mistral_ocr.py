import os

from mistralai.client import Mistral

from models.image_encoding import image_to_png_base64
from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


class MistralOCR(OCRModel):
    def __init__(self, model_id: str, task: str):
        self.id = f"Mistral/{model_id}"
        self.task = task
        self.model_id = model_id
        self.client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    def __call__(self, inputs: OCRInput) -> OCROutput:
        image = image_to_png_base64(inputs.image)
        response = self.client.ocr.process(
            model=self.model_id,
            document={
                "type": "image_url",
                "image_url": f"data:image/png;base64,{image}",
            },
            include_blocks=False,
            include_image_base64=False,
        )

        return OCROutput(text=response.pages[0].markdown)


MISTRAL_OCR_4_1 = ModelMeta(
    loader=MistralOCR,
    name="Mistral/mistral-ocr-4-1",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "mistral-ocr-4-1"},
    family="Mistral OCR",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="proprietary",
    reference="https://docs.mistral.ai/models/ocr-4-1",
    notes="Hosted OCR 4.1 API; returns the provider's raw Markdown transcription",
)
