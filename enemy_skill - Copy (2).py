import json

card_path = 'reformatted/cards.json'
enemy_skill_path = 'reformatted/enemy_skills.json'
jp_enemy_skill_path = 'reformatted/JP/enemy_skills.json'

card_data = json.load(open(card_path))
enemy_skill_data = json.load(open(enemy_skill_path))
jp_enemy_skill_data = json.load(open(jp_enemy_skill_path))

cd = card_data
esd = enemy_skill_data
jesd = jp_enemy_skill_data

"""
==============================
1 result(s) for 4016
------------------------------
4016
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
-------------------------------
104016
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
      skillid arg1 arg2
       "text text text text"
       type
==============================
"""

"""
@preemptive
class medjedra():
    hp = 100
    flag = 0
    search_index = 1
    preemptive_level = 1

    def get_skill(this.):
        this.search_index = 1
        for 
"""

#              skill_type: meaning
ANNOTATED_SKILLS = {21: ">> Unused?",
                    22: ">> Set flag {ai} to True",
                    23: ">> If flag {ai} is True, jump to action {rnd}+1?",
                    24: ">> Set flag {ai} to False",
                    25: ">> Set counter to {ai}",
                    26: ">> Counter +1",
                    27: ">> Counter -1",
                    28: ">> If HP is below (or equal to?) {ai}%, jump to action {rnd}",
                    29: ">> If HP is above (or equal to?) {ai}%, jump to action {rnd}",
                    30: ">> If counter is less than (or equal to?) {ai}, jump to action {rnd}",
                    31: ">> If counter equals {ai}, jump to action {rnd}",
                    32: ">> If counter is above (or equal to?) {ai}, jump to action {rnd}",
                    33: ">> If level is less than (or equal to?) {ai}, jump to action {rnd}",
                    34: ">> If level equals {ai}, jump to action {rnd}",
                    35: ">> If level is above (or equal to?) {ai}, jump to action {rnd}",
                    36: ">> End of path <<",
                    37: ">> Display counter?",
                    38: ">> Set (flag?) {rnd} when counter equals {ai}?",
                    43: ">> If flag {ai} is True, jump to action {rnd}?",
                    44: ">> Flag OR {ai}",
                    45: ">> Flag XOR {ai}",
                    49: ">> Pre-emptive at level {param_0}+",
                    113:">> If player reached {ai}+ combos last turn, jump to action {rnd}",
                    120:">> When {ai} enemies remain, jump to action {rnd}"}

def get_control_skills():
    return {int(e_id):skill for e_id,skill in jp_enemy_skill_data['skills'].items() if skill['text'].startswith('\u203b')}

def print_ctrl():
    for skill in sorted(get_control_skills().values(), key= lambda skill: skill['type']):
        print(f"{skill['id']} ({skill['type']}) \n  {skill['text']}\n    {skill['text_after']}")

def t(skill_type):
    for i in sorted(s['id'] for s in enemy_skill_data['skills'].values() if s['type'] == skill_type):
        print(i)
        ii(i)
    
