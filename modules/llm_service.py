from openai import OpenAI

from config import settings
from modules.utils import clean_text


client = OpenAI(
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url,
)


def generate_ai_response(user_text: str) -> str:
    user_text = clean_text(user_text)

    if not user_text:
        raise ValueError("User text empty hai. GroqCloud ko empty message send nahi kar sakte.")

    print("Generating AI response using GroqCloud...")

    response = client.chat.completions.create(
        model=settings.groq_llm_model,
        messages=[
            {
                "role": "system",
                "content": settings.system_prompt,
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        temperature=0.3,
        max_tokens=100,
    )

    ai_text = response.choices[0].message.content
    ai_text = clean_text(ai_text)

    if not ai_text:
        raise ValueError("GroqCloud ne empty response diya.")

    print(f"Assistant: {ai_text}")

    return ai_text