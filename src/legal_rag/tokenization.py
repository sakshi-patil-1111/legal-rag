import re


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())
