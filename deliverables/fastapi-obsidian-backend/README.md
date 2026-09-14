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
| Obsidian | `/obsidian` | bridge to the Obsidian Local REST API (vault read/search/write) |

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

## Obsidian Local REST API bridge

Connect a running Obsidian vault through the [Local REST API] plugin. The bridge
is **off until configured** — set `OBSIDIAN_API_URL` and the `/obsidian` routes
become live; leave it unset and they return `503` with a clear message.

```bash
# read-only (default)
OBSIDIAN_API_URL=http://127.0.0.1:27123 \
OBSIDIAN_API_KEY=<plugin-api-key> \
uvicorn app.main:app --reload

# enable writes (PUT/PATCH/DELETE, commands, open)
OBSIDIAN_API_URL=https://127.0.0.1:27124 \
OBSIDIAN_API_KEY=<plugin-api-key> \
OBSIDIAN_ALLOW_WRITE=1 \
OBSIDIAN_VERIFY_TLS=0 \
uvicorn app.main:app --reload
```

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/obsidian/status` | connected? writes enabled? |
| GET | `/obsidian/version` | authenticated call to the API root |
| GET | `/obsidian/vault?path=` | list vault root or a directory |
| GET | `/obsidian/note?filename=&meta=` | read a note (markdown, or parsed frontmatter/tags) |
| GET | `/obsidian/note/map?filename=` | heading tree + concurrency token |
| GET | `/obsidian/active` | the note open in Obsidian |
| GET | `/obsidian/tags` | tag counts |
| GET | `/obsidian/commands` | registered commands |
| POST | `/obsidian/search` | JsonLogic query over the vault |
| POST | `/obsidian/search/simple?query=` | plain full-text search |
| PUT | `/obsidian/note?filename=` | create / replace a note |
| POST | `/obsidian/note/append?filename=&target=` | append, optionally into a heading |
| PATCH | `/obsidian/note?filename=` | one structured markdown-patch instruction |
| DELETE | `/obsidian/note?filename=&permanent=` | trash (default) or delete |
| POST | `/obsidian/commands/{id}/execute` | run an Obsidian command |
| POST | `/obsidian/open?filename=` | open a note in the UI |

**Writes require both** a valid JWT (`Authorization: Bearer <token>`) **and**
`OBSIDIAN_ALLOW_WRITE=1`. Reads never mutate the vault.

### Security

- Vault-relative paths only: `..`, absolute paths, and NUL bytes are rejected
  with `422` before a request is built.
- Every JSON payload crossing the boundary — request bodies, JsonLogic queries,
  and vault responses — is passed through the **CWE-1321** sanitizer
  (`app/cwe1321_bridge.py`, mirrored from `deliverables/cwe1321-protection-suite/`),
  which strips `__proto__` / `prototype` / `constructor` at every depth.
- The API key is read from `OBSIDIAN_API_KEY` and never echoed in errors.

[Local REST API]: https://github.com/coddingtonbear/obsidian-local-rest-api

## Tests

```bash
pip install -r requirements.txt pytest
pytest tests/ -q      # 33 passed
```
