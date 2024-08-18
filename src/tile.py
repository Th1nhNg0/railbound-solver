from enum import IntEnum
from typing import NamedTuple


class Position(NamedTuple):
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)


class Direction(IntEnum):
    TOP, RIGHT, BOTTOM, LEFT = range(4)

    @property
    def delta(self):
        return {
            Direction.TOP: Position(0, -1),
            Direction.RIGHT: Position(1, 0),
            Direction.BOTTOM: Position(0, 1),
            Direction.LEFT: Position(-1, 0),
        }[self]

    @property
    def opposite(self):
        return Direction((self + 2) % 4)


class Tile(IntEnum):
    EMPTY = 0

    CURVE_BR = 1
    CURVE_BL = 2
    CURVE_TL = 3
    CURVE_TR = 4

    STRAIGHT_V = 5
    STRAIGHT_H = 6

    T_TURN_VBL = 7
    T_TURN_HLT = 8
    T_TURN_VTR = 9
    T_TURN_HBR = 10
    T_TURN_VTL = 11
    T_TURN_HRT = 12
    T_TURN_VRB = 13
    T_TURN_HLB = 14

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

    def get_connection_direction(self):
        result = {
            Direction.TOP: False,
            Direction.RIGHT: False,
            Direction.BOTTOM: False,
            Direction.LEFT: False,
        }
        d = self.name.split("_")
        if len(d) == 1:
            return result
        d = d[-1]
        if "V" in d:
            result[Direction.TOP] = True
            result[Direction.BOTTOM] = True
        if "H" in d:
            result[Direction.RIGHT] = True
            result[Direction.LEFT] = True
        if "T" in d:
            result[Direction.TOP] = True
        if "B" in d:
            result[Direction.BOTTOM] = True
        if "L" in d:
            result[Direction.LEFT] = True
        if "R" in d:
            result[Direction.RIGHT] = True
        return result


def make_connectable_dict():
    data = {}
    for tile_src in Tile:
        src_connection_direction = tile_src.get_connection_direction()
        data[tile_src] = {}
        for tile_dst in Tile:
            dst_connection_direction = tile_dst.get_connection_direction()
            data[tile_src][tile_dst] = {}
            for direction in Direction:
                data[tile_src][tile_dst][direction] = False
                if (
                    src_connection_direction[direction]
                    and dst_connection_direction[direction.opposite]
                ):
                    data[tile_src][tile_dst][direction] = True
    return data
