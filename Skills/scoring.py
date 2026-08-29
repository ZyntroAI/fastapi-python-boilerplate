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
