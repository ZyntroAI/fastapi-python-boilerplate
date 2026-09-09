"""CLI ตัวอย่าง — สร้าง task แล้ว poll ผล (ต้องตั้ง MANUS_API_KEY หรือ MANUS_BEARER_TOKEN)

ใช้งาน:
    export MANUS_API_KEY=manus_...
    python -m manus_client.cli "ไปที่ https://example.com แล้วดึงข้อมูลสินค้า" --format json
"""
from __future__ import annotations

import argparse
import asyncio
import os

from manus_client.client import ManusClient, ManusAPIError


async def main(prompt: str, fmt: str, interval: float, max_wait: float) -> None:
    key = os.getenv("MANUS_API_KEY", "")
    bearer = os.getenv("MANUS_BEARER_TOKEN", "")
    client = ManusClient(api_key=key, bearer_token=bearer)
    try:
        result = await client.run_task(
            prompt,
            options={"response_format": fmt},
            interval=interval,
            max_wait=max_wait,
        )
        print("=== Task เรียบร้อย ===")
        print(result)
    except ManusAPIError as exc:
        print(f"[error:{exc.code}] {exc} (request_id={exc.request_id})")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manus v2 task runner")
    parser.add_argument("prompt", help="งานเป็นภาษา natural language")
    parser.add_argument("--format", default="json", choices=["json", "markdown", "text"])
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--max-wait", type=float, default=600.0)
    args = parser.parse_args()
    asyncio.run(main(args.prompt, args.format, args.interval, args.max_wait))
