# World OCR Benchmark

> This is draft documentation for the future MVP release. The current `README.md` remains unchanged until then.

A research benchmark for evaluating classical and vision-language OCR models across languages and document types.

## Status

The project is in pre-MVP development. The environment is locked for Python 3.12 on NVIDIA Windows and Linux x86-64 systems, and has been validated on an RTX 3090.

## Setup

Install [uv](https://docs.astral.sh/uv/) 0.12.5 or newer, then run:

```shell
uv sync --locked
```

## Current entry point

```shell
uv run python main.py
```

The current entry point defaults to the two-image Qwen2-VL demo. Its first run downloads the selected model weights; it is not yet the final benchmark interface.

Available models, datasets, and command-line options can be listed with:

```shell
uv run python main.py --help
```

Runs are limited to 100 examples by default while dataset cases are held in memory.

For example, run ten NorHand lines with Qwen2-VL using:

```shell
uv run python main.py --model Qwen/Qwen2-VL-2B-Instruct --dataset norhand --batch-size 2 --max-examples 10
```

Page transcription is available for annotated handwriting and modern printed
page datasets, including `historical-danish`, `modern-danish`,
`oj4ocrmt-danish`, `oj4ocrmt-swedish`, and `nasjonalt-vitenarkiv`:

```shell
uv run python main.py --model Qwen/Qwen2-VL-2B-Instruct --dataset historical-danish --task page-transcription --max-examples 10
```

The current local page-capable adapters are Qwen2-VL, Qwen3-VL, GLM-OCR,
GOT-OCR2, and Tesseract. TrOCR, EasyOCR, and the Transformers-only PaddleOCR-VL
adapter remain line-only. Unsupported combinations fail before model weights
are loaded.

Modern printed-page references are extracted from the source PDFs rather than
manually transcribed. This provenance is included in each evaluation report.

## Hosted API models

Hosted adapters send each evaluated image to the selected provider and may
incur usage charges. API credentials are read from environment variables and
are never stored in evaluation reports.

Mistral, OpenAI, and Anthropic currently make one synchronous request per case;
their `--batch-size` groups benchmark cases but does not make a provider batch
request. Transkribus submits every job in a batch before polling. Hosted APIs do
not guarantee identical output across repeated calls.

Mistral OCR requires `MISTRAL_API_KEY`:

```shell
uv run python main.py --model Mistral/mistral-ocr-4-1 --dataset simple --max-examples 1
```

Mistral OCR returns raw Markdown. On page datasets, Markdown markers are scored
as characters until the benchmark defines a shared page-output policy.

OpenAI models require `OPENAI_API_KEY`. Luna is the economical baseline and
Terra is the balanced baseline:

```shell
uv run python main.py --model OpenAI/gpt-5.6-luna --dataset simple --max-examples 1
uv run python main.py --model OpenAI/gpt-5.6-terra --dataset simple --max-examples 1
```

Claude models require `ANTHROPIC_API_KEY`. Haiku is the economical baseline
and Sonnet is the stronger baseline:

```shell
uv run python main.py --model Anthropic/claude-haiku-4-5-20251001 --dataset simple --max-examples 1
uv run python main.py --model Anthropic/claude-sonnet-5 --dataset simple --max-examples 1
```

Very small line crops can reduce Claude's vision accuracy. The benchmark sends
the original image without provider-specific resizing.

Transkribus requires `TRANSKRIBUS_USERNAME`, `TRANSKRIBUS_PASSWORD`, API access,
and processing credits. Four Danish models are registered; for example:

```shell
uv run python main.py --model Transkribus/Dansk-Dokumentalist-309713 --dataset danish-typewritten --max-examples 1
```

The adapter uses the currently live v1 processing API. For line crops,
Transkribus performs its own line detection before recognition, so those scores
measure both stages. Lossless page images must stay within the API's 20 MB image
limit. The `Danish-1870-1950-v3.5-26311` model may contain training material that
overlaps `historical-danish`; do not present that pairing as an out-of-domain
result.

Before running or publishing a large comparative evaluation, clarify with
READ-COOP whether its restriction on infrastructure benchmarks also applies to
OCR accuracy benchmarking.

## Tesseract

The Tesseract adapters assume that the Tesseract engine is installed and available as `tesseract` from a new shell. Install the official `dan`, `nor`, and `swe` files from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best) in Tesseract's active `tessdata` directory. If that directory is not writable, place the files in another directory and set `TESSDATA_PREFIX` to it.

Check the installation before running an evaluation:

```shell
tesseract --version
tesseract --list-langs
```

For example, evaluate the Danish model on ten typewritten lines:

```shell
uv run python main.py --model Tesseract/tessdata_best-dan --dataset danish-typewritten --batch-size 2 --max-examples 10
```
