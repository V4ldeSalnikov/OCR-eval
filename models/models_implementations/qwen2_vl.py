from models.model_interface import OCRModel, OCRInput, OCROutput
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch

from models.model_meta import ModelMeta


QWEN2_TASK_SETTINGS = {
    "line-recognition": (
        "You are an OCR engine. Transcribe the text. Return ONLY the text from "
        "the image, Do not include coordinates, bounding boxes, labels, or "
        "explanations. Output text in a single line",
        "Transcribe the text on the image. Output text only in a single line.",
        1024,
    ),
    "page-transcription": (
        "You are an OCR engine. Transcribe all text on the page in natural "
        "reading order. Return ONLY the text from the image. Preserve line "
        "breaks. Do not include coordinates, bounding boxes, labels, or "
        "explanations.",
        "Transcribe all text on this page in natural reading order. Preserve "
        "line breaks and output text only.",
        4096,
    ),
}


class Qwen2VL(OCRModel):

    def __init__(self, model_id: str, task: str):
        self.id = model_id
        self.task = task
        self.system_prompt, self.user_prompt, self.max_new_tokens = (
            QWEN2_TASK_SETTINGS[task]
        )

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        messages = []
        for ocr_input in inputs:
            image = ocr_input.image.convert("RGB")
            messages.append([
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.system_prompt}],
                },
                {"role": "user", "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": self.user_prompt},
                ]},
            ])

        #preprocessing the input
        texts = [
            self.processor.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
            for message in messages
        ]
        image_inputs, video_inputs = process_vision_info(messages)
        model_inputs = self.processor(
            text=texts, images=image_inputs, videos=video_inputs,
            padding=True, return_tensors="pt"
        )
        model_inputs = model_inputs.to(self.device)

        #Model inference
        generated_ids = self.model.generate(
            **model_inputs,
            do_sample=False,
            max_new_tokens=self.max_new_tokens,
        )
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        output_texts = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return [OCROutput(text=output_text) for output_text in output_texts]

QWEN2_VL_2B_INSTRUCT = ModelMeta(
    loader=Qwen2VL,
    name="Qwen/Qwen2-VL-2B-Instruct",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "Qwen/Qwen2-VL-2B-Instruct"},
    languages=["da-Latn", "eng-Latn"],
    license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct",
    notes="Qwen2 2B OCR baseline",
)

QWEN2_VL_4B_INSTRUCT = ModelMeta(
    loader=Qwen2VL,
    name="Qwen/Qwen2-VL-7B-Instruct",
    supported_tasks=("line-recognition", "page-transcription"),
    loader_kwargs={"model_id": "Qwen/Qwen2-VL-7B-Instruct"},
    languages=["da-Latn", "eng-Latn"],
    license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct",
    notes="Qwen2 7B OCR baseline",
)
