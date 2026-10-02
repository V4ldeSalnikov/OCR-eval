# OpenAI/gpt-6.1-sol — ScandiOCR results

Completed 2026-10-02: 6,477 images across 11 tasks. Estimated API cost: $27.68 before tax.

Standard API, low reasoning, original image detail.
Images were sent at their original dimensions as RGB PNG.

| Benchmark | CER | WER |
|---|---:|---:|
| Scandinavian OCR | 15.31% | 27.80% |
| Danish OCR | 12.99% | 23.33% |
| Norwegian OCR | 18.60% | 31.75% |
| Swedish OCR | 17.74% | 34.12% |

Each task report contains all references, unmodified predictions, per-example and corpus CER/WER, image hashes, source revisions, inference settings and token/page usage. The index records SHA256 hashes of these public reports.

Task scores use NFC and whitespace normalization, preserving case and punctuation. Benchmark scores are equal-weight means of task corpus scores. Failed attempts are empty predictions; insertion errors are not capped.

Source texts remain subject to the original dataset terms, linked in each report. Input images are not included. Private runtime paths, credentials, HTTP headers and provider response identifiers are excluded.

[Leaderboard and dataset documentation](https://v4ldesalnikov.github.io/ocr-eval/)
