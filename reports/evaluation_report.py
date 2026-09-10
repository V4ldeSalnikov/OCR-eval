import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic_evals import Case, Dataset

from models.model_interface import OCROutput, OCRModel
from tasks.task_interface import OCRTask


def build_evaluation_report(
    model: OCRModel,
    dataset: Dataset,
    task: OCRTask,
    batch_size: int,
    results: list[tuple[Case, OCROutput]],
) -> dict:
    predictions = [output.text for _, output in results]
    references = [case.expected_output for case, _ in results]
    case_results = [
        {
            "name": case.name,
            "reference": case.expected_output,
            "prediction": output.text,
            **task.calculate_metrics(output.text, case.expected_output),
            "metadata": case.metadata,
        }
        for case, output in results
    ]

    return {
        "model": model.id,
        "dataset": dataset.name,
        "task": task.id,
        "batch_size": batch_size,
        "cases": case_results,
        "corpus_metrics": task.calculate_metrics(predictions, references),
    }


def print_evaluation_report(report: dict) -> None:
    print(f"Task: {report['task']}")
    print()

    for case_result in report["cases"]:
        print(case_result["name"])
        print(f"Expected: {case_result['reference']}")
        print(f"Predicted: {case_result['prediction']}")
        for name in report["corpus_metrics"]:
            print(f"{name.upper()}: {case_result[name]:.4f}")
        print()

    print("Corpus")
    for name, value in report["corpus_metrics"].items():
        print(f"{name.upper()}: {value:.4f}")


def save_evaluation_report(report: dict) -> Path:
    runs_dir = Path(__file__).resolve().parents[1] / "runs"
    runs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    model_name = report["model"].replace("/", "--")
    report_path = runs_dir / (
        f"{timestamp}_{report['dataset']}_{report['task']}_{model_name}.json"
    )

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")

    return report_path
