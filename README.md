## OAuth FastAPI (Vercel + Kubernetes)

### Endpoints
- GET /health
- GET /ready
- GET /api/auth/login
- GET /api/auth/callback

### Required env
- BASE_URL
- CLIENT_ID
- CLIENT_SECRET
- JWT_SECRET

### OAuth callback
OAUTH_CALLBACK_PATH ต้องตรงกับที่ตั้งใน OAuth Provider
ค่าเริ่มต้น: /api/auth/callback
