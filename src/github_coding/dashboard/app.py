from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

app = FastAPI()

# 📋 โมเดลข้อมูลเหตุการณ์
class Incident(BaseModel):
    id: str
    title: str
    level: str  # CRITICAL/ERROR/WARNING/INFO
    status: str  # active/resolved/acknowledged
    time: str
    details: list[str]
    log_ref: str
    assignee: str | None

# 📂 โหลด/บันทึกข้อมูล (JSON/Log)
INCIDENT_FILE = Path("./.audit_logs/incidents.json")
if not INCIDENT_FILE.exists():
    INCIDENT_FILE.write_text(json.dumps([]))

def load_incidents() -> list[Incident]:
    return [Incident(**i) for i in json.loads(INCIDENT_FILE.read_text())]

def save_incidents(data: list[Incident]):
    INCIDENT_FILE.write_text(json.dumps([i.model_dump() for i in data], indent=2))

# 📊 หน้าหลักแดชบอร์ด
@app.get("/incidents", response_class=HTMLResponse)
async def incidents_dashboard(request: Request, filter: str = "all"):
    all_data = load_incidents()
    if filter != "all":
        all_data = [i for i in all_data if i.status == filter or i.level == filter]
    
    # สถิติรวม
    stats = {
        "total": len(all_data),
        "active": sum(1 for i in all_data if i.status == "active"),
        "critical": sum(1 for i in all_data if i.level == "CRITICAL"),
        "resolved": sum(1 for i in all_data if i.status == "resolved")
    }
    return templates.TemplateResponse("incidents.html", {
        "request": request, "incidents": all_data, "stats": stats, "filter": filter
    })

# 📝 รายละเอียด + อัปเดตสถานะ
@app.get("/incident/{incident_id}")
async def incident_detail(request: Request, incident_id: str):
    data = next((i for i in load_incidents() if i.id == incident_id), None)
    return templates.TemplateResponse("incident_detail.html", {"request": request, "inc": data})

@app.post("/incident/{incident_id}/update")
async def update_incident(incident_id: str, status: str = Query(""), assignee: str = Query("")):
    data = load_incidents()
    for i in data:
        if i.id == incident_id:
            if status: i.status = status
            if assignee: i.assignee = assignee
    save_incidents(data)
    return {"ok": True}
