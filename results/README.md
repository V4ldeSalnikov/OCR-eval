# Published evaluation results

The runs below evaluate the same frozen 6,477 images across 11 tasks. Each model's folder contains the full predictions, references, scores, inference settings and dataset provenance. Reports contain no input images or private API runtime data.

| Model | Configuration | Report |
|---|---|---|
| Mistral OCR 4.1 | Dedicated OCR API, original image dimensions | [Results](mistral_20261001/README.md) |
| GPT-6.1 Sol | Standard API, low reasoning, original image dimensions | [Results](gpt61_sol_full_20261002/README.md) |

[Website leaderboard and examples](https://v4ldesalnikov.github.io/ocr-eval/)

To regenerate these public bundles from the local audited runs:

```sh
python scripts/export_hosted_results.py --run-dir runs/mistral_20261001 --run-dir runs/gpt61_sol_full_20261002
```

The exporter selects public fields explicitly and recomputes corpus CER/WER before writing. Run folders, credentials and raw API responses remain local and ignored by Git. Original dataset terms still apply to source text; source links and revisions are in each task report.
