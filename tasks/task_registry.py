from tasks.line_recognition import LineRecognitionTask
from tasks.page_transcription import PageTranscriptionTask
from tasks.task_interface import OCRTask


LINE_RECOGNITION = LineRecognitionTask()
PAGE_TRANSCRIPTION = PageTranscriptionTask()

TASK_REGISTRY = {
    LINE_RECOGNITION.id: LINE_RECOGNITION,
    PAGE_TRANSCRIPTION.id: PAGE_TRANSCRIPTION,
}


def get_task(name: str) -> OCRTask:
    return TASK_REGISTRY[name]
