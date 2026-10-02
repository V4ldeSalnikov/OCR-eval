# World-OCR-Benchmark (MVP)

Evaluation framework for Multilingual, Multitype OCR models (classical + VLM based). Based on Pydantic Eval framework

[Published evaluation results](results/README.md) · [ScandiOCR leaderboard](https://v4ldesalnikov.github.io/ocr-eval/)

Dataset TODO list:

  Danish :
  - [X] [Historical Danish Handwriting](https://huggingface.co/datasets/aarhus-city-archives/historical-danish-handwriting)

  Swedish :
  - [ ] [Swedish newspapers 1871-1906](https://spraakbanken.gu.se/en/resources/svenska-tidningar-1871-1906)
  - [ ] [Swedish newspapers 1818-1870](https://spraakbanken.gu.se/en/resources/svenska-tidningar-1818-1870)
  - [ ] [Swedish fraktur 1626-1816](https://spraakbanken.gu.se/en/resources/svensk-fraktur-1626-1816)
  
  Faroese :
  - [ ] [FaroeseOCR](https://mtd.setur.fo/en/resource/faroeseocr/)

  Icelandic:
  - [ ] [OCR Icelandic benchmark](https://huggingface.co/datasets/Sigurdur/OCR-Icelandic-benchmark)


Models TODO list :

  Classical OCR models :
  - [ ] [docTR danish](https://huggingface.co/diversen/doctr-torch-crnn_vgg16_bn-danish-v1)
  - [ ] [Tesseract](https://tesseract-ocr.github.io/tessdoc/)


  VLM-based models :
  - [ ] [Gemma3-27b](https://huggingface.co/google/gemma-3-27b-it)
  - [ ] [Gemma3-12b](https://huggingface.co/google/gemma-3-12b-it)
  - [ ] [Gemma3-4b](https://huggingface.co/google/gemma-3-4b-it)
  - [ ] [Qwen3-VL-2B-Instruct](huggingface.co/Qwen/Qwen3-VL-2B-Instruct)
  - [ ] [Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct)
  - [ ] [DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
  - [ ] [PaddleOCR-VL](https://huggingface.co/PaddlePaddle/PaddleOCR-VL)
  - [ ] [Nanonets-OCR2-3B](https://huggingface.co/nanonets/Nanonets-OCR2-3B)

General benchmark TODO list :

- [ ] Transfer project ot uv to manage dependencies
- [ ] Create tests for datasets
- [ ] Create tests for models
- [ ] Automatically set the language for the model, depending on the dataset that is being used for evaluation
