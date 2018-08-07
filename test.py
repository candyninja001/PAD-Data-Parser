import json

enemy_skills_data = json.load(open('reformatted/enemy_skills_new.json'))

for x in sorted({n['type'] for n in enemy_skills_data['skills'].values()}):
    print(x)
