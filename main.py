# main.py

from models.model_registry import get_model
from ocr_datasets.datasets.simple_dataset import SimpleDataset
from reports.evaluation_report import (
    build_evaluation_report,
    print_evaluation_report,
    save_evaluation_report,
)
from tasks.ocr_task import run_batch_ocr


def main():
    model = get_model("Qwen/Qwen2-VL-2B-Instruct")
    dataset = SimpleDataset().load_dataset()
    batch_size = 2
    results = run_batch_ocr(model, dataset, batch_size=batch_size)
    report = build_evaluation_report(model, dataset, batch_size, results)

    print_evaluation_report(report)
    report_path = save_evaluation_report(report)
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
