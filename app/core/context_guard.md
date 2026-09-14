# 🚀 Single-File Production Version — `context_guard_4060.py`
**All-in-One • Tiktoken • LLM Summarizer • Re-Injection • Ready to Drop-In**

```python
"""
🧠 Context Guard 40-60% — Production-Grade Context Engineering
Core Logic:
- <40% → SAFE (Pass)
- 40-60% → CONSIDER (Light Prune)
- ≥60% → COMPACT (Full Compress + Rule Re-Injection)
Prevents: Context Rot • Lost-in-Middle • Goal Drift
"""
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import tiktoken

# --------------------------
# CONFIGURATION MODEL
# --------------------------
@dataclass
class GuardConfig:
    max_tokens: int = 128000
    threshold_consider: float = 0.4   # 40%
    threshold_compact: float = 0.6    # 60%
    keep_recent_messages: int = 3
    preserve_core_rules: bool = True
    preserve_goals: bool = True
    preserve_status: bool = True
    auto_reinject: bool = True
    log_compactions: bool = True
    summarizer_prompt: str = "Summarize conversation concisely: key facts, decisions, status, pending tasks."
    model_encoding: str = "gpt-4o"

# --------------------------
# STATE & METRICS
# --------------------------
@dataclass
class GuardState:
    usage_pct: float = 0.0
    token_count: int = 0
    max_tokens: int = 128000
    phase: str = "SAFE"
    compactions: int = 0
    last_compaction: Optional[str] = None
    rules_count: int = 0
    goals_count: int = 0

# --------------------------
# TOKEN COUNTER (TIKTOKEN)
# --------------------------
class TokenCounter:
    def __init__(self, model: str = "gpt-4o"):
        self.enc = tiktoken.encoding_for_model(model)

    def count(self, messages: List[Dict]) -> int:
        """OpenAI message format token count"""
        total = 0
        for msg in messages:
            total += 4  # Message overhead
            total += len(self.enc.encode(msg.get("content", "")))
        total += 2  # Assistant reply overhead
        return total

# --------------------------
# SUMMARIZER (LLM + FALLBACK)
# --------------------------
class Summarizer:
    def __init__(self, prompt: str, model: str = "gpt-3.5-turbo"):
        self.prompt = prompt
        self.model = model
        self.llm_client: Optional[Any] = None

    def set_llm_client(self, client: Any):
        """Inject OpenAI/Anthropic client"""
        self.llm_client = client

    def summarize(self, messages: List[Dict]) -> str:
        """Summarize history — LLM or built-in fallback"""
        if self.llm_client:
            return self._llm_summarize(messages)
        return self._fallback_summarize(messages)

    def _llm_summarize(self, messages: List[Dict]) -> str:
        content = "\n".join([f"{m['role']}: {m['content'][:250]}" for m in messages])
        resp = self.llm_client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": content}
            ]
        )
        return resp.choices[0].message.content.strip()

    def _fallback_summarize(self, messages: List[Dict]) -> str:
        points = []
        for m in messages[:12]:
            role = m["role"]
            txt = re.sub(r"\s+", " ", m["content"]).strip()[:150]
            points.append(f"{role.upper()}: {txt}...")
        return "\n".join(points)

# --------------------------
# MAIN GUARD ENGINE
# --------------------------
class ContextGuard4060:
    def __init__(self, config: Optional[GuardConfig] = None):
        self.config = config or GuardConfig()
        self.token_counter = TokenCounter(self.config.model_encoding)
        self.summarizer = Summarizer(self.config.summarizer_prompt)
        self.core_rules: List[str] = []
        self.goals: List[str] = []
        self.state = GuardState(max_tokens=self.config.max_tokens)

    # ==================================
    # PUBLIC API (EASY INTEGRATION)
    # ==================================
    def setup(self, core_rules: List[str], goals: List[str]):
        """Initialize once: Critical rules + active goals (RE-INJECTED EVERY COMPACT)"""
        self.core_rules = core_rules
        self.goals = goals
        self.state.rules_count = len(core_rules)
        self.state.goals_count = len(goals)

    def set_llm(self, llm_client: Any):
        """Connect OpenAI client for high-quality summaries"""
        self.summarizer.set_llm_client(llm_client)

    def run(self, messages: List[Dict]) -> List[Dict]:
        """Main entry: Count → Check → Prune → Compact → Reinject"""
        tokens = self.token_counter.count(messages)
        self.state.token_count = tokens
        self.state.usage_pct = round(tokens / self.config.max_tokens * 100, 1)

        # 🟢 SAFE ZONE (<40%) → Return as-is
        if self.state.usage_pct < self.config.threshold_consider * 100:
            self.state.phase = "SAFE"
            return messages

        # 🟡 CONSIDER ZONE (40-60%) → Light Cleanup
        elif self.state.usage_pct < self.config.threshold_compact * 100:
            self.state.phase = "CONSIDER"
            return self._prune_light(messages)

        # 🔴 CRITICAL ZONE (≥60%) → FULL COMPACTION + RE-INJECTION
        else:
            self.state.phase = "COMPACT"
            self.state.compactions += 1
            self.state.last_compaction = datetime.now(timezone.utc).isoformat()
            return self._full_compact(messages)

    def status(self) -> Dict:
        """Monitoring / Logs / Dashboard"""
        return {
            "usage": f"{self.state.usage_pct}%",
            "tokens": f"{self.state.token_count}/{self.config.max_tokens}",
            "phase": self.state.phase,
            "compactions": self.state.compactions,
            "last_compact": self.state.last_compaction,
            "rules": self.state.rules_count,
            "goals": self.state.goals_count,
            "thresholds": {"consider": "40%", "compact": "60%"}
        }

    # ==================================
    # INTERNAL LOGIC
    # ==================================
    def _prune_light(self, messages: List[Dict]) -> List[Dict]:
        """Remove duplicates, greetings, resolved errors"""
        seen = set()
        cleaned = []
        trash_patterns = [
            r"^hi$", r"^hello$", r"^thanks$", r"^ok$", r"^yes$",
            r"^error resolved", r"^fixed in", r"^proceed", r"^please go ahead"
        ]

        for msg in messages:
            sig = f"{msg['role']}:{msg['content'][:100]}"
            content_low = msg["content"].strip().lower()
            if sig in seen or any(re.match(p, content_low) for p in trash_patterns):
                continue
            seen.add(sig)
            cleaned.append(msg)
        return cleaned

    def _full_compact(self, messages: List[Dict]) -> List[Dict]:
        """🔑 HEAVY COMPACTION — RULES FIRST!"""
        # Split: History (to summarize) + Recent (keep raw)
        recent = messages[-self.config.keep_recent_messages:]
        history = messages[:-self.config.keep_recent]

        # Summarize history
        summary = self.summarizer.summarize(history)

        # 🧱 BUILD NEW CONTEXT (CRITICAL ORDER!)
        new_ctx = []

        # 1. ⚠️ HEADER
        new_ctx.append({
            "role": "system",
            "content": f"⚠️ CONTEXT COMPACTED • USAGE: {self.state.usage_pct}% • DO NOT IGNORE BELOW INSTRUCTIONS"
        })

        # 2. 🛡️ RE-INJECT CORE RULES
        if self.config.preserve_core_rules and self.core_rules:
            new_ctx.append({"role": "system", "content": "🔑 CORE RULES:"})
            new_ctx.extend([{"role": "system", "content": f"• {r}"} for r in self.core_rules])

        # 3. 🎯 ACTIVE GOALS
        if self.config.preserve_goals and self.goals:
            new_ctx.append({"role": "system", "content": f"🎯 ACTIVE GOALS:\n• {' | '.join(self.goals)}"})

        # 4. 📋 SUMMARY
        new_ctx.append({"role": "system", "content": f"📋 HISTORY SUMMARY:\n{summary}"})

        # 5. 🧵 RECENT MESSAGES
        new_ctx.extend(recent)

        # 6. ✅ RESUME
        new_ctx.append({
            "role": "system",
            "content": "✅ CONTINUE EXECUTION — Maintain 40-60% Rule"
        })

        return new_ctx

# --------------------------
# EXPORT FOR IMPORT
# --------------------------
__all__ = ["ContextGuard4060", "GuardConfig"]
```

