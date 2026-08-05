from dataclasses import dataclass
from typing import Optional
import urllib.parse

@dataclass(frozen=True)
class OAuthEndpoints:
    authorization_endpoint: str
    token_endpoint: str

GOOGLE_ENDPOINTS = OAuthEndpoints(
    authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

def get_provider_endpoints(provider: str) -> OAuthEndpoints:
    if provider.lower() == "google":
        return GOOGLE_ENDPOINTS
    raise ValueError(f"Unsupported provider: {provider}")

def build_authorization_url(
    *,
    endpoints: OAuthEndpoints,
    client_id: str,
    redirect_uri: str,
    scope: str,
    code_challenge: str,
    state: str,
    nonce: Optional[str],
) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "access_type": "online",
        "prompt": "consent",
    }
    if nonce:
        params["nonce"] = nonce

    return endpoints.authorization_endpoint + "?" + urllib.parse.urlencode(params)
