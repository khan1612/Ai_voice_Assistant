from modules.audio_recorder import record_audio
from modules.speech_to_text import transcribe_audio
from modules.llm_service import generate_ai_response
from modules.text_to_speech import convert_text_to_speech, play_audio
from modules.utils import is_exit_command


def run_single_turn() -> None:
    audio_path = record_audio()

    user_text = transcribe_audio(audio_path)

    if is_exit_command(user_text):
        print("Exit command detected. Conversation stopped.")
        raise KeyboardInterrupt

    ai_response = generate_ai_response(user_text)

    response_audio_path = convert_text_to_speech(ai_response)

    play_audio(response_audio_path)


def run_conversation_loop() -> None:
    print("\nAI Voice Assistant started.")
    print("Press Enter to speak.")
    print("Say 'stop', 'exit', 'quit', or 'bye' to close the assistant.")

    while True:
        try:
            input("\nPress Enter when you are ready to speak...")
            run_single_turn()

        except KeyboardInterrupt:
            print("\nAssistant closed.")
            break

        except Exception as error:
            print("\nError occurred:")
            print(error)
            print("Please try again.")