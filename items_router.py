from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

# ตัวอย่างข้อมูลจำลอง
items_db = [
    {"id": 1, "name": "Laptop", "price": 35000},
    {"id": 2, "name": "Smartphone", "price": 15000},
    {"id": 3, "name": "Headphones", "price": 2000},
]

@router.get("/items", response