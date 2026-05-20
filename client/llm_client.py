import os
import asyncio
from typing import Any, AsyncGenerator
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError

from client.response import TextDelta, TokenUsage, StreamEvent, EventType


class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._max_retries = 4

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=os.getenv("API_KEY"),
                base_url=os.getenv("BASE_URL") or "",
            )
        return self._client
    
    async def close(self)-> None:
        if self._client is not None:
            await self._client.close()

    async def chat_completions(self, messages: list[dict[str,Any]], stream: bool = True)-> AsyncGenerator[StreamEvent, None]:
        for attempt in range(self._max_retries):
            try:           
                client = self.get_client()
                model = os.getenv("MODEL")
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "stream": stream
                }

                if stream:
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                return 
            except RateLimitError as e:
                if(attempt == self._max_retries - 1):
                    wait_time = 2 ** attempt
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(type=EventType.ERROR, error=f"Rate limit exceeded: {str(e)}")
            except APIConnectionError as e:
                if(attempt == self._max_retries - 1):
                    wait_time = 2 ** attempt
                    print(f"API connection error. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(type=EventType.ERROR, error=f"API connection error: {str(e)}")
            except APIError as e:
                if(attempt == self._max_retries - 1):
                    wait_time = 2 ** attempt
                    print(f"API error. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(type=EventType.ERROR, error=f"API error: {str(e)}")

    async def _stream_response(self, client: AsyncOpenAI, kwargs:dict[str,Any])-> AsyncGenerator[StreamEvent, None]:
        response = await client.chat.completions.create(**kwargs) 

        finish_reason:str | None = None
        usage: TokenUsage | None = None
        async for chunk in response:
            if hasattr(chunk, "usage") and chunk.usage:
                usage = TokenUsage(
                    prompt_tokens=chunk.usage.prompt_tokens,
                    completion_tokens=chunk.usage.completion_tokens,
                    total_tokens=chunk.usage.total_tokens,
                    cached_tokens= chunk.usage.prompt_tokens_details.cached_tokens
                )
            if not chunk.choices:
                continue
            if chunk.choices[0].finish_reason is not None:
                finish_reason = chunk.choices[0].finish_reason
 
            if chunk.choices[0].delta.content:
                text_delta = TextDelta(content=chunk.choices[0].delta.content)
                yield StreamEvent(type=EventType.TEXT_DELTA, text_delta=text_delta, usage=usage)

            yield StreamEvent(type=EventType.MESSAGE_COMPLETE, finish_reason=finish_reason, usage=usage)

    async def _non_stream_response(self, client: AsyncOpenAI, kwargs:dict[str,Any])-> StreamEvent:
        response = await client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        text_delta = None 
        if message.content:
            text_delta = TextDelta(content=message.content)
        usage = None
        if response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cached_tokens= response.usage.prompt_tokens_details.cached_tokens
            )

        return StreamEvent(
            type=EventType.MESSAGE_COMPLETE,
            text_delta=text_delta,
            finish_reason=response.choices[0].finish_reason,
            usage=usage
        )
