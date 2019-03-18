_INFO = """

Created by CandyNinja

This script reformats the raw json files from pad to a more usable
and readable format. The script accepts a dict with a str key for the 
mode and the tuple value storing the str of the input and output file
locations, modes and examples below. There is an optional parameter
for pretty printing the json instead of minimizing the file.

While writing this script, I have found numerous mistakes. If there
are any misspelled, poorly named, inaccurate or incorrect values or
information, please inform me and I will correct them ASAP.

Supported Modes:
'skill' for card skills (active and leader)
'dungeon' for dungeon data (list of dungeons and floors, not data within them)
'card' for card data (awakenings, stats, types, etc.)
'enemy_skill' for dungeon encounter skills

------------------------------------

Using this script with python

Import this script and call the 'parse' function.

Examples:

padparse.parse({'skill': ('download_skill_data.json','parsed/skills.json'),
                'card':  ('download_card_data.json', 'parsed/cards.json' )},
               pretty=True)
                       
padparse.parse({'dungeon': ('download_dungeon_data.json','parsed/dungeons.json')})

------------------------------------

Using this script in command line

Call the script with three arguments, the mode, input file path, and output file path

The option to pretty print can be enabled with '-p' before the mode

Examples:

padparse.py -p skill "download_skill_data.json" "parsed/skills.json"

padparse.py dungeon "download_dungeon_data.json" "parsed/dungeons.json"

"""

ATTRIBUTES = {0: 'Fire',
              1: 'Water',
              2: 'Wood',
              3: 'Light',
              4: 'Dark',
              5: 'Heart',
              6: 'Jammer',
              7: 'Poison',
              8: 'Mortal Poison',
              9: 'Bomb'}

TYPES = {0: 'Evo Material',
         1: 'Balanced',
         2: 'Physical',
         3: 'Healer',
         4: 'Dragon',
         5: 'God',
         6: 'Attacker',
         7: 'Devil',
         8: 'Machine',
         12:'Awaken Material',
         14:'Enhance Material',
         15:'Redeemable Material'}

AWAKENINGS = {1: 'Enhanced HP',
              2: 'Enhanced Attack',
              3: 'Enhanced Heal',
              4: 'Reduce Fire Damage',
              5: 'Reduce Water Damage',
              6: 'Reduce Wood Damage',
              7: 'Reduce Light Damage',
              8: 'Reduce Dark Damage',
              9: 'Auto-Recover',
              10:'Resistance-Bind',
              11:'Resistance-Dark',
              12:'Resistance-Jammers',
              13:'Resistance-Poison',
              14:'Enhanced Fire Orbs',
              15:'Enhanced Water Orbs',
              16:'Enhanced Wood Orbs',
              17:'Enhanced Light Orbs',
              18:'Enhanced Dark Orbs',
              19:'Extend Time',
              20:'Recover Bind',
              21:'Skill Boost',
              22:'Enhanced Fire Att.',
              23:'Enhanced Water Att.',
              24:'Enhanced Wood Att.',
              25:'Enhanced Light Att.',
              26:'Enhanced Dark Att.',
              27:'Two-Pronged Attack',
              28:'Resistance-Skill Bind',
              29:'Enhanced Heal',
              30:'Multi Boost',
              31:'Dragon Killer',
              32:'God Killer',
              33:'Devil Killer',
              34:'Machine Killer',
              35:'Balanced Killer',
              36:'Attacker Killer',
              37:'Physical Killer',
              38:'Healer Killer',
              39:'Awaken Killer',
              40:'Enhance Killer',
              41:'Redeemable Killer',
              42:'Evo Killer',
              43:'Enhanced Combos',
              44:'Guard Break',
              45:'Bonus Attack',
              46:'Enhanced Team HP',
              47:'Enhanced Team RCV',
              48:'Void Damage Piercer',
              49:'Awoken Assist',
              50:'Super Bonus Attack',
              51:'Skill Charge',
              52:'Resistance-Bind+',
              53:'Extended Move Time+',
              54:'Resistance-Clouds',
              55:'Resistance-Immobility',
              56:'Skill Boost+',
              57:'80% or more HP Enhanced',
              58:'50% or less HP Enhanced',
              59:'[L] Damage Reduction',
              60:'[L] Increased Attack',
              61:'Super Enhanced Combos',
              62:'Combo Orbs',
              63:'Skill Voice',
              64:'Dungeon Bonus',}

_DEV = False

import json
from collections import defaultdict

# Converts the /almost/ csv text from the dungeon and enemy_skill jsons to a list of lists of strings.
# Almost because gungho did some hideous stuff with strings (denoted with a pair of ' characters) like
# putting new lines and even the ' character inside their strings.
def csv_decoder(s: str):
    stop_lead = ''
    result = []
    line = []
    start = 0
    end = 0
    while end < len(s):
        if start == end:
            if s[start] == "'":
                stop_lead = "'"
            else:
                stop_lead = ''
        if stop_lead == "'":
            if s[end:end+2] == "',":
                line.append(s[start:end+1])
                end += 2
                start = end
            elif s[end:end+2] == "'\n":
                line.append(s[start:end+1])
                result.append(line)
                line = []
                end += 2
                start = end
            else:
                end += 1
        else:
            if s[end] == ',':
                line.append(s[start:end])
                end += 1
                start = end
            elif s[end] == '\n':
                line.append(s[start:end])
                result.append(line)
                line = []
                end += 1
                start = end
            else:
                end += 1

    line.append(s[start:end])
    result.append(line)
    return result

# base code from https://stackoverflow.com/a/8749640/8150086
class defaultlist(list):
    def __init__(self, fx, initial=[]):
        self._fx = fx
        self.extend(initial)
    def _fill(self, index):
        if type(index) == slice:
            if index.step == None or index.step > 0:
                if index.stop == None:
                    return
                while len(self) <= index.stop:
                    self.append(self._fx())
            else:
                if index.start == None:
                    return
                while len(self) <= index.start:
                    self.append(self._fx())
        else:
            while len(self) <= index:
                self.append(self._fx())
    def __setitem__(self, index, value):
        self._fill(index)
        list.__setitem__(self, index, value)
    def __getitem__(self, index):
        self._fill(index)
        if type(index) == slice:
            return defaultlist(self._fx, list.__getitem__(self, index))
        else:
            return list.__getitem__(self, index)


# this is used to name the skill ids and their arguments
# 

cc = lambda x: x
multiplier = lambda x: x/100
multiplier_with_default = lambda x: x/100 if x != 0 else 1.0
increase_multiplier = lambda x: (x + 100) /100
single_to_list = lambda x: [x]
collection_to_list = lambda x: list(x)
positive_values_to_list = lambda x: [i for i in x if i > 0]
binary_to_list = lambda x: [i for i,v in enumerate(str(bin(x))[:1:-1]) if v == '1']
list_of_binary_to_list = lambda x: [b for i in x for b in binary_to_list(i)]

atk_from_slice = lambda x: multiplier(x[2]) if 1 in x[:2] else 1.0
rcv_from_slice = lambda x: multiplier(x[2]) if 2 in x[:2] else 1.0
all_attr = [0,1,2,3,4]

hex_to_list = lambda h: [d for d,b in enumerate(str(bin(int(h, 16)))[:1:-1]) if b == '1']

def convert(type_name, arguments):
    def i(x):
        args = {}
        x = defaultlist(int, x)
               
        for name,t in arguments.items():
            if type(t) == tuple:
                index, funct = t[0], t[1]
                value = x[index]
                args[name] = funct(value)
            else:
                args[name] = t
        return (type_name, args)
    return i

def unimplimented(type_id):
    return convert('unimplimented', {'type': type_id})

##########################################################################################################
# Skills                                                                                                 #
##########################################################################################################

passive_stats_defaults = {'for_attr': [], 'for_type': [], 'hp_multiplier': 1.0, 'atk_multiplier': 1.0, 'rcv_multiplier': 1.0, 'reduction_attributes': all_attr, 'damage_reduction': 0.0}   
def passive_stats_convert(arguments):
    return convert('passive_stats', {k:(arguments[k] if k in arguments else v) for k,v in passive_stats_defaults.items()})

threshold_stats_defaults = {'for_attr': [], 'for_type': [], 'threshold': False, 'atk_multiplier': 1.0, 'rcv_multiplier': 1.0, 'reduction_attributes': all_attr, 'damage_reduction': 0.0}
ABOVE = True
BELOW = False
def threshold_stats_convert(above, arguments):
    if above:
        return convert('above_threshold_stats', {k:(arguments[k] if k in arguments else v) for k,v in threshold_stats_defaults.items()})
    else:
        return convert('below_threshold_stats', {k:(arguments[k] if k in arguments else v) for k,v in threshold_stats_defaults.items()})

combo_match_defaults = {'for_attr': [], 'for_type': [], 'minimum_combos': 0, 'minimum_atk_multiplier': 1.0, 'minimum_rcv_multiplier': 1.0, 'minimum_damage_reduction': 0.0,
                                                                            'bonus_atk_multiplier': 0.0,   'bonus_rcv_multiplier': 0.0,   'bonus_damage_reduction': 0.0,
                                                       'maximum_combos': 0, 'reduction_attributes': all_attr}
def combo_match_convert(arguments):
    def f(x):
        _,c = convert('combo_match', {k:(arguments[k] if k in arguments else v) for k,v in combo_match_defaults.items()})(x)
        if c['maximum_combos'] == 0:
            c['maximum_combos'] = c['minimum_combos']
        return 'combo_match',c
    return f

attribute_match_defaults = {'attributes': [], 'minimum_attributes': 0, 'minimum_atk_multiplier': 1.0, 'minimum_rcv_multiplier': 1.0, 'minimum_damage_reduction': 0.0,
                                                                      'bonus_atk_multiplier': 0.0,   'bonus_rcv_multiplier': 0.0,   'bonus_damage_reduction': 0.0,
                                             'maximum_attributes': 0, 'reduction_attributes': all_attr}   
def attribute_match_convert(arguments):
    def f(x):
        _,c = convert('attribute_match', {k:(arguments[k] if k in arguments else v) for k,v in attribute_match_defaults.items()})(x)
        if c['maximum_attributes'] == 0:
            c['maximum_attributes'] = c['minimum_attributes']
        return 'attribute_match',c
    return f
multi_attribute_match_defaults = {'attributes': [], 'minimum_match': 0, 'minimum_atk_multiplier': 1.0, 'minimum_rcv_multiplier': 1.0, 'minimum_damage_reduction': 0.0,
                                                                       'bonus_atk_multiplier': 0.0,   'bonus_rcv_multiplier': 0.0,   'bonus_damage_reduction': 0.0,
                                                   'reduction_attributes': all_attr}   
def multi_attribute_match_convert(arguments):
    return convert('multi-attribute_match', {k:(arguments[k] if k in arguments else v) for k,v in multi_attribute_match_defaults.items()})

mass_match_defaults = {'attributes': [], 'minimum_count': 0, 'minimum_atk_multiplier': 1.0, 'minimum_rcv_multiplier': 1.0, 'minimum_damage_reduction': 0.0,
                                                            'bonus_atk_multiplier': 0.0,   'bonus_rcv_multiplier': 0.0,   'bonus_damage_reduction': 0.0,
                                        'maximum_count': 0, 'reduction_attributes': all_attr}   
def mass_match_convert(arguments):
    def f(x):
        _,c = convert('mass_match', {k:(arguments[k] if k in arguments else v) for k,v in mass_match_defaults.items()})(x)
        if c['maximum_count'] == 0:
            c['maximum_count'] = c['minimum_count']
        return 'mass_match',c
    return f

