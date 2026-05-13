"""Smoke test: verifica que Claude Agent SDK conecta con la sesión local de Claude Max.

Uso:
    python scripts/check_llm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.llm.claude_agent_client import ClaudeAgentClient
from src.llm.client import LLMRequest


def main() -> int:
    print("[check_llm] Enviando prompt de prueba a Claude...")
    client = ClaudeAgentClient()
    response = client.complete(
        LLMRequest(
            prompt="Responde SOLO con la palabra: PONG",
            system="Eres un eco. Responde literalmente lo que se te pida.",
        )
    )
    text = response.text.strip()
    print(f"[check_llm] Respuesta: {text!r}")
    if "PONG" in text.upper():
        print("[check_llm] OK")
        return 0
    print("[check_llm] FALLO: respuesta inesperada", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
