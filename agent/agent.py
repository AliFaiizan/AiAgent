from typing import AsyncGenerator
from agent.events import AgentEvent

class Agent:
    def __init__(self):
        pass

    async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        # This is where the agent's main loop would go, yielding StreamEvents as it processes information and makes decisions.
        yield AgentEvent.agent_start("Agent has started processing.")