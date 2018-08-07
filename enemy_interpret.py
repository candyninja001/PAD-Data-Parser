import json
from collections import namedtuple, defaultdict

enemy_skill_path = 'reformatted/enemy_skills_new.json'
enemy_skill_data = json.load(open(enemy_skill_path))
esd = enemy_skill_data

card_path = 'reformatted/cards.json'
card_data = json.load(open(card_path))
cd = card_data


ESkill = namedtuple('ESkill', 'mode icons text damage description extra')
SkillSet = namedtuple('SkillSet', 'mode eskills')

# ordered as minimum damage, maximum damage
no_damage = [0.0, 0.0]

FALLBACK_ESKILL = ESkill('Unexpected', [], 'Error', no_damage, 'Skill not found', {})

attrs = {0: 'Fire',
         1: 'Water',
         2: 'Wood',
         3: 'Light',
         4: 'Dark',
         5: 'Heal',
         6: 'Jammer',
         7: 'Poison',
         8: 'Mortal Poison',
         9: 'Bomb'}

types = {0: 'Evo Material',
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

list_it = lambda l: ', '.join(l[:-1])+' and '+l[-1] if len(l) > 1 else ('' if len(l) == 0 else l[0])
int_comma = lambda i: f'{i:n}'
attrs_con = lambda a: [attrs[attr] for attr in a]
attrs_str = lambda a: list_it(attrs_con(a))
attrs_icons = lambda aa: [attrs[a].lower().split()[0] for a in aa]
attrs_icons_prefix = lambda pre,aa: [pre + attrs[a].lower().split()[0] for a in aa]
types_con = lambda t: [types[tt] for tt in t]
types_str = lambda t: list_it(types_con(t))
types_icons = lambda tt: [types[t].lower().split()[0] for t in tt]
types_icons_prefix = lambda pre,tt: [pre + types[t].lower().split()[0] for t in tt]
or_less = lambda l: f'{l} or less' if l > 1 else str(l)
turns = lambda t: f"{t} {plural(t, 'turn', 'turns')}"
turns_minmax = lambda mi, ma: f"{to(mi, ma)} {plural(ma, 'turn', 'turns')}"
to = lambda a, b: f'{a} to {b}' if a != b else str(a)
and_hit_for = lambda d: f' and hit for '
plural = lambda x, single, multiple: multiple if x > 1 else single
percent = lambda p: f'{round(p*100)}%'
pattern_board_simulation = lambda p: {'6x5': '\n'.join(''.join('●' if x == 1 else '○' for x in row) for row in p), '7x6': '\n'.join(''.join('●' if p[y][x] == 1 else '○' for x in [0,1,2,3,3,4,5]) for y in [0,1,2,2,3,4])}
cloud_board_simulation = lambda w,h,x,y: {'6x5': '\n'.join(''.join('●' if (x - 1 < xx < x + w and y - 1 < yy < y + h) else '○' for xx in range(1,7)) for yy in range(1,6)), '7x6': '\n'.join(''.join('●' if ((w == 6 or x - 1 < xx < x + w) and (h == 5 or y - 1 < yy < y + h)) else '○' for xx in range(1,8)) for yy in range(1,7))}
bind_targets_2 = lambda slots, count: (('all cards' if count >= 6 else f'{count} cards') if 0 in slots and 5 in slots else ('all subs' if count >= 4 else f'{count} subs')) if all(i in slots for i in {1,2,3,4}) else (('both leaders' if count >= 2 else '1 leader') if 0 in slots and 5 in slots else ('your leader' if 0 in slots else 'friend leader'))
bind_targets = lambda attrs, types, slots, count: (f'{types_str(types)} attribute cards' if count >= 6 else f'{count} {types_str(types)} attribute cards') if attrs != [] else ((f'{types_str(types)} type cards' if count >= 6 else f'{count} {types_str(types)} type cards') if types != [] else (bind_targets_2(slots, count)))
column_text = lambda col: {0: 'the leftmost column', 1: 'the second column from the left', 2: 'the third column from the left', -3: 'the third column from the right', -2: 'the second column from the right', -1: 'the rightmost column'}[col]
row_text = lambda col: {0: 'the topmost row', 1: 'the second row from the top', -3: 'the third row from the bottom', -2: 'the second row from the bottom', -1:'the bottommost row'}[col]

def columns_list(column_list):
    cols = defaultdict(set)
    for col in column_list:
        cols[frozenset(col['orbs'])].add(col['index'])
    cols = sorted((tuple(sorted(v, key=lambda x: x if x >= 0 else x + 10)), sorted(k)) for k,v in rows.items())
    return list_it([f'{list_it([column_text(i) for i in c])} to {attrs_str(o)} orbs' for c,o in cols])

def rows_list(row_list):
    rows = defaultdict(set)
    for row in row_list:
        rows[frozenset(row['orbs'])].add(row['index'])
    rows = sorted((tuple(sorted(v, key=lambda x: x if x >= 0 else x + 10)), sorted(k)) for k,v in rows.items())
    return list_it([f'{list_it([row_text(i) for i in r])} to {attrs_str(o)} orbs' for r,o in rows])


def get_skill(skill_id):
    ss = esd['skills'][str(skill_id)]
    if ss['type'] not in ENEMY_SKILL_INTERPRET:
        return FALLBACK_ESKILL
    return ENEMY_SKILL_INTERPRET[ss['type']](ss['text'], **ss['args'])

def re_mode(mode, skill_id):
    inter = get_skill(skill_id)
    if type(inter) == ESkill:
        return ESkill(mode, inter.icons, inter.text, inter.description)
    if type(inter) == SkillSet:
        return SkillSet(mode, inter.eskills)

ENEMY_SKILL_INTERPRET = {

'absorb_attribute': lambda text, **args: ESkill('', attrs_icons_prefix('absorb_',args['attributes']), text, no_damage,
    f"For {turns_minmax(args['minimum_duration'], args['maximum_duration'])}, absorb {attrs_str(args['attributes'])} attribute damage", {}),

'absorb_combo': lambda text, **args: ESkill('', ['absorb_combo_'], text, no_damage,
    f"For {turns_minmax(args['minimum_duration'], args['maximum_duration'])}, absorb damage from {args['combo_count']} combos or less", {}),

'absorb_damage': lambda text, **args: ESkill('', ['absorb_damage'], text, no_damage,
    f"For {turns(args['duration'])}, absorb damage of {int_comma(args['amount'])} or more", {}),

'attack_boost': lambda text, **args: ESkill('', [], text, no_damage,
    f"Look into, attack boost", {}),

'awoken_bind': lambda text, **args: ESkill('', ['awoken_bind'], text, no_damage,
    f"For {turns(args['duration'])}, awoken skills are invalid", {}),

'board_change': lambda text, **args: ESkill('', ['board', 'to'] + attrs_icons(args['attributes']), text, [args['damage'],args['damage']],
    f"Changes the board to {attrs_str(args['attributes'])} orbs", {}),

'bomb_pattern': lambda text, **args: ESkill('', ['bomb'], text, no_damage,
    f"Spawn {'Locked Bomb' if args['locked'] else 'Bomb'} orbs at certain positions", pattern_board_simulation(args['pattern'])),

'card_bind': lambda text, **args: ESkill('', ['bind'], text, [args['damage'],args['damage']],
    f"Bind {bind_targets(args['attributes'], args['types'], args['slots'], args['card_count'])} for count turns", {}),

'change_skyfall': lambda text, **args: ESkill('', attrs_icons_prefix('skyfall_',args['orbs']), text, no_damage,
    f"For {turns(args['duration'])}, {attrs_str(args['attributes'])} orbs have a{' ' if args['percentage'] else ' extra '}{percent(args['percentage'])} chance to skyfall", {}),

'cloud_spawn': lambda text, **args: ESkill('', ['cloud'], text, no_damage,
    f"For {turns(args['duration'])}, a {args['width']}x{args['height']} cloud appears on the board", {}),

'cloud_spawn_position': lambda text, **args: ESkill('', ['cloud'], text, no_damage,
    f"For {turns(args['duration'])}, a {args['width']}x{args['height']} cloud appears on the board at a predetermined location", cloud_board_simulation(args['width'],args['height'],args['position_x'],args['position_y'])),

'column_change': lambda text, **args: ESkill('', ['column'], text, no_damage,
    f"Change {columns_list(args['columns'])}", {}),

'combine_enemy_skills': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'damage_shield': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'dispel': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'element_change': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'enemy_heal': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'fixed_start': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'fixed_start_position': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'force_attack': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'gravity': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'leader_swap': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'lock_orbs': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'lock_skyfall': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'multi_attack': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'next_attack_boost': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'normal_attack': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'normal_blind': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'null_damage_shield': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'null_skill': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'orb_convert': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'orb_convert_multiple': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'orb_convert_random': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'passive_attribute_reduction': lambda text, **args: ESkill('Passive', attrs_icons_prefix('resist_',args['attributes']), text, no_damage,
    f"Reduce {attrs_str(args['attributes'])} attribute damage by {percent(args['reduction'])}", {}),

'passive_next_turn_change_enemies': lambda text, **args: ESkill('Passive', ['clock'], text, no_damage,
    f"When {or_less(args['enemy_count'])} {plural(args['enemy_count'], 'enemy', 'enemies')} remain, this enemy's turn changes to {args['turn']}", {}),

'passive_next_turn_change_threshold': lambda text, **args: ESkill('Passive', ['clock'], text, no_damage,
    f"When enemy HP is <{percent(args['threshold'])}, this enemy's turn changes to {args['turn']}", {}),

'passive_on_death': lambda text, **args: re_mode('On death', args['skill_id']),

'passive_resolve': lambda text, **args: ESkill('Passive', ['resolve'], text, no_damage,
    f"When enemy HP is >{percent(args['threshold'])}, a hit that would normally kills the enemy leaves it with 1 HP", {}),

'passive_type_reduction': lambda text, **args: ESkill('Passive', types_icons_prefix('resist_',args['types']), text, no_damage,
    f"Reduce {types_str(args['types'])} type damage by {percent(args['reduction'])}", {}),

'player_heal': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'rcv_debuff': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'remove_null_damage_shield': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'revive': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'row_change': lambda text, **args: ESkill('', ['row'], text, no_damage,
    f"Change {rows_list(args['rows'])}", {}),

'scroll_lock': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'skill_bind': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'skill_delay': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'skip': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'spawn_orbs': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'spinner_pattern': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'spinner_random': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'status_shield': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'suicide': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'super_blind': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'super_blind_pattern': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'time_debuff': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'transformation': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'unimplimented': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'unmatchable': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

'void_damage': lambda text, **args: ESkill('', [], text, no_damage,
    f"", {}),

}

def make(monster_id):
    if str(monster_id) not in cd['enemies']:
        return ''
    result = f'Enemy: [{monster_id}] {cd["cards"][str(monster_id)]["name"]}\n\n'
    skills = cd['enemies'][str(monster_id)]['skills']
    for s in skills:
        s.update(esd['skills'][str(s['enemy_skill_id'])])
    for passive in [s for s in skills if s['type'].startswith('passive')]:
        inter = get_skill(passive['enemy_skill_id'])
        result += f"{'['+inter.mode+'] ' if inter.mode else ''}{inter.text} : {inter.description}\n"
    for skill in [s for s in skills if s['type'] in ENEMY_SKILL_INTERPRET]:
        inter = get_skill(skill['enemy_skill_id'])
        result += f"{'['+inter.mode+'] ' if inter.mode else ''}{inter.text} : {inter.description}\n"
    return result

def m(m_id):
    print(make(m_id))

def onetime():
    for k in sorted({l['type'] for l in esd['skills'].values()}):
        print(f"'{k}': lambda text, **args: ESkill('', [], text,\n    f\"\"),\n")
