import unittest
from response_cache import ResponseCache

class TestResponseCache(unittest.TestCase):
    def setUp(self):
        self.cache = ResponseCache()

    def test_miss_then_hit(self):
        prompt = "What is refund policy?"
        self.assertIsNone(self.cache.get(prompt, "haiku"))
        self.cache.set(prompt, "haiku", "Policy text")
        self.assertIsNotNone(self.cache.get(prompt, "haiku"))

    def test_different_prompts_different_keys(self):
        self.cache.set("A", "haiku", "Answer A")
        self.assertIsNone(self.cache.get("B", "haiku"))

    def test_different_models_different_entries(self):
        self.cache.set("Q", "haiku", "Haiku answer")
        self.assertIsNone(self.cache.get("Q", "opus"))

if __name__ == "__main__":
    unittest.main()
