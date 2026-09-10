"""Program Management Backend.

A single integrated FastAPI application containing four equal modules:

1. Program Management CSV template generation (``pm_csv``)
2. Billing interoperability via a provider-neutral interface (``billing``)
3. A runtime tool switcher (``tool_switcher``)
4. Opt-in database encryption at rest (``db``), gated by ``ENCRYPT_AT_REST``
"""

__version__ = "1.0.0"
