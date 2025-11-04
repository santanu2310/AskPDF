import asyncio
from google import genai
from fastapi import Request


class LLMManager:
    def __init__(self, api_key: str, model_name: str):
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def get_client(self) -> genai.Client:
        return self._client

    def generate_content(self, prompt: str):
        return self._client.models.generate_content(
            model=self.model_name, contents=prompt
        )

    async def generate_content_async(self, prompt: str):
        return await asyncio.to_thread(self.generate_content, prompt)


def get_llm_lg(request: Request) -> LLMManager:
    return request.state.model_lg


def get_llm_sm(request: Request) -> LLMManager:
    return request.state.model_sm
