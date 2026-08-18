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

The current entry point is a two-image Qwen2-VL demo. Its first run downloads the selected model weights; it is not yet the final benchmark interface.
