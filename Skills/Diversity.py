def diversity_bonus(team):
    """Reward skill coverage + experience mix"""
    all_skills = set()
    senior_count = 0
    for p in team:
        all_skills.update(s.name for s in p.skills)
        if "senior" in p.tags:
            senior_count += 1

    skill_coverage = len(all_skills) * 2.0
    balance_penalty = abs(2 - senior_count) * -1.5 # aim for ~2 seniors
    return skill_coverage + balance_penalty
