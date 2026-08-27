def explain_team(team, score_breakdown):
    lines = [f"Team Score: {score_breakdown['total']:.1f}"]
    for reason, val in score_breakdown['parts'].items():
        sign = "+" if val >= 0 else ""
        lines.append(f" {sign}{val:.1f} {reason}")
    return "\n".join(lines)
