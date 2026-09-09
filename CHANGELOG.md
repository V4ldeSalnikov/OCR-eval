# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
From v0.1.0 onward, each development commit advances the minor version.

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
