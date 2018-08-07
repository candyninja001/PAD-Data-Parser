from collections import defaultdict

ATTRIBUTES = {'r','g','b','l','d','h','j','p','m','x','u'}

pool = ['r','l']

add = lambda a,b: a or b
mask_blank = lambda f,w,h: [[f() for _ in range(h)] for _ in range(w)]
mask_mod = lambda a,b,f: [[f(a[x][y],b[x][y]) for y in range(len(a[0]))] for x in range(len(a))]
board_sort_key = lambda x: x == None

class Board:
    def __init__(self, string=''):
        self.width  = 7
        self.height = 6
        self._string = string.lower()
        self._board = mask_blank(lambda: None, self.width, self.height)
        self._mask = mask_blank(lambda: False, self.width, self.height)
        i = iter(string)
        for y in range(self.height-1, -1, -1):
            for x in range(self.width):
                self._board[x][y] = next(i)

    def __str__(self):
        return '\n'.join(''.join(self._board[x][y].upper() for x in range(self.width)) for y in range(self.height-1, -1, -1))

    def __repr__(self):
        return f'Board({repr(self._string)})'

    def export(self):
        return f'https://candyninja001.github.io/Puzzled/?patt={self._string}'

    def _mask_at(self, x, y, d_x, d_y):
        if x < 0 or x >= self.width:
            return
        if x + 2 * d_x < 0 or x + 2 * d_x >= self.width:
            return
        if x < 0 or y >= self.width:
            return
        if y + 2 * d_y < 0 or y + 2 * d_y >= self.height:
            return
        if self._board[x][y] != None and self._board[x][y] == self._board[x+d_x][y+d_y] == self._board[x+2*d_x][y+2*d_y]:
            self._mask[x][y] = True
            self._mask[x+d_x][y+d_y] = True
            self._mask[x+2*d_x][y+2*d_y] = True
    
    def _full_mask(self):
        self._mask = mask_blank(lambda: False, self.width, self.height)
        for x in range(self.width):
            for y in range(self.height):
                self._mask_at(x,y,0,1)
                self._mask_at(x,y,1,0)

    def _nearest_neighbors(self, x, y, c):
        result = set()
        for (xx,yy) in {(x,y+1),(x+1,y),(x,y-1),(x-1,y)}:
            if 0 <= xx < self.width and 0 <= yy < self.height:
                if type(self._mask[xx][yy]) == int and self._board[xx][yy] == c:
                    result.add(self._mask[xx][yy])
        return result

    def _merge(self, a, b):
        for x in range(self.width):
            for y in range(self.height):
                if type(self._mask[x][y]) == int and self._mask[x][y] == b:
                    self._mask[x][y] = a

    def _merge_all(self, s):
        s = list(s)
        for n in range(len(s)-1):
            self._merge(s[-1],n)

    def _matches(self):
        matches = defaultdict(lambda: mask_blank(lambda: False, self.width, self.height))
        flag = True
        while flag:
            self._full_mask()
            flag = False
            c_count = 0
            for x in range(self.width):
                for y in range(self.height):
                    if type(self._mask[x][y]) == bool and self._mask[x][y] == True:
                        flag = True
                        nn = list(self._nearest_neighbors(x,y,self._board[x][y]))
                        if len(nn) == 0:
                            c_count += 1
                            self._mask[x][y] = c_count
                        elif len(nn) == 1:
                            self._mask[x][y] = nn[0]
                        else:
                            self._merge_all(nn)
                            self._mask[x][y] = nn[-1]

            for x in range(self.width):
                for y in range(self.height):
                    if type(self._mask[x][y]) == int:
                        matches[self._mask[x][y]][x][y] = self._board[x][y]
                        self._board[x][y] = None
                        
            for x in range(self.width):
                self._board[x].sort(key=board_sort_key)
        return matches

    def get_matches(self):
        return [Match(m, self.width, self.height) for m in self._matches().values()]