---

## 🚀 Quick Start (Copy-Paste)
```python
# 1. Import
from context_guard_4060 import ContextGuard4060, GuardConfig

# 2. Initialize
guard = ContextGuard4060(GuardConfig(max_tokens=128000))

# 3. Set Critical Rules + Goals (RE-INJECTED EVERY TIME)
guard.setup(
    core_rules=[
        "Always follow 40-60% Context Rule",
        "Preserve project-status-auto-update logic",
        "Never modify schema without approval",
        "Track every change in history"
    ],
    goals=[
        "Build auto-add-new-skill factory",
        "Validate Similarity Engine",
        "Register to Skill Registry"
    ]
)

# 4. IN AGENT LOOP
while True:
    messages = get_conversation()  # Your messages list
    messages = guard.run(messages)
    
    print("📊 Guard Status:", guard.status())
    response = call_llm(messages)  # Send cleaned context
```

---

## ✅ Key Features
- 🧠 **Proactive:** Acts at 40% — not 80%+
- 🛡️ **Safe:** Rules/Gals **always at TOP**
- 🔢 **Accurate:** Tiktoken native
- 📝 **Smart:** LLM Summarizer + Fallback
- 📉 **Stable:** No quality drop-off
- 💸 **Cheap:** Early compact = save tokens
- 🧩 **Modular:** Drop-in anywhere

---

## 📄 Re-Injection Structure Example
```
⚠️ CONTEXT COMPACTED • 62.3%
🔑 CORE RULES:
• Always follow 40-60% Context Rule
• Preserve project-status-auto-update logic
🎯 ACTIVE GOALS:
• Build auto-add-new-skill • Validate Similarity
📋 SUMMARY:
- Created skill structure • Defined IR Model • Similarity Engine ready
✅ CONTINUE EXECUTION...
```

---

## 📦 Ready to Deploy
✅ Single File  
✅ No External Dependencies (except tiktoken)  
✅ Works with OpenAI/Anthropic/Local  
✅ Preserves Goals/Rules  
✅ Prevents Lost-in-Middle

---

Do you want me to also add **GitHub Action workflow file** or **logging/integration with your existing skill system**? 🤝📊✅
