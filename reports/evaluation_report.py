import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic_evals import Case, Dataset

from metrics.metrics import cer, wer
from models.model_interface import OCROutput, OCRModel


def build_evaluation_report(
    model: OCRModel,
    dataset: Dataset,
    task: str,
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
            "cer": cer(output.text, case.expected_output),
            "wer": wer(output.text, case.expected_output),
            "metadata": case.metadata,
        }
        for case, output in results
    ]

    return {
        "model": model.id,
        "dataset": dataset.name,
        "task": task,
        "batch_size": batch_size,
        "cases": case_results,
        "corpus_metrics": {
            "cer": cer(predictions, references),
            "wer": wer(predictions, references),
        },
    }


def print_evaluation_report(report: dict) -> None:
    print(f"Task: {report['task']}")
    print()

    for case_result in report["cases"]:
        print(case_result["name"])
        print(f"Expected: {case_result['reference']}")
        print(f"Predicted: {case_result['prediction']}")
        print(f"CER: {case_result['cer']:.4f}")
        print(f"WER: {case_result['wer']:.4f}")
        print()

    print("Corpus")
    print(f"CER: {report['corpus_metrics']['cer']:.4f}")
    print(f"WER: {report['corpus_metrics']['wer']:.4f}")


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
