import os

class BytePlusClient:
def init(self):
self.access_key = os.environ["BYTEPLUS_ACCESS_KEY"]
self.secret_key = os.environ["BYTEPLUS_SECRET_KEY"]
self.region = os.getenv(
"BYTEPLUS_REGION",
"ap-southeast-1",
)

def get_region(self) -> str:
    return self.region
ไม่ควรใส่ business logic ในไฟล์นี้.

client.py
↓
credentials
region
SDK initialization
connection configuration

