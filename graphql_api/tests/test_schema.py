"""GraphQL schema execution tests — login, me, users, permission (camelCase)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import create_access_token
from app.schema import schema


async def execute(q, context=None):
    return await schema.execute(q, context_value=context or {})


def decode(token):
    from app.auth import decode_token
    return decode_token(token)


async def test_login_mutation_returns_token():
    res = await execute('mutation { login(email:"a@b.c", password:"x") { accessToken user { role } } }')
    assert res.errors is None
    data = res.data["login"]
    assert data["accessToken"]
    assert data["user"]["role"] == "admin"


async def test_me_requires_auth():
    res = await execute("{ me { id } }")
    assert res.errors


async def test_me_with_token():
    token = create_access_token({"sub": "7", "role": "user", "email": "u@x.io"})
    res = await execute("{ me { id role email } }", context={"user": decode(token)})
    assert res.errors is None
    assert res.data["me"]["id"] == 7


async def test_users_pagination():
    token = create_access_token({"sub": "1", "role": "admin"})
    res = await execute("{ users(first:3) { edges { cursor } totalCount } }", context={"user": decode(token)})
    assert res.errors is None
    assert res.data["users"]["totalCount"] == 100
    assert len(res.data["users"]["edges"]) == 3


async def test_create_user_denied_for_non_admin():
    token = create_access_token({"sub": "2", "role": "user"})
    res = await execute('mutation { createUser(email:"x@y.z", name:"X", password:"p") { id } }',
                        context={"user": decode(token)})
    assert res.errors  # permission denied
