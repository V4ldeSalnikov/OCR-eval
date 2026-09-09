from unicodedata import normalize

import jiwer


def normalize_text(text: str) -> str:
    return " ".join(normalize("NFC", text).split())


def normalize_texts(texts: str | list[str]) -> list[str]:
    if isinstance(texts, str):
        texts = [texts]
    return [normalize_text(text) for text in texts]


def cer(model_output: str | list[str], ground_truth: str | list[str]) -> float:
    return jiwer.cer(
        normalize_texts(ground_truth),
        normalize_texts(model_output),
    )


def wer(model_output: str | list[str], ground_truth: str | list[str]) -> float:
    return jiwer.wer(
        normalize_texts(ground_truth),
        normalize_texts(model_output),
    )

