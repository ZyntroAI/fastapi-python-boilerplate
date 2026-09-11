# WhatsApp CI/CD Notifications

Send CI/CD alerts to WhatsApp using the Meta Graph API (WhatsApp Cloud API).
Adapted for this repo: Python helper + a ready-to-enable GitHub Actions workflow.

## Files
- `scripts/whatsapp_notify.py` — client (`WhatsAppClient`), connection check, send.
- `tests/test_whatsapp_notify.py` — 9 tests (mocked HTTP; no real calls).
- `templates/workflows/notify-whatsapp.yml` — workflow **template** (see below).

## Configure (repo secrets)
Settings → Secrets and variables → Actions, add:

| Secret | Meaning |
|---|---|
| `WHATSAPP_TOKEN` | Bearer token with `whatsapp_business_messaging` |
| `WHATSAPP_PHONE_ID` | sender phone-number id — **digits only** |
| `ADMIN_PHONE` | recipient, international format, no `+` (e.g. `66812345678`) |

Optional: `WHATSAPP_API_VER` (default `v18.0`).

## Use
```bash
export WHATSAPP_TOKEN=...  WHATSAPP_PHONE_ID=...  ADMIN_PHONE=66812345678
python scripts/whatsapp_notify.py     # checks connection, then sends a test
```

```python
from scripts.whatsapp_notify import WhatsAppClient

client = WhatsAppClient()
ok, info = client.test_connection()   # (True, {...})
client.send_message("66812345678", "CI failed on main")
```

## Endpoint shape (the usual mistake)
- Correct: `POST https://graph.facebook.com/v18.0/<PHONE_ID>/messages`
- `GET` on that URL sends nothing — messaging is always `POST`.
- `GET https://graph.facebook.com/v18.0/` (no phone id) returns
  `code 100 / error_subcode 33 — Unsupported get request`.

`test_connection()` GETs the phone-number node, which is the right way to
validate token + phone id before sending.

## Common errors
| Code | Meaning | Fix |
|---|---|---|
| 100 / 33 | Unsupported get request | use the full `<PHONE_ID>/messages` URL, `POST` to send |
| 131008 | number not allowed | add recipient to the test recipients list |
| 132000 | template/policy mismatch | use an approved template or get consent |
| 401 | token expired/wrong | regenerate the token |

## Rule of thumb
- Never put tokens in code or logs — env/secrets only.
- Throttle: ≤1–2 messages/minute per recipient.
- Consent first; treat notifications as opt-in.

## Enabling the workflow
`templates/workflows/notify-whatsapp.yml` is a **template**, kept outside
`.github/workflows/` because the automation identity lacks the GitHub App
`workflows` permission. To enable it, a repo admin copies it to
`.github/workflows/notify-whatsapp.yml` (or grants the App **Workflows: Read and write**).
