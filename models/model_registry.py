from models.model_meta import ModelMeta
from models.models_implementations import easyocr_adapter, qwen2_vl, qwen3_vl
from typing import Any
model_modules = [easyocr_adapter, qwen3_vl, qwen2_vl]

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

def get_model(name: str, **overrides: Any):
    return get_model_meta(name).load(**overrides)
