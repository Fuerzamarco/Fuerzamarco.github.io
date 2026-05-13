from __future__ import annotations

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from .client import LLMClient, LLMRequest, LLMResponse


class ClaudeAgentClient(LLMClient):
    """Cliente que delega en Claude Agent SDK.

    Usa la sesión local de Claude Code (suscripción Max) — no consume API facturable.
    Requiere `claude` CLI instalado y autenticado.
    """

    def __init__(self, model: str | None = None) -> None:
        self._model = model

    def complete(self, request: LLMRequest) -> LLMResponse:
        return asyncio.run(self._complete_async(request))

    async def _complete_async(self, request: LLMRequest) -> LLMResponse:
        options = ClaudeAgentOptions(
            system_prompt=request.system,
            model=self._model,
            allowed_tools=[],
        )
        chunks: list[str] = []
        async for message in query(prompt=request.prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
        return LLMResponse(text="".join(chunks))
