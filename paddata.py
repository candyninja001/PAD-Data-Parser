# This module impliments datastructures used for
# elements of the game, such as boards and cards

from enum import IntEnum

class Attribute(IntEnum):
    FIRE = 0
    WATER = 1
    WOOD = 2
    LIGHT = 3
    DARK = 4

class OrbType(IntEnum):
    FIRE = 0
    WATER = 1
    WOOD = 2
    LIGHT = 3
    DARK = 4
    HEART = 5
    JAMMER = 6
    POISON = 7
    MORTAL = 8
    BOMB = 9

    def get_spin_orb(self):
        OrbType((min(self, 5) + 1) % 6)

class Orb():
    BLIND = 0
    SUPER_BLIND = 1
    def __init__(self, att=None, enhance=False, lock=False, blind=None):
        self.att = att
        self.enhance = enhance
        self.lock = lock
        self.blind = blind

    def __setatt__(self, name, value):
        if name == 'att':
            if type(value) not in {OrbType, None}:
                raise ValueError('Orb.att must be OrbType or None')
        elif name == 'enhance':
            if type(value) not in {bool}:
                raise ValueError('Orb.enhance must be bool')
        elif name == 'lock':
            if type(value) not in {bool}:
                raise ValueError('Orb.lock must be bool')
        elif name == 'blind':
            if type(value) not in {Orb.BLIND, Orb.SUPER_BLIND, None}:
                raise ValueError('Orb.blind must be Orb.BLIND, Orb.SUPERBLIND or None')
        else:
            raise AttributeError(f'{name} is not an attribute of Orb')
        object.__setattr__(self, name, value)
        if self.enhance and self.att != None and self.att > int(OrbType.HEART):
            self.enhance = False

    def spin(self) -> bool:
        if self.lock:
            return False
        if self.att != None:
            self.att = get_spin_orb)
        return True
        

class StrictBoardSelection(): # exclusive to 6x5 or 7x6
    def __init__(self, points=None, size=30):
        self.points = []

class AdjustableBoardSelection(): # adjusts 6x5 selection to 7x6
    def __init__(self, points=None):
        self.points = []

class BoardColumn(AdjustableBoardSelection):
    def __init__(self, index):
        super().__init__(self)

class BoardRow(AdjustableBoardSelection):
    pass

class Board():
    width = 6
    height = 5
    def __init__(self, inital=None, size='6x5'):
        if inital != None:
            if len(initial) == 42:
                self.width = 7
                self.height = 6
            elif len(intial) == 30:
                self.width = 6
                self.height = 5
        else:
            if size == '7x6' or size == '76' or str(size) == '42':
                self.width = 7
                self.height = 6
            else:
                self.width = 6
                self.height = 5
            for x in range(self.width):
                for y in range(self.height):
                    

    def __getitem__(self, index):
        return orbs
