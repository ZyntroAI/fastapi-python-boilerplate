import requests
import json
from urllib.parse import quote

BASE_URL = "http://localhost:27123" 
API_KEY = "your_api_key_here" 

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def _request(method, endpoint, **kwargs):
    """wrapper จัดการ error + url encode path"""
    url = f"{BASE_URL}{endpoint}"
    try:
        res = requests.request(method, url, headers=headers, timeout=10, **kwargs)
        res.raise_for_status()
        return res.json() if res.content else {"status": "ok"}
    except requests.exceptions.RequestException as e:
        print(f"API Error [{method} {endpoint}]: {e}")
        if hasattr(e.response, 'text'):
            print("Response:", e.response.text)
        raise

def list_notes(folder=""):
    """ดึงรายชื่อโน้ตทั้งหมดใน folder"""
    params = {"folder": folder} if folder else {}
    return _request("GET", "/api/v1/notes", params=params)

def get_note(path):
    """ดึงเนื้อหา + frontmatter 1 โน้ต. ต้อง urlencode path"""
    path_encoded = quote(path)
    return _request("GET", f"/api/v1/notes/{path_encoded}")

def create_note(path, content, tags=None):
    """สร้างโน้ตใหม่. ถ้ามี folder จะ auto สร้างให้"""
    payload = {"content": content}
    if tags: payload["tags"] = tags
    path_encoded = quote(path)
    return _request("POST", f"/api/v1/notes/{path_encoded}", data=json.dumps(payload))

def update_note(path, content):
    """อัปเดตเนื้อหาทั้งหมด"""
    payload = {"content": content}
    path_encoded = quote(path)
    return _request("PUT", f"/api/v1/notes/{path_encoded}", data=json.dumps(payload))

def append_to_note(path, content):
    """เพิ่มข้อความต่อท้ายโน้ต - ใช้บ่อยมาก"""
    note = get_note(path)
    new_content = note['content'] + "\n" + content
    return update_note(path, new_content)

def search_notes(query):
    """ค้นหาโน้ตด้วย keyword"""
    return _request("GET", "/api/v1/search", params={"query": query})

def delete_note(path):
    """ลบโน้ต"""
    path_encoded = quote(path)
    return _request("DELETE", f"/api/v1/notes/{path_encoded}")

# --- ตัวอย่างการใช้งานจริง ---
if __name__ == "__main__":
    folder = "CrystalCastle"
    
    print("1. List Notes")
    notes
