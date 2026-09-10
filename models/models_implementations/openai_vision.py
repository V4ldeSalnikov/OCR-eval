from openai import OpenAI

from models.image_encoding import image_to_png_base64
from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


OPENAI_TASK_SETTINGS = {
    "line-recognition": (
        "You are an OCR engine. Transcribe the text. Return only the text "
        "from the image in a single line.",
        "Transcribe the text on the image.",
        1024,
    ),
    "page-transcription": (
        "You are an OCR engine. Transcribe all text on the page in natural "
        "reading order. Return only the text and preserve line breaks.",
        "Transcribe all text on this page in natural reading order.",
        4096,
    ),
}


class OpenAIVision(OCRModel):
    def __init__(self, model_id: str, task: str):
        self.id = f"OpenAI/{model_id}"
        self.task = task
        self.model_id = model_id
        self.system_prompt, self.user_prompt, self.max_output_tokens = (
            OPENAI_TASK_SETTINGS[task]
        )
        self.client = OpenAI()

    def __call__(self, inputs: OCRInput) -> OCROutput:
        image = image_to_png_base64(inputs.image)
        response = self.client.responses.create(
            model=self.model_id,
            instructions=self.system_prompt,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image}",
                            "detail": "original",
                        },
                        {"type": "input_text", "text": self.user_prompt},
                    ],
                }
            ],
            max_output_tokens=self.max_output_tokens,
            reasoning={"effort": "none"},
            store=False,
        )
        if response.status != "completed":
            raise RuntimeError(
                f"OpenAI response ended with status '{response.status}': "
                f"{response.incomplete_details}"
            )

        return OCROutput(text=response.output_text)


OPENAI_GPT_5_6_LUNA = ModelMeta(
    loader=OpenAIVision,
    name="OpenAI/gpt-5.6-luna",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "gpt-5.6-luna"},
    family="GPT-5.6",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="proprietary",
    reference="https://developers.openai.com/api/docs/models/gpt-5.6-luna",
    notes="Economical hosted vision-language baseline",
)

OPENAI_GPT_5_6_TERRA = ModelMeta(
    loader=OpenAIVision,
    name="OpenAI/gpt-5.6-terra",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "gpt-5.6-terra"},
    family="GPT-5.6",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="proprietary",
    reference="https://developers.openai.com/api/docs/models/gpt-5.6-terra",
    notes="Balanced hosted vision-language baseline",
)
