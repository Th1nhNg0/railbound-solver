from enum import IntEnum
from typing import NamedTuple


class Position(NamedTuple):
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)


class DIRECTION(IntEnum):
    TOP, RIGHT, BOTTOM, LEFT = range(4)

    @property
    def delta(self):
        return {
            DIRECTION.TOP: Position(0, -1),
            DIRECTION.RIGHT: Position(1, 0),
            DIRECTION.BOTTOM: Position(0, 1),
            DIRECTION.LEFT: Position(-1, 0),
        }[self]

    @property
    def opposite(self):
        return DIRECTION((self + 2) % 4)


class TileName(IntEnum):
    EMPTY = 0
    CURVE_BR = 1
    CURVE_RB = 1  # same as CURVE_BR
    CURVE_BL = 2
    CURVE_LB = 2  # same as CURVE_BL
    CURVE_TL = 3
    CURVE_LT = 3  # same as CURVE_TL
    CURVE_TR = 4
    CURVE_RT = 4  # same as CURVE_TR

    STRAIGHT_V = 5
    STRAIGHT_H = 6

    T_TURN_VBL = 7
    T_TURN_VLB = 7  # same as T_TURN_V_BL
    T_TURN_HLT = 8
    T_TURN_HTL = 8  # same as T_TURN_H_LT
    T_TURN_VTR = 9
    T_TURN_VRT = 9  # same as T_TURN
    T_TURN_HBR = 10
    T_TURN_HRB = 10  # same as T_TURN_H_BR
    T_TURN_VTL = 11
    T_TURN_VLT = 11  # same as T_TURN_V_TL
    T_TURN_HRT = 12
    T_TURN_HTR = 12  # same as T_TURN_H_RT
    T_TURN_VRB = 13
    T_TURN_VBR = 13  # same as T_TURN_V_RB
    T_TURN_HLB = 14
    T_TURN_HBL = 14  # same as T_TURN_H_LB

    FENCE = 15

    @classmethod
    def curve_tiles(cls):
        return [
            cls.CURVE_BR,
            cls.CURVE_BL,
            cls.CURVE_TL,
            cls.CURVE_TR,
        ]

    @classmethod
    def straight_tiles(cls):
        return [
            cls.STRAIGHT_V,
            cls.STRAIGHT_H,
        ]

    @classmethod
    def t_turn_tiles(cls):
        return [
            cls.T_TURN_VBL,
            cls.T_TURN_HLT,
            cls.T_TURN_VTR,
            cls.T_TURN_HBR,
            cls.T_TURN_VTL,
            cls.T_TURN_HRT,
            cls.T_TURN_VRB,
            cls.T_TURN_HLB,
        ]

    @classmethod
    def is_curve(cls, tile):
        return tile in cls.curve_tiles()

    @classmethod
    def is_straight(cls, tile):
        return tile in cls.straight_tiles()

    @classmethod
    def is_t_turn(cls, tile):
        return tile in cls.t_turn_tiles()
