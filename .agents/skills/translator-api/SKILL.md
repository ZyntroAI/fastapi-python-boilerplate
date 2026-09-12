# Translator API — Overview & Implementation
A **Translator API** enables programmatic text translation between languages, typically via REST/HTTP endpoints, JSON request/response, and standard authentication. Below is a complete practical guide, including common providers, a minimal self-hosted FastAPI version, and usage examples.

---

## 📋 Popular Translator API Providers
| Provider | Free Tier | Key Features | Docs |
|---|---|---|---|
| **Google Cloud Translation API** | Yes (limited chars/month) | 130+ langs, auto-detect, glossary | cloud.google.com/translate |
| **DeepL API** | Yes (500k chars/month) | High-quality, context-aware, formal/informal | deepl.com/pro-api |
| **Microsoft Translator (Azure)** | Yes (2M chars/month) | 100+ langs, batch, dictionary | azure.com/ai-services/translator |
| **LibreTranslate** | Free/self-hosted | Open-source, no API key needed (self-host) | libretranslate.com |

---

## 🛠️ Build Your Own Minimal Translator API (FastAPI)
Uses `deep-translator` library (wraps multiple backends: Google, DeepL, etc.).

### 1. Install Dependencies
```bash
pip install fastapi uvicorn deep-translator pydantic
```

### 2. API Code (`translator_api.py`)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deep_translator import GoogleTranslator, DeepLTranslator
from typing import Optional

app = FastAPI(title="Translator API", version="1.0.0")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"   # e.g. "en", "th", "zh-CN"
    target_lang: str
    provider: str = "google"    # "google" or "deepl"
    deepl_api_key: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    detected_source: Optional[str]
    provider: str

@app.post("/translate", response_model=TranslationResponse)
async def translate(req: TranslationRequest):
    try:
        if req.provider.lower() == "google":
            translator = GoogleTranslator(source=req.source_lang, target=req.target_lang)
            result = translator.translate(req.text)
            detected = translator.source if req.source_lang != "auto" else None

        elif req.provider.lower() == "deepl":
            if not req.deepl_api_key:
                raise HTTPException(401, "DeepL API key required")
            translator = DeepLTranslator(
                api_key=req.deepl_api_key,
                source=req.source_lang.upper() if req.source_lang != "auto" else None,
                target=req.target_lang.upper()
            )
            result = translator.translate(req.text)
            detected = None

        else:
            raise HTTPException(400, "Supported providers: google, deepl")

        return TranslationResponse(
            translated_text=result,
            detected_source=detected,
            provider=req.provider
        )

    except Exception as e:
        raise HTTPException(500, detail=f"Translation error: {str(e)}")

@app.get("/languages/{provider}")
async def list_languages(provider: str):
    """Return supported language codes"""
    if provider.lower() == "google":
        return {"languages": GoogleTranslator.get_supported_languages(as_dict=True)}
    raise HTTPException(400, f"Language list not available for {provider}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Run & Test
```bash
uvicorn translator_api:app --reload
# Docs at: http://127.0.0.1:8000/docs
```

**Example Request (curl):**
```bash
curl -X POST "http://127.0.0.1:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, welcome!",
    "source_lang": "en",
    "target_lang": "th",
    "provider": "google"
  }'
```

**Response:**
```json
{
  "translated_text": "สวัสดี ยินดีต้อนรับ!",
  "detected_source": "en",
  "provider": "google"
}
```

---

## 🔑 Key Implementation Notes
- **Language Codes**: Use standard codes (`en`, `th`, `zh-CN`, `ja`, `ko`...) — `/languages` endpoint returns full list.
- **Authentication**: For production, add API key middleware, rate limiting, and environment-based secrets.
- **Error Handling**: Implement retries, timeouts, and input length limits.
- **Batch Support**: Extend the schema to accept `text: list[str]` for bulk translation.
- **Self-Hosted Option**: Deploy LibreTranslate locally for full privacy without third-party calls.

---

Would you like me to **add authentication, rate limiting, and multi-language batch endpoints** to this API? Or integrate it with a specific provider (DeepL/Google/Azure) with full production-ready config? Tap **"Fast"** below and select **"Pro"** to generate the complete enhanced version.
