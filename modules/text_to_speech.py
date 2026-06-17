from pathlib import Path
import time

import pygame
from gtts import gTTS

from config import AUDIO_DIR
from modules.utils import ensure_directory, timestamp_filename


def convert_text_to_speech(text: str) -> Path:
    ensure_directory(AUDIO_DIR)

    if not text.strip():
        raise ValueError("TTS ke liye text empty hai.")

    output_path = AUDIO_DIR / timestamp_filename("response", "mp3")

    print("Converting text to speech using gTTS...")

    tts = gTTS(text=text, lang="en")
    tts.save(str(output_path))

    print(f"Speech audio saved: {output_path}")

    return output_path


def play_audio(audio_path: Path) -> None:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print("Playing assistant response...")

    pygame.mixer.init()

    try:
        pygame.mixer.music.load(str(audio_path))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()

    finally:
        pygame.mixer.quit()