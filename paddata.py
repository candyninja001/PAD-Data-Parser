import json

CARD_PATH = 'reformatted/cards.json'
ENEMY_SKILL_PATH = 'reformatted/enemy_skills.json'

CARD_DATA = json.load(open(CARD_PATH))
ENEMY_SKILL_DATA = json.load(open(ENEMY_SKILL_PATH))

def get_curved_value(min_y, max_y, curve, max_x, x):
    return min_y + (max_y - min_y) * ((x - 1) / (max_x - 1)) ** curve

class Enemy:
    def __init__(self, monster_id, level):
        if str(monster_id) not in CARD_DATA['enemies']:
            raise ValueError('Invalid enemy monster id')
        if type(level) != int or level < 1 or level > 99:
            raise ValueError('Invalid enemy level')
        self._id = monster_id
        self._level = level

    def __getattr__(self, name):
        enemy_data = CARD_DATA['enemies'][str(self._id)]
        if name == 'hp':
            return get_curved_value(enemy_data['hp_at_lv_1'], enemy_data['hp_at_lv_10'], 1, 10, self._level)
        if name == 'defense':
            return get_curved_value(enemy_data['def_at_lv_1'], enemy_data['def_at_lv_10'], 1, 10, self._level)
        if name == 'atk' or name == 'attack':
            return get_curved_value(enemy_data['atk_at_lv_1'], enemy_data['atk_at_lv_10'], 1, 10, self._level)
        if name == 'coins':
            return enemy_data['coins_at_lv_2'] * self._level / 2
        if name == 'exp' or name == 'experience':
            return enemy_data['experience_at_lv_2'] * self._level / 2
        if name == 'default_turn_timer':
            return enemy_data['turn_timer']
        raise AttributeError
        
