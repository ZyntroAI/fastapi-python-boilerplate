from.models import Person, TeamRequirements
from.resolver import resolve

def find_best_team(candidates: list[Person], req: TeamRequirements):
    """Returns: (best_team, score, explanation)"""
    return resolve(candidates, req)

def score_pair(a: Person, b: Person) -> float:
    """Quick pairwise compatibility"""
    from.matrix import pairwise_score
    return pairwise_score(a, b)
