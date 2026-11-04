"""Frozen, scan-reviewed Danish Wikisource Fraktur pages."""

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

import requests
from PIL import Image

from ocr_datasets.dataset_interface import OCRDocument, PageAnnotation, PageDatasetSource

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "ocr_datasets" / "data" / "danish_fraktur" / "manifest.jsonl"
DEFAULT_CACHE = ROOT / ".cache" / "danish-fraktur-v1"


def download_image(record: dict, cache_dir: Path) -> Path:
    path = cache_dir / record["image_path"]
    if path.exists():
        content = path.read_bytes()
    else:
        response = requests.get(
            record["image_url"], timeout=60,
            headers={"User-Agent": "ScandiOCR/0.1 (https://github.com/V4ldeSalnikov/OCR-eval; dataset download)"},
        )
        response.raise_for_status()
        content = response.content
    if hashlib.sha256(content).hexdigest() != record["image_sha256"]:
        raise ValueError(f"Image checksum mismatch: {record['id']}; do not score changed scans")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return path


class DanishFrakturPages(PageDatasetSource):
    id = "danish-fraktur"
    languages = ["da"]

    def __init__(self, cache_dir: Path = DEFAULT_CACHE):
        self.cache_dir = Path(cache_dir)

    def load_documents(self) -> Iterable[OCRDocument]:
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            text = record["text"]
            if hashlib.sha256(text.encode()).hexdigest() != record["text_sha256"]:
                raise ValueError(f"Reference checksum mismatch: {record['id']}")
            with Image.open(download_image(record, self.cache_dir)) as image:
                if image.size != (record["image_width"], record["image_height"]):
                    raise ValueError(f"Unexpected image dimensions: {record['id']}")
                rgb = image.convert("RGB")
            metadata = {key: value for key, value in record.items() if key != "text"}
            yield OCRDocument(
                id=record["id"],
                pages=[PageAnnotation(name=record["id"], image=rgb, text=text, metadata={})],
                metadata=metadata,
            )
