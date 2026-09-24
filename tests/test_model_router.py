import unittest
from model_router import ModelRouter, ModelTier

class TestModelRouter(unittest.TestCase):
    def setUp(self):
        self.router = ModelRouter()

    def test_summary_uses_cheap_model(self):
        tier = self.router.select_model("สรุปเนื้อหาเอกสารนี้")
        self.assertEqual(tier, ModelTier.CHEAP)

    def test_code_uses_premium_model(self):
        tier = self.router.select_model("เขียนโค้ด Python แก้ไขปัญหานี้")
        self.assertEqual(tier, ModelTier.PREMIUM)

    def test_general_uses_standard(self):
        tier = self.router.select_model("สวัสดี ช่วยอธิบายแนวคิดนี้")
        self.assertEqual(tier, ModelTier.STANDARD)

    def test_unknown_falls_back_to_standard(self):
        tier = self.router.select_model("")
        self.assertEqual(tier, ModelTier.STANDARD)

if __name__ == "__main__":
    unittest.main()
