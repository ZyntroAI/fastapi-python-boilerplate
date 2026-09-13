import requests

# ส่งคำขอเพื่อสร้าง Access Token ชุดใหม่จาก Refresh Token เดิม
url = "https://example.com"
payload = {
    "grant_type": "refresh_token",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
}

response = requests.post(url, json=payload)
new_tokens = response.json()
print("New Access Token:", new_tokens.get("access_token"))
