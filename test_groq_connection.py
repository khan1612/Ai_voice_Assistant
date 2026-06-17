from openai import OpenAI

from config import settings


def test_groq_connection() -> None:
    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )

    print("Testing GroqCloud API connection...")

    response = client.chat.completions.create(
        model=settings.groq_llm_model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "Say only: GroqCloud connection successful.",
            },
        ],
        temperature=0,
        max_tokens=20,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    test_groq_connection()