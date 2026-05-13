from client.llm_client import LLMClient

async def main():
    llm_client = LLMClient(None)
    client = llm_client.get_client()
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-global-poland",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await llm_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())