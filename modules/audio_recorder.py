from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write

from config import AUDIO_DIR, settings
from modules.utils import ensure_directory, timestamp_filename


def record_audio() -> Path:
    ensure_directory(AUDIO_DIR)

    output_path = AUDIO_DIR / timestamp_filename("input", "wav")

    print("\nRecording started...")
    print(f"Please speak for {settings.record_seconds} seconds.")

    audio_data = sd.rec(
        int(settings.record_seconds * settings.sample_rate),
        samplerate=settings.sample_rate,
        channels=settings.audio_channels,
        dtype="int16",
    )

    sd.wait()

    write(output_path, settings.sample_rate, audio_data)

    print(f"Recording saved: {output_path}")

    return output_path