from pathlib import Path
from datetime import datetime


EXIT_COMMANDS = {"exit", "stop", "quit", "bye", "close"}


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    if not text:
        return ""

    cleaned = " ".join(text.strip().split())
    return cleaned


def is_exit_command(text: str) -> bool:
    cleaned = clean_text(text).lower()
    return cleaned in EXIT_COMMANDS


def timestamp_filename(prefix: str, extension: str) -> str:
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{current_time}.{extension}"