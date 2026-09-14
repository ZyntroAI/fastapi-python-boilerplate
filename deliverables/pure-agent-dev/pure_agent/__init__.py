"""pure_agent — provider-agnostic agent skeleton for FastAPI.

The dependency direction this package enforces:

    api -> services -> agents -> providers.base (interface)
                                      ^
                                      |
                          providers.mock / providers.byteplus (adapters)

`pure_agent.agents` must never import a provider implementation. That rule is
checked by tests/test_architecture.py, not by convention alone.
"""

__version__ = "1.0.0"
