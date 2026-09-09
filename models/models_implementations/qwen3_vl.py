from models.model_interface import OCRModel, OCRInput, OCROutput
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
from qwen_vl_utils import process_vision_info
import torch

from models.model_meta import ModelMeta


class Qwen3VL(OCRModel):

    def __init__(self, model_id: str):
        self.id = model_id

        self.model = Qwen3VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)
        self.prompt = "You are an OCR engine. Transcribe the text. Return ONLY the text from the image, Do not include coordinates, bounding boxes, labels, or explanations. Output text in a single line"

    def __call__(self,inputs : OCRInput) -> OCROutput:
        img = inputs.image.convert("RGB")
        messages = [
            {"role": "system", "content": [{"type": "text", "text": self.prompt}]},
            {"role": "user", "content": [{"type": "image", "image": img},
                                         {"type": "text", "text": "Transcribe the text on the image. Output text only in a single line."}]},
        ]

        #preprocessing the input
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        model_input = self.processor(
            text=[text], images=image_inputs, videos=video_inputs,
            padding=True, return_tensors="pt"
        )
        model_input = model_input.to(self.device)

        #Model inference
        generated_ids = self.model.generate(**model_input, do_sample=False, max_new_tokens=1024)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(model_input.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

        return OCROutput(text=output_text)

QWEN3_VL_2B_INSTRUCT = ModelMeta(
    loader=Qwen3VL,
    name="Qwen/Qwen3-VL-2B-Instruct",
    loader_kwargs={"model_id": "Qwen/Qwen3-VL-2B-Instruct"},
    languages=["da-Latn", "eng-Latn"],
    license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct",
    notes="Qwen3 2B OCR baseline",
)

QWEN3_VL_4B_INSTRUCT = ModelMeta(
    loader=Qwen3VL,
    name="Qwen/Qwen3-VL-4B-Instruct",
    loader_kwargs={"model_id": "Qwen/Qwen3-VL-4B-Instruct"},
    languages=["da-Latn", "eng-Latn"],
    license="apache-2.0",
    reference="https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct",
    notes="Qwen3 4B OCR baseline",
)
