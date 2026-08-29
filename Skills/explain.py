from.models import Person, Role

def explain_score(team: list[Person] | None, role: Role) -> str:
    if not team: return "No team"
    lines = [f"Team: {', '.join(p.name for p in team)}"]
    for skill, req in role.required_skills.items():
        levels = [s.level for p in team for s in p.skills if s.name == skill]
        best = max(levels) if levels else 0
        lines.append(f"- {skill}: need {req}, best has {best} → +{min(best, req)*10}")
    return "\n".join(lines)
