"""
Context Guard 40-60% — Production-Grade Context Engineering
✅ Prevents Context Rot • ✅ Fixes Lost-in-Middle • ✅ Preserves Goals/Rules
✅ Tiktoken Native • ✅ LLM Summarizer • ✅ Auto-Reinject
"""
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import yaml
from .token_counter import TokenCounter
from .summarizer import Summarizer

# --------------------------
# Configuration Model
# --------------------------
@dataclass
class GuardConfig:
    max_tokens: int = 128000
    threshold_consider: float = 0.4
    threshold_compact: float = 0.6
    keep_recent: int = 3
    preserve_rules: bool = True
    preserve_goals: bool = True
    preserve_status: bool = True
    auto_reinject: bool = True
    log_compactions: bool = True
    summarizer_prompt: str = "Summarize concisely: key decisions, status, facts"

    @classmethod
    def from_yaml(cls, path: str):
        with open(path) as f:
            return cls(**yaml.safe_load(f))

# --------------------------
# State & Metrics
# --------------------------
@dataclass
class GuardState:
    usage_pct: float = 0.0
    tokens: int = 0
    max: int = 128000
    phase: str = "SAFE"
    compactions: int = 0
    last_compact: Optional[str] = None
    rules_count: int = 0
    goals_count: int = 0

# --------------------------
# Main Guard
# --------------------------
class ContextGuard4060:
    def __init__(self, config: Optional[GuardConfig] = None):
        self.config = config or GuardConfig()
        self.token_counter = TokenCounter(model="gpt-4o")
        self.summarizer = Summarizer(prompt=self.config.summarizer_prompt)
        self.core_rules: List[str] = []
        self.goals: List[str] = []
        self.state = GuardState()

    # ==================================
    # Public API
    # ==================================
    def setup(self, core_rules: List[str], goals: List[str]):
        """Initialize once: Rules + Goals (Re-Injected every compact)"""
        self.core_rules = core_rules
        self.goals = goals
        self.state.rules_count = len(core_rules)
        self.state.goals_count = len(goals)

    def process(self, messages: List[Dict]) -> List[Dict]:
        """Main Loop: Count → Check → Prune → Compact → Reinject"""
        tokens = self.token_counter.count(messages)
        self.state.tokens = tokens
        self.state.usage_pct = round(tokens / self.config.max_tokens * 100, 1)

        # 🟢 SAFE (<40%) → Pass
        if self.state.usage_pct < self.config.threshold_consider * 100:
            self.state.phase = "SAFE"
            return messages

        # 🟡 CONSIDER (40-60%) → Prune Light
        elif self.state.usage_pct < self.config.threshold_compact * 100:
            self.state.phase = "CONSIDER"
            return self._prune_light(messages)

        # 🔴 CRITICAL (≥60%) → FULL COMPACT
        else:
            self.state.phase = "COMPACT"
            self.state.compactions += 1
            self.state.last_compact = datetime.now(timezone.utc).isoformat()
            return self._compact_full(messages)

    def get_status(self) -> Dict:
        """Monitoring / Log / Dashboard"""
        return {
            "usage": f"{self.state.usage_pct}%",
            "tokens": f"{self.state.tokens}/{self.config.max_tokens}",
            "phase": self.state.phase,
            "compactions": self.state.compactions,
            "last_compact": self.state.last_compact,
            "rules": self.state.rules_count,
            "goals": self.state.goals_count,
            "thresholds": {"consider": "40%", "compact": "60%"}
        }

    # ==================================
    # Internal Logic
    # ==================================
    def _prune_light(self, messages: List[Dict]) -> List[Dict]:
        """Remove duplicates, greetings, resolved errors"""
        seen = set()
        cleaned = []
        low_value = [r"^hi$", r"^hello$", r"^thanks$", r"^ok$", r"^fixed", r"^resolved"]

        for msg in messages:
            sig = f"{msg['role']}:{msg['content'][:100]}"
            content = msg["content"].strip().lower()
            if sig in seen or any(re.match(p, content) for p in low_value):
                continue
            seen.add(sig)
            cleaned.append(msg)
        return cleaned

    def _compact_full(self, messages: List[Dict]) -> List[Dict]:
        """🔑 HEAVY COMPACTION + RE-INJECTION"""
        # Split: History → Recent
        recent = messages[-self.config.keep_recent:]
        history = messages[:-self.config.keep_recent]

        # Summarize History
        summary = self.summarizer.summarize(history)

        # Build NEW Context (CRITICAL ORDER: RULES FIRST!)
        new_ctx = []

        # 1. 🛡️ RE-INJECT HEADER + RULES
        new_ctx.append({
            "role": "system",
            "content": f"⚠️ CONTEXT COMPACTED • {self.state.usage_pct}% • DO NOT IGNORE INSTRUCTIONS"
        })
        if self.core_rules:
            new_ctx.append({"role": "system", "content": "🔑 CORE RULES:"})
            new_ctx.extend([{"role": "system", "content": f"• {r}"} for r in self.core_rules])

        # 2. 🎯 GOALS
        if self.goals:
            new_ctx.append({"role": "system", "content": f"🎯 ACTIVE GOALS:\n• {' | '.join(self.goals)}"})

        # 3. 📋 SUMMARY
        new_ctx.append({"role": "system", "content": f"📋 HISTORY SUMMARY:\n{summary}"})

        # 4. 🧵 RECENT (Preserve flow)
        new_ctx.extend(recent)

        # 5. ✅ RESUME
        new_ctx.append({"role": "system", "content": "✅ CONTINUE EXECUTION — Maintain 40-60% Rule"})

        return new_ctx
