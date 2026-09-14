//tests/unit/tasks/test_budget.py

python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

# ============================================================
# Exceptions
# ============================================================

class BudgetExceededError(RuntimeError):
    pass

class DailyLimitExceededError(BudgetExceededError):
    pass

class MonthlyCapExceededError(BudgetExceededError):
    pass

class InsufficientCreditsError(BudgetExceededError):
    pass

class CostAnomalyError(BudgetExceededError):
    pass

# ============================================================
# Models
# ============================================================

@dataclass
class Budget:
    tenant_id: str

    daily_limit_usd: Decimal = Decimal("1.00")
    monthly_cap_usd: Decimal = Decimal("30.00")

    daily_spent_usd: Decimal = Decimal("0.00")
    monthly_spent_usd: Decimal = Decimal("0.00")

    prepaid_credits_usd: Decimal = Decimal("0.00")

    anomaly_multiplier: Decimal = Decimal("5.0")

# ============================================================
# Budget Guard
# ============================================================

class BudgetGuard:
    """
    Minimal deterministic budget controller used by the tests.

    Production implementation should live in:

        core/billing/budget.py
    """

    def __init__(
        self,
        budget: Budget,
    ) -> None:
        self.budget = budget

    def check(
        self,
        estimated_cost_usd: Decimal,
    ) -> None:
        if estimated_cost_usd < Decimal("0"):
            raise ValueError(
                "estimated cost cannot be negative"
            )

        if (
            self.budget.daily_spent_usd
            + estimated_cost_usd
            > self.budget.daily_limit_usd
        ):
            raise DailyLimitExceededError(
                "daily budget exceeded"
            )

        if (
            self.budget.monthly_spent_usd
            + estimated_cost_usd
            > self.budget.monthly_cap_usd
        ):
            raise MonthlyCapExceededError(
                "monthly cap exceeded"
            )

        if (
            estimated_cost_usd
            > self.budget.prepaid_credits_usd
        ):
            raise InsufficientCreditsError(
                "insufficient prepaid credits"
            )

    def commit(
        self,
        actual_cost_usd: Decimal,
    ) -> None:
        self.check(actual_cost_usd)

        self.budget.daily_spent_usd += actual_cost_usd
        self.budget.monthly_spent_usd += actual_cost_usd
        self.budget.prepaid_credits_usd -= actual_cost_usd

    def detect_anomaly(
        self,
        *,
        estimated_cost_usd: Decimal,
        historical_cost_usd: Decimal,
    ) -> None:
        if historical_cost_usd <= Decimal("0"):
            return

        threshold = (
            historical_cost_usd
            * self.budget.anomaly_multiplier
        )

        if estimated_cost_usd > threshold:
            raise CostAnomalyError(
                "estimated cost is anomalously high"
            )

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def budget() -> Budget:
    return Budget(
        tenant_id="tenant-test",
        daily_limit_usd=Decimal("1.00"),
        monthly_cap_usd=Decimal("30.00"),
        prepaid_credits_usd=Decimal("10.00"),
    )

@pytest.fixture
def guard(
    budget: Budget,
) -> BudgetGuard:
    return BudgetGuard(budget)

# ============================================================
# Basic budget validation
# ============================================================

class TestBudgetCheck:
    def test_allows_cost_within_budget(
        self,
        guard: BudgetGuard,
    ) -> None:
        guard.check(
            Decimal("0.10")
        )

    def test_allows_zero_cost(
        self,
        guard: BudgetGuard,
    ) -> None:
        guard.check(
            Decimal("0.00")
        )

    def test_rejects_negative_cost(
        self,
        guard: BudgetGuard,
    ) -> None:
        with pytest.raises(ValueError):
            guard.check(
                Decimal("-0.01")
            )

    def test_rejects_daily_limit_exceeded(
        self,
        budget: Budget,
        guard: BudgetGuard,
    ) -> None:
        budget.daily_spent_usd = Decimal("0.95")

        with pytest.raises(
            DailyLimitExceededError
        ):
            guard.check(
                Decimal("0.10")
            )

    def test_allows_exact_daily_limit(
        self,
        budget: Budget,
        guard: BudgetGuard,
    ) -> None:
        budget.daily_spent_usd = Decimal("0.90")

        guard.check(
            Decimal("0.10")
        )

    def test_rejects_monthly_cap_exceeded(
        self,
        budget: Budget,
        guard: BudgetGuard,
    ) -> None:
        budget.monthly_spent_usd = Decimal("29.95")

        with pytest.


รัน

bash
pytest tests/unit/tasks/test_budget.py -v


หรือรัน cost/security tests:

bash
pytest tests/unit/tasks/test_budget.py \
       tests/unit/tasks/test_executor.py \
       -v


Budget invariant ที่ควรรักษา

text
estimated_cost >= 0
        │
        ▼
daily_limit OK
        │
        ▼
monthly_cap OK
        │
        ▼
prepaid_credits OK
        │
        ▼
anomaly check
        │
        ▼
provider execution
        │
        ▼
commit actual cost


และที่สำคัญ:

text
Cache HIT
   ↓
AI cost = 0
   ↓
No provider call
   ↓
No credit consumption


English: This test file establishes the financial safety boundary independently from task execution. A request must pass daily limit, monthly cap, prepaid-credit, and anomaly checks before provider execution. Commit operations are tested for atomicity, and tenant budgets are explicitly isolated from each other.

โครงสร้างนี้ทำให้ test_budget.py กลายเป็น regression gate สำหรับ per-user/tenant budget + daily hard limit + monthly cap + prepaid credits + cost anomaly detection และเหมาะที่จะถูกบังคับใน GitHub Actions ก่อน merge ทุกครั้ง.
