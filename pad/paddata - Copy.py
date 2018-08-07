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

card_data = json.load(open('padEN/download_skill_data.json'))
# uprint(json.dumps(card_data, indent=4, sort_keys=True))
# uprint(card_data)

skill_list = {}
for i,c in enumerate(card_data['skill']):
    skill_list[i] = {}
    skill_list[i]['id'] = i
    skill_list[i]['name'] = c[0]
    skill_list[i]['desc'] = c[1]
    skill_list[i]['type'] = c[2]
    skill_list[i]['max_skill'] = c[3]
    skill_list[i]['base_cooldown'] = c[4]
    skill_list[i]['un'] = c[5]
    skill_list[i]['args'] = c[6:]

def r(p):
    find = [s for s in skill_list.values() if p(s)]
    pprint(find)

#print(find)

def pprint(t):
    print('\n--------Start-------')
    for l in t:
        print(f'--------------------\n{l["id"]:5} {l["name"]}\n      {l["desc"]}\n      {l["args"]}')
    print('\n---------End--------\n')

#r(lambda s: s['type'] == 124 and any(x not in {0,1,2,4,8,16,32} for x in s['args'][:5]))
r(lambda s: s['type'] == 176)
#r(lambda s: s['type'] == 130)
r(lambda s: any(x in s['args'] for x in {8333,8334,8394,8395}))
