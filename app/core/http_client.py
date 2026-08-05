# app/core/http_client.py
import httpx
from app.config import settings

http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(5.0),  # 5s total timeout
    limits=httpx.Limits(
        max_connections=100,     # Max open connections
        max_keepalive_connections=20,
        keepalive_expiry=30.0,   # Close idle connections after 30s
    ),
    follow_redirects=True,
    http2=True,                  # HTTP/2 for multiplexing
)

async def fetch_external(url: str):
    response = await http_client.get(url)
    response.raise_for_status()
    return response.json()
