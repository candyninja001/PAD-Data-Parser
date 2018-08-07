import json

card_file = open('cards.json')
cards = json.load(card_file)
card_file.close()

enemy_skill_file = open('enemy_skills.json')
enemy_skills = json.load(enemy_skill_file)
enemy_skill_file.close()

def card_es_search(f,**conditions):
    results = []
    p = lambda c: f(c[k] == v for k,v in conditions.items())
    for c_id,c_es in cards['enemies'].items():
        for skill in c_es['skills']:
            if p(skill):
                results.append(c_es)
                break
    results.sort(key=lambda x: x['id'])
    return results

def list_enemy_skill_params(skill):
    keys = {'param_0','param_1','param_2','param_3','param_4','param_5','param_6','param_7',
            'ratio','ai_param_0','ai_param_1','ai_param_2','ai_param_3','ai_param_4'}
    return {key:skill[key] for key in keys}

def enemy_skill_print(skill):
    nl = '\n'
    ex = '\n        '
    print(\
f"""{skill['id']:7d} {skill['text']}
            {skill['text_after']}
        cards: {', '.join(str(c['id']) for c in card_es_search(any,enemy_skill_id=skill['id'])) if len(card_es_search(any,enemy_skill_id=skill['id'])) > 0 else 'none'}
        type: {skill['type']}
         param_0: {str(skill['param_0']) if skill['param_0'] != 0 else '0 default'}
         param_1: {str(skill['param_1']) if skill['param_1'] != 0 else '0 default'}
         param_2: {str(skill['param_2']) if skill['param_2'] != 0 else '0 default'}
         param_3: {str(skill['param_3']) if skill['param_3'] != 0 else '0 default'}
         param_4: {str(skill['param_4']) if skill['param_4'] != 0 else '0 default'}
         param_5: {str(skill['param_5']) if skill['param_5'] != 0 else '0 default'}
         param_6: {str(skill['param_6']) if skill['param_6'] != 0 else '0 default'}
         param_7: {str(skill['param_7']) if skill['param_7'] != 0 else '0 default'}
         ratio: {str(skill['ratio']) if skill['ratio'] != 100 else '100 default'}
         ai_param_0: {str(skill['ai_param_0']) if skill['ai_param_0'] != 100 else '100 default'}
         ai_param_1: {str(skill['ai_param_1']) if skill['ai_param_1'] != 100 else '100 default'}
         ai_param_2: {str(skill['ai_param_2']) if skill['ai_param_2'] != 10000 else '10000 default'}
         ai_param_3: {str(skill['ai_param_3']) if skill['ai_param_3'] != 0 else '0 default'}
         ai_param_4: {str(skill['ai_param_4']) if skill['ai_param_4'] != 0 else '0 default'}
--------------------------""")

def enemy_skill_search(f,**conditions):
    results = []
    p = lambda s: f(s[k] == v if not k.startswith('arg_') else len(s['args']) > int(k[4:]) and s['args'][int(k[4:])] == v for k,v in conditions.items())# if k in s or k.startswith('arg_'))
    for s_id,e_s in enemy_skills['skills'].items():
        if p(e_s):
            results.append(e_s)
    results.sort(key=lambda s: s['id'])
    for result in results:
        enemy_skill_print(result)
    print(f'Summary: {len(results)} skills found')

def search_all(**con):
    enemy_skill_search(all, **con)
    
def search_any(**con):
    enemy_skill_search(any, **con)

def enemy_skill_search_predicate(p):
    results = []
    for s_id,e_s in enemy_skills['skills'].items():
        if p(e_s):
            results.append(e_s)
    results.sort(key=lambda s: s['id'])
    for result in results:
        enemy_skill_print(result)
    print(f'Summary: {len(results)} skills found')

def card_print(card):
    print(f'')
    
def card_search_predicate(p):
    results = []
    for c_id,e_s in cards['enemies'].items():
        if p(e_s):
            results.append(e_s)
    results.sort(key=lambda s: s['id'])
    for result in results:
        enemy_skill_print(result)
    print(f'Summary: {len(results)} skills found')



if __name__ == '__main__':
    #enemy_skill_search_predicate(lambda skill: skill['ratio'] != 100)
    #enemy_skill_search_predicate(lambda skill: skill['ai_param_1'] == 100)
    #enemy_skill_search_predicate(lambda skill: skill['id'] in {318,7599,7600})
    #enemy_skill_search_predicate(lambda skill: skill['type'] == 48 and skill['param_1'] < 0)
    enemy_skill_search_predicate(lambda skill: skill['id'] in {9237})
    enemy_skill_search_predicate(lambda skill: skill['type'] in {17})



