import copy
import numpy as np

from tile import create_tiles, DIRECTION

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
            self.x, self.y, self.previous_x, self.previous_y, self.direction, self.crashed, self.reached_destination)


def solve(grid, carts):
    carts = copy.deepcopy(carts)
    for cart in carts:
        next_x, next_y = cart.get_next_position()
        if next_y < 0 or next_y >= len(grid) or next_x < 0 or next_x >= len(grid[0]):
            cart.crash()
            continue
        tile_index = grid[next_y][next_x]
        tile = tiles[tile_index]
        print(tile)


def find_solution(grid, carts, destination):
    for cart in carts:
        cart.destination = destination
    solve(grid, carts)


if __name__ == "__main__":
    GRID = np.array([[1, 0, 15, 0, 5],
                     [0, 0, 0, 0, 0]])
    CARTS = [
        Cart(x=0, y=0, direction=DIRECTION['right']),
    ]
    DESTINATION = (5, 5)

    find_solution(GRID, CARTS, DESTINATION)
