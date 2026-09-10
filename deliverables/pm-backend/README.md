# Program Management Backend (pm_backend)

A single integrated FastAPI application with four equal modules:

| Module | Purpose | Route prefix |
|--------|---------|--------------|
| **Program Management CSV** | Generate / validate program-management CSV templates | `/api/csv` |
| **Billing interoperability** | Provider-neutral billing (stub, Stripe, Chargebee, Paddle) | `/api/billing` |
| **Tool switcher** | Switch the active tool at runtime | `/api/tool` |
| **Encryption at rest** | Opt-in Fernet column encryption | `/api/programs` |

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open the interactive docs at <http://127.0.0.1:8000/docs>.

Run the tests:

```bash
pytest -q        # 58 unit tests; 15 sandbox integration tests skip by default
```

### Integration tests (opt-in)

`tests/test_integration_*.py` exercise the real provider **sandbox** APIs
(Stripe test mode, Paddle sandbox, Chargebee test site). They are skipped
unless you opt in with `--run-integration` and supply credentials:

```bash
# Stripe test mode
export STRIPE_TEST_API_KEY=sk_test_xxxxxxxxxxxx
# Paddle sandbox
export PADDLE_SANDBOX_API_KEY=pdl_sdbx_xxxxxxxxxxxx
export PADDLE_SANDBOX_BASE_URL=https://sandbox-api.paddle.com
# Chargebee test site
export CHARGEBEE_TEST_API_KEY=cb_xxxxxxxxxxxx
export CHARGEBEE_TEST_SITE=your-site-test

pytest --run-integration -q
```

Safety guards in `conftest.py` refuse to run against production credentials —
a live Stripe key (`sk_live_*`), a non-sandbox Paddle host, or a Chargebee site
without a `-test` suffix will fail fast rather than touch a real account.
Guard behaviour is itself unit-tested in `tests/test_integration_guards.py`
(always runs, no network). Customers created by integration runs are deleted on
teardown.

---

## Configuration

All settings come from environment variables (an optional `.env` file in the
project root is also loaded). Defaults are shown.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./pm_backend.db` | SQLAlchemy database URL |
| `ENCRYPT_AT_REST` | `false` | Enable at-rest encryption of PII fields |
| `ENCRYPTION_KEY` | *(derived)* | Explicit Fernet key (see below) |
| `ENCRYPTION_SECRET` | `change-me` | Secret used to derive a key when `ENCRYPTION_KEY` unset |
| `BILLING_PROVIDER` | `stub` | `stub`, `stripe`, `chargebee`, or `paddle` |
| `BILLING_API_KEY` | *(empty)* | Provider API key (required for real providers) |
| `BILLING_BASE_URL` | *(empty)* | Override the provider API base (testing) |
| `ACTIVE_TOOL` | `pm_csv` | Initial tool for the tool switcher (`pm_csv`/`billing`/`settings`) |

---

## Modules

### 1. Program Management CSV

Canonical 12-column sheet:

```
program_id, name, owner, status, start_date, end_date,
budget, spent, risk, health, milestone, notes
```

- `GET /api/csv/template` — download a blank CSV template.
- `POST /api/csv/generate` — generate CSV from a JSON list of rows.
- `POST /api/csv/validate` — validate rows against the schema and report
  per-row errors (`status` and `health` are enumerated).

### 2. Billing interoperability

The app talks to a single **provider-neutral interface**
(`BillingProvider`): `create_customer`, `get_customer`, `create_invoice`,
`charge`, `health`. Only the adapter for the configured `BILLING_PROVIDER`
is loaded, so nothing else changes when you swap providers.

Provider failures surface through a small error hierarchy that the HTTP layer
maps to status codes:

| Error | HTTP |
|-------|------|
| `ProviderAuthError` | `401` — bad / missing key |
| `ProviderNotFoundError` | `404` — resource missing at the provider |
| `ProviderError` | `502` — upstream failure |

Endpoints:

- `GET /api/billing/provider` — provider name, status, mode.
- `POST /api/billing/customers` — create a customer.
- `POST /api/billing/invoices` — create + finalize an invoice for a customer.
- `POST /api/billing/charges` — create a PaymentIntent for a customer.

Amounts are in **minor units** (e.g. `2500` = $25.00).

#### Stripe

Set the provider and a Stripe API key:

```bash
export BILLING_PROVIDER=stripe
export BILLING_API_KEY=sk_test_xxxxxxxxxxxx   # or sk_live_...
uvicorn app.main:app --reload
```

- Test vs live mode is **auto-detected** from the key prefix and reported in
  `/health` and `/api/billing/provider`.
- The Stripe SDK is imported lazily and only required when this provider is
  selected; `stripe>=8.0` is declared in `requirements.txt`.
- The adapter creates a draft invoice, adds one line item, and finalizes it —
  mirroring a discrete charge in Stripe's data model.

No live key? The default `stub` provider runs offline with no network or
credentials and is a reference for writing other adapters. Add a new provider
by implementing `BillingProvider` and registering it in `build_provider()`.

#### Chargebee

```bash
export BILLING_PROVIDER=chargebee
export BILLING_API_KEY=cb_xxxxxxxxxxx
export BILLING_BASE_URL=https://<your-site>.chargebee.com/api/v2
uvicorn app.main:app --reload
```

Chargebee authenticates against your **site subdomain**; both the API key and
the full `https://<site>.chargebee.com/api/v2` base URL are required. Test vs
live mode is inferred from the site (`-test` suffix → `test`). The adapter
calls Chargebee's REST API over `requests` (lazy-imported) and sends amounts
in Chargebee's major units.

