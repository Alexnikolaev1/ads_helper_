import google.generativeai as genai

from src.config import MODELS_CHAIN, GenerationOptions
from src.prompts import build_system_prompt, build_user_prompt


class PostGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    def generate(self, brief: str, options: GenerationOptions) -> str:
        system = build_system_prompt(options)
        user = build_user_prompt(brief, options)
        prompt = f"{system}\n\n{user}"
        last_error: Exception | None = None

        for model_name in MODELS_CHAIN:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.85,
                        max_output_tokens=2500,
                    ),
                )
                text = getattr(response, "text", None)
                if text and text.strip():
                    return text.strip()
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"Все модели недоступны. Последняя ошибка: {last_error}"
        )
