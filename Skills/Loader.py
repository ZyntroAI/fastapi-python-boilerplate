import json
from.models import Person, Skill

def load_from_json(path):
    data = json.load(open(path))
    return [Person(
        id=p['id'],
        name=p['name'],
        skills=[Skill(**s) for s in p['skills']],
        tags=set(p.get('tags', []))
    ) for p in data['people']].
