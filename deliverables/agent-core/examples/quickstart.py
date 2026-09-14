"""Library-mode example: submit, poll, print the result.

Run with credentials in the environment::

    AGENT_API_KEY=... python examples/quickstart.py "summarise this repo"
"""
from __future__ import annotations

import asyncio
import sys

from agent_core import AgentClient, poll_task


async def main(prompt: str) -> None:
    async with AgentClient() as client:
        task_id = await client.submit({"prompt": prompt})
        print(f"submitted: {task_id}")

        task = await poll_task(task_id, client)
        print(f"status:    {task.status}")
        print(f"result:    {task.result}")


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "hello"))
