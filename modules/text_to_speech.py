from pathlib import Path

from gtts import gTTS

from config import AUDIO_DIR
from modules.utils import ensure_directory, timestamp_filename


def convert_text_to_speech(text: str) -> Path:
    if not text or not text.strip():
        raise ValueError("Text-to-Speech failed. Empty text received.")

    ensure_directory(AUDIO_DIR)

    audio_path = AUDIO_DIR / timestamp_filename("assistant_response", "mp3")

    print("Converting text to speech using gTTS...")

    tts = gTTS(text=text, lang="en")
    tts.save(str(audio_path))

    print(f"TTS audio saved at: {audio_path}")
    return audio_path


def play_audio(audio_path: Path) -> None:
    print(f"Audio ready: {audio_path}")
