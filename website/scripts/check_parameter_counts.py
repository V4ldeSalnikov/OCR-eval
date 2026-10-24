"""Reproduce the website's size estimates; downloads configs, never weights.

Run with the evaluation environment's Python (Transformers 5.15.0).
Hugging Face access to the Gemma 3 config may require accepting its terms.
"""
from pathlib import Path
import re

import torch
import transformers

if transformers.__version__ != "5.15.0":
    raise RuntimeError("Use Transformers 5.15.0 to reproduce these recorded estimates.")

source = (Path(__file__).resolve().parents[1] / "src/data/ocr-parameters.ts").read_text()
records = re.findall(r"'([^']+)': count\((\d+), (\d+), '([a-f0-9]+)'\)", source)
if not records:
    raise RuntimeError("No parameter records found.")
for model_id, expected_total, expected_active, revision in records:
    config = transformers.AutoConfig.from_pretrained(model_id, revision=revision, trust_remote_code=False)
    with torch.device("meta"):
        model = getattr(transformers, config.architectures[0])(config)
    model.tie_weights()
    embeddings = {id(p) for module in model.modules() if isinstance(module, torch.nn.Embedding) for p in module.parameters()}
    total = sum(p.numel() for p in model.parameters())
    active = sum(p.numel() for name, p in model.named_parameters()
                 if id(p) not in embeddings and not name.startswith(("model.audio_tower.", "model.embed_audio.")))
    assert (total, active) == (int(expected_total), int(expected_active)), model_id
    print(f"{model_id}: {active:,} active / {total:,} total")
    del model
