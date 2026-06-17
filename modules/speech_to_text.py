from pathlib import Path

from groq import Groq

from config import settings
from modules.utils import clean_text


def get_groq_sdk_base_url() -> str:
    base_url = settings.groq_base_url.rstrip("/")

    if base_url.endswith("/openai/v1"):
        return base_url[: -len("/openai/v1")]

    return base_url


client = Groq(
    api_key=settings.groq_api_key,
    base_url=get_groq_sdk_base_url(),
)


def transcribe_audio(audio_path: Path) -> str:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print("Converting speech to text using Groq Whisper...")

    try:
        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=settings.groq_stt_model,
                response_format="text",
            )

        text = clean_text(str(transcription))

        if not text:
            raise ValueError("Speech-to-Text failed. No text detected.")

        print(f"STT output: {text}")
        return text

    except Exception as error:
        raise RuntimeError(f"Groq Speech-to-Text failed: {error}")