def ii(skill_id):
    if str(skill_id) in jp_enemy_skill_data['skills']:
        print(jp_enemy_skill_data['skills'][str(skill_id)]['text'])
    else:
        print('null')
    if str(skill_id) not in enemy_skill_data['skills']:
        print('null')
        return
    skill = enemy_skill_data['skills'][str(skill_id)]
    if skill['type'] in ANNOTATED_SKILLS:
        print( f"      {skill_id:< 8d} ({skill['type']:4d}) ---- ---- | {skill['ai_param_0']:4d} {skill['ai_param_1']:4d} {skill['ai_param_2']:7d} {skill['ai_param_3']:3d} {skill['ai_param_4']:4d} |\n{' | '.join(str(skill['param_'+str(i)]) for i in range(8))}\n\n         {ANNOTATED_SKILLS[skill['type']]}\n\n")
        return
    if skill['type'] == 83:
        result = f"      {skill_id:< 8d} ({skill['type']:4d}) ---- ----\n\n         multi: {repr(skill['text'])}\n"
        for subskill in (enemy_skill_data['skills'][str(skill['param_'+str(x)])] for x in range(8) if skill['param_'+str(x)] != 0):
            result += f"          {subskill['id']:< 8d} ({subskill['type']:4d}) | {subskill['ai_param_0']:4d} {subskill['ai_param_1']:4d} {subskill['ai_param_2']:7d} {subskill['ai_param_3']:3d} {subskill['ai_param_4']:4d} |\n{' | '.join(str(subskill['param_'+str(i)]) for i in range(8))}\n            {repr(subskill['text'])}\n"
        print( result + '\n' )
    else:
        print( f"      {skill_id:< 8d} ({skill['type']:4d}) ---- ---- | {skill['ai_param_0']:4d} {skill['ai_param_1']:4d} {skill['ai_param_2']:7d} {skill['ai_param_3']:3d} {skill['ai_param_4']:4d} |\n{' | '.join(str(skill['param_'+str(i)]) for i in range(8))}\n\n         {repr(skill['text'])}\n\n")


def skill_text(index,skill_id, ai, rnd):
    if str(skill_id) not in enemy_skill_data['skills']:
        return f"  {index:3d} {skill_id:< 8d} (ERRO) {ai:4d} {rnd:4d}\n\n"
    skill = enemy_skill_data['skills'][str(skill_id)]
    if skill['type'] in ANNOTATED_SKILLS:
        return f"  {index:3d} {skill_id:< 8d} ({skill['type']:4d}) {ai:4d} {rnd:4d} | {skill['ai_param_0']:4d} {skill['ai_param_1']:4d} {skill['ai_param_2']:7d} {skill['ai_param_3']:3d} {skill['ai_param_4']:4d} |\n{' | '.join(str(skill['param_'+str(i)]) for i in range(8))}\n\n         {ANNOTATED_SKILLS[skill['type']].format(ai=ai,rnd=rnd,**skill)}\n\n"
    if skill['type'] == 83:
        result = f"  {index:3d} {skill_id:< 8d} ({skill['type']:4d}) {ai:4d} {rnd:4d} | {skill['ai_param_0']:4d} {skill['ai_param_1']:4d} {skill['ai_param_2']:7d} {skill['ai_param_3']:3d} {skill['ai_param_4']:4d} |\n{' | '.join(str(skill['param_'+str(i)]) for i in range(8))}\n\n         multi: {repr(skill['text'])}\n"
        for subskill in (enemy_skill_data['skills'][str(skill['param_'+str(x)])] for x in range(8) if skill['param_'+str(x)] != 0):
            result += f"          {subskill['id']:< 8d} ({subskill['type']:4d}) | {subskill['ai_param_0']:4d} {subskill['ai_param_1']:4d} {subskill['ai_param_2']:7d} {subskill['ai_param_3']:3d} {subskill['ai_param_4']:4d} |\n{' | '.join(str(subskill['param_'+str(i)]) for i in range(8))}\n            {repr(subskill['text'])}\n"
        return result + '\n'
    else:
        note = ''
        if ai == 0:
            note = '         Passive:\n  '
        return f"  {index:3d} {skill_id:< 8d} ({skill['type']:4d}) {ai:4d} {rnd:4d} | {skill['ai_param_0']:4d} {skill['ai_param_1']:4d} {skill['ai_param_2']:7d} {skill['ai_param_3']:3d} {skill['ai_param_4']:4d} |\n{' | '.join(str(skill['param_'+str(i)]) for i in range(8))}\n\n{note}         {repr(skill['text'])}\n\n"

