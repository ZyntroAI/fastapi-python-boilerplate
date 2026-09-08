import httpx
from typing import List, Dict

async def rerun_failed_job(run_id: str, job_id: str, token: str) -> Dict:
    """Rerun ONLY specific failed job — NOT full workflow"""
    url = f"https://api.github.com/repos/ZyntroAI/fastapi-python-boilerplate/actions/jobs/{job_id}/rerun"
    async with httpx.AsyncClient() as c:
        resp = await c.post(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        })
        resp.raise_for_status()
        return {"status": "rerun_started", "job_id": job_id, "run_id": run_id}


async def check_permission(token: str) -> bool:
    """Verify actions:write — DO NOT require workflows:write"""
    url = "https://api.github.com/repos/ZyntroAI/fastapi-python-boilerplate/actions/permissions"
    async with httpx.AsyncClient() as c:
        resp = await c.get(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        })
        data = resp.json()
        return data.get("actions") in ["write", "admin"]
