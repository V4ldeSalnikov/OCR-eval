# main.py

from cli import parse_args
from models.model_registry import get_model
from ocr_datasets.dataset_registry import get_dataset
from reports.evaluation_report import (
    build_evaluation_report,
    print_evaluation_report,
    save_evaluation_report,
)
from tasks.ocr_task import run_batch_ocr


def main():
    args = parse_args()
    model = get_model(args.model)
    dataset = get_dataset(args.dataset, args.max_examples).load_dataset()
    results = run_batch_ocr(model, dataset, batch_size=args.batch_size)
    report = build_evaluation_report(model, dataset, args.batch_size, results)

    print_evaluation_report(report)
    report_path = save_evaluation_report(report)
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