def lookup(monster):
    results = {}
    for i in {monster + (x * 10000) for x in range(10)}:
        if str(i) in card_data['enemies']:
            result = '' 
            for index,skill in enumerate(card_data['enemies'][str(i)]['skills'],1):
                result += skill_text(index, skill['enemy_skill_id'], skill['ai'], skill['rnd'])
            results[i] = result
    sep = '=============================='
    br = '------------------------------'
    nl = '\n'
    print( f"{sep}\n{len(results)} result(s) for {monster}\n{br}\n{br.join(str(i) + nl + t for i,t in results.items())}{sep}" )

def lookup_skill_type(skill_type):
    results = {}
    for i in sorted((monster['id'] for monster in card_data['enemies'].values() if \
                     any( (enemy_skill_data['skills'][str(skill['enemy_skill_id'])]['type'] == skill_type or \
                           (esd['skills'][str(skill['enemy_skill_id'])]['type'] == 83 and \
                            any(esd['skills'][str(esd['skills'][str(skill['enemy_skill_id'])]['param_'+str(p)])]['type'] == skill_type for p in range(8)))) \
                         for skill in monster['skills']))):
        if str(i) in card_data['enemies']:
            result = '' 
            for index,skill in enumerate(card_data['enemies'][str(i)]['skills'],1): 
                result += skill_text(index, skill['enemy_skill_id'], skill['ai'], skill['rnd'])
            results[i] = result
    sep = '=============================='
    br = '------------------------------\n'
    nl = '\n'
    print( f"{sep}\n{len(results)} result(s) for type {skill_type}\n{br}{br.join(str(i) + nl + t for i,t in results.items())}{sep}" )

def lookup_skill_id(skill_id):
    results = {}
    for i in sorted((monster['id'] for monster in card_data['enemies'].values() if \
                     any( (skill['enemy_skill_id'] == skill_id or \
                           (esd['skills'][str(skill['enemy_skill_id'])]['type'] == 83 and \
                            any(esd['skills'][str(skill['enemy_skill_id'])]['param_'+str(p)] == skill_id for p in range(8)))) \
                         for skill in monster['skills']))):
        if str(i) in card_data['enemies']:
            result = '' 
            for index,skill in enumerate(card_data['enemies'][str(i)]['skills'],1): 
                result += skill_text(index, skill['enemy_skill_id'], skill['ai'], skill['rnd'])
            results[i] = result
    sep = '=============================='
    br = '------------------------------\n'
    nl = '\n'
    print( f"{sep}\n{len(results)} result(s) for skill id {skill_id}\n{br}{br.join(str(i) + nl + t for i,t in results.items())}{sep}" )


# search for > "text": "\u203b

class n_ary_node():
    def __init__(self, skill=None, next_text=None, children=None):
        if children == None:
            self.children = list()
        else:
            self.children = [c for c in children]
            
        if next_text == None:
            self.next_text = str()
        else:
            self.next_text = next_text
            
        self.skill = skill
        


    

def n(monster):
    if str(monster) not in card_data['enemies']:
        return None
    moveset = {k:v for k,v in enumerate(card_data['enemies'][str(monster)]['skills'],1)}
    
    n_ary_node
    
l_t = lookup_skill_type

l_i = lookup_skill_id

l = lookup

p = lambda n,s: s if n > 1 else ''

ENEMY_SKILL_TRANSFORM = {0: ''}

ENEMY_SKILL_TEXT_TRANSFORM = {1: lambda skill: f"Bind {str(skill['param_0'])} card{p(skill['param_0'],'s')} for {str(skill['param_1'])}{'' if skill['param_2'] == skill['param_1'] else ' to '+str(skill['param_2'])} turn{p(max(skill['param_1'],skill['param_2']),'s')}"}

def textify(skill_id):
    if enemy_skill_data['skills'][str(skill_id)]['type'] in ENEMY_SKILL_TEXT_TRANSFORM:
        print(ENEMY_SKILL_TEXT_TRANSFORM[enemy_skill_data['skills'][str(skill_id)]['type']](enemy_skill_data['skills'][str(skill_id)]))




clear = lambda: print('\n'*25)



