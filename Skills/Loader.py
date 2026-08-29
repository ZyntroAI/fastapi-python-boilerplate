import json
from pathlib import Path
from.models import Person, Role

def load_json(path: str):
    return json.loads(Path(path).read_text())

def load_people(path: str) -> list[Person]:
    data = load_json(path)
    return [Person(**p) for p in data]

def load_roles(path: str) -> list[Role]:
    data = load_json(path)
    return [Role(**r) for r in data]
