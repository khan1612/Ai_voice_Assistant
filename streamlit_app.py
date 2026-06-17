from pathlib import Path
import base64
import hashlib
import html

import streamlit as st
import streamlit.components.v1 as components

from config import AUDIO_DIR
from modules.utils import ensure_directory, timestamp_filename
from modules.speech_to_text import transcribe_audio
from modules.llm_service import generate_ai_response
from modules.text_to_speech import convert_text_to_speech


st.set_page_config(
    page_title="AI Assistant",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
    }

    html, body, .stApp {
        height: 100%;
        overflow: hidden !important;
        background: #f3f4f6;
    }

    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .fixed-top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 76px;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid #e5e7eb;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 30px;
        box-shadow: 0 4px 18px rgba(17, 24, 39, 0.05);
    }

    .brand-area {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo {
        width: 46px;
        height: 46px;
        border-radius: 999px;
        background: linear-gradient(135deg, #111827, #374151);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 17px;
        font-weight: 900;
        letter-spacing: 0.03em;
        box-shadow: 0 8px 22px rgba(17, 24, 39, 0.20);
    }

    .brand-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
    }

    .brand-status {
        font-size: 13px;
        color: #6b7280;
        margin-top: 2px;
    }

    .status-dot {
        width: 9px;
        height: 9px;
        background: #22c55e;
        border-radius: 999px;
        display: inline-block;
        margin-right: 6px;
    }

    div.stButton {
        position: fixed !important;
        top: 16px !important;
        right: 30px !important;
        z-index: 10020 !important;
        width: auto !important;
        margin: 0 !important;
    }

    div.stButton > button {
        width: auto !important;
        min-width: 126px !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #4338ca, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.62rem 1.2rem !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        box-shadow: 0 10px 24px rgba(79, 70, 229, 0.28) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        transform: translateY(-1px);
    }

    .chat-fixed {
        position: fixed;
        top: 76px;
        left: 0;
        right: 0;
        bottom: 142px;
        overflow-y: auto;
        padding: 28px 28px 26px 28px;
        background:
            radial-gradient(circle at top left, rgba(99, 102, 241, 0.07), transparent 30%),
            radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.07), transparent 30%),
            #f3f4f6;
        scroll-behavior: smooth;
        z-index: 1;
    }

    .chat-inner {
        max-width: 980px;
        min-height: 100%;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        gap: 14px;
    }

    .empty-state {
        margin: auto;
        text-align: center;
        color: #9ca3af;
    }

    .empty-icon {
        width: 92px;
        height: 92px;
        border-radius: 999px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 12px 30px rgba(17, 24, 39, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 900;
        color: #111827;
        margin: 0 auto 16px auto;
    }

    .empty-title {
        font-size: 21px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 6px;
    }

    .empty-subtitle {
        font-size: 15px;
        color: #6b7280;
    }

    .history-note {
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .user-row {
        display: flex;
        justify-content: flex-end;
        width: 100%;
    }

    .user-bubble {
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        color: #14532d;
        border-radius: 20px 20px 5px 20px;
        padding: 12px 18px;
        min-width: 150px;
        max-width: 360px;
        box-shadow: 0 8px 20px rgba(20, 83, 45, 0.08);
        font-weight: 800;
        font-size: 14px;
        text-align: center;
    }

    .assistant-row {
        display: flex;
        justify-content: flex-start;
        width: 100%;
    }

    .assistant-bubble {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        color: #111827;
        border-radius: 20px 20px 20px 5px;
        padding: 18px 20px;
        max-width: 720px;
        box-shadow: 0 10px 28px rgba(17, 24, 39, 0.07);
    }

    .assistant-label {
        font-size: 13px;
        font-weight: 800;
        color: #6b7280;
        margin-bottom: 7px;
    }

    .assistant-text {
        font-size: 16px;
        line-height: 1.7;
        color: #111827;
    }

    .assistant-audio {
        margin-top: 14px;
        width: 100%;
    }

    .assistant-audio audio {
        width: 100%;
        height: 38px;
    }

    .fixed-bottom-shell {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        height: 142px;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(18px);
        border-top: 1px solid #e5e7eb;
        z-index: 9999;
        box-shadow: 0 -8px 28px rgba(17, 24, 39, 0.08);
    }

    .input-glow-label {
        position: fixed;
        left: 50%;
        bottom: 112px;
        transform: translateX(-50%);
        z-index: 10002;
        color: #4338ca;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.02em;
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        padding: 5px 14px;
        border-radius: 999px;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.14);
    }

    div[data-testid="stAudioInput"] {
        position: fixed !important;
        left: 50% !important;
        bottom: 28px !important;
        transform: translateX(-50%) !important;
        width: min(720px, calc(100vw - 42px)) !important;
        z-index: 10000 !important;
        margin: 0 !important;
        padding: 13px !important;
        background: linear-gradient(135deg, #ffffff, #f8fafc) !important;
        border: 2px solid #6366f1 !important;
        border-radius: 30px !important;
        box-shadow:
            0 0 0 5px rgba(99, 102, 241, 0.10),
            0 18px 46px rgba(79, 70, 229, 0.20) !important;
        animation: voiceGlow 2s infinite ease-in-out;
    }

    div[data-testid="stAudioInput"] button {
        border-radius: 999px !important;
        background: linear-gradient(135deg, #ec4899, #8b5cf6, #3b82f6) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 22px rgba(99, 102, 241, 0.28) !important;
    }

    div[data-testid="stAudioInput"] button:hover {
        transform: scale(1.04);
        box-shadow: 0 10px 26px rgba(99, 102, 241, 0.35) !important;
    }

    div[data-testid="stAudioInput"] svg {
        color: white !important;
        fill: white !important;
        stroke: white !important;
    }

    @keyframes voiceGlow {
        0% {
            box-shadow:
                0 0 0 5px rgba(99, 102, 241, 0.10),
                0 18px 46px rgba(79, 70, 229, 0.18);
        }
        50% {
            box-shadow:
                0 0 0 8px rgba(99, 102, 241, 0.16),
                0 20px 52px rgba(79, 70, 229, 0.24);
        }
        100% {
            box-shadow:
                0 0 0 5px rgba(99, 102, 241, 0.10),
                0 18px 46px rgba(79, 70, 229, 0.18);
        }
    }

    div[data-testid="stAudioInput"] label {
        display: none !important;
    }

    div[data-testid="stAudioInput"] section {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 22px !important;
    }

    div[data-testid="stAudioInput"] audio {
        width: 100% !important;
    }

    .stSpinner {
        position: fixed;
        bottom: 150px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10001;
    }

    @media (max-width: 768px) {
        .fixed-top-bar {
            height: 66px;
            padding: 0 16px;
        }

        .brand-logo {
            width: 38px;
            height: 38px;
            font-size: 15px;
        }

        .brand-title {
            font-size: 18px;
        }

        .brand-status {
            font-size: 12px;
        }

        div.stButton {
            top: 14px !important;
            right: 14px !important;
        }

        div.stButton > button {
            min-width: 106px !important;
            padding: 0.5rem 0.85rem !important;
            font-size: 13px !important;
        }

        .chat-fixed {
            top: 66px;
            bottom: 132px;
            padding: 18px 14px 20px 14px;
        }

        .assistant-bubble {
            max-width: 92%;
            padding: 15px 16px;
        }

        div[data-testid="stAudioInput"] {
            width: calc(100vw - 24px) !important;
            bottom: 18px !important;
        }

        .input-glow-label {
            bottom: 98px;
        }
    }
</style>
"""


def initialize_session_state() -> None:
    if "chat_items" not in st.session_state:
        st.session_state.chat_items = []

    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = ""

    if "recorder_key" not in st.session_state:
        st.session_state.recorder_key = 0


def get_audio_hash(uploaded_audio) -> str:
    return hashlib.sha256(uploaded_audio.getvalue()).hexdigest()


def save_uploaded_audio(uploaded_audio) -> Path:
    ensure_directory(AUDIO_DIR)
    audio_path = AUDIO_DIR / timestamp_filename("user_voice", "wav")

    with open(audio_path, "wb") as audio_file:
        audio_file.write(uploaded_audio.getvalue())

    return audio_path


def audio_file_to_data_uri(audio_path: str) -> str:
    file_path = Path(audio_path)

    if not file_path.exists():
        return ""

    audio_bytes = file_path.read_bytes()
    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
    return f"data:audio/mp3;base64,{encoded_audio}"


def process_voice(uploaded_audio) -> None:
    user_audio_path = save_uploaded_audio(uploaded_audio)

    user_text = transcribe_audio(user_audio_path)
    ai_response = generate_ai_response(user_text)
    assistant_audio_path = convert_text_to_speech(ai_response)

    assistant_audio_uri = audio_file_to_data_uri(str(assistant_audio_path))

    st.session_state.chat_items.append(
        {
            "role": "user_voice",
            "audio": str(user_audio_path),
        }
    )

    st.session_state.chat_items.append(
        {
            "role": "assistant",
            "text": ai_response,
            "audio_uri": assistant_audio_uri,
        }
    )


def reset_chat() -> None:
    st.session_state.chat_items = []
    st.session_state.last_audio_hash = ""
    st.session_state.recorder_key += 1

    for key in list(st.session_state.keys()):
        if str(key).startswith("voice_recorder_"):
            del st.session_state[key]


def render_top_bar() -> None:
    st.markdown(
        """
        <div class="fixed-top-bar">
            <div class="brand-area">
                <div class="brand-logo">AI</div>
                <div>
                    <div class="brand-title">AI Assistant</div>
                    <div class="brand-status">
                        <span class="status-dot"></span>Voice mode ready
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_chat_html() -> str:
    visible_items = st.session_state.chat_items[-20:]

    html_parts = [
        '<div class="chat-fixed" id="chat-fixed">',
        '<div class="chat-inner">',
    ]

    if not visible_items:
        html_parts.append(
            """
            <div class="empty-state">
                <div class="empty-icon">AI</div>
                <div class="empty-title">Ready for Voice Input</div>
                <div class="empty-subtitle">Use the highlighted microphone bar below.</div>
            </div>
            """
        )
    else:
        hidden_count = len(st.session_state.chat_items) - len(visible_items)

        if hidden_count > 0:
            html_parts.append(
                f"""
                <div class="history-note">
                    {hidden_count} older messages hidden to keep latest reply visible.
                </div>
                """
            )

        latest_assistant_index = None
        for index, item in enumerate(visible_items):
            if item["role"] == "assistant":
                latest_assistant_index = index

        for index, item in enumerate(visible_items):
            if item["role"] == "user_voice":
                html_parts.append(
                    """
                    <div class="user-row">
                        <div class="user-bubble">Voice sent</div>
                    </div>
                    """
                )

            elif item["role"] == "assistant":
                safe_text = html.escape(item["text"])
                audio_html = ""

                if index == latest_assistant_index and item.get("audio_uri"):
                    audio_html = f"""
                    <div class="assistant-audio">
                        <audio controls autoplay src="{item["audio_uri"]}"></audio>
                    </div>
                    """

                html_parts.append(
                    f"""
                    <div class="assistant-row">
                        <div class="assistant-bubble">
                            <div class="assistant-label">AI Assistant</div>
                            <div class="assistant-text">{safe_text}</div>
                            {audio_html}
                        </div>
                    </div>
                    """
                )

    html_parts.append('<div id="latest-message-anchor"></div>')
    html_parts.append("</div></div>")

    return "\n".join(
        line.strip()
        for line in "\n".join(html_parts).splitlines()
        if line.strip()
    )


def render_chat() -> None:
    st.markdown(build_chat_html(), unsafe_allow_html=True)


def auto_scroll_chat_to_bottom() -> None:
    components.html(
        """
        <script>
            function scrollChatToBottom() {
                const doc = window.parent.document;
                const chat = doc.getElementById("chat-fixed");
                if (chat) {
                    chat.scrollTop = chat.scrollHeight;
                }
            }

            setTimeout(scrollChatToBottom, 100);
            setTimeout(scrollChatToBottom, 400);
            setTimeout(scrollChatToBottom, 900);
            setTimeout(scrollChatToBottom, 1400);
        </script>
        """,
        height=0,
        width=0,
    )


def render_bottom_recorder() -> object:
    st.markdown(
        """
        <div class="fixed-bottom-shell"></div>
        <div class="input-glow-label">Tap to record your voice</div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_audio = st.audio_input(
        "Record voice",
        label_visibility="collapsed",
        key=f"voice_recorder_{st.session_state.recorder_key}",
    )

    return uploaded_audio


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_session_state()

    render_top_bar()

    if st.button("Clear Chat", key="clear_chat_button"):
        reset_chat()
        st.rerun()

    render_chat()
    auto_scroll_chat_to_bottom()

    uploaded_audio = render_bottom_recorder()

    if uploaded_audio is not None:
        current_hash = get_audio_hash(uploaded_audio)

        if current_hash != st.session_state.last_audio_hash:
            try:
                with st.spinner("Processing voice..."):
                    process_voice(uploaded_audio)

                # Hash success ke baad set hoga
                st.session_state.last_audio_hash = current_hash

                # Recorder reset for next input
                st.session_state.recorder_key += 1
                st.session_state.last_audio_hash = ""

                st.rerun()

            except Exception as error:
                # Agar error aaye to same audio dobara process ho sake
                st.session_state.last_audio_hash = ""

                st.error("Assistant could not process your voice.")
                st.exception(error)

if __name__ == "__main__":
    main()