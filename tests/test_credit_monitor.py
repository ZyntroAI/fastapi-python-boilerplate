import unittest
from unittest.mock import Mock, patch
from credit_monitor import CreditMonitor, AlertLevel

class TestCreditMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = CreditMonitor(
            alert_threshold=2000,
            safety_buffer=5000
        )

    def test_ok_when_sufficient_balance(self):
        with patch("credit_monitor.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"balance": 6000}
            level, msg = self.monitor.check_balance()
            self.assertEqual(level, AlertLevel.OK)

    def test_warning_when_below_threshold(self):
        with patch("credit_monitor.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"balance": 1500}
            level, msg = self.monitor.check_balance()
            self.assertEqual(level, AlertLevel.WARNING)

    def test_critical_when_zero(self):
        with patch("credit_monitor.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"balance": 0}
            level, msg = self.monitor.check_balance()
            self.assertEqual(level, AlertLevel.CRITICAL)

    def test_handles_api_failure_gracefully(self):
        with patch("credit_monitor.requests.get") as mock_get:
            mock_get.side_effect = Exception("API unreachable")
            level, msg = self.monitor.check_balance()
            self.assertEqual(level, AlertLevel.ERROR)

if __name__ == "__main__":
    unittest.main()
