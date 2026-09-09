from typing import Protocol

from app.core.config import Settings


class Generator(Protocol):
    def generate(self, prompt: str) -> str: ...


class OpenAICompatibleGenerator:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key or not settings.llm_model:
            raise ValueError("LLM_API_KEY and LLM_MODEL are required for remote generation")
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        self.model = settings.llm_model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


class DeterministicGenerator:
    def generate(self, prompt: str) -> str:
        context = prompt.split("Official context:\n", 1)[-1].split("\n\nQuestion:", 1)[0]
        return f"검색된 공식 근거를 바탕으로 안내합니다.\n\n{context}"
