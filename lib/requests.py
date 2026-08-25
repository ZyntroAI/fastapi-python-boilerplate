import requests

def get_github_repo_license(owner, repo, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/license"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        license_info = data.get("license", {})
        print(f"License name: {license_info.get('name')}")
        print(f"License key: {license_info.get('key')}")
        print(f"License spdx_id: {license_info.get('spdx_id')}")
        print(f"License URL: {license_info.get('url')}")
        print(f"License node_id: {license_info.get('node_id')}")
    else:
        print(f"Failed to get license info. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# ตัวอย่างการใช้งาน
owner = "octocat"
repo = "Hello-World"
# ถ้ามี Personal Access Token ให้ใส่ลงไปในตัวแปรนี้
token = "YOUR_PERSONAL_ACCESS_TOKEN"

get_github_repo_license(owner, repo, token)
 

คำอธิบายโค้ด

ฟังก์ชัน  get_github_repo_license  รับพารามิเตอร์ชื่อเจ้าของ repository ( owner ), ชื่อ repository ( repo ), และ token (ถ้ามี)
สร้าง URL สำหรับเรียก API
กำหนด header เพื่อรับข้อมูลในรูปแบบ JSON ของ GitHub API
ถ้ามี token จะเพิ่ม header สำหรับการยืนยันตัวตน
ส่งคำขอ GET ไปยัง API
ถ้าสำเร็จ (status code 200) จะดึงข้อมูลใบอนุญาตและแสดงผลชื่อใบอนุญาตและข้อมูลที่เกี่ยวข้อง
ถ้าไม่สำเร็จจะแสดงสถานะและข้อความตอบกลับ

 

ถ้าต้องการให้ช่วยเขียนโค้ดสำหรับภาษาอื่น ๆ หรือเพิ่มฟีเจอร์อื่น ๆ แจ้งได้เลยครับ!
