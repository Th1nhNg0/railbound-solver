from enum import IntEnum
from typing import NamedTuple


class Position(NamedTuple):
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)

    def __copy__(self):
        return Position(self.x, self.y)

    def __deepcopy__(self, memo):
        return Position(self.x, self.y)


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

    TUNNEL_T = 16
    TUNNEL_R = 17
    TUNNEL_B = 18
    TUNNEL_L = 19

    @property
    def is_curve(self):
        return self in {
            Tile.CURVE_BR,
            Tile.CURVE_BL,
            Tile.CURVE_TL,
            Tile.CURVE_TR,
        }

    @property
    def is_straight(self):
        return self in {
            Tile.STRAIGHT_V,
            Tile.STRAIGHT_H,
        }

    @property
    def is_t_turn(self):
        return self in {
            Tile.T_TURN_VBL,
            Tile.T_TURN_HLT,
            Tile.T_TURN_VTR,
            Tile.T_TURN_HBR,
            Tile.T_TURN_VTL,
            Tile.T_TURN_HRT,
            Tile.T_TURN_VRB,
            Tile.T_TURN_HLB,
        }

    def get_output_direction(self, input_direction) -> Direction:
        flow_direction = {
            Tile.EMPTY: {},
            Tile.CURVE_BR: {
                Direction.TOP: Direction.RIGHT,
                Direction.LEFT: Direction.BOTTOM,
            },
            Tile.CURVE_BL: {
                Direction.TOP: Direction.LEFT,
                Direction.RIGHT: Direction.BOTTOM,
            },
            Tile.CURVE_TL: {
                Direction.RIGHT: Direction.TOP,
                Direction.BOTTOM: Direction.LEFT,
            },
            Tile.CURVE_TR: {
                Direction.LEFT: Direction.TOP,
                Direction.BOTTOM: Direction.RIGHT,
            },
            Tile.STRAIGHT_V: {
                Direction.TOP: Direction.TOP,
                Direction.BOTTOM: Direction.BOTTOM,
            },
            Tile.STRAIGHT_H: {
                Direction.RIGHT: Direction.RIGHT,
                Direction.LEFT: Direction.LEFT,
            },
            Tile.T_TURN_VBL: {
                Direction.TOP: Direction.LEFT,
                Direction.BOTTOM: Direction.BOTTOM,
                Direction.RIGHT: Direction.BOTTOM,
            },
            Tile.T_TURN_HLT: {
                Direction.BOTTOM: Direction.LEFT,
                Direction.RIGHT: Direction.TOP,
                Direction.LEFT: Direction.LEFT,
            },
            Tile.T_TURN_VTR: {
                Direction.TOP: Direction.TOP,
                Direction.BOTTOM: Direction.RIGHT,
                Direction.LEFT: Direction.TOP,
            },
            Tile.T_TURN_HBR: {
                Direction.TOP: Direction.RIGHT,
                Direction.RIGHT: Direction.RIGHT,
                Direction.LEFT: Direction.BOTTOM,
            },
            Tile.T_TURN_VTL: {
                Direction.TOP: Direction.TOP,
                Direction.RIGHT: Direction.TOP,
                Direction.BOTTOM: Direction.LEFT,
            },
            Tile.T_TURN_HRT: {
                Direction.BOTTOM: Direction.RIGHT,
                Direction.LEFT: Direction.TOP,
                Direction.RIGHT: Direction.RIGHT,
            },
            Tile.T_TURN_VRB: {
                Direction.BOTTOM: Direction.BOTTOM,
                Direction.TOP: Direction.RIGHT,
                Direction.LEFT: Direction.BOTTOM,
            },
            Tile.T_TURN_HLB: {
                Direction.TOP: Direction.LEFT,
                Direction.LEFT: Direction.LEFT,
                Direction.RIGHT: Direction.BOTTOM,
            },
            Tile.FENCE: {},
        }
        if input_direction not in flow_direction[self]:
            return -1
        return flow_direction[self][input_direction]

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

    def to_t_turn(self, direction: Direction, direction_flow: Direction | None = None):
        # direction is direction to connect
        # direction_flow is direction of the straight way
        transform_dict = {
            Tile.CURVE_BL: {
                Direction.TOP: Tile.T_TURN_VBL,
                Direction.RIGHT: Tile.T_TURN_HLB,
            },
            Tile.CURVE_BR: {
                Direction.TOP: Tile.T_TURN_VRB,
                Direction.LEFT: Tile.T_TURN_HBR,
            },
            Tile.CURVE_TL: {
                Direction.RIGHT: Tile.T_TURN_HLT,
                Direction.BOTTOM: Tile.T_TURN_VTL,
            },
            Tile.CURVE_TR: {
                Direction.LEFT: Tile.T_TURN_HRT,
                Direction.BOTTOM: Tile.T_TURN_VTR,
            },
            Tile.STRAIGHT_H: {
                Direction.RIGHT: {
                    Direction.TOP: Tile.T_TURN_HRT,
                    Direction.BOTTOM: Tile.T_TURN_HBR,
                },
                Direction.LEFT: {
                    Direction.TOP: Tile.T_TURN_HLT,
                    Direction.BOTTOM: Tile.T_TURN_HLB,
                },
            },
            Tile.STRAIGHT_V: {
                Direction.TOP: {
                    Direction.LEFT: Tile.T_TURN_VTL,
                    Direction.RIGHT: Tile.T_TURN_VTR,
                },
                Direction.BOTTOM: {
                    Direction.LEFT: Tile.T_TURN_VBL,
                    Direction.RIGHT: Tile.T_TURN_VRB,
                },
            },
        }

        if self in transform_dict:
            if direction in transform_dict[self] and direction_flow is None:
                if direction_flow is None:
                    return transform_dict[self][direction]
            if direction_flow is not None and direction_flow in transform_dict[self]:
                if direction in transform_dict[self][direction_flow]:
                    return transform_dict[self][direction_flow][direction]
        return -1


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
                ) or not (
                    src_connection_direction[direction]
                    or dst_connection_direction[direction.opposite]
                ):
                    data[tile_src][tile_dst][direction] = True
    return data


TILES_CONNECT = make_connectable_dict()
