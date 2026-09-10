from models.model_meta import ModelMeta
from models.models_implementations import (
    anthropic_vision,
    easyocr_adapter,
    glm_ocr,
    got_ocr2,
    mistral_ocr,
    openai_vision,
    paddleocr_vl,
    qwen2_vl,
    qwen3_vl,
    tesseract_adapter,
    trocr,
)
from typing import Any

model_modules = [
    anthropic_vision,
    easyocr_adapter,
    glm_ocr,
    got_ocr2,
    mistral_ocr,
    openai_vision,
    paddleocr_vl,
    qwen3_vl,
    qwen2_vl,
    tesseract_adapter,
    trocr,
]

MODEL_REGISTRY = {}

for module in model_modules:
    for mdl in vars(module).values():
        if isinstance(mdl, ModelMeta):
            MODEL_REGISTRY[mdl.name] = mdl

def get_model_meta(name: str) -> ModelMeta:
    try:
        return MODEL_REGISTRY[name]
    except KeyError :
        raise KeyError(f"Unknown model '{name}'.")

def get_model(name: str, task: str, **overrides: Any):
    return get_model_meta(name).load(task, **overrides)
