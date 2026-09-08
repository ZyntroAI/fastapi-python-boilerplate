import tiktoken
from typing import List, Dict

class TokenCounter:
    def __init__(self, model: str = "gpt-4o"):
        self.enc = tiktoken.encoding_for_model(model)

    def count(self, messages: List[Dict]) -> int:
        """OpenAI-style message token count"""
        total = 0
        for msg in messages:
            total += 4  # Message overhead
            total += len(self.enc.encode(msg["content"]))
        total += 2  # Assistant reply overhead
        return total
