from transformers import AutoProcessor, GotOcr2ForConditionalGeneration

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


GOT_MAX_NEW_TOKENS = {
    "line-recognition": 1024,
    "page-transcription": 4096,
}


class GOTOCR2(OCRModel):
    def __init__(self, model_id: str, task: str):
        self.id = model_id
        self.task = task
        self.max_new_tokens = GOT_MAX_NEW_TOKENS[task]
        self.model = GotOcr2ForConditionalGeneration.from_pretrained(
            model_id,
            dtype="auto",
            device_map="auto",
        )
        self.model.eval()
        self.processor = AutoProcessor.from_pretrained(model_id)

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        images = [ocr_input.image.convert("RGB") for ocr_input in inputs]
        model_inputs = self.processor(images=images, return_tensors="pt")
        model_inputs = model_inputs.to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            do_sample=False,
            tokenizer=self.processor.tokenizer,
            stop_strings="<|im_end|>",
            max_new_tokens=self.max_new_tokens,
        )
        input_length = model_inputs["input_ids"].shape[1]
        output_texts = self.processor.batch_decode(
            generated_ids[:, input_length:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        return [OCROutput(text=output_text) for output_text in output_texts]


GOT_OCR_2 = ModelMeta(
    loader=GOTOCR2,
    name="stepfun-ai/GOT-OCR-2.0-hf",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "stepfun-ai/GOT-OCR-2.0-hf"},
    family="GOT-OCR 2.0",
    languages=["multilingual"],
    license="apache-2.0",
    reference="https://huggingface.co/stepfun-ai/GOT-OCR-2.0-hf",
    notes="0.6B multilingual OCR model for line and page transcription",
)