class Match:
    def __init__(self, data, width, height):
        self.attr = ''
        self.size = 0
        self.pattern = [['x','x','x']]
        self.tags = set()
        self._w_range = []
        self._h_range = []
        self.dim = (1,3)
        for x in range(width):
            if any(data[x][y] != 'u' for y in range(height)):
                self._w_range.append(x)
                continue
        for y in range(height):
            if any(data[x][y] != 'u' for x in range(width)):
                self._h_range.append(y)
                continue
        self.pattern = [[data[x][y] if data[x][y] != 'u' else None for y in self._h_range] for x in self._w_range]
        self.dim = (len(self._w_range), len(self._h_range))
        for a in self.pattern:
            for b in a:
                if b != None:
                    if self.attr == '':
                        self.attr = b
                    self.size += 1
        #tagging
        if self.attr in {'r','g','b','l','d'}:
            if self.size == 4:
                self.tags.add('tpa')
            if self.size == 9 and self.dim[0] == 3 and self.dim[1] == 3:
                self.tags.add('vdp')
            if self.dim[0] == width and any(all(self.pattern[x][y] != None for x in range(self.dim[0])) for y in range(self.dim[1])):
                self.tags.add('row')
        elif self.attr == 'h':
            if self.size == 4:
                self.tags.add('htpa')
            if self.size == 9 and self.dim[0] == 3 and self.dim[1] == 3:
                self.tags.add('sfua')
            if self.dim[0] == 1 and self.dim[1] == height:
                self.tags.add('fua')
            if self.dim[0] == width and any(all(self.pattern[x][y] != None for x in range(self.dim[0])) for y in range(self.dim[1])):
                self.tags.add('bindclear')
        if self.size >= 5:
            self.tags.add('mass')
        if self.size == 5 and self.dim[0] == 3 and self.dim[1] == 3 and self.pattern[1][1] == None:
            self.tags.add('L')
        if self.size == 5 and self.dim[0] == 3 and self.dim[1] == 3 and all(self.pattern[d[0]][d[1]] == None for d in {(0,0), (0,2), (2,0), (2,2)}):
            self.tags.add('cross')
            

    def __str__(self):
        return '\n'.join(''.join(self.pattern[x][y].upper() if self.pattern[x][y] != None else ' ' for x in range(len(self._w_range))) for y in range(len(self._h_range)-1,-1,-1))
                
        
import itertools
import time
import random

has_vdp = lambda b: any(all(b[x+xx+7*(y+yy)] == 'r' for yy in range(3) for xx in range(3)) and \
                        all(True if y == 0 else b[x+xx+7*(y-1)] for xx in range(3)) and \
                        all(True if y == 3 else b[x+xx+7*(y+3)] for xx in range(3)) and \
                        all(True if x == 0 else b[x-1+7*(y+yy)] for yy in range(3)) and \
                        all(True if x == 4 else b[x+3+7*(y+yy)] for yy in range(3)) \
                        for y in range(4) for x in range(5))
vdp = lambda b: 9 <= b._string.count('r') <= 33 and has_vdp(b._string)

def optimal_boards(p):
    start = time.time()
    try:
        combo_counts = {}
        count = 0
        for board_string in itertools.product('rl', repeat=42):
            count += 1
            board_string = ''.join(board_string)
            if count % 50000 == 0:
                print(board_string)
                print(count)
                print(time.time() - start)
            board = Board(board_string)
            if p(Board(board._string)):
                index = board_string.count('r')
                cc = board.get_matches()
                if index not in combo_counts:
                    combo_counts[index] = (len(cc),board_string)
                if len(cc) > combo_counts[index][0]:
                    combo_counts[index] = (len(cc),board_string)

        return combo_counts
    except:
        print(board_string)
        print(count)
        raise
    finally:
        end = time.time()
        print(end - start)

def giff(x):
    s = ['r' for _ in range(x)]
    s.extend(['l' for _ in range(42-x)])
    random.shuffle(s)
    return ''.join(s)
                                       
