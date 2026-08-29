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
