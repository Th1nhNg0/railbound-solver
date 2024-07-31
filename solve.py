import copy
import numpy as np
from utils import DIRECTION, DIRECTION_TO_STR, flip_direction
from tile import create_tiles

tiles = create_tiles()


class Cart:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y

        self.previous_x = x
        self.previous_y = y

        self.direction = direction
        self.crashed = False
        self.reached_destination = False

    def move(self, new_x, new_y, new_direction):
        self.previous_x, self.previous_y = self.x, self.y
        self.x = new_x
        self.y = new_y
        self.direction = new_direction

    def get_next_position(self):
        next_x, next_y = self.x, self.y
        if self.direction == DIRECTION['top']:
            next_y -= 1
        elif self.direction == DIRECTION['bottom']:
            next_y += 1
        elif self.direction == DIRECTION['left']:
            next_x -= 1
        elif self.direction == DIRECTION['right']:
            next_x += 1
        return next_x, next_y

    def __repr__(self):
        return "Cart(x={}, y={}, previous_x={}, previous_y={}, direction={}, crashed={}, reached_destination={})".format(
            self.x, self.y, self.previous_x, self.previous_y, DIRECTION_TO_STR[self.direction], self.crashed, self.reached_destination)


def solve(grid, carts, c=0):
    carts = copy.deepcopy(carts)
    tile_to_place = []
    for cart in carts:
        next_x, next_y = cart.get_next_position()
        # check if next position is valid
        if next_y < 0 or next_y >= len(grid) or next_x < 0 or next_x >= len(grid[0]):
            cart.crash()
            continue
        tile_index = grid[next_y][next_x]
        tile = tiles[tile_index]
        if tile_index == 0:
            # add to tile_to_place (posx, posy, direction need to connect)
            tile_to_place.append(
                (next_x, next_y, flip_direction(cart.direction)))
        else:
            new_direction = tile.get_output_direction(cart.direction)
            cart.move(next_x, next_y, new_direction)
    print([f'{x[0]} {x[1]} {DIRECTION_TO_STR[x[2]]}' for x in tile_to_place])
    print(carts)
    # SHOULD CONTINUE WORK HERE
    if c == 0:
        # place random tile bla bla...
        solve(grid, carts, 1)


def find_solution(grid, carts, destination):
    for cart in carts:
        cart.destination = destination
    solve(grid, carts)


if __name__ == "__main__":
    GRID = np.array([[1, 2, 15, 0, 5],
                     [0, 0, 0, 0, 0]])
    CARTS = [
        Cart(x=0, y=0, direction=DIRECTION['right']),
    ]
    DESTINATION = (5, 5)
    find_solution(GRID, CARTS, DESTINATION)
