ATTRIBUTES = {'r','g','b','l','d','h','j','p','m','x','u'}

pool = ['r','l']

add = lambda a,b: a or b
mask_mod = lambda a,b,f: [[f(a[x][y],b[x][y]) for y in range(len(a[0]))] for x in range(len(a))]
board_sort_key = lambda x: x == 'u'

class Board:
    def __init__(self, string=''):
        self.width  = 6
        self.height = 5
        self._board = \
        [['u','u','u','u','u'], # column 1 (bottom to top)
         ['u','u','u','u','u'], # column 2
         ['u','u','u','u','u'], # column 3
         ['u','u','u','u','u'], # column 4
         ['u','u','u','u','u'], # column 5
         ['u','u','u','u','u'],]# column 6
        if len(string) in {20,30,42}:
            self.set(string)

    def set(self, string):
        string = string.lower()
        if len(string) == 20:
            self.width  = 5
            self.height = 4
            self._board = self._blank_mask(lambda: 'u')
        if len(string) == 30:
            self.width  = 6
            self.height = 5
            self._board = self._blank_mask(lambda: 'u')
        if len(string) == 42:
            self.width  = 7
            self.height = 6
            self._board = self._blank_mask(lambda: 'u')
        i = iter(string)
        for y in range(self.height-1, -1, -1):
            for x in range(self.width):
                self._board[x][y] = next(i)

    def __str__(self):
        return '\n'.join(''.join(self._board[x][y].upper() for x in range(self.width)) for y in range(self.height-1, -1, -1))

    def __repr__(self):
        return f'Board({repr(self._string())})'

    def export(self):
        return f'https://candyninja001.github.io/Puzzled/?patt={self._string().lower()}'
        
    def _string(self):
        return ''.join(''.join(self._board[x][y] for x in range(self.width)) for y in range(self.height-1, -1, -1))
    
    def combo_count(self, p):
        return 0

    def attr_count(self):
        attrs = {a:0 for a in ATTRIBUTES}
        for y in range(len(self._board)):
            for x in range(len(self._board[0])):
                attrs[self._board[y][x]] += 1
        return attrs

    def _blank_mask(self, val):
        return [[val() for y in range(self.height)] for x in range(self.width)]

    def _match_at(self, x, y, d_x, d_y):
        m = self._blank_mask(lambda: False)
        if x < 0 or x >= self.width:
            return m
        if x + 2 * d_x < 0 or x + 2 * d_x >= self.width:
            return m
        if x < 0 or y >= self.width:
            return m
        if y + 2 * d_y < 0 or y + 2 * d_y >= self.height:
            return m
        if self._board[x][y] != 'u' and self._board[x][y] == self._board[x+d_x][y+d_y] == self._board[x+2*d_x][y+2*d_y]:
            m[x][y] = True
            m[x+d_x][y+d_y] = True
            m[x+2*d_x][y+2*d_y] = True
        return m
    
    def _match_mask(self):
        m = self._blank_mask(lambda: False)
        for x in range(self.width):
            for y in range(self.height):
                m = mask_mod(m, self._match_at(x,y,1,0), add)
                m = mask_mod(m, self._match_at(x,y,0,1), add)
        return m

#rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrlrrrlrrr
    def _matches(self, minimum=3):
        matches = []
        c = Board(self._string())
        while True:
            flag = True
            while flag:
                match_mask = c._match_mask()
                flag = False
                for x in range(c.width):
                    for y in range(c.height):
                        if match_mask[x][y]:
                            flag = True
                            match = c._blank_mask(lambda: 'u')
                            match[x][y] = c._board[x][y]
                            while True:
                                match_old = match
                                c._bleed_match(match, match_mask)
                                if match == match_old:
                                    break
                            matches.append(match)
                            for xx in range(len(match)):
                                for yy in range(len(match[0])):
                                    if match[xx][yy] != 'u':
                                        c._board[xx][yy] = 'u'
            if all(c._board[x] == sorted(c._board[x], key=board_sort_key) for x in range(c.width)):
                break
            for x in range(c.width):
                c._board[x] = sorted(c._board[x], key=board_sort_key)
        return matches

    def get_matches(self):
        return [Match(m, self.width, self.height) for m in self._matches()]

    def _bleed_match(self, match, mask):
        for x in range(self.width):
            for y in range(self.height):
                if match[x][y] != 'u':
                    if x-1 >= 0 and mask[x-1][y] and match[x][y] == self._board[x-1][y]:
                        match[x-1][y] = match[x][y]
                        mask[x-1][y] = False
                    if x+1 < self.width and mask[x+1][y] and match[x][y] == self._board[x+1][y]:
                        match[x+1][y] = match[x][y]
                        mask[x+1][y] = False
                    if y-1 >= 0 and mask[x][y-1] and match[x][y] == self._board[x][y-1]:
                        match[x][y-1] = match[x][y]
                        mask[x][y-1] = False
                    if y+1 < self.height and mask[x][y+1] and match[x][y] == self._board[x][y+1]:
                        match[x][y+1] = match[x][y]
                        mask[x][y+1] = False

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

vdp = lambda b: 9 <= b._string().count('r') <= 33 and any('vdp' in m.tags for m in b.get_matches())

def optimal_boards(p):
    start = time.time()
    try:
        combo_counts = {}
        count = 0
        for board_string in itertools.product('rl', repeat=42):
            count += 1
            board_string = ''.join(board_string)
            if time.time() - start >= 5:
                print(board_string)
                print(count)
                start = time.time()
            board = Board(board_string)
            if p(board):
                index = board_string.count('r')
                cc = len(board.get_matches())
                if index not in combo_counts:
                    combo_counts[index] = cc
                if cc > combo_counts[index]:
                    combo_counts[index] = cc

        return combo_counts
    except:
        print(board_string)
        print(count)
    
    end = time.time()
    print(end - start)

        
