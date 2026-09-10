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

Page transcription is available for the `historical-danish` and
`modern-danish` page datasets:

```shell
uv run python main.py --model Qwen/Qwen2-VL-2B-Instruct --dataset historical-danish --task page-transcription --max-examples 10
```

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
