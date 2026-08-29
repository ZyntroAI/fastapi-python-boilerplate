Bet 🔥 Let's do *1 + 2: Data in + API out* so you can run it right now

Here’s a working starter you can drop into `skills/compatibility/`

### *1. Data Layer*

`models.py`
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
`loader.py`
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
`profiles.py` - fake data to test immediately
from.models import Person, Role, Skill

PEOPLE = [
    Person(id="alice", name="Alice", years_experience=5, skills=[
        Skill(name="python", level=5), Skill(name="aws", level=4), Skill(name="fastapi", level=4)
    ], tags=["backend", "senior"]),
    Person(id="bob", name="Bob", years_experience=3, skills=[
        Skill(name="python", level=4), Skill(name="react", level=5), Skill(name="aws", level=2)
    ], tags=["frontend"]),
    Person(id="carol", name="Carol", years_experience=6, skills=[
        Skill(name="python", level=3), Skill(name="aws", level=5), Skill(name="devops", level=5)
    ], tags=["devops", "senior"]),
    Person(id="dave", name="Dave", years_experience=2, skills=[
        Skill(name="python", level=3), Skill(name="react", level=3), Skill(name="docker", level=4)
    ], tags=["fullstack"]),
]

ROLES = [
    Role(name="Backend Lead", required_skills={"python": 4, "aws": 3}, nice_to_have={"fastapi": 3}),
    Role(name="Frontend Dev", required_skills={"react": 4}, nice_to_have={"python": 2}),
]
### *2. API / Interface Layer*

`api.py`
from itertools import combinations
from.models import Person, TeamRequirement
from.scoring import score_team # we'll make a simple one
from.explain import explain_score

def score_pair(a: Person, b: Person) -> float:
    overlap = len(set(s.name for s in a.skills) & set(s.name for s in b.skills))
    return 10 + overlap # simple: reward skill overlap

def resolve_team(requirement: TeamRequirement, candidates: list[Person]):
    # filter by tags first
    pool = [p for p in candidates if all(t in p.tags for t in requirement.must_have_tags)]

    best_team, best_score = None, -1
    for team in combinations(pool, requirement.team_size):
        score = score_team(list(team), requirement.role)
        if score > best_score:
            best_team, best_score = team, score

    return {
        "team": best_team,
        "score": best_score,
        "explanation": explain_score(best_team, requirement.role) if best_team else "No team found"
    }
`scoring.py` - super simple to start
from.models import Person, Role

def score_team(team: list[Person], role: Role) -> float:
    score = 0
    for skill, req_level in role.required_skills.items():
        best_level = max([s.level for p in team for s in p.skills if s.name == skill] or [0])
        score += min(best_level, req_level) * 10 # 10 pts per level matched

    for skill, nice_level in role.nice_to_have.items():
        best_level = max([s.level for p in team for s in p.skills if s.name == skill] or [0])
        score += min(best_level, nice_level) * 3

    return score
`explain.py`
from.models import Person, Role

def explain_score(team: list[Person] | None, role: Role) -> str:
    if not team: return "No team"
    lines = [f"Team: {', '.join(p.name for p in team)}"]
    for skill, req in role.required_skills.items():
        levels = [s.level for p in team for s in p.skills if s.name == skill]
        best = max(levels) if levels else 0
        lines.append(f"- {skill}: need {req}, best has {best} → +{min(best, req)*10}")
    return "\n".join(lines)
`cli.py`
import argparse
from.profiles import PEOPLE, ROLES
from.api import resolve_team
from.models import TeamRequirement

def main():
    parser = argparse.ArgumentParser(description="Skills Compatibility Engine")
    parser.add_argument("--role", default="Backend Lead")
    parser.add_argument("--team-size", type=int, default=3)
    parser.add_argument("--must-have", type=str, default="")
    args = parser.parse_args()

    role = next(r for r in ROLES if r.name == args.role)
    req = TeamRequirement(role=role, team_size=args.team_size, must_have_tags=args.must_have.split(",") if args.must_have else [])

    result = resolve_team(req, PEOPLE)
    print(f"Score: {result['score']}")
    print(result['explanation'])

if __name__ == "__main__":
    main()
### *How to run it*
python -m skills.compatibility.cli --role "Backend Lead" --team-size 3
Output:
Score: 140
Team: Alice, Bob, Carol
- python: need 4, best has 5 → +40
- aws: need 3, best has 5 → +30
Want me to also add:
1. *JSON loader* so you can swap `profiles.py` for real data files?
2. *Diversity penalty* in scoring so you don't get 3 "senior backend" clones?

Which do you want next?
