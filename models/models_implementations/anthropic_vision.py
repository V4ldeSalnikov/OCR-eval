from anthropic import Anthropic

from models.image_encoding import image_to_png_base64
from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


ANTHROPIC_TASK_SETTINGS = {
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


class AnthropicVision(OCRModel):
    def __init__(self, model_id: str, task: str):
        self.id = f"Anthropic/{model_id}"
        self.task = task
        self.model_id = model_id
        self.system_prompt, self.user_prompt, self.max_tokens = (
            ANTHROPIC_TASK_SETTINGS[task]
        )
        self.client = Anthropic()

    def __call__(self, inputs: OCRInput) -> OCROutput:
        image = image_to_png_base64(inputs.image)
        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image,
                            },
                        },
                        {"type": "text", "text": self.user_prompt},
                    ],
                }
            ],
            thinking={"type": "disabled"},
        )
        if response.stop_reason != "end_turn":
            raise RuntimeError(
                f"Anthropic response ended with stop reason "
                f"'{response.stop_reason}'"
            )
        [text] = [block.text for block in response.content if block.type == "text"]

        return OCROutput(text=text)


ANTHROPIC_CLAUDE_HAIKU_4_5 = ModelMeta(
    loader=AnthropicVision,
    name="Anthropic/claude-haiku-4-5-20251001",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "claude-haiku-4-5-20251001"},
    family="Claude 4.5",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="proprietary",
    reference="https://platform.claude.com/docs/en/models/overview",
    notes="Economical hosted vision-language baseline",
)

ANTHROPIC_CLAUDE_SONNET_5 = ModelMeta(
    loader=AnthropicVision,
    name="Anthropic/claude-sonnet-5",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "claude-sonnet-5"},
    family="Claude 5",
    languages=["da-Latn", "no-Latn", "sv-Latn"],
    license="proprietary",
    reference="https://platform.claude.com/docs/en/models/overview",
    notes="Stronger hosted vision-language baseline",
)
