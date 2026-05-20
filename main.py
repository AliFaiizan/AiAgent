import click
import asyncio
from client.llm_client import LLMClient

class CLI:
    def __init__(self):
        pass

    def run_single(self, prompt: str):
        asyncio.run(self._run(prompt))

async def run(prompt):
    llm_client = LLMClient()
    async for event in llm_client.chat_completions(
        messages=[{
            "role": "user",
            "content": prompt
        }],
        stream=True):
        print(event.text_delta.content if event.text_delta else "", end="", flush=True)
       


@click.command()
@click.argument("prompt", type=str, required=False)
def main(prompt):
    if prompt is None:
        prompt = "What is the capital of France?"
    asyncio.run(run(prompt))

main()