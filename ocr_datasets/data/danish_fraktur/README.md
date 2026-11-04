---
language:
- da
license: cc-by-sa-4.0
task_categories:
- image-to-text
size_categories:
- n<1K
tags:
- ocr
- fraktur
- historical-documents
---

# Danish Fraktur — Wikisource

Version **1.0.0**: 20 complete page scans with Danish reference transcriptions,
forming a complete `page-transcription` task in the Danish and Scandinavian OCR
benchmarks. This is a small evaluation set,
not a training dataset. It contains ten pages from each of two books:

| Book | Author | Year | Scan pages |
| --- | --- | --- | --- |
| [Af en endnu Levendes Papirer](https://commons.wikimedia.org/wiki/File:Af_en_endnu_Levendes_Papirer.djvu) | Søren Kierkegaard | 1838 | 17, 18, 19, 23, 24, 25, 30, 33, 36, 40 |
| [Billedbog uden Billeder](https://commons.wikimedia.org/wiki/File:Billedbog_uden_Billeder.djvu) | Hans Christian Andersen | 1840 | 9, 12, 15, 16, 20, 26, 34, 39, 40, 54 |

These are **scan indices**, not the printed page numbers. The Royal Danish Library
digitised both books. Wikimedia Commons supplies the scans, and Danish Wikisource
contributors supply the transcriptions.

## Selection and review

The source inventory contained 35 validated pages in the Kierkegaard book and 48
in the Andersen book. This dataset uses a curated selection of body-text pages,
including short passages, dense prose, headings, poetry, printer's signatures and
words continuing across pages. Title pages, blank pages, unvalidated pages and
pages with footnotes are excluded. Selection preceded any model evaluation.

Every selected source revision has Wikisource quality level 4 (validated), meaning
it passed proofreading by two contributors. See the
[Wikisource page-status documentation](https://en.wikisource.org/wiki/Help:Page_status).
Codex subsequently compared all 20 scans with their references. Changes are
recorded explicitly in `review.json`, including restored line-end hyphens, three
omitted printer's signatures and corrections to case or transcription errors.
The original source snapshots remain unchanged in `sources.json`.

The additional comparison was performed by an AI
assistant, not an independent human transcription team. No numerical ground-truth
accuracy has been established. The local `review.html` displays every scan beside
its reference for further inspection.

## Transcription conventions

- Transcribe the complete visible page in reading order: page number, heading,
  body, then any printer's signature or footer.
- Keep original spelling, capitalisation and apparent printing errors. For
  example, the printed `blene` on Andersen scan page 34 is retained.
- Preserve visible word-division hyphens, including fragments at page boundaries;
  do not supply letters from the preceding or following page. Both single and
  double typographic hyphens are represented as `-`.
- Represent long s as `s` and ligatures by their ordinary letter sequences.
  Use `„…”` for Danish quotation marks, including doubled marks where printed.
- Remove wiki markup, decorative rules, ornaments, indentation and letter spacing.
  Include text in headers and footers rather than dropping `noinclude` sections.
- Reference line wrapping is not a line annotation. Existing ScandiOCR scoring
  normalises Unicode NFC and whitespace; it does not remove hyphens or ignore case
  and punctuation. Models that join divided words will therefore incur errors.

The images are unaltered Wikimedia page JPEGs, 960 pixels wide and 1,529–1,537
pixels tall. No image enhancement or cropping is used.

## Reproduce and inspect

From the repository root:

```sh
uv run ocr_datasets/data/danish_fraktur/create.py
```

The script rebuilds the references from the frozen source snapshots and explicit
corrections, checks them against `manifest.jsonl`, and downloads the scans into
`.cache/danish-fraktur-v1/images/`. It also writes `test.jsonl`, copies the dataset
card, licence and provenance, and creates `.cache/danish-fraktur-v1/review.html`.
Use `--output PATH` to prepare the same portable folder elsewhere.

Images and references have SHA-256 checksums. The manifest records the Wikisource
revision IDs and timestamps, contributor-history links, Commons file version and
SHA-1, exact image URLs, dimensions and licences. A changed source image is
rejected instead of silently changing the benchmark. Rebuilding does not query
the latest transcription or re-select pages. `--write-manifest` is only for an
intentional, reviewed dataset update; bump the version when changing the data.

## Run an evaluation

Use `--dataset danish-fraktur --task page-transcription --max-examples 20` with a
page-capable model. For example:

```sh
uv run main.py --model Qwen/Qwen2-VL-2B-Instruct --dataset danish-fraktur --task page-transcription --max-examples 20 --batch-size 1
```

The loader downloads missing images automatically and otherwise works from the
local cache. [Initial results for five open models](https://v4ldesalnikov.github.io/OCR-eval/?benchmark=danish&sample=page-transcription%2Fdanish-fraktur&metric=cer)
and [full prediction reports](https://github.com/V4ldeSalnikov/resultsScandiOCReval)
are published separately. These models were selected by their saved Swedish
Fraktur CER; the Swedish task uses cropped lines and this task uses whole pages.
All five models were evaluated on all 20 pages. Danish Fraktur is included in the
Danish and Scandinavian OCR benchmarks.

Release 1.0.0 preserves every image, reference and annotation from the evaluated
snapshot. Saved reports retain their original source revision identifiers and
hashes; the release changes only the dataset version and completion status.

## Scope

Both books were printed by Bianco Luno in Copenhagen, two years apart. This is a
small test of nineteenth-century Danish book Fraktur, not representative coverage
of Danish newspapers, all Fraktur styles or periods. There are no line boxes,
training or development splits. These well-known public texts may have appeared
in model training data; the set is not guaranteed to be free of contamination.

## Attribution and reuse

The scans and original literary works are marked **public domain** on the linked
Commons file pages. The transcription contributions and this adapted reference
set are distributed under **CC BY-SA 4.0**. See `LICENSE.txt`.

Credit the original authors, the Royal Danish Library, Wikimedia Commons and the
Danish Wikisource contributors. Each manifest row links the exact source revision
and its contributor history. State that ScandiOCR removed wiki formatting and
applied the corrections recorded in `review.json`. Preserve this attribution and
the applicable share-alike licence when redistributing adapted transcriptions.
