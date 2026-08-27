from datetime import datetime

def to_html(team, score_breakdown, requirements):
    rows = ""
    for p in team:
        skills = ", ".join([f"{s.name} L{s.level}" for s in p.skills])
        tags = ", ".join(p.tags)
        rows += f"<tr><td>{p.name}</td><td>{skills}</td><td>{tags}</td></tr>"

    parts_html = ""
    for reason, val in score_breakdown['parts'].items():
        color = "green" if val >= 0 else "red"
        parts_html += f"<li><span style='color:{color}'>{val:+.1f}</span> {reason}</li>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Team Compatibility Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f7f7f7; }}
            .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
            .score {{ font-size: 32px; font-weight: bold; color: #2a7; }}
            .meta {{ color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Team Compatibility Report</h1>
            <p class="meta">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            
            <h2>Requirements</h2>
            <p>Team Size: {requirements.team_size}</p>
            <p>Must Have: {requirements.must_have_skills}</p>

            <h2>Score <span class="score">{score_breakdown['total']:.1f}</span></h2>
            <ul>{parts_html}</ul>

            <h2>Selected Team</h2>
            <table>
                <tr><th>Name</th><th>Skills</th><th>Tags</th></tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """
    return html

def save_html(path, team, score_breakdown, requirements):
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_html(team, score_breakdown, requirements))
