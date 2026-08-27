from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class Skill:
    name: str
    level: int = 1 # 1-5

@dataclass
class Person:
    id: str
    name: str
    skills: List[Skill] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set) # "senior", "remote", etc

@dataclass
class TeamRequirements:
    must_have_skills: Dict[str, int] = field(default_factory=dict) # {"python": 3}
    team_size: int = 4
    constraints: Dict = field(default_factory=dict) # {"max_seniors": 2}
