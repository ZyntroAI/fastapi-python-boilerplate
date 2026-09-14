import uuid
import json
from pathlib import Path
from typing import Dict, Any

class MigrationPlanner:
    def __init__(self, config_path: str = "agent.yaml"):
        self.config = self._load_config(config_path)
        self.session_id = str(uuid.uuid4())
        self.plan: Dict[str, Any] = {
            "session_id": self.session_id,
            "phase": "plan",
            "status": "ready",
            "steps": [],
            "source": self.config["source"],
            "target": self.config["target"]
        }

    def _load_config(self, path: str) -> Dict[str, Any]:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def build_plan(self) -> Dict[str, Any]:
        """สร้างแผนลำดับขั้นตอนเต็มรูปแบบ"""
        self.plan["steps"] = [
            {"name": "validate", "run": True},
            {"name": "clone_mirror", "run": True, "temp_dir": f"tmp/{self.session_id}"},
            {"name": "lfs_analyze", "run": self.config.get("lfs_enabled", True)},
            {"name": "create_repo", "run": True},
            {"name": "push_mirror", "run": True},
            {"name": "configure_repo", "run": True},
            {"name": "verify", "run": True},
            {"name": "report", "run": True}
        ]
        return self.plan

    def save_plan(self, output_path: str = "plan.json") -> None:
        """บันทึกแผนตาม Schema"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.plan, f, indent=2, ensure_ascii=False)
        print(f"✅ แผนบันทึก: {output_path} | Session: {self.session_id}")

if __name__ == "__main__":
    planner = MigrationPlanner()
    plan = planner.build_plan()
    planner.save_plan()
