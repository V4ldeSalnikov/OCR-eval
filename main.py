# main.py

from metrics.metrics import cer, wer
from models.model_registry import get_model
from ocr_datasets.datasets.simple_dataset import SimpleDataset
from tasks.ocr_task import run_batch_ocr


def main():
    model = get_model("Qwen/Qwen2-VL-2B-Instruct")
    dataset = SimpleDataset().load_dataset()
    results = run_batch_ocr(model, dataset, batch_size=2)
    predictions = [output.text for _, output in results]
    references = [case.expected_output for case, _ in results]

    for case, output in results:
        print(f"{case.name}")
        print(f"Expected: {case.expected_output}")
        print(f"Predicted: {output.text}")
        print(f"CER: {cer(output.text, case.expected_output):.4f}")
        print(f"WER: {wer(output.text, case.expected_output):.4f}")
        print()

    print("Corpus")
    print(f"CER: {cer(predictions, references):.4f}")
    print(f"WER: {wer(predictions, references):.4f}")


if __name__ == "__main__":
    main()
