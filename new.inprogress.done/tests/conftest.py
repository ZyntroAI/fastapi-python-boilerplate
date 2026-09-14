"""ให้ tests import `tasks` ได้ โดยไม่ต้องติดตั้งเป็น package"""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
