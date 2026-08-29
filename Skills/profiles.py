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
