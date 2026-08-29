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
