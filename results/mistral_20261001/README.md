# Mistral/mistral-ocr-4-1 — ScandiOCR results

Completed 2026-10-01: 6,477 images across 11 tasks. Estimated API cost: $25.91 before tax.

Dedicated OCR API; raw Markdown output.
Images were sent at their original dimensions as RGB PNG.

| Benchmark | CER | WER |
|---|---:|---:|
| Scandinavian OCR | 121.67% | 138.98% |
| Danish OCR | 193.82% | 201.73% |
| Norwegian OCR | 33.80% | 56.00% |
| Swedish OCR | 35.96% | 68.78% |

Each task report contains all references, unmodified predictions, per-example and corpus CER/WER, image hashes, source revisions, inference settings and token/page usage. The index records SHA256 hashes of these public reports.

Task scores use NFC and whitespace normalization, preserving case and punctuation. Benchmark scores are equal-weight means of task corpus scores. Failed attempts are empty predictions; insertion errors are not capped.

Source texts remain subject to the original dataset terms, linked in each report. Input images are not included. Private runtime paths, credentials, HTTP headers and provider response identifiers are excluded.

[Leaderboard and dataset documentation](https://v4ldesalnikov.github.io/ocr-eval/)
