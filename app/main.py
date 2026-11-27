from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
app = FastAPI(title="FastAPI Python Boilerplate", version="1.0.0")

# ==========================================
# 🌐 CORS Configuration
# ==========================================

# 🔹 Allowed Origins — Update these with YOUR frontend URLs
ALLOWED_ORIGINS = [
    "http://localhost:3000",         # Local dev (React/Vue/etc.)
    "http://localhost:5173",         # Vite dev server
    "http://127.0.0.1:3000",
    "https://fastapi-python-boilerplate-kappa-brown.vercel.app",  # Vercel frontend
    "https://your-production-domain.com",  # Your production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,        # Explicit origins — safer than "*"
    allow_credentials=True,               # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],                  # Allow all common headers
    expose_headers=["Content-Disposition"],  # For file downloads
    max_age=86400,                        # Cache preflight request: 24 hours
)

# 👇 Your routes go below
# @app.get("/") ...
