# FastAPI + Obsidian Backend

Integrated FastAPI backend serving an **Obsidian skill library** as a REST API, with JWT auth, per-user skill access, and opt-in encryption at rest.

## Modules

| Module | Prefix | Purpose |
|---|---|---|
| Auth | `/auth` | register + login -> JWT |
| Skills | `/skills` | serve Obsidian skill library (per-user) |
| Programs | `/programs` | CSV generation |
| Billing | `/billing` | records + CSV export |
| Tools | `/tools` | module switcher |
| Security | `/security` | encryption-at-rest status |

## Setup & run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload    # from this directory
```

### JWT auth & per-user skill access

- `POST /auth/register {username,password}` and `POST /auth/login` return a JWT token.
- Send `Authorization: Bearer <token>` on `/skills*` (401 without).
- Add an `allowed_skills` list to a user record to restrict which skills they see (unrestricted if absent; out-of-list -> 403).

### Opt-in encryption at rest

```bash
ENCRYPT_AT_REST=1 uvicorn app.main:app
```

Fernet/AES-128; set `ENCRYPTION_KEY` or let it generate a key. Point at your vault with `SKILLS_DIR=/path/to/vault/Skills`.

## Sample skills

Three example Obsidian skill notes ship under `data/skills/` so `/skills` returns data out of the box.
