from tasks.line_recognition import LineRecognitionTask
from tasks.task_interface import OCRTask


LINE_RECOGNITION = LineRecognitionTask()

TASK_REGISTRY = {
    LINE_RECOGNITION.id: LINE_RECOGNITION,
}


def get_task(name: str) -> OCRTask:
    return TASK_REGISTRY[name]
