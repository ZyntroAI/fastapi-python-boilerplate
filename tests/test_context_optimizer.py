import unittest
from context_optimizer import trim_conversation_history

class TestContextOptimizer(unittest.TestCase):
    def test_keeps_only_recent_messages(self):
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
            {"role": "user", "content": "Q3"},
        ]
        trimmed = trim_conversation_history(messages, max_recent=2)
        # system + 2 latest exchanges = 5 items
        self.assertEqual(len(trimmed), 5)

    def test_preserves_system_message(self):
        messages = [
            {"role": "system", "content": "Always here"},
            {"role": "user", "content": "Old"},
        ]
        trimmed = trim_conversation_history(messages, max_recent=1)
        system_roles = [m["role"] for m in trimmed]
        self.assertIn("system", system_roles)

    def test_short_history_unchanged(self):
        messages = [
            {"role": "system", "content": "S"},
            {"role": "user", "content": "Q"},
        ]
        trimmed = trim_conversation_history(messages, max_recent=5)
        self.assertEqual(len(trimmed), len(messages))

if __name__ == "__main__":
    unittest.main()
