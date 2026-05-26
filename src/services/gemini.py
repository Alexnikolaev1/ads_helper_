from dataclasses import dataclass

import google.generativeai as genai

from src.config import MODELS_CHAIN, GenerationOptions
from src.prompts import build_system_prompt, build_user_prompt
from src.utils.token_budget import extract_token_count


@dataclass(frozen=True)
class GenerationResult:
    text: str
    tokens_used: int


class PostGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    def generate(self, brief: str, options: GenerationOptions) -> GenerationResult:
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
                    tokens_used = extract_token_count(response)
                    return GenerationResult(
                        text=text.strip(),
                        tokens_used=tokens_used,
                    )
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"Все модели недоступны. Последняя ошибка: {last_error}"
        )
