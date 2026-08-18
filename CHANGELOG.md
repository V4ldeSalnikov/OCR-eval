# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Added this changelog for a human-readable record of project changes.
- Added a draft README for documentation that will be published with the MVP.

### Changed

- Updated dataset construction for the current Pydantic Evals API.
- Migrated the development environment to Python 3.12 and uv with a cross-platform lockfile.
- Replaced the legacy dependency freeze with direct, reproducible dependencies and explicit CUDA 12.6 PyTorch wheels.

### Fixed

- Repaired the Git ignore rules so Python version files and dataset adapter source files can be tracked.

### Docs

- Documented the verified setup and current entry point in the draft README.

## Pre-MVP prototype - 2025-10-04 to 2025-11-04

### Added

- Established the OCR model, task, evaluator, and CER/WER metric interfaces.
- Added prototype adapters for local images, NorHand, Gothenburg price tags, and historical Danish handwriting.
- Added EasyOCR and Qwen2-VL model adapters, followed by Qwen3-VL metadata and model registry support.
