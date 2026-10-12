# ScandiOCR

Evaluate OCR and vision-language models on printed and handwritten documents in Danish, Norwegian and Swedish.

[Leaderboard](https://v4ldesalnikov.github.io/ocr-eval/) · [Datasets](https://v4ldesalnikov.github.io/ocr-eval/datasets/) · [Methodology](https://v4ldesalnikov.github.io/ocr-eval/methodology/) · [Published results](results/README.md)

## Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (version 0.12.5 or newer), then:

```sh
git clone https://github.com/V4ldeSalnikov/OCR-eval.git
cd OCR-eval
uv sync --locked
```

This creates a virtual environment with Python 3.12 and the project dependencies. The provided environment supports Windows and Linux on x86-64. An NVIDIA GPU is recommended for local models.

## Run an evaluation

Each command evaluates one model on one dataset. For example, recognise 100 Norwegian handwritten lines with TrOCR:

```sh
uv run main.py --model Sprakbanken/TrOCR-norhand-v3 --dataset norhand --task line-recognition --max-examples 100 --batch-size 1
```

Or transcribe 10 full Danish document pages with Qwen:

```sh
uv run main.py --model Qwen/Qwen2-VL-2B-Instruct --dataset oj4ocrmt-danish --task page-transcription --max-examples 10 --batch-size 1
```

Models and datasets are downloaded as needed on the first run.

- `--model`: the model to evaluate.
- `--dataset`: the dataset to use.
- `--task`: `line-recognition` for cropped text lines, or `page-transcription` for whole pages. The model and dataset must support the chosen task.
- `--max-examples`: how many examples to evaluate (default: 100).
- `--batch-size`: how many images to process together. Start with 1 to reduce memory use.

To see all available models, datasets and options:

```sh
uv run main.py --help
```

Tesseract models also require [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) and the relevant language data. Hosted models require the provider's API credentials.

## Results

After evaluation, scores are printed in the terminal and a timestamped JSON report is saved in `runs/`. Each report contains the reference text, model prediction, and character and word error rates (CER/WER) for every example, plus scores for the whole evaluation. Lower error rates are better.

These commands use the first requested examples from the dataset. The published leaderboard uses fixed evaluation samples; see the [methodology](https://v4ldesalnikov.github.io/ocr-eval/methodology/#sampling) for details.
