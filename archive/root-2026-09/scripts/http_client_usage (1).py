from app.core.http_client import http_client

@router.get("/external-data")
async def get_external_data():
    data = await fetch_external("https://api.example.com/data")
    return data
