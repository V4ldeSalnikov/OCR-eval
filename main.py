# main.py

from ocr_datasets.datasets.simple_dataset import SimpleDataset
from tasks.ocr_task import run_batch_ocr
from models.model_registry import get_model


def main():
    model = get_model("Qwen/Qwen2-VL-2B-Instruct")
    dataset = SimpleDataset().load_dataset()
    results = run_batch_ocr(model, dataset, batch_size=2)

    for case, output in results:
        print(f"{case.name}")
        print(f"Expected: {case.expected_output}")
        print(f"Predicted: {output.text}")


if __name__ == "__main__":
    main()
