from transformers import AutoProcessor, GlmOcrForConditionalGeneration

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


class GLMOCR(OCRModel):
    def __init__(self, model_id: str):
        self.id = model_id
        self.model = GlmOcrForConditionalGeneration.from_pretrained(
            model_id,
            dtype="auto",
            device_map="auto",
        )
        self.model.eval()
        self.processor = AutoProcessor.from_pretrained(model_id)

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        conversations = []
        for ocr_input in inputs:
            conversations.append([
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": ocr_input.image.convert("RGB")},
                        {"type": "text", "text": "Text Recognition:"},
                    ],
                }
            ])

        model_inputs = self.processor.apply_chat_template(
            conversations,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            processor_kwargs={"padding": True, "padding_side": "left"},
        )
        model_inputs = model_inputs.to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            do_sample=False,
            max_new_tokens=1024,
        )
        input_length = model_inputs["input_ids"].shape[1]
        output_texts = self.processor.batch_decode(
            generated_ids[:, input_length:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        return [OCROutput(text=output_text) for output_text in output_texts]


GLM_OCR = ModelMeta(
    loader=GLMOCR,
    name="zai-org/GLM-OCR",
    loader_kwargs={"model_id": "zai-org/GLM-OCR"},
    family="GLM-OCR",
    languages=["zh", "en", "fr", "es", "ru", "de", "ja", "ko"],
    license="mit",
    reference="https://huggingface.co/zai-org/GLM-OCR",
    notes="0.9B OCR model evaluated zero-shot on Scandinavian line recognition",
)
