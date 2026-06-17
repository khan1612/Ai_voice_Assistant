from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio_files"


def get_secret(key: str, default: str = "") -> str:
    """
    First read from environment/.env.
    If not found, try Streamlit secrets.
    This makes the project work locally and on Streamlit Cloud.
    """
    value = os.getenv(key, "").strip()
    if value:
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    return default


@dataclass
class Settings:
    groq_api_key: str
    groq_base_url: str
    groq_llm_model: str
    groq_stt_model: str
    record_seconds: int
    sample_rate: int
    audio_channels: int
    system_prompt: str


def load_settings() -> Settings:
    groq_api_key = get_secret("GROQ_API_KEY")

    if not groq_api_key or groq_api_key == "your_real_groqcloud_api_key_here":
        raise ValueError(
            "GROQ_API_KEY missing hai. Local .env ya Streamlit secrets me apni real GroqCloud API key add karein."
        )

    return Settings(
    groq_api_key=groq_api_key,
    groq_base_url=get_secret("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
    groq_llm_model=get_secret("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
    groq_stt_model=get_secret("GROQ_STT_MODEL", "whisper-large-v3-turbo"),
    record_seconds=int(get_secret("RECORD_SECONDS", "8")),
    sample_rate=int(get_secret("SAMPLE_RATE", "16000")),
    audio_channels=int(get_secret("AUDIO_CHANNELS", "1")),
    system_prompt=(
        "You are a helpful AI voice assistant. "
        "Give short, clear, and simple answers suitable for speaking aloud. "
        "Answer in 2 to 4 sentences unless the user asks for detail."
    ),
)


settings = load_settings()