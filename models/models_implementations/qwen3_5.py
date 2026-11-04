"""Qwen 3.5 OCR using the native Transformers chat processor."""

from transformers import AutoModelForImageTextToText, AutoProcessor

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


TASK_PROMPTS = {
    "line-recognition": "Transcribe the text in this image. Return only the original text in a single line, without explanation or translation.",
    "page-transcription": "Transcribe all text on this page in natural reading order. Preserve line breaks. Return only the original text, without explanation or translation.",
}


class Qwen35OCR(OCRModel):
    def __init__(self, model_id: str, task: str,
                 revision: str | None = None, device_map="auto"):
        self.id, self.task, self.profile = model_id, task, "qwen3_5"
        self.prompt = TASK_PROMPTS[task]
        self.max_new_tokens = 1024 if task == "line-recognition" else 4096
        self.processor = AutoProcessor.from_pretrained(model_id, revision=revision)
        self.processor.tokenizer.padding_side = "left"
        self.template_options = (
            {"enable_thinking": False} if "enable_thinking" in self.processor.chat_template else {}
        )
        self.image_options = {
            "size": {**dict(self.processor.image_processor.size), "longest_edge": 2048 * 32 * 32}
        }
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, revision=revision, dtype="bfloat16", device_map=device_map,
            attn_implementation="sdpa",
        ).eval()
        # These checkpoints omit the chat turn boundary from their EOS defaults.
        eos = self.model.generation_config.eos_token_id
        eos = [eos] if isinstance(eos, int) else list(eos or [])
        turn_end = self.processor.tokenizer.convert_tokens_to_ids("<|im_end|>")
        if turn_end is not None and turn_end not in eos:
            eos.append(turn_end)
        self.model.generation_config.eos_token_id = eos

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


QWEN35_2B = ModelMeta(
    name="Qwen/Qwen3.5-2B", loader=Qwen35OCR,
    loader_kwargs={"model_id": "Qwen/Qwen3.5-2B"},
    supported_tasks=("line-recognition", "page-transcription"),
    family="Qwen 3.5", license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen3.5-2B",
    notes="BF16, greedy decoding, thinking disabled; zero-shot Scandinavian OCR.",
)


QWEN35_4B = ModelMeta(
    name="Qwen/Qwen3.5-4B", loader=Qwen35OCR,
    loader_kwargs={"model_id": "Qwen/Qwen3.5-4B"},
    supported_tasks=("line-recognition", "page-transcription"),
    family="Qwen 3.5", license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen3.5-4B",
    notes="BF16, greedy decoding, thinking disabled; zero-shot Scandinavian OCR.",
)
