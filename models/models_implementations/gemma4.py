"""Gemma 4 OCR using the native Transformers chat processor."""

from transformers import AutoModelForImageTextToText, AutoProcessor

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


TASK_PROMPTS = {
    "line-recognition": "Transcribe the text in this image. Return only the original text in a single line, without explanation or translation.",
    "page-transcription": "Transcribe all text on this page in natural reading order. Preserve line breaks. Return only the original text, without explanation or translation.",
}


class Gemma4OCR(OCRModel):
    def __init__(self, model_id: str, task: str,
                 revision: str | None = None, device_map="auto"):
        self.id, self.task, self.profile = model_id, task, "gemma4"
        self.prompt = TASK_PROMPTS[task]
        self.max_new_tokens = 1024 if task == "line-recognition" else 4096
        self.processor = AutoProcessor.from_pretrained(model_id, revision=revision)
        self.processor.tokenizer.padding_side = "left"
        self.template_options = (
            {"enable_thinking": False} if "enable_thinking" in self.processor.chat_template else {}
        )
        self.image_options = {"max_soft_tokens": 280 if task == "line-recognition" else 1120}
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, revision=revision, dtype="bfloat16", device_map=device_map,
            attn_implementation="sdpa",
        ).eval()

    @property
    def inference_settings(self) -> dict:
        image_processor = self.processor.image_processor
        return {
            "model_revision": getattr(self.model.config, "_commit_hash", None),
            "dtype": str(self.model.dtype), "attention_implementation": "sdpa",
            "max_new_tokens": self.max_new_tokens, "do_sample": False,
            "chat_template_options": self.template_options, "prompt": self.prompt,
            "image_options": self.image_options,
            "image_processor": image_processor.to_dict(),
            "eos_token_id": self.model.generation_config.eos_token_id,
            "postprocessing": "none",
        }

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        conversations = [[{"role": "user", "content": [
            {"type": "image", "image": item.image.convert("RGB")},
            {"type": "text", "text": self.prompt},
        ]}] for item in inputs]
        model_inputs = self.processor.apply_chat_template(
            conversations, add_generation_prompt=True, **self.template_options,
            tokenize=True, return_dict=True, return_tensors="pt",
            processor_kwargs={"padding": True, "images_kwargs": self.image_options},
        ).to(self.model.device, dtype=self.model.dtype)
        generated = self.model.generate(
            **model_inputs, do_sample=False, max_new_tokens=self.max_new_tokens,
        )
        texts = self.processor.batch_decode(
            generated[:, model_inputs["input_ids"].shape[1]:],
            skip_special_tokens=True, clean_up_tokenization_spaces=False,
        )
        return [OCROutput(text=text) for text in texts]


GEMMA4_E2B = ModelMeta(
    name="google/gemma-4-E2B-it", loader=Gemma4OCR,
    loader_kwargs={"model_id": "google/gemma-4-E2B-it"},
    supported_tasks=("line-recognition", "page-transcription"),
    family="Gemma 4", license="apache-2.0",
    reference="https://huggingface.co/google/gemma-4-E2B-it",
    notes="BF16, greedy decoding, thinking disabled; zero-shot Scandinavian OCR.",
)


GEMMA4_E4B = ModelMeta(
    name="google/gemma-4-E4B-it", loader=Gemma4OCR,
    loader_kwargs={"model_id": "google/gemma-4-E4B-it"},
    supported_tasks=("line-recognition", "page-transcription"),
    family="Gemma 4", license="apache-2.0",
    reference="https://huggingface.co/google/gemma-4-E4B-it",
    notes="BF16, greedy decoding, thinking disabled; zero-shot Scandinavian OCR.",
)