SKILL_TRANSFORM = { 'version': 1220,
  0: lambda x: \
  convert('null_skill', {})(x) \
  if defaultlist(int,x)[1] == 0 else \
  convert('attack_attr_x_atk', {'attribute': (0,cc), 'multiplier': (1,multiplier), 'mass_attack': True})(x),
  1: convert('attack_attr_damage', {'attribute': (0,cc), 'damage': (1,cc), 'mass_attack': True}),
  2: convert('attack_x_atk', {'multiplier': (0,multiplier), 'mass_attack': False}),
  3: convert('damage_shield_buff', {'duration': (0,cc), 'reduction': (1,multiplier)}),
  4: convert('poison', {'multiplier': (0,multiplier)}),
  5: convert('change_the_world', {'duration': (0,cc)}),
  6: convert('gravity', {'percentage_hp': (0,multiplier)}),
  7: convert('heal_active', {'rcv_multiplier_as_hp': (0,multiplier), 'card_bind': 0, 'hp': 0, 'percentage_max_hp': 0.0, 'awoken_bind': 0, 'team_rcv_multiplier_as_hp': 0.0}),
  8: convert('heal_active', {'hp': (0,cc), 'card_bind': 0, 'rcv_multiplier_as_hp': 0.0, 'percentage_max_hp': 0.0, 'awoken_bind': 0, 'team_rcv_multiplier_as_hp': 0.0}),
  9: convert('single_orb_change', {'from': (0,cc), 'to': (0,cc)}),
 10: convert('board_refresh', {}),
 18: convert('delay', {'turns': (0,cc)}),
 19: convert('defense_reduction', {'duration': (0,cc), 'reduction': (1,multiplier)}),
 20: convert('double_orb_change', {'from_1': (0,cc), 'to_1': (1,cc), 'from_2': (2,cc), 'to_2': (3,cc)}),
 21: convert('elemental_shield_buff', {'duration': (0,cc), 'attribute': (1,cc), 'reduction': (2,multiplier)}),
 35: convert('drain_attack', {'atk_multiplier': (0,multiplier), 'recover_multiplier': (1,multiplier), 'mass_attack': False}),
 37: convert('attack_attr_x_atk', {'attribute': (0,cc), 'multiplier': (1,multiplier), 'mass_attack': False}),
 42: convert('element_attack_attr_damage', {'enemy_attribute': (0,cc), 'attack_attribute':(1,cc) , 'damage': (2,cc)}),
 50: lambda x: \
  convert('rcv_boost', {'duration': (0,cc), 'multiplier': (2,multiplier)})(x) \
  if defaultlist(int,x)[1] == 5 else \
  convert('attribute_attack_boost', {'duration': (0,cc), 'attributes': (1,single_to_list), 'multiplier': (2,multiplier)})(x),
 51: convert('force_mass_attack', {'duration': (0,cc)}),
 52: convert('enhance_orbs', {'orbs': (0,single_to_list)}),
 55: convert('laser', {'damage': (0,cc), 'mass_attack': False}),
 56: convert('laser', {'damage': (0,cc), 'mass_attack': True}),
 58: convert('attack_attr_random_x_atk', {'attribute': (0,cc), 'minimum_multiplier': (1,multiplier), 'maximum_multiplier': (2,multiplier), 'mass_attack': True}),
 59: convert('attack_attr_random_x_atk', {'attribute': (0,cc), 'minimum_multiplier': (1,multiplier), 'maximum_multiplier': (2,multiplier), 'mass_attack': False}),
 60: convert('counter_attack_buff', {'duration': (0,cc), 'multiplier': (1,multiplier), 'attribute': (2,cc)}),
 71: convert('board_change', {'attributes': (slice(None),lambda x: [v for v in x if v != -1])}),
 84: convert('suicide_attack_attr_random_x_atk', {'attribute': (0,cc), 'minimum_multiplier': (1,multiplier), 'maximum_multiplier': (2,multiplier), 'hp_remaining': (3,multiplier), 'mass_attack': False}),
 85: convert('suicide_attack_attr_random_x_atk', {'attribute': (0,cc), 'minimum_multiplier': (1,multiplier), 'maximum_multiplier': (2,multiplier), 'hp_remaining': (3,multiplier), 'mass_attack': True}),
 86: convert('suicide_attack_attr_damage', {'attribute': (0,cc), 'damage': (1,multiplier), 'hp_remaining': (3,multiplier), 'mass_attack': False}),
 87: convert('suicide_attack_attr_damage', {'attribute': (0,cc), 'damage': (1,multiplier), 'hp_remaining': (3,multiplier), 'mass_attack': True}),
 88: convert('type_attack_boost', {'duration': (0,cc), 'types': (1,single_to_list), 'multiplier': (2,multiplier)}),
 90: convert('attribute_attack_boost', {'duration': (0,cc), 'attributes': (slice(1,3),collection_to_list), 'multiplier': (2,multiplier)}),
 91: convert('enhance_orbs', {'orbs': (slice(0,2), collection_to_list)}),
 92: convert('type_attack_boost', {'duration': (0,cc), 'types': (slice(1,3),collection_to_list), 'multiplier': (2,multiplier)}),
 93: convert('leader_swap', {}),
110: convert('grudge_strike', {'mass_attack': (0,lambda x: x == 0), 'attribute': (1,cc), 'high_multiplier': (2,multiplier), 'low_multiplier': (3,multiplier)}),
115: convert('drain_attack_attr', {'attribute': (0,cc),'atk_multiplier': (1,multiplier), 'recover_multiplier': (2,multiplier), 'mass_attack': False}),
116: convert('combine_active_skills', {'skill_ids': (slice(None),collection_to_list)}),
117: convert('heal_active', {'card_bind': (0,cc), 'rcv_multiplier_as_hp': (1,multiplier), 'hp': (2,cc), 'percentage_max_hp': (3,multiplier), 'awoken_bind': (4,cc), 'team_rcv_multiplier_as_hp': 0.0}),
118: convert('random_skill', {'skill_ids': (slice(None),collection_to_list)}),
126: convert('change_skyfall', {'orbs': (0,binary_to_list), 'duration': (1,cc), 'percentage': (3,multiplier)}),
127: convert('column_change', {'columns': (slice(None),lambda x: [{'index':i if i < 3 else i-6,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}), # 0 1 2 -3 -2 -1
128: convert('row_change', {'rows': (slice(None),lambda x: [{'index':i if i < 2 else i-5,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}), # 0 1 -3 -2 -1
132: convert('move_time_buff', {'duration': (0,cc), 'static': (1,lambda x: x/10), 'percentage': (2,multiplier)}),
140: convert('enhance_orbs', {'orbs': (0,binary_to_list)}),
141: convert('spawn_orbs', {'amount': (0,cc), 'orbs': (1,binary_to_list), 'excluding_orbs': (2, binary_to_list)}),
142: convert('attribute_change', {'duration': (0,cc), 'attribute': (1,cc)}),
144: convert('attack_attr_x_team_atk', {'team_attributes': (0,binary_to_list), 'multiplier': (1,multiplier), 'mass_attack': (2,lambda x: x == 0), 'attack_attribute': (3,cc),}),
145: convert('heal_active', {'team_rcv_multiplier_as_hp': (0,multiplier), 'card_bind': 0, 'rcv_multiplier_as_hp': 0.0, 'hp': 0, 'percentage_max_hp': 0.0, 'awoken_bind': 0}),
146: convert('haste', {'minimum_turns': (0,cc), 'maximum_turns': (1,cc)}),
152: convert('lock_orbs', {'orbs': (0,binary_to_list)}),
153: convert('change_enemies_attribute', {'attribute': (0,cc)}),
154: convert('random_orb_change', {'from': (0,binary_to_list), 'to': (1,binary_to_list)}),
156: lambda x: \
  convert('awakening_heal', {'duration': (0,cc), 'awakenings': (slice(1,4),collection_to_list), 'amount_per': (5,cc)})(x) \
  if defaultlist(int,x)[4] == 1 else \
  ( convert('awakening_attack_boost', {'duration': (0,cc), 'awakenings': (slice(1,4),collection_to_list), 'amount_per': (5,lambda x: (x - 100) / 100)})(x) \
  if defaultlist(int,x)[4] == 2 else \
  ( convert('awakening_shield', {'duration': (0,cc), 'awakenings': (slice(1,4),collection_to_list), 'amount_per': (5,multiplier)})(x) \
  if defaultlist(int,x)[4] == 3 else \
  ( unimplimented(156)(x) ) ) ),
160: convert('extra_combo', {'duration': (0,cc), 'combos': (1,cc)}),
161: convert('true_gravity', {'percentage_max_hp': (0,multiplier)}),
172: convert('unlock', {}),
173: convert('absorb_mechanic_void', {'duration': (0,cc), 'attribute_absorb': (1,bool), 'damage_absorb': (3,bool)}),
179: convert('auto_heal_buff', {'duration': (0,cc), 'percentage_max_hp': (2,multiplier)}),
180: convert('enhanced_skyfall_buff', {'duration': (0,cc), 'percentage_increase': (1,multiplier)}),
184: convert('no_skyfall_buff', {'duration': (0,cc)}),
188: convert('multihit_laser', {'damage': (0,cc), 'mass_attack': False}),
 11: passive_stats_convert({'for_attr': (0,single_to_list), 'atk_multiplier': (1,multiplier)}),
 12: convert('after_attack_on_match', {'multiplier': (0,multiplier)}),
 13: convert('heal_on_match', {'multiplier': (0,multiplier)}),
 14: convert('resolve', {'threshold': (0,multiplier)}),
 15: convert('bonus_move_time', {'time': (0,multiplier), 'for_attr': [], 'for_type': [], 'hp_multiplier': 1.0, 'atk_multiplier': 1.0, 'rcv_multiplier': 1.0}),
 16: passive_stats_convert({'reduction_attributes': all_attr, 'damage_reduction': (0,multiplier)}),
 17: passive_stats_convert({'reduction_attributes': (0,single_to_list), 'damage_reduction': (1,multiplier)}),
 22: passive_stats_convert({'for_type': (0,single_to_list), 'atk_multiplier': (1,multiplier)}),
 23: passive_stats_convert({'for_type': (0,single_to_list), 'hp_multiplier': (1,multiplier)}),
 24: passive_stats_convert({'for_type': (0,single_to_list), 'rcv_multiplier': (1,multiplier)}),
 26: passive_stats_convert({'for_attr': all_attr, 'atk_multiplier': (0,multiplier)}),
 28: passive_stats_convert({'for_attr': (0,single_to_list), 'atk_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 29: passive_stats_convert({'for_attr': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'atk_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 30: passive_stats_convert({'for_type': (slice(0,2),collection_to_list), 'hp_multiplier': (2,multiplier)}),
 31: passive_stats_convert({'for_type': (slice(0,2),collection_to_list), 'atk_multiplier': (2,multiplier)}),
 33: convert('drumming_sound', {}),
 36: passive_stats_convert({'reduction_attributes': (slice(0,2),collection_to_list), 'damage_reduction': (2,multiplier)}),
 38: threshold_stats_convert(BELOW, {'for_attr': all_attr, 'threshold': (0,multiplier), 'damage_reduction': (2,multiplier)}),
 39: threshold_stats_convert(BELOW, {'for_attr': all_attr, 'threshold': (0,multiplier), 'atk_multiplier': (slice(1,4),atk_from_slice), 'rcv_multiplier': (slice(1,4),rcv_from_slice)}),
 40: passive_stats_convert({'for_attr': (slice(0,2),collection_to_list), 'atk_multiplier': (2,multiplier)}),
 41: convert('counter_attack', {'chance': (0,multiplier), 'multiplier': (1,multiplier), 'attribute': (2,cc)}),
 43: threshold_stats_convert(ABOVE, {'for_attr': all_attr, 'threshold': (0,multiplier), 'damage_reduction': (2,multiplier)}),
 44: threshold_stats_convert(ABOVE, {'for_attr': all_attr, 'threshold': (0,multiplier), 'atk_multiplier': (slice(1,4),atk_from_slice), 'rcv_multiplier': (slice(1,4),rcv_from_slice)}),
 45: passive_stats_convert({'for_attr': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'atk_multiplier': (1,multiplier)}),
 46: passive_stats_convert({'for_attr': (slice(0,2),collection_to_list), 'hp_multiplier': (2,multiplier)}),
 48: passive_stats_convert({'for_attr': (0,single_to_list), 'hp_multiplier': (1,multiplier)}),
 49: passive_stats_convert({'for_attr': (0,single_to_list), 'rcv_multiplier': (1,multiplier)}),
 53: convert('egg_drop_rate', {'multiplier': (0,multiplier)}),
 54: convert('coin_drop_rate', {'multiplier': (0,multiplier)}),
 61: attribute_match_convert({'attributes': (0,binary_to_list), 'minimum_attributes': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'minimum_rcv_multiplier': (2,multiplier), 'bonus_atk_multiplier': (3,multiplier), 'bonus_rcv_multiplier': (3,multiplier)}),
 62: passive_stats_convert({'for_type': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'atk_multiplier': (1,multiplier)}),
 63: passive_stats_convert({'for_type': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 64: passive_stats_convert({'for_type': (0,single_to_list), 'atk_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 65: passive_stats_convert({'for_type': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'atk_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 66: combo_match_convert({'for_attr': all_attr, 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (1,multiplier)}),
 67: passive_stats_convert({'for_attr': (0,single_to_list), 'hp_multiplier': (1,multiplier), 'rcv_multiplier': (1,multiplier)}),
 69: passive_stats_convert({'for_attr': (0,single_to_list), 'for_type': (1,single_to_list), 'atk_multiplier': (2,multiplier)}),
 73: passive_stats_convert({'for_attr': (0,single_to_list), 'for_type': (1,single_to_list), 'hp_multiplier': (2,multiplier), 'atk_multiplier': (2,multiplier)}),
 75: passive_stats_convert({'for_attr': (0,single_to_list), 'for_type': (1,single_to_list), 'atk_multiplier': (2,multiplier), 'rcv_multiplier': (2,multiplier)}),
 76: passive_stats_convert({'for_attr': (0,single_to_list), 'for_type': (1,single_to_list), 'hp_multiplier': (2,multiplier), 'atk_multiplier': (2,multiplier), 'rcv_multiplier': (2,multiplier)}),
 77: passive_stats_convert({'for_type': (slice(0,2),collection_to_list), 'hp_multiplier': (2,multiplier), 'atk_multiplier': (2,multiplier)}),
 79: passive_stats_convert({'for_type': (slice(0,2),collection_to_list), 'atk_multiplier': (2,multiplier), 'rcv_multiplier': (2,multiplier)}),
 94: threshold_stats_convert(BELOW, {'for_attr': (1,single_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (slice(2,5),atk_from_slice), 'rcv_multiplier': (slice(2,5),rcv_from_slice)}),
 95: threshold_stats_convert(BELOW, {'for_type': (1,single_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (slice(2,5),atk_from_slice), 'rcv_multiplier': (slice(2,5),rcv_from_slice)}),
 96: threshold_stats_convert(ABOVE, {'for_attr': (1,single_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (slice(2,5),atk_from_slice), 'rcv_multiplier': (slice(2,5),rcv_from_slice)}),
 97: threshold_stats_convert(ABOVE, {'for_type': (1,single_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (slice(2,5),atk_from_slice), 'rcv_multiplier': (slice(2,5),rcv_from_slice)}),
 98: combo_match_convert({'for_attr': all_attr, 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (1,multiplier), 'bonus_atk_multiplier': (2,multiplier), 'maximum_combos':(3,cc)}),
100: convert('skill_used_stats', {'for_attr': all_attr, 'for_type': [], 'atk_multiplier': (slice(0,4),atk_from_slice), 'rcv_multiplier': (slice(0,4),rcv_from_slice)}),
101: convert('exact_combo_match', {'combos': (0,cc), 'atk_multiplier': (1,multiplier)}),
103: combo_match_convert({'for_attr': all_attr, 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (slice(1,4),atk_from_slice), 'minimum_rcv_multiplier': (slice(1,4),rcv_from_slice), 'maximum_combos':(0,cc)}),
104: combo_match_convert({'for_attr': (1,binary_to_list), 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (slice(2,5),atk_from_slice), 'minimum_rcv_multiplier': (slice(2,5),rcv_from_slice), 'maximum_combos':(0,cc)}),
105: passive_stats_convert({'for_attr': all_attr, 'atk_multiplier': (1,multiplier), 'rcv_multiplier': (0,multiplier)}),
106: passive_stats_convert({'for_attr': all_attr, 'hp_multiplier': (0,multiplier), 'atk_multiplier': (1,multiplier)}),
107: passive_stats_convert({'for_attr': all_attr, 'hp_multiplier': (0,multiplier)}),
108: convert('passive_stats_type_atk_all_hp', {'for_type': (1,single_to_list), 'atk_multiplier': (2,multiplier), 'hp_multiplier': (0,multiplier)}),
109: mass_match_convert({'attributes': (0,binary_to_list), 'minimum_count': (1,cc), 'minimum_atk_multiplier': (2,multiplier)}),
111: passive_stats_convert({'for_attr': (slice(0,2),collection_to_list), 'hp_multiplier': (2,multiplier), 'atk_multiplier': (2,multiplier)}),
114: passive_stats_convert({'for_attr': (slice(0,2),collection_to_list), 'hp_multiplier': (2,multiplier), 'atk_multiplier': (2,multiplier), 'rcv_multiplier': (2,multiplier)}),
119: mass_match_convert({'attributes': (0,binary_to_list), 'minimum_count': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'bonus_atk_multiplier': (3,multiplier), 'maximum_count': (4,cc)}),
121: passive_stats_convert({'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list), 'hp_multiplier': (2,increase_multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier)}),
122: threshold_stats_convert(BELOW, {'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier)}),
123: threshold_stats_convert(ABOVE, {'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier)}),
124: multi_attribute_match_convert({'attributes': (slice(0,5),list_of_binary_to_list), 'minimum_match': (5,cc), 'minimum_atk_multiplier': (6,multiplier), 'bonus_atk_multiplier': (7,multiplier)}),
125: convert('team_build_bonus', {'monster_ids': (slice(0,5),positive_values_to_list), 'hp_multiplier': (5,increase_multiplier), 'atk_multiplier': (6,increase_multiplier), 'rcv_multiplier': (7,increase_multiplier)}),
129: passive_stats_convert({'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list), 'hp_multiplier': (2,increase_multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier), 'reduction_attributes': (5,binary_to_list), 'damage_reduction': (6,multiplier)}),
130: threshold_stats_convert(BELOW, {'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier), 'reduction_attributes': (5,binary_to_list), 'damage_reduction': (6,multiplier)}),
131: threshold_stats_convert(ABOVE, {'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'threshold': (0,multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier), 'reduction_attributes': (5,binary_to_list), 'damage_reduction': (6,multiplier)}),
133: convert('skill_used_stats', {'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list), 'atk_multiplier': (2,increase_multiplier), 'rcv_multiplier': (3,increase_multiplier)}),
136: convert('dual_passive_stats', {'for_attr_1': (0,binary_to_list), 'for_type_1': [], 'hp_multiplier_1': (1,increase_multiplier), 'atk_multiplier_1': (2,increase_multiplier), 'rcv_multiplier_1': (3,increase_multiplier), 'for_attr_2': (4,binary_to_list), 'for_type_2': [], 'hp_multiplier_2': (5,increase_multiplier), 'atk_multiplier_2': (6,increase_multiplier), 'rcv_multiplier_2': (7,increase_multiplier)}),
137: convert('dual_passive_stats', {'for_attr_1': [], 'for_type_1': (0,binary_to_list), 'hp_multiplier_1': (1,increase_multiplier), 'atk_multiplier_1': (2,increase_multiplier), 'rcv_multiplier_1': (3,increase_multiplier), 'for_attr_2': [], 'for_type_2': (4,binary_to_list), 'hp_multiplier_2': (5,increase_multiplier), 'atk_multiplier_2': (6,increase_multiplier), 'rcv_multiplier_2': (7,increase_multiplier)}),
138: convert('combine_leader_skills', {'skill_ids': (slice(None),collection_to_list)}),
139: convert('dual_threshold_stats', {'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list),
    'threshold_1': (2,multiplier), 'above_1': (3,lambda x: not bool(x)), 'atk_multiplier_1': (4,multiplier), 'rcv_multiplier_1': 1.0, 'damage_reduction_1': 0.0,
    'threshold_2': (5,multiplier), 'above_2': (6,lambda x: not bool(x)), 'atk_multiplier_2': (7,multiplier), 'rcv_multiplier_2': 1.0, 'damage_reduction_2': 0.0}),
148: convert('rank_experience_rate', {'multiplier': (0,multiplier)}),
149: convert('heath_tpa_stats', {'rcv_multiplier': (0,multiplier)}),
150: convert('five_orb_one_enhance', {'atk_multiplier': (1,multiplier)}),
151: convert('heart_cross', {'atk_multiplier': (0,increase_multiplier), 'rcv_multiplier': (1,increase_multiplier), 'damage_reduction': (2,multiplier)}),
155: convert('multiplayer_stats', {'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list), 'hp_multiplier': (2,increase_multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier)}),
157: convert('color_cross', {'crosses': (slice(None), lambda x: [{'attribute':a,'atk_multiplier':multiplier(d)} for a,d in zip(x[::2],x[1::2])])}),
158: convert('minimum_match', {'minimum_match': (0,cc), 'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'hp_multiplier': (4,increase_multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (5,increase_multiplier)}),
159: mass_match_convert({'attributes': (0,binary_to_list), 'minimum_count': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'bonus_atk_multiplier': (3,multiplier), 'maximum_count': (4,cc)}),
162: convert('large_board', {'for_attr': [], 'for_type': [], 'hp_multiplier': 1.0, 'atk_multiplier': 1.0, 'rcv_multiplier': 1.0}),
163: convert('no_skyfall', {}),
164: multi_attribute_match_convert({'attributes': (slice(0,4),list_of_binary_to_list), 'minimum_match': (4,cc), 'minimum_atk_multiplier': (5,multiplier), 'minimum_rcv_multiplier': (6,multiplier), 'bonus_atk_multiplier': (7,multiplier), 'bonus_rcv_multiplier': (7,multiplier)}),
165: attribute_match_convert({'attributes': (0,binary_to_list), 'minimum_attributes': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'minimum_rcv_multiplier': (3,multiplier), 'bonus_atk_multiplier': (4,multiplier), 'bonus_rcv_multiplier': (5,multiplier), 'maximum_attributes': (slice(1,7,6),lambda x: x[0] + x[1])}),
166: combo_match_convert({'for_attr': all_attr, 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (1,multiplier), 'minimum_rcv_multiplier': (2,multiplier), 'bonus_atk_multiplier': (3,multiplier), 'bonus_rcv_multiplier': (4,multiplier), 'maximum_combos':(5,cc)}),
167: mass_match_convert({'attributes': (0,binary_to_list), 'minimum_count': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'minimum_rcv_multiplier': (3,multiplier), 'bonus_atk_multiplier': (4,multiplier), 'bonus_atk_multiplier': (5,multiplier), 'maximum_count': (6,cc)}),
169: combo_match_convert({'for_attr': all_attr, 'minimum_combos': (0,cc), 'minimum_atk_multiplier': (1,multiplier), 'minimum_damage_reduction': (2,multiplier)}),
170: attribute_match_convert({'attributes': (0,binary_to_list), 'minimum_attributes': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'minimum_damage_reduction': (3,multiplier)}),
171: multi_attribute_match_convert({'attributes': (slice(0,4),list_of_binary_to_list), 'minimum_match': (4,cc), 'minimum_atk_multiplier': (5,multiplier), 'minimum_damage_reduction': (6,multiplier)}),
175: convert('collab_bonus', {'collab_id': (0,cc), 'hp_multiplier': (3,increase_multiplier), 'atk_multiplier': (4,increase_multiplier), 'rcv_multiplier': (5,increase_multiplier)}),
177: convert('orbs_remaining', {'orb_count': (5,cc), 'atk_multiplier': (6,multiplier)}),
178: convert('fixed_move_time', {'time': (0,cc), 'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'hp_multiplier': (3,increase_multiplier), 'atk_multiplier': (4,increase_multiplier), 'rcv_multiplier': (5,increase_multiplier)}),
182: mass_match_convert({'attributes': (0,binary_to_list), 'minimum_count': (1,cc), 'minimum_atk_multiplier': (2,multiplier), 'minimum_damage_reduction': (3,multiplier)}),
183: convert('dual_threshold_stats', {'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list),
    'threshold_1': (2,multiplier), 'above_1': True, 'atk_multiplier_1': (3,multiplier), 'rcv_multiplier_1': 1.0, 'damage_reduction_1': (4,multiplier),
    'threshold_2': (5,multiplier), 'above_2': False, 'atk_multiplier_2': (6,increase_multiplier), 'rcv_multiplier_2': (7,increase_multiplier), 'damage_reduction_2': 0.0}),
185: convert('bonus_move_time', {'time': (0,multiplier), 'for_attr': (1,binary_to_list), 'for_type': (2,binary_to_list), 'hp_multiplier': (3,increase_multiplier), 'atk_multiplier': (4,increase_multiplier), 'rcv_multiplier': (5,increase_multiplier)}),
186: convert('large_board', {'for_attr': (0,binary_to_list), 'for_type': (1,binary_to_list), 'hp_multiplier': (2,increase_multiplier), 'atk_multiplier': (3,increase_multiplier), 'rcv_multiplier': (4,increase_multiplier)}),
}



def _parse_skills(raw_json):
    print('[Skills] Starting to parse skills')
    if raw_json['v'] > SKILL_TRANSFORM['version']:
        print(f"[Skills] The raw json is running a newer version than what's supported. ( {raw_json['v']} vs {SKILL_TRANSFORM['version']} )")
    if raw_json['res'] != 0:
        print('[Skills] The "res" property is not zero, the results might not be accurate')
    
    parsed_json = {}
    parsed_json['version'] = raw_json['v']
    parsed_json['active_skills'] = {}
    parsed_json['leader_skills'] = {}
    
    for i,skill_data in enumerate(raw_json['skill']):
        if skill_data[3] == 0 and skill_data[4] == 0: # this distinguishes leader skills from active skills
            parsed_json['leader_skills'][i] = {}
            parsed_json['leader_skills'][i]['id'] = i
            parsed_json['leader_skills'][i]['name'] = skill_data[0]
            parsed_json['leader_skills'][i]['card_description'] = skill_data[1]
            if skill_data[2] in SKILL_TRANSFORM:
                parsed_json['leader_skills'][i]['type'],parsed_json['leader_skills'][i]['args'] = SKILL_TRANSFORM[skill_data[2]](skill_data[6:])
            else:
                print(f'[Skills] Found unexpected leader skill ( id: {i}, type:{skill_data[2]} )')
                parsed_json['leader_skills'][i]['type'] = 'unexpected'
                parsed_json['leader_skills'][i]['args'] = {'type': skill_data[2]}
        else:
            parsed_json['active_skills'][i] = {}
            parsed_json['active_skills'][i]['id'] = i
            parsed_json['active_skills'][i]['name'] = skill_data[0]
            parsed_json['active_skills'][i]['card_description'] = skill_data[1]
            parsed_json['active_skills'][i]['max_skill'] = skill_data[3]
            parsed_json['active_skills'][i]['base_cooldown'] = skill_data[4]
            if skill_data[2] in SKILL_TRANSFORM:
                try:
                    parsed_json['active_skills'][i]['type'],parsed_json['active_skills'][i]['args'] = SKILL_TRANSFORM[skill_data[2]](skill_data[6:])
                except Exception as e:
                    print(i)
                    print(skill_data[2])
                    print(skill_data[6:])
                    print(SKILL_TRANSFORM[skill_data[2]](skill_data[6:]))
            else:
                print(f'[Skills] Found unexpected active skill ( id: {i}, type:{skill_data[2]} )')
                parsed_json['active_skills'][i]['type'] = 'unexpected'
                parsed_json['active_skills'][i]['args'] = {'type': skill_data[2]}
    print('[Skills] Skill parsing complete')
    
    if _DEV:
        def verify(skills):
            type_verification = defaultdict(lambda: defaultdict(set))
            for i,skill in skills.items():
                type_verification[skill['type']]['_arg_names'].add(frozenset(skill['args'].keys()))
                for arg_name,arg_value in skill['args'].items():
                    type_verification[skill['type']][arg_name].add(type(arg_value))
            for skill_type,args in type_verification.items():
                for arg_name,arg_types in args.items():
                    if len(arg_types) != 1:
                        print(f'[Skills] INCONSISTENT name: {skill_type} difference in {repr(arg_name)}: {repr(arg_types)}\n[Skills] ')

        print('[Skills] Checking active skill consistency\n[Skills] -------start-------\n[Skills] ')
        verify(parsed_json['active_skills'])
        print('[Skills] --------end--------\n[Skills] ')

        print('[Skills] Checking leader skill consistency\n[Skills] -------start-------\n[Skills] ')
        verify(parsed_json['leader_skills'])
        print('[Skills] --------end--------\n[Skills] ')

    return parsed_json

##########################################################################################################
# Enemy Skills                                                                                           #
##########################################################################################################

def orb_convert(from_index, args):
    def internal(x):
        if defaultlist(int,x)[from_index] < 0:
            return convert('orb_convert_random', {'from_count': (args['from'][0], lambda x: abs(args['from'][1](x))), 'to': args['to'], 'damage': args['damage']})(x)
        return convert('orb_convert', {'from': args['from'], 'to': args['to'], 'damage': args['damage']})(x)
    return internal

orb_spawn_defaults = {'damage': 0.0, 'amount': 0, 'orbs': [], 'exclude_orbs': []}
def orb_spawn(arguments):
    return convert('spawn_orbs', {k:(arguments[k] if k in arguments else v) for k,v in orb_spawn_defaults.items()})
    
all_slots = [0,1,2,3,4,5]
def card_bind_slots(b):
    if b == 0:
        return all_slots
    result = []
    if b & 1:
        result.append(0)
    if b >> 2 & 1:
        result.extend([1,2,3,4])
    if b >> 1 & 1:
        result.append(5)
    return result

def card_bind(arguments):
    arguments['damage'] = arguments['damage'] if 'damage' in arguments else 0.0
    arguments['slots'] = arguments['slots'] if 'slots' in arguments else []
    arguments['types'] = arguments['types'] if 'types' in arguments else []
    arguments['attributes'] = arguments['attributes'] if 'attributes' in arguments else []
    arguments['card_count'] = arguments['card_count'] if 'card_count' in arguments else 6
    return convert('card_bind', arguments)

def pattern(values):
    result = []
    for value in values:
        r = []
        for c in range(6):
            r.append(value >> c & 1)
        result.append(r)
    return result

pos_x = {0: 0, 1: 1, 2: 2, 3: 3, 4: -3, 5: -2, 6: -1}
def position_x(x):
    if x in pos_x:
        return pos_x[x]
    print(f'Unexpected position x value: {x}')
    return x

pos_y = {1: 0, 2: 1, 3: 2, 3: 3, 4: -2, 5: -1}
def position_y(y):
    if y in pos_y:
        return pos_y[y]
    print(f'Unexpected position y value: {y}')
    return y

ENEMY_SKILL_TRANSFORM = { 'version': 2,
0:   convert('null_skill', {}),
1:   card_bind({'slots': all_slots, 'card_count': (0,lambda x: max(1,x)), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc)}),
2:   card_bind({'attributes': (0,single_to_list), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc)}),
3:   card_bind({'types': (0,single_to_list), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc)}),
4:   orb_convert(0, {'damage': 0.0, 'from': (0,cc), 'to': (1,cc)}),
5:   convert('normal_blind', {'damage': 0.0}),
6:   convert('dispel', {}),
7:   convert('enemy_heal', {'minimum_percentage': (0,multiplier), 'maximum_percentage': (1,multiplier)}),
8:   convert('next_attack_boost', {'minimum_percentage': (0,increase_multiplier), 'maximum_percentage': (1,increase_multiplier)}),
9:   unimplimented(9),
10:  unimplimented(10),
11:  unimplimented(11),
12:  orb_convert(0, {'damage': 0.0, 'from': (0,cc), 'to': 6}),
13:  orb_convert(0, {'damage': 0.0, 'from': (0,lambda x: -x), 'to': 6}),
14:  convert('skill_bind', {'minimum_duration': (0,cc), 'maximum_duration': (1,cc)}),
15:  convert('multi_attack', {'minimum_hits': (0,cc), 'maximum_hits': (1,cc), 'damage': (2,multiplier)}),
16:  convert('skip', {}), # does nothing but say text
17:  convert('attack_boost_1', {'un': (0,cc), 'duration': (1,cc), 'multiplier': (2,multiplier)}), ### look into this later
18:  convert('attack_boost_2', {'duration': (0,cc), 'multiplier': (1,multiplier)}), ### look into this later
19:  convert('attack_boost_3', {'un': (0,cc), 'duration': (1,cc), 'multiplier': (2,multiplier)}), ### look into this later
20:  convert('status_shield', {'duration': (2,cc)}),
21:  convert('_unused_1', {}), # unused  #the following are special skills used to control monster behavior, details later
22:  convert('_flag_set', {}), # Set flag {ai} to True
23:  convert('_if_flag_jump_0_index', {}), # If flag {ai} is True, jump to action {rnd+1}?
24:  convert('_flag_remove', {}), # Set flag {ai} to False
25:  convert('_counter_set', {}), # Set counter to {ai}
26:  convert('_counter_add', {}), # Add 1 to counter
27:  convert('_counter_subtract', {}), # Subtract 1 from counter
28:  convert('_if_hp_below_jump', {}), # If HP is less than (or equal to?) {ai}%, jump to action {rnd}
29:  convert('_if_hp_above_jump', {}), # If HP is more than (or equal to?) {ai}%, jump to action {rnd}
30:  convert('_if_counter_below_jump', {}), # If counter is less than (or equal to?) {ai}, jump to action {rnd}
31:  convert('_if_counter_equal_jump', {}), # If counter is equal to {ai}, jump to action {rnd}
32:  convert('_if_counter_above_jump', {}), # If counter is more than (or equal to?) {ai}, jump to action {rnd}
33:  convert('_if_level_below_jump', {}), # If counter is less than (or equal to?) {ai}, jump to action {rnd}
34:  convert('_if_level_equal_jump', {}), # If counter is equal to {ai}, jump to action {rnd}
35:  convert('_if_level_below_jump', {}),
36:  convert('_end_path', {}), # seems to force a normal attack, but most recent monsters use them as unreachable buffers
37:  convert('_display_counter', {}), # unused?
38:  convert('_if_counter_set', {}), # unsure of exact meaning, guess: Set (flag?) {rnd} when counter equals {ai}?
39:  convert('time_debuff', {'duration': (0,cc), 'static': (1,lambda x: x/10), 'percentage': (2,multiplier)}),
40:  convert('suicide', {}),
41:  unimplimented(41),
42:  unimplimented(42),
43:  convert('_if_flag_jump', {}), # If flag {ai} is True, jump to action {rnd}?
44:  convert('_or_flag', {}), # MUST LOOK INTO
45:  convert('_xor_flag', {}), # MUST LOOK INTO
46:  convert('element_change', {'attribute_pool': (slice(0,5), lambda x: list(set(x)))}),
47:  convert('normal_attack', {'damage': (0,multiplier)}),
48:  orb_convert(1, {'damage': (0,multiplier), 'from': (1,cc), 'to': (2,cc)}),
49:  convert('_preemptive', {'minimum_level': (0,cc)}),
50:  convert('gravity', {'amount': (0,multiplier)}),
51:  unimplimented(51),
52:  convert('revive', {'percentage_hp': (0,multiplier)}),
53:  convert('absorb_attribute', {'minimum_duration': (0,cc), 'maximum_duration': (1,cc), 'attributes': (2,binary_to_list)}),
54:  card_bind({'slots': (0,card_bind_slots), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc)}),
55:  convert('player_heal', {'minimum_amount': (0,multiplier), 'maximum_amount': (1,multiplier)}),
56:  orb_convert(0, {'damage': 0.0, 'from': (0,cc), 'to': 7}),
57:  unimplimented(57),
58:  unimplimented(58),
59:  unimplimented(59),
60:  orb_spawn({'amount': (0,cc), 'orbs': [7], 'exclude_orbs': [7]}),
61:  orb_spawn({'amount': (0,cc), 'orbs': [8], 'exclude_orbs': [8]}),
62:  convert('normal_blind', {'damage': (0,multiplier)}),
63:  card_bind({'damage': (0,multiplier), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc), 'slots': (3,card_bind_slots), 'card_count': (4,lambda x: max(1,x))}),
64:  orb_spawn({'damage': (0,multiplier), 'amount': (1,cc), 'orbs': [7], 'exclude_orbs': [7]}),
65:  card_bind({'slots': [1,2,3,4], 'card_count': (0,cc), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc)}),
66:  convert('skip', {}),
67:  convert('absorb_combo', {'minimum_duration': (0,cc), 'maximum_duration': (1,cc), 'combo_count': (2,cc)}),
68:  convert('change_skyfall', {'orbs': (0,binary_to_list), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc), 'percentage': (3,multiplier)}),
69:  convert('transformation', {}), # first skill, passive, animation for transformation on death, eg. nordis
70:  unimplimented(70),
71:  convert('void_damage', {'duration': (0,cc), 'amount': (2,cc)}), # unused? flag for what to void
72:  convert('passive_attribute_reduction', {'attributes': (0,binary_to_list), 'reduction': (1,multiplier)}),
73:  convert('passive_resolve', {'threshold': (0,multiplier)}),
74:  convert('damage_shield', {'duration': (0,cc), 'reduction': (1,multiplier)}),
75:  convert('leader_swap', {'duration': (0,cc)}),
76:  convert('column_change', {'damage': 0.0, 'columns': (slice(None),lambda x: [{'index':i if i < 3 else i-6,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}), # order 0 1 2 -3 -2 -1
77:  convert('column_change', {'damage': (6,multiplier), 'columns': (slice(0,6),lambda x: [{'index':i if i < 3 else i-6,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}),
78:  convert('row_change', {'damage': 0.0, 'rows': (slice(None),lambda x: [{'index':i if i < 2 else i-5,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}),       # order 0 1 -3 -2 -1
79:  convert('row_change', {'damage': (6,multiplier), 'rows': (slice(0,6),lambda x: [{'index':i if i < 2 else i-5,'orbs':binary_to_list(orbs)} for indices,orbs in zip(x[::2],x[1::2]) for i in binary_to_list(indices)])}),
80:  unimplimented(80),
81:  convert('board_change', {'damage': (0,multiplier), 'attributes': (slice(1,None),lambda x: [v for v in x if v != -1])}),
82:  convert('normal_attack', {'damage': 1.0}), # unsure of extra, seems like a normal 100% damage hit
83:  convert('combine_enemy_skills', {'skill_ids': (slice(None),collection_to_list)}),
84:  convert('board_change', {'damage': 0.0, 'attributes': (0,binary_to_list)}),
85:  convert('board_change', {'damage': (0,multiplier), 'attributes': (1,binary_to_list)}),
86:  convert('enemy_heal', {'minimum_percentage': (0,multiplier), 'maximum_percentage': (1,multiplier)}),
87:  convert('absorb_damage', {'duration': (0,cc), 'amount': (1,cc)}),
88:  convert('awoken_bind', {'duration': (0,cc)}),
89:  convert('skill_delay', {'minimum_amount': (0,cc), 'maximum_amount': (0,cc)}),
90:  convert('_if_on_team_jump', {'monster_ids': (slice(None), lambda x: [i for i in x if i != 0])}), # if one of the cards in monster_ids is on the team, jump to {rnd}
91:  unimplimented(91),
92:  orb_spawn({'amount': (0,cc), 'orbs': (1,binary_to_list), 'exclude_orbs': (2,binary_to_list)}),
93:  unimplimented(93), # Unsure how to handle properly, found only on the original final fantasy dungeon boss, something to do with special effects
94:  convert('lock_orbs', {'amount': (1,cc), 'attributes': (0,binary_to_list)}),
95:  convert('passive_on_death', {'skill_id': (0,cc)}), # On death ability, registered through a passive (see anji for example)
96:  convert('lock_skyfall', {'specific_attributes': (0,lambda x: binary_to_list(x) if x != -1 else []), 'minimum_duration': (1,cc), 'maximum_duration': (2,cc), 'chance': (3,multiplier)}), # specific_attributes is the attributes locked, or empty list for all
97:  convert('super_blind', {'duration': (0,cc), 'minimum_amount': (1,cc), 'maximum_amount': (2,cc)}), # random orbs
98:  convert('super_blind_pattern', {'duration': (0,cc), 'pattern': (slice(1,6),pattern)}), # list of rows; 7x6 boards copy row 3 (1-index from top) to rows 3 and 4, and column 4 (1-index from left) to columns 4 and 5
99:  convert('scroll_lock', {'duration': (1,cc), 'rows': [], 'columns': (0,lambda x: [i if i < 4 else i-6 for i in binary_to_list(x)])}), # scroll attacks like khepri and azazel
100: convert('scroll_lock', {'duration': (1,cc), 'columns': [], 'rows': (0,lambda x: [i if i < 3 else i-5 for i in binary_to_list(x)])}),
101: lambda x: \
  convert('fixed_start', {})(x) \
  if defaultlist(int,x)[0] == 1 else \
  convert('fixed_start_position', {'positon_x': (1,position_x), 'position_y': (2,position_y)})(x), # subject to change, I don't understand the positions yet. 3 cases: Phoenix Wright 4,1->3rd from right,top; Lakshmi 6,1->right,top (7x6 too); Leeza 0,5->left,bottom (7x6 too)
102: orb_spawn({'damage': 0.0, 'amount': (1,cc), 'orbs': [9], 'exclude_orbs': [9]}), #unsure of bomb index, since it is never stated in game files (but it would be in the source code)
103: convert('bomb_pattern', {'pattern': (slice(1,6),pattern), 'locked': (7,bool)}),
104: lambda x: \
  convert('cloud_spawn', {'duration': (0,cc), 'width': (1,cc), 'height': (2,cc)})(x) \
  if defaultlist(int,x)[3:5] == [0,0] else \
  convert('cloud_spawn_position', {'duration': (0,cc), 'width': (1,cc), 'height': (2,cc), 'positon_x': (3,cc), 'position_y': (4,cc)})(x),
  # unsure of full behavior with 7x6, I think it acts like a pattern, duplicating column 4 and row 3, even after placement
105: convert('rcv_debuff', {'duration': (0,cc), 'multiplier': (1,multiplier)}), # not always debuff, eg 2x rcv
106: convert('passive_next_turn_change_threshold', {'threshold': (0,multiplier), 'turn': (1,cc)}), # change turn timer when hp reduced to xx%, then immediately take a turn
107: convert('unmatchable', {'duration': (0,cc), 'attributes': (1,binary_to_list)}), #eg. Enoch
108: convert('orb_convert_multiple', {'damage': (0,multiplier), 'from_attributes': (1,binary_to_list), 'to_attributes': (2,binary_to_list)}), #unsure if to_attributes forces 3 of each
109: convert('spinner_random', {'duration': (0,cc), 'speed': (1,multiplier), 'amount': (2,cc)}),
110: convert('spinner_pattern', {'duration': (0,cc), 'speed': (1,multiplier), 'pattern': (slice(2,7),pattern)}),
111: unimplimented(111),
112: convert('force_attack', {'duration': (0,cc)}), #eg. hexazeon shield
113: convert('_if_combo_above_jump', {}), # if the player reached {ai} or more combos last turn, jump to action {rnd}
114: unimplimented(114),
115: unimplimented(115),
116: unimplimented(116),
117: unimplimented(117),
118: convert('passive_type_reduction', {'types': (0,binary_to_list), 'reduction': (1,multiplier)}),
119: convert('null_damage_shield', {}), # satan void turn 1, gilles legato
120: convert('_if_enemy_remain_equals_jump', {}), # if {ai} enemies remain, jump to action {rnd}
121: convert('remove_null_damage_shield', {}), # applies to shields from both 119 and 123
122: convert('passive_next_turn_change_enemies', {'enemy_count': (0,cc), 'turn': (1,cc)}), # change turn timer when xx or less enemies remain, then immediately take a turn. eg. hexa, hexa yellow jewel, gilles legato
123: convert('null_damage_shield', {}), # hexa only, unsure if meaning is different
}



def _parse_enemy_skills(raw_json):
    print('[Enemy Skills] Starting to parse enemy skills')
    if raw_json['v'] > ENEMY_SKILL_TRANSFORM['version']:
        print(f"[Enemy Skills] The raw json is running a newer version than what's supported. ( {raw_json['v']} vs {ENEMY_SKILL_TRANSFORM['version']} )")
    if raw_json['res'] != 0:
        print('[Enemy Skills] The "res" property is not zero, the results might not be accurate')
    
    parsed_json = {}
    parsed_json['version'] = raw_json['v']
    parsed_json['enemy_skills'] = {}

    enemy_skills_csv = csv_decoder(raw_json['enemy_skills'])
    for raw_skill in enemy_skills_csv:
        if raw_skill[0] != 'c': # ckey
            parsed_skill = {}
            parsed_skill['id'] = int(raw_skill[0])
            if len(raw_skill[1]) > 1 and raw_skill[1][0] == raw_skill[1][-1] == "'":
                parsed_skill['text'] = raw_skill[1][1:-1]
            else:
                parsed_skill['text'] = raw_skill[1]
            parsed_skill['type'] = int(raw_skill[2])
            skill_arg_names = ['text_after', 'param_0', 'param_1', 'param_2', 'param_3',
                                             'param_4', 'param_5', 'param_6', 'param_7',
                               'ratio', 'ai_param_0', 'ai_param_1', 'ai_param_2', 'ai_param_3', 'ai_param_4']
            skill_arg_defaults = ['', 0, 0, 0, 0, 0, 0, 0, 0, 100, 100, 100, 10000, 0, 0]
            raw_skill_args_defined = hex_to_list(raw_skill[3])
            def arg_convert(arg):
                if type(arg) != int and len(arg) > 1 and arg[0] == arg[-1] == "'":
                    return arg[1:-1]
                else:
                    try:
                        return int(arg)
                    except:
                        return arg

            skill_args = {skill_arg_names[i]:(arg_convert(raw_skill[4 + raw_skill_args_defined.index(i)]) if i in raw_skill_args_defined else skill_arg_defaults[i]) for i in range(15)}
            parsed_skill['text_after'] = skill_args['text_after']
            parsed_skill['ratio'] = skill_args['ratio']
            parsed_skill['ai_param_0'] = int(skill_args['ai_param_0'])
            parsed_skill['hp_threshold'] = int(skill_args['ai_param_1'])/100 # if hp % >= hp_threshold % then ...
            parsed_skill['ai_param_2'] = int(skill_args['ai_param_2'])
            parsed_skill['ai_param_3'] = int(skill_args['ai_param_3'])
            parsed_skill['damage'] = int(skill_args['ai_param_4'])/100 # eventually check for damage in args and place here

            parameter_list = [skill_args['param_'+str(i)] for i in range(8)]
            if int(raw_skill[2]) in ENEMY_SKILL_TRANSFORM:
                parsed_skill['type'],parsed_skill['args'] = ENEMY_SKILL_TRANSFORM[int(raw_skill[2])](parameter_list)
            else:
                print(f'[Enemy Skills] Found unexpected enemy skill ( id: {i}, type:{raw_skill[2]} )')
                parsed_skill['type'] = 'unexpected'
                parsed_skill['args'] = {'type': raw_skill[2]}

            parsed_json['enemy_skills'][parsed_skill['id']] = parsed_skill
    print('[Enemy Skills] Enemy skill parsing complete')
    
    if _DEV:
        def verify(skills):
            type_verification = defaultdict(lambda: defaultdict(set))
            for i,skill in skills.items():
                type_verification[skill['type']]['_arg_names'].add(frozenset(skill['args'].keys()))
                for arg_name,arg_value in skill['args'].items():
                    type_verification[skill['type']][arg_name].add(type(arg_value))
            for skill_type,args in type_verification.items():
                for arg_name,arg_types in args.items():
                    if len(arg_types) != 1:
                        print(f'[Skills] INCONSISTENT name: {skill_type} difference in {repr(arg_name)}: {repr(arg_types)}\n[Skills] ')

        print('[Enemy Skills] Checking enemy skill consistency\n[Enemy Skills] -------start-------\n[Enemy Skills] ')
        verify(parsed_json['enemy_skills'])
        print('[Enemy Skills] --------end--------\n[Enemy Skills] ')

    return parsed_json


_parse_dungeons_version = 4
def _parse_dungeons(raw_json):
    print('[Dungeons] Starting to parse dungeons')
    if raw_json['v'] > _parse_dungeons_version:
        print(f"[Dungeons] The raw json is running a newer version than what's supported. ( {raw_json['v']} vs {_parse_dungeons_version} )")
    if raw_json['res'] != 0:
        print('[Dungeons] The "res" property is not zero, the results might not be accurate')
        
    parsed_json = {}
    try:
        parsed_json = {}
        parsed_json['version'] = raw_json['v']
        parsed_json['dungeons'] = []

        def dungeon_floor_parameters(parameter_string):
            parameters = parameter_string.split('|')
            result = {}

            if '7*6' in parameters:
                result['board'] = 'large'
            elif '5*4' in parameters:
                result['board'] = 'small'
            else:
                result['board'] = 'normal'

            result['skyfalls'] = 'ndf' not in parameters

            parameter_dict = {t[0]:t[1] for p in parameters for t in tuple(p.split(':')) if len(t)>1}

            result['fixed_move_time'] = parameter_dict['ft']/10 if 'ft' in parameter_dict else -1

            def raw_parameters_to_card(raw_parameters):
                parameter_names = ['id','level','plus_hp','plus_atk','plus_rcv','awakenings','skill_level']
                parameter_defaults = [0,99,0,0,0,99,99]
                card = {parameter_names[i]:(int(raw_parameters[i]) if len(raw_parameters) > i else parameter_defaults[i]) for i in range(len(parameter_names))}
                return card

            result['fixed_team'] = [raw_parameters_to_card(parameter_dict['fc'+i].split(';') if 'fc'+i in parameter_dict else []) for i in range(1,7)] if any('fc'+i in parameter_dict for i in range(1,7)) else []

            result['dungeon_messages'] = [parameter_dict['dmsg'+i] for i in range(1,5) if 'dmsg'+i in parameter_dict]
            result['small_messages'] = [parameter_dict['smsg'+i] for i in range(1,5) if 'smsg'+i in parameter_dict]

            def get_bonuses(data, name):
                bonuses = {}
                bonuses[name] = binary_to_list(int(data[0])) if len(data) > 0 else []
                bonuses['hp_multiplier'] = int(data[1]) if len(data) > 1 else 1.0
                bonuses['atk_multiplier'] = int(data[2]) if len(data) > 2 else 1.0
                bonuses['rcv_multiplier'] = int(data[3]) if len(data) > 3 else 1.0
                return bonuses

            result['type_bonus'] = get_bonuses(parameter_dict['btype'].split(';') if 'btype' in parameter_dict else [], 'types')            
            result['attribute_bonus'] = get_bonuses(parameter_dict['battr'].split(';') if 'battr' in parameter_dict else [], 'attributes')            
            result['rarity_bonus'] = get_bonuses(parameter_dict['btype'].split(';') if 'btype' in parameter_dict else [], 'rarities')

            # these arguments have an unknown purpose
            result['hp'] = parameter_dict['hp'] if 'hp' in parameter_dict else 0 # hp? enemy? team?
            result['at'] = parameter_dict['at'] if 'at' in parameter_dict else 0 # attack? enemy? team?
            result['df'] = parameter_dict['df'] if 'df' in parameter_dict else 0 # defense?
            result['dg'] = parameter_dict['dg'] if 'dg' in parameter_dict else 0 # damage? enemy? team?
            result['hpfix'] = parameter_dict['hpfix'] if 'hpfix' in parameter_dict else 0 # never seen this mechanic

            return result

        data = iter(csv_decoder(raw_json['dungeons']))
        curr = next(data)
        counters = {'floor_length': set(), 'floor_data': {k:{r:set() for r in range(k)} for k in [11, 12, 13, 14, 15, 16, 17, 18, 19]}}
        try:
            while True:
                if curr[0].startswith('d;'):
                    dungeon = {}
                    dungeon['id'] = curr[0][2:]
                    dungeon['name'] = curr[1]
                    dungeon['floors'] = []
                    dungeon['flags'] = binary_to_list(int(curr[2]))
                    dungeon['category'] = {7: '3_player', 5: 'coop',  4: 'ranking_dungeon', 3: 'gift_dungeon', 2: 'technical_dungeon', 1: 'special_dungeon', 0: 'normal_dungeon'}[int(curr[3])]
                    dungeon['weekday'] = {8: 'weekend', 5: 'friday', 4: 'thursday', 3: 'wednesday', 2: 'tuesday', 1: 'monday', 0: 'non_weekday'}[int(curr[4])]
                    dungeon['category_2'] = int(curr[5])

                    curr = next(data)
                    while curr[0].startswith('f;'):
                        floor = {}
                        floor['id'] = curr[0][2:]
                        floor['name'] = curr[1]
                        floor['floor_count'] = curr[4]
                        floor['stamina_cost'] = curr[4]
                        floor['unknown_data'] = {k:curr[k] for k in {2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19} if k < len(curr)}
                        dungeon['floors'].append(floor)
                        counters['floor_length'].add(len(curr))
                        for i in range(len(curr)):
                            if i not in {0,1}:
                                counters['floor_data'][len(curr)][i].add(curr[i])
                        curr = next(data)

                    parsed_json['dungeons'].append(dungeon)

                elif curr[0].startswith('c;'):
                    pass # ckey

                else:
                    print(f'[Dungeons] Something went wrong while reading a line of dungeon data, skipping')
                    curr = next(data)
        except StopIteration:
            pass
        print('[Dungeons] Dungeon parsing complete')
    except Exception as e:
        print('[Dungeons] A CRITICAL ERROR OCCURED, SAVING SUCCESSFUL DATA')
        if _DEV:
            print(e)
    return parsed_json

# TODO remove
card_bitmaps = {"9": defaultdict(lambda: set()),
                "51": defaultdict(lambda: set()),
                "52": defaultdict(lambda: set()),
                "53": defaultdict(lambda: set()),
                "54": defaultdict(lambda: set()),
                "55": defaultdict(lambda: set()),
                "56": defaultdict(lambda: set()),}
pretty_card_bitmap = {}
# TODO remove
_parse_cards_version = 1250
def _parse_cards(raw_json):
    print('[Cards] Starting to parse cards')
    if raw_json['v'] > _parse_cards_version:
        print(f"[Cards] The raw json is running a newer version than what's supported. ( {raw_json['v']} vs {_parse_cards_version} )")
    if raw_json['res'] != 0:
        print('[Cards] The "res" property is not zero, the results might not be accurate')
    
    parsed_json = {}
    parsed_json['version'] = raw_json['v']
    parsed_json['cards'] = {}
    parsed_json['enemies'] = {}
    parsed_json['evolutions'] = defaultdict(list)
    for raw_card in raw_json['card']:
        parsed_card = {}
        parsed_card['id'] = raw_card[0]
        parsed_card['name'] = raw_card[1]
        parsed_card['attribute'] = raw_card[2]
        parsed_card['subattribute'] = raw_card[3]
        parsed_card['types'] = [raw_card[t] for t in [5,6] if raw_card[t] != -1] # add type 3 later
        parsed_card['rarity'] = raw_card[7]
        parsed_card['cost'] = raw_card[8]
        # 9, unsure of purpose
        parsed_card['max_level'] = raw_card[10]
        parsed_card['feed_experience'] = raw_card[11] / 4 # per level
        parsed_card['released'] = raw_card[12] == 100
        parsed_card['sell_value_coin'] = raw_card[13] / 10 # per level
        parsed_card['hp_minimum'] = raw_card[14]
        parsed_card['hp_maximum'] = raw_card[15]
        parsed_card['hp_curve'] = raw_card[16]
        parsed_card['atk_minimum'] = raw_card[17]
        parsed_card['atk_maximum'] = raw_card[18]
        parsed_card['atk_curve'] = raw_card[19]
        parsed_card['rcv_minimum'] = raw_card[20]
        parsed_card['rcv_maximum'] = raw_card[21]
        parsed_card['rcv_curve'] = raw_card[22]
        parsed_card['max_experience'] = raw_card[23]
        parsed_card['experience_curve'] = raw_card[24]
        parsed_card['active_skill_id'] = raw_card[25]
        parsed_card['leader_skill_id'] = raw_card[26]
        
        parsed_enemy = {}
        parsed_enemy['id'] = parsed_card['id']
        parsed_enemy['turn_timer_normal'] = raw_card[27]
        parsed_enemy['hp_at_lv_1'] = raw_card[28]
        parsed_enemy['hp_at_lv_10'] = raw_card[29]
        parsed_enemy['hp_curve'] = raw_card[30]
        parsed_enemy['atk_at_lv_1'] = raw_card[31]
        parsed_enemy['atk_at_lv_10'] = raw_card[32]
        parsed_enemy['atk_curve'] = raw_card[33]
        parsed_enemy['def_at_lv_1'] = raw_card[34]
        parsed_enemy['def_at_lv_10'] = raw_card[35]
        parsed_enemy['def_curve'] = raw_card[36]
        parsed_enemy['max_level'] = raw_card[37]
        parsed_enemy['coins_at_lv_2'] = raw_card[38]
        parsed_enemy['experience_at_lv_2'] = raw_card[39]
        if raw_card[40] != 0:
            evo = {}
            evo['base'] = raw_card[40]
            evo['materials'] = [raw_card[t] for t in range(41,46) if raw_card[t] != 0]
            evo['is_ultimate'] = raw_card[4] == 1
            evo['result'] = parsed_card['id']
            evo['devo_materials'] = [raw_card[t] for t in range(46,51) if raw_card[t] != 0] # mats to devolve
            parsed_json['evolutions'][evo['base']].append(evo)
        parsed_enemy['turn_timer_technical'] = raw_card[51]
        # bitmaps 52 - 56
        # TODO remove
        card_bitmaps["9"][str(raw_card[9])].add(parsed_card['id'])
        for i in range(52,57):
            if raw_card[i] != 0: card_bitmaps[str(i)][str(raw_card[i])].add(parsed_card['id'])
        # TODO remove
        enemy_skill_count = raw_card[57]
        parsed_enemy['skills'] = []
        for i in range(enemy_skill_count):
            enemy_skill = {}
            enemy_skill['enemy_skill_id'] = raw_card[58 + 3 * i]
            enemy_skill['ai'] = raw_card[59 + 3 * i]
            enemy_skill['rnd'] = raw_card[60 + 3 * i]
            parsed_enemy['skills'].append(enemy_skill)
        index_shift_1 = 58 + 3 * enemy_skill_count
        awakening_count = raw_card[index_shift_1]
        parsed_card['awakenings'] = [raw_card[a + index_shift_1 + 1] for a in range(awakening_count)]
        index_shift_2 = index_shift_1 + awakening_count + 1
        parsed_card['superawakenings'] = [int(a) for a in raw_card[index_shift_2].split(',') if a != '']
        parsed_card['base_evo_id'] = raw_card[index_shift_2 + 1]
        parsed_card['group'] = raw_card[index_shift_2 + 2]
        parsed_card['types'].extend([raw_card[index_shift_2 + 3]] if -1 != -1 else []) # add type 3
        parsed_card['sell_value_mp'] = raw_card[index_shift_2 + 4]
        parsed_card['latent_on_fuse'] = raw_card[index_shift_2 + 5] # which latent awakening is granted upon fusing this card away
        parsed_card['collab'] = raw_card[index_shift_2 + 6] # collab id, also includes dbdc as a special collab id
        parsed_card['inheritable'] = raw_card[index_shift_2 + 7] == 3
        parsed_card['furigana'] = raw_card[index_shift_2 + 8]
        parsed_card['limitbreakable'] = raw_card[index_shift_2 + 9] > 0
        parsed_card['limitbreak_stat_increase'] = raw_card[index_shift_2 + 9] / 100 # percentage increase
        parsed_json['cards'][parsed_card['id']] = parsed_card
        parsed_json['enemies'][parsed_enemy['id']] = parsed_enemy
    print('[Cards] Card parsing complete')
    # TODO remove
    pretty_card_bitmap = {b:{m:list(i) for m,i in v.items()} for b,v in card_bitmaps.items()}
    # TODO remove
    return parsed_json
                
                
                
        
def _parse_exchange(raw_json):
    return raw_json


# keys are keys that uniquely identify the json file type
# values are funtions that handle the file
_parse_names = {'card': _parse_cards,
               'skill': _parse_skills,
               'dungeons': _parse_dungeons,
               'enemy_skills': _parse_enemy_skills,
               'd': _parse_exchange}

def parse(input_path: str, output_path: str, pretty_print=False):
    print()
    input_file = None
    try:
        print(f'Opening input file ( {input_path} )')
        input_file = open(input_path, 'r')
        try:
            print('Reading json')
            input_json = json.load(input_file)
            
            print('Determining the contents of the json')
            if 'res' not in input_json.keys():
                print('The json does not have a "res" property. Please ensure this is a raw data file')
            elif 'v' not in input_json.keys():
                print('The json does not have a "v" property. Please ensure this is a raw data file')
            else:
                json_parser = [(k,v) for k,v in _parse_names.items() if k in input_json.keys()]
                if len(json_parser) == 0:
                    print('The json does not have a supported parsing method for this file')
                elif len(json_parser) > 1:
                    print('More than one parsing method applied to json, it will be skipped')
                else:
                    output_json = None
                    exception = None
                    try:
                        output_json = json_parser[0][1](input_json)
                    except Exception as e:
                        exception = e
                        print(f'The parsing method threw an exception ( {e} )')
                    finally:
                        if output_json == None:
                            print('The json failed to parse, nothing will be saved')
                        else:
                            print(f'Saving results ( {output_path} )')
                            try:
                                output_file = open(output_path, 'w')
                                if pretty_print:
                                    output_file.write(json.dumps(output_json, indent=4, sort_keys=True))
                                else:
                                    output_file.write(json.dumps(output_json, sort_keys=True))
                                output_file.close()
                                print('Results saved')
                            except:
                                print('The file failed to save')
                        if exception != None:
                            raise exception
        except IOError:
            print('The input file does not contain a valid json file')
    except IOError:
        print('The input file could not be opened, it will be skipped')
    finally:
        if input_file != None:
            input_file.close()




if __name__ == '__main__':
    _DEV = True
    parse('raw/na/download_card_data.json', 'parsed/na/cards.json', True)
    parse('raw/na/download_skill_data.json', 'parsed/na/skills.json', True)
    parse('raw/na/download_dungeon_data.json', 'parsed/na/dungeons.json', True)
    parse('raw/na/download_enemy_skill_data.json', 'parsed/na/enemy_skills.json', True)
    parse('raw/na/mdatadl.json', 'parsed/na/exchange.json', True)
##    import sys
##    args = sys.argv[1:]
##    pretty_option = False
##    if len(args) == 0:
##        print(_INFO)
##    else:
##        if len(args) >= 2 and args[0] == '-p':
##            pretty_option = True
##            args = args[1:]
##        if len(args) == 2:
##            tparse(args[0], args[1], pretty_print=pretty_option)
##        else:
##            print(_INFO)
