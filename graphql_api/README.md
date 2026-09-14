# GraphQL API (FastAPI + Strawberry)

Production-shaped FastAPI + Strawberry GraphQL API with async SQLAlchemy, JWT
auth, cursor pagination, subscriptions scaffold, health check, and Docker.

## Run (dev)
```bash
pip install -r requirements.txt
cp .env.example .env          # set SECRET_KEY
uvicorn app.main:app --reload
# Playground → http://localhost:8000/graphql  |  Health → /health
```

## Tests
```bash
pip install pytest pytest-asyncio
pytest tests/ -q        # 7 passed
```

## Layout
```
app/config.py      settings (SECRET_KEY from env)
app/auth.py        JWT create/decode (+ AuthError)
app/database.py    async SQLAlchemy engine/session
app/models.py      User ORM model
app/schema.py      Strawberry Query/Mutation/Subscription
app/main.py        FastAPI + GraphQLRouter(/graphql) + health
tests/             auth + schema execution tests
```

## Notes / gaps vs "production-ready"
- Resolvers use in-memory/demo data; wire to the ORM/CRUD layer + Redis cache
  for real use.
- `login` is a demo stub (any creds -> token); add passlib/bcrypt + real lookup.
- Subscription `user_created` is a template (Redis pub/sub not wired).
- Timezone-aware datetimes (UTC) used throughout.

## Database migrations (Alembic)

```bash
# Apply migrations (creates schema from alembic/versions)
cd graphql_api
alembic upgrade head

# After changing app/models.py, generate a new migration
alembic revision --autogenerate -m "describe change"

# Rollback one step
alembic downgrade -1
```

## DB-backed resolvers
- `login` verifies against the `users` table (bcrypt password hash).
- `me` / `users` query the DB through async SQLAlchemy sessions.
- `create_user` inserts a real row (admin-gated).
- Tests run against an in-memory SQLite DB (`tests/test_schema_db.py`).
