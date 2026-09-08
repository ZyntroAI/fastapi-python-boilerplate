from typing import List, Dict, Optional
from openai import OpenAI

class Summarizer:
    def __init__(self, prompt: str, model: str = "gpt-3.5-turbo"):
        self.prompt = prompt
        self.model = model
        self.client: Optional[OpenAI] = None

    def set_client(self, client: OpenAI):
        """Inject OpenAI client"""
        self.client = client

    def summarize(self, messages: List[Dict]) -> str:
        """Summarize history"""
        if not self.client:
            return self._fallback(messages)

        content = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in messages])
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.3
        )
        return resp.choices[0].message.content

    def _fallback(self, messages: List[Dict]) -> str:
        """Built-in if no LLM"""
        points = []
        for m in messages[:10]:
            r = m["role"]
            c = m["content"].replace("\n", " ")[:120]
            points.append(f"{r}: {c}...")
        return "\n".join(points)
