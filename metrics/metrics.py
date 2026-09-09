import jiwer


def cer(model_output: str | list[str], ground_truth: str | list[str]) -> float:
    return jiwer.cer(ground_truth, model_output)


def wer(model_output: str | list[str], ground_truth: str | list[str]) -> float:
    return jiwer.wer(ground_truth, model_output)

