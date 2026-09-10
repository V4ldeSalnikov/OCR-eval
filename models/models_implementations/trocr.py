import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from models.model_interface import OCRInput, OCRModel, OCROutput
from models.model_meta import ModelMeta


class TrOCR(OCRModel):
    def __init__(self, model_id: str, task: str):
        self.id = model_id
        self.task = task
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id)
        self.model.to(self.device)
        self.model.eval()
        self.processor = TrOCRProcessor.from_pretrained(model_id)

        if not self.model.config.decoder.use_learned_position_embeddings:
            position_embeddings = self.model.decoder.model.decoder.embed_positions
            position_embeddings.weights = position_embeddings.get_embedding(
                position_embeddings.weights.size(0),
                position_embeddings.embedding_dim,
                position_embeddings.padding_idx,
            ).to(self.device)

    def __call__(self, inputs: OCRInput) -> OCROutput:
        return self.batch_call([inputs])[0]

    def batch_call(self, inputs: list[OCRInput]) -> list[OCROutput]:
        images = [ocr_input.image.convert("RGB") for ocr_input in inputs]
        pixel_values = self.processor(
            images=images,
            return_tensors="pt",
        ).pixel_values
        pixel_values = pixel_values.to(self.device)

        generated_ids = self.model.generate(
            pixel_values=pixel_values,
            do_sample=False,
            num_beams=1,
        )
        output_texts = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        return [OCROutput(text=output_text) for output_text in output_texts]


SWEDISH_LION_LIBRE = ModelMeta(
    loader=TrOCR,
    name="Riksarkivet/trocr-base-handwritten-hist-swe-2",
    supported_tasks=("line-recognition",),
    loader_kwargs={
        "model_id": "Riksarkivet/trocr-base-handwritten-hist-swe-2",
    },
    family="TrOCR",
    languages=["sv-Latn"],
    license="apache-2.0",
    reference="https://huggingface.co/Riksarkivet/trocr-base-handwritten-hist-swe-2",
    notes="Swedish handwriting from 1600-1900; use riksarkivet-ood to avoid training overlap",
)

NORHAND_V3 = ModelMeta(
    loader=TrOCR,
    name="Sprakbanken/TrOCR-norhand-v3",
    supported_tasks=("line-recognition",),
    loader_kwargs={"model_id": "Sprakbanken/TrOCR-norhand-v3"},
    family="TrOCR",
    languages=["no-Latn"],
    license="cc-by-4.0",
    reference="https://huggingface.co/Sprakbanken/TrOCR-norhand-v3",
    notes="Norwegian historical handwriting model fine-tuned on NorHand v3; norhand is an in-domain evaluation",
)
