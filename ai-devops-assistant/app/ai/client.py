import os

import ollama
from dotenv import load_dotenv


load_dotenv()

MODEL = "qwen3:4b"
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
def is_ai_available() -> bool:
    if AI_PROVIDER != "ollama":
        return False

    try:
        ollama.list()
        return True
    except Exception:
        return False

def ask_ollama(prompt: str, timeout: int = 45) -> str:
    if AI_PROVIDER != "ollama":
        raise RuntimeError(
            f"Unsupported AI provider: {AI_PROVIDER}"
        )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={
            "num_predict": 60,
        },
    )

    return response["message"]["content"]