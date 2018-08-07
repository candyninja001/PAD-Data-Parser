import json
import sys

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
        
def jprint(j):
    uprint(json.dumps(j, indent=4, sort_keys=True))

card_data = json.load(open('padEN/download_card_data.json'))
# uprint(json.dumps(card_data, indent=4, sort_keys=True))
# uprint(card_data)
for c in range(3262, 3266):
    pass
#     jprint(card_data['card'][c])
    

class Monster:
    def __init__(self, values):
        self.id = values[0]
        self.name = values[1]
        self.attribute = values[2]
        self.sub_attribute = values[3] if values[3] != -1 else None
        self.is_ult = bool(values[4])
        self.type1 = values[5]
        self.type2 = values[6]
        self.rarity = values[7]
        self.team_cost = values[8]
#         self.? = values[9]
        self.max_level = values[10] # is still 99 for limitbreakable
        self.feed_exp = values[11]
#         self.? = values[12]
#         self.? = values[13] something to do with feed exp
        self.min_hp = values[14]
        self.min_hp = values[15]
        self.hp_scale = values[16]
        self.min_atk = values[17]
        self.min_atk = values[18]
        self.atk_scale = values[19]
        self.min_rcv = values[20]
        self.min_rcv = values[21]
        self.rcv_scale = values[22]
        self.xp_curve = values[23]
#         Evolution: base, mats[1-5] values[40-45] followd by devo mats [46-50]
#         values [46-50] are the ids of the devo-lits
#         if 51-57 are 0, 58 is how many awakenings there are
#         meaning 59-xx are awakenings
#         the very next index is ""
#         after this index is the id of the base evo
#         next???
#         next is type3
        
        
def print_all(*args):
    iters = [iter(it) for it in args]
    count = 0
    while any(it != None for it in iters):
        print(end=f'{count:3}: ')
        for i in range(len(iters)):
            next_value = None
            if iters[i] != None:
                try:
                    next_value = next(iters[i])
                except StopIteration:
                    iters[i] = None
            if type(next_value) == str:
                try:
                    uprint(end='{v:<10} '.format(v=f'"{next_value:<.8}"'))
                except:
                    uprint(end='"str_error ')
            elif type(next_value) in {int, float}:
                print(end=f'{next_value:<10} ')
            elif next_value == None:
                print(end=' '*11)
            else:
                print(end='error      ')
        print()
        count += 1
        
def get_monsters(*indexes):
    return [card_data['card'][index] for index in indexes]

print_all(*get_monsters(3949, 3947))
