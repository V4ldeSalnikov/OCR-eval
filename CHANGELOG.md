# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
From v0.1.0 onward, each development commit advances the minor version.

## [v0.42.0] - 2026-09-10

### Added

- Added four hosted Danish Transkribus models covering broad documents,
  historical handwriting, modern cursive handwriting, and Fraktur newspapers.
- Added direct authentication and polling for the Transkribus processing API.

### Changed

- Made Transkribus batches submit every image before waiting for results, while
  preserving the input order in the returned transcriptions.

## [v0.41.0] - 2026-09-10

### Added

- Added Claude Haiku 4.5 and Claude Sonnet 5 as hosted vision-language
  baselines for line recognition and page transcription.

### Changed

- Disabled Claude's thinking mode for direct OCR transcription.

## [v0.40.0] - 2026-09-10

### Added

- Added OpenAI GPT-5.6 Luna and Terra as hosted vision-language baselines for
  line recognition and page transcription.

### Changed

- Sent lossless PNG inputs with original image detail and disabled reasoning so
  evaluation tokens are used for the OCR transcription itself.

## [v0.39.0] - 2026-09-10

### Added

- Added the hosted Mistral OCR 4.1 model for line recognition and page
  transcription.
- Added lossless PNG encoding for images sent to hosted OCR APIs.

### Changed

- Pinned the Mistral model and Python SDK versions for reproducible runs.

## [v0.38.0] - 2026-09-10

### Added

- Added task-owned metric definitions so future OCR tasks can use metrics other
  than text error rates.

### Changed

- Made evaluation reporting calculate and display the metrics declared by the
  selected task.
- Kept line recognition and page transcription on the same CER/WER metrics and
  preserved the existing report fields.
- Removed the unused Pydantic evaluator wrapper.

## [v0.37.0] - 2026-09-10

### Added

- Added recent Norwegian research publications from Nasjonalt vitenarkiv as a
  page-transcription dataset.
- Added PDFium for cross-platform PDF page rendering and text extraction.

### Changed

- Selected a fixed set of 19 Norwegian-language PDFs from 2020 onward and
  excluded English attachments and short event programmes.
- Excluded pages without embedded PDF text instead of using OCR-generated text
  as evaluation references.

## [v0.36.0] - 2026-09-10

### Changed

- Pinned OJ4OCRMT to an exact Hugging Face revision so its evaluation pages
  remain reproducible.

## [v0.35.0] - 2026-09-10

### Added

- Added the 2023 OJ4OCRMT regular-page evaluation set for Danish and Swedish.
- Added selective Hugging Face file streaming so evaluations do not download the
  complete 128 GB multilingual dataset.

### Changed

- Recorded OJ4OCRMT's PDF-derived reference text explicitly in report metadata.

## [v0.34.0] - 2026-09-10

### Added

- Added explicit page transcription text independently from optional line
  annotations.
- Added a source type for pages that provide line-level annotations.

### Changed

- Page transcription now reads the page reference directly.
- Page-only datasets now fail clearly when used for line recognition.

## [v0.33.0] - 2026-09-10

### Added

- Added explicit supported tasks to every model registration.
- Added page transcription prompts for Qwen2-VL and Qwen3-VL.

### Changed

- Added longer page output limits for Qwen, GLM-OCR, and GOT-OCR2.
- Configured Tesseract for automatic page segmentation during page transcription.
- Unsupported model and task combinations now fail before loading datasets or
  model weights.

## [v0.32.0] - 2026-09-10

### Added

- Added page transcription using complete page images and references assembled
  from human line annotations in source order.

### Changed

- Invalid task and dataset combinations now fail before the OCR model is loaded.

## [v0.31.0] - 2026-09-10

### Added

- Added separate source types for documents, annotated pages, line annotations,
  and standalone line samples.

### Changed

- Migrated dataset adapters to return source data instead of evaluation cases.
- Moved line cropping, case construction, evaluation limits, and evaluator
  selection into `LineRecognitionTask`.

## [v0.30.0] - 2026-09-10

### Added

- Added an explicit OCR task interface and the `line-recognition` task.
- Added command-line task selection and task identity to saved reports.

### Changed

- Routed existing line dataset loading through the selected task.

## [v0.29.0] - 2026-09-10

### Added

- Added the Sprakbanken TrOCR model for historical Norwegian handwritten lines.

### Changed

- Applied the Transformers 5 positional-embedding compatibility fix only to TrOCR models that use fixed sinusoidal positions.

## [v0.28.0] - 2026-09-10

### Added

- Added the Riksarkivet TrOCR model for historical Swedish handwritten lines.
- Added native batched inference with deterministic greedy decoding.

## [v0.27.0] - 2026-09-10

### Added

- Added Tesseract `tessdata_best` baselines for Danish, Norwegian, and Swedish printed lines.
- Documented the external Tesseract engine and language-data setup in the draft README.

## [v0.26.0] - 2026-09-10

### Added

- Added GOT-OCR 2.0 as a multilingual line-recognition model.
- Added native batched inference through Hugging Face Transformers.

## [v0.25.0] - 2026-09-10

### Added

