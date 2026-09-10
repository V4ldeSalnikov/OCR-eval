# main.py

import sys

from cli import parse_args
from models.model_registry import get_model_meta
from ocr_datasets.dataset_registry import get_dataset
from reports.evaluation_report import (
    build_evaluation_report,
    print_evaluation_report,
    save_evaluation_report,
)
from tasks.ocr_task import run_batch_ocr
from tasks.task_registry import get_task


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    source = get_dataset(args.dataset)
    task = get_task(args.task)
    model_meta = get_model_meta(args.model)
    model_meta.validate_task(task.id)
    dataset = task.build_dataset(source, args.max_examples)
    model = model_meta.load(task.id)
    results = run_batch_ocr(model, dataset, batch_size=args.batch_size)
    report = build_evaluation_report(
        model,
        dataset,
        task.id,
        args.batch_size,
        results,
    )

    report_path = save_evaluation_report(report)
    print_evaluation_report(report)
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
