import os
from typing import Any
from openai import AsyncAzureOpenAI


class LLMClient:
    def __init__(self, llm_api) -> None:
        self.__client: AsyncAzureOpenAI | None = None

    def get_client(self) -> AsyncAzureOpenAI:
        if self.__client is None:
            self.__client = AsyncAzureOpenAI(
                api_key=os.getenv("OPENAI_KEY"),
                azure_endpoint= os.getenv("API_ENDPOINT") or "",
                api_version="2025-01-01-preview"
            )
        return self.__client
    
    async def close(self)-> None:
        if self.__client is not None:
            await self.__client.close()

    async def chat_completions(self, messages: list[dict[str,Any]], stream: bool = True):
        if stream:
            self._stream_response()
        else:
            self._non_stream_response()

    def _stream_response(self):
        pass

    def _non_stream_response(self):
        pass