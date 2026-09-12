from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from deep_translator import GoogleTranslator, DeepLTranslator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, List
import os

# ─── Configuration ───
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("TRANSLATOR_API_KEY", "change_this_secure_key_in_env")
deepl_default_key = os.getenv("DEEPL_API_KEY")

# ─── Limiter ───
limiter = Limiter(key_func=get_remote_address)

# ─── App Metadata ───
app = FastAPI(
    title="Translator API",
    description="""
A production-ready REST API for text translation between languages.

**Features:**
- 🌍 Google Translate & DeepL support
- 🔍 Auto language detection
- 📦 Batch translation endpoint
- 🔑 API Key authentication
- ⏱️ Rate limiting protection
- 📖 Interactive OpenAPI documentation
    """,
    version="2.0.0",
    contact={"name": "ZyntroAI Team"},
    license_info={"name": "MIT"}
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Authentication ───
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key

# ─── Schemas ───
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field(default="auto", description="Source language code, or 'auto' to detect")
    target_lang: str = Field(..., description="Target language code")
    provider: str = Field(default="google", description="google or deepl")
    deepl_api_key: Optional[str] = Field(None, description="DeepL API key; falls back to env default")

class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to translate")
    source_lang: str = Field(default="auto")
    target_lang: str = Field(..., description="Target language code")
    provider: str = Field(default="google")
    deepl_api_key: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    detected_source: Optional[str]
    provider: str

class BatchTranslationResponse(BaseModel):
    results: List[str]
    detected_source: Optional[str]
    provider: str

# ─── Helper ───
def do_translate(text: str, source_lang: str, target_lang: str, provider: str, deepl_key: Optional[str]):
    if provider.lower() == "google":
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text), translator.source if source_lang != "auto" else None
    elif provider.lower() == "deepl":
        key = deepl_key or deepl_default_key
        if not key:
            raise HTTPException(401, "DeepL API key required (header or environment)")
        src = source_lang.upper() if source_lang != "auto" else None
        translator = DeepLTranslator(api_key=key, source=src, target=target_lang.upper())
        return translator.translate(text), None
    else:
        raise HTTPException(400, "Supported providers: google, deepl")

# ─── Endpoints ───
@app.post("/translate", response_model=TranslationResponse, summary="Translate single text")
@limiter.limit("100/minute")
async def translate(
    request: Request,
    req: TranslationRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        translated, detected = do_translate(req.text, req.source_lang, req.target_lang, req.provider, req.deepl_api_key)
        return TranslationResponse(translated_text=translated, detected_source=detected, provider=req.provider)
    except Exception as e:
        raise HTTPException(500, detail=f"Translation error: {str(e)}")


@app.post("/translate/batch", response_model=BatchTranslationResponse, summary="Batch translate multiple texts")
@limiter.limit("30/minute")
async def translate_batch(
    request: Request,
    req: BatchTranslationRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        results: List[str] = []
        detected_src = None
        for txt in req.texts:
            out, detected = do_translate(txt, req.source_lang, req.target_lang, req.provider, req.deepl_api_key)
            results.append(out)
            if detected:
                detected_src = detected
        return BatchTranslationResponse(results=results, detected_source=detected_src, provider=req.provider)
    except Exception as e:
        raise HTTPException(500, detail=f"Batch translation error: {str(e)}")


@app.get("/languages/{provider}", summary="List supported languages")
@limiter.limit("200/minute")
async def list_languages(
    request: Request,
    provider: str,
    api_key: str = Depends(verify_api_key)
):
    if provider.lower() == "google":
        return {"provider": provider, "languages": GoogleTranslator.get_supported_languages(as_dict=True)}
    raise HTTPException(400, f"Language list not available for: {provider}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
