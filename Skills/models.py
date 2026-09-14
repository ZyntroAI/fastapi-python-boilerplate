from pydantic import BaseModel
from typing import List, Dict, Literal

SkillLevel = Literal[0, 1, 2, 3, 4, 5] # 0=none, 5=expert

class Skill(BaseModel):
    name: str
    level: SkillLevel

class Person(BaseModel):
    id: str
    name: str
    skills: List[Skill]
    years_experience: int = 0
    tags: List[str] = [] # "senior", "backend", "remote"

class Role(BaseModel):
    name: str
    required_skills: Dict[str, SkillLevel] # {"python": 4, "aws": 3}
    nice_to_have: Dict[str, SkillLevel] = {}

class TeamRequirement(BaseModel):
    role: Role
    team_size: int = 3
    must_have_tags: List[str] = []