- Added GLM-OCR as a zero-shot Scandinavian line-recognition model.
- Added native batched inference through Hugging Face Transformers.

## [v0.24.0] - 2026-09-10

### Added

- Added PaddleOCR-VL 1.6 as a multilingual line-recognition model.
- Added native batched inference through Hugging Face Transformers.

## [v0.23.0] - 2026-09-10

### Added

- Registered EasyOCR as a Scandinavian OCR baseline for Danish, Norwegian, and Swedish.

### Changed

- Simplified the existing EasyOCR adapter and made greedy decoding explicit.
- Used recognition-only inference because evaluation samples are already cropped lines.
- Kept EasyOCR inference serial because its batched API requires equal-sized images.

## [v0.22.0] - 2026-09-10

### Added

- Published the EHRI Danish typewritten material as 1,007 prepared line images on Hugging Face.
- Added `danish-typewritten` as a streaming evaluation dataset loaded directly from Hugging Face.

## [v0.21.0] - 2026-09-10

### Added

- Added modern Danish handwriting as a streaming line evaluation dataset.
- Added PAGE XML line parsing and `modern-danish` command-line selection.

## [v0.20.0] - 2026-09-10

### Added

- Added the Riksarkivet printed Swedish Fraktur lines as a streaming evaluation dataset.
- Added `swedish-fraktur` to command-line dataset selection.

## [v0.19.0] - 2026-09-10

### Added

- Added the Riksarkivet out-of-domain Swedish historical handwriting lines as a streaming evaluation dataset.
- Added `riksarkivet-ood` to command-line dataset selection.

## [v0.18.0] - 2026-09-09

### Added

- Added native batched inference to the Qwen3-VL adapter.

### Changed

- Routed single-image Qwen3-VL inference through the same batch path.

## [v0.17.0] - 2026-09-09

### Fixed

- Saved evaluation reports before printing results so completed runs survive console failures.
- Configured command-line output as UTF-8 so OCR predictions can contain any Unicode character.

## [v0.16.0] - 2026-09-09

### Added

- Added command-line selection for registered OCR models, line datasets, batch size, and example limits.

### Changed

- Allowed Historical Danish example limits to span multiple pages.
- Limited command-line runs to 100 examples by default while datasets are held in memory.

## [v0.15.0] - 2026-09-09

### Changed

- Moved evaluation report construction, display, and saving out of `main.py` into a dedicated reporting module.

## [v0.14.0] - 2026-09-09

### Added

- Saved each evaluation run as readable JSON containing its model, dataset, raw text, metadata, and CER/WER scores.

## [v0.13.0] - 2026-09-09

### Fixed

- Made Historical Danish case names unique across pages.
- Applied `max_examples` to the complete Historical Danish dataset instead of separately to every page.

## [v0.12.0] - 2026-09-09

### Changed

- Made Qwen2-VL and Qwen3-VL OCR generation deterministic by using greedy decoding.

## [v0.11.0] - 2026-09-09

### Changed

- Normalized Unicode and whitespace before CER/WER so formatting-only line breaks do not count as recognition errors.

## [v0.10.0] - 2026-09-09

### Added

- Added per-case and corpus CER/WER reporting to the batched OCR demo.

## [v0.9.0] - 2026-09-09

### Added

- Added an explicit batch runner that keeps each dataset case paired with its model output.

### Changed

- Updated the current two-image demo to run as one batch and print each reference and prediction.

## [v0.8.0] - 2026-09-09

### Added

- Added native batched inference to the Qwen2-VL adapter.

### Changed

- Routed single-image Qwen2-VL inference through the same batch path.

## [v0.7.0] - 2026-09-09

### Changed

- Reorganized the changelog so each development commit has its own version.
- Updated the project version to 0.7.0.

## [v0.6.0] - 2026-09-09

### Changed

- Replaced Hugging Face Evaluate metric loading with direct JiWER CER and WER calculations.
- Removed Hugging Face Evaluate from the project dependencies.

## [v0.5.0] - 2026-08-18

### Added

- Added this changelog for a human-readable record of project changes.
- Added a draft README for documentation that will be published with the MVP.

### Docs

- Documented the verified setup and current entry point in the draft README.

## [v0.4.0] - 2026-08-18

### Changed

- Migrated the development environment to Python 3.12 and uv.
- Replaced the legacy dependency freeze with direct, reproducible dependencies.
- Added a cross-platform lockfile with explicit CUDA 12.6 PyTorch wheels.

## [v0.3.0] - 2026-08-18

### Changed

- Removed unused imports left over from the prototype.

## [v0.2.0] - 2026-08-18

### Changed

- Updated dataset construction for the current Pydantic Evals API.

## [v0.1.0] - 2026-08-18

### Fixed

- Repaired the Git ignore rules so Python version files and dataset adapter source files can be tracked.

## Pre-versioned prototype - 2025-10-04 to 2025-11-04

### Added

- Established the OCR model, task, evaluator, and CER/WER metric interfaces.
- Added prototype adapters for local images, NorHand, Gothenburg price tags, and historical Danish handwriting.
- Added EasyOCR and Qwen2-VL model adapters, followed by Qwen3-VL metadata and model registry support.
