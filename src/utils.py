import json
from tile import Tile, Direction, Position


def make_effects(data):
    effects = {}
    for x in range(len(data["grid"][0])):
        for y in range(len(data["grid"])):
            tile = Tile(data["grid"][y][x])
            if tile.is_tunnel:
                other_tunnel = None
                for x2 in range(len(data["grid"][0])):
                    for y2 in range(len(data["grid"])):
                        if (x2 != x or y2 != y) and (
                            data["numberLayer"][y2][x2] == data["numberLayer"][y][x]
                        ):
                            other_tunnel = (x2, y2, Tile(data["grid"][y2][x2]))
                            break
                    if other_tunnel:
                        break

                if other_tunnel:
                    direction = other_tunnel[-1].name.split("_")[-1]
                    direction = "TRBL".index(direction)
                    effects[(x, y)] = (
                        "tunnel",
                        other_tunnel[:2],
                        Direction(direction),
                    )
    return effects


def make_immutable_positions(data):
    immutable_positions = set()
    for x in range(len(data["grid"][0])):
        for y in range(len(data["grid"])):
            if Tile(data["grid"][y][x]) != Tile.EMPTY:
                immutable_positions.add(Position(x, y))
    return immutable_positions


def load_data(level):
    with open(f"./src/levels/{level}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    data["effects"] = make_effects(data)
    data["immutable_positions"] = make_immutable_positions(data)
    return data
