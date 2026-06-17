from openai import OpenAI

from config import settings


def test_connection() -> None:
    client = OpenAI(api_key=settings.openai_api_key)

    print("Testing OpenAI API connection...")

    response = client.responses.create(
        model=settings.llm_model,
        input="Say only: Connection successful.",
    )

    print(response.output_text)


if __name__ == "__main__":
    test_connection()