import logging
from google import genai
from fastapi import Request
from google.genai.types import GenerateContentResponse
from .exceptions import LLMRequestFailedError

logger = logging.getLogger(__name__)


class LLMManager:
    def __init__(self, api_key: str, model_name: str):
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def get_client(self) -> genai.Client:
        return self._client

    async def generate_content(self, prompt: str) -> GenerateContentResponse:
        try:
            return await self._client.aio.models.generate_content(
                model=self.model_name, contents=prompt
            )
        except Exception as e:
            logger.error(f"exception will calling llm : ${e}")
            raise LLMRequestFailedError()


def get_llm_lg(request: Request) -> LLMManager:
    return request.state.model_lg


def get_llm_sm(request: Request) -> LLMManager:
    return request.state.model_sm
