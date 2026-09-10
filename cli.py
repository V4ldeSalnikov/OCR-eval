from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)

from models.model_registry import MODEL_REGISTRY
from ocr_datasets.dataset_registry import DATASET_REGISTRY
from tasks.task_registry import TASK_REGISTRY


def positive_integer(value: str) -> int:
    number = int(value)
    if number < 1:
        raise ArgumentTypeError("must be greater than zero")
    return number


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Run an OCR evaluation.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model",
        choices=sorted(MODEL_REGISTRY),
        default="Qwen/Qwen2-VL-2B-Instruct",
        help="Model to evaluate.",
    )
    parser.add_argument(
        "--dataset",
        choices=sorted(DATASET_REGISTRY),
        default="simple",
        help="Dataset to evaluate.",
    )
    parser.add_argument(
        "--task",
        choices=sorted(TASK_REGISTRY),
        default="line-recognition",
        help="OCR task to evaluate.",
    )
    parser.add_argument(
        "--batch-size",
        type=positive_integer,
        default=2,
        help="Inference batch size.",
    )
    parser.add_argument(
        "--max-examples",
        type=positive_integer,
        default=100,
        help="Maximum number of evaluation cases.",
    )
    return parser.parse_args()