#### Paddle

```bash
export BILLING_PROVIDER=paddle
export BILLING_API_KEY=pdl_xxxxxxxxxxx
# optional — defaults to live; use the sandbox for testing:
export BILLING_BASE_URL=https://sandbox-api.paddle.com
uvicorn app.main:app --reload
```

Paddle Billing authenticates with a bearer token and sends amounts in **minor
units as strings** (`"2500"`). It is transaction-led: `create_invoice` creates
a manually-collected transaction (an invoice to send) and `charge` creates an
automatically-collected one (an immediate charge). Test vs live mode is
inferred from the base URL (`sandbox-api` → `test`). The adapter calls Paddle's
REST API over `requests` (lazy-imported).

### 3. Tool switcher

- `GET /api/tool` — current active tool + available tools.
- `POST /api/tool` `{"tool": "billing"}` — switch the active tool.

The selection is persisted to `tool_state.json` and survives restarts.

### 4. Encryption at rest (opt-in)

PII-bearing string columns (currently the program `note` field) are stored
**plain-text by default**. Enable transparent Fernet encryption without
changing application code:

```bash
export ENCRYPT_AT_REST=true
export ENCRYPTION_SECRET='a-long-random-secret'
```

When enabled, values are encrypted before they reach the database and
decrypted on read via a SQLAlchemy `TypeDecorator`. When disabled (default),
the `cryptography` package is never imported — no hard dependency.

Generate and pin an explicit key instead of deriving one:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
export ENCRYPTION_KEY='<that output>'
```

> **Rotating keys or changing the flag after data exists requires a
> migration** — rows written under one mode are not re-encrypted
> automatically. Back up before toggling on a live database.

`/health` reports `encrypt_at_rest: true|false` so clients can verify.

---

## Project layout

```
pm_backend/
├── app/
│   ├── main.py          # FastAPI app + all routers
│   ├── config.py        # env-driven settings
│   ├── db.py            # engine, session, opt-in EncryptedString
│   ├── billing.py       # provider-neutral interface + stub & Stripe adapters
│   ├── chargebee.py     # Chargebee billing adapter (same interface)
│   ├── paddle.py        # Paddle Billing adapter (same interface)
│   ├── pm_csv.py        # program-management CSV template logic
│   ├── tool_switcher.py # active-tool state
│   └── repository.py    # program record CRUD
├── tests/
│   ├── test_app.py                   # API + opt-in encryption subprocess check
│   ├── test_stripe_adapter.py        # Stripe adapter vs mocked SDK
│   ├── test_chargebee_adapter.py     # Chargebee adapter vs mocked HTTP
│   ├── test_paddle_adapter.py        # Paddle adapter vs mocked HTTP
│   ├── test_integration_guards.py    # live-credential safety guards (no network)
│   ├── test_integration_stripe.py    # real Stripe test-mode API (opt-in)
│   ├── test_integration_paddle.py    # real Paddle sandbox API (opt-in)
│   └── test_integration_chargebee.py # real Chargebee test site (opt-in)
├── conftest.py                       # sys.path + --run-integration harness
└── requirements.txt
```
