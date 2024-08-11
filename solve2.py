import argparse
import copy
import json
import time
from collections import defaultdict, deque


import cv2
import numpy as np
import PIL

from tile import Tile, create_tiles
from utils import DIRECTION, DIRECTION_TO_STR, TimingManager

timer = TimingManager()
tiles = create_tiles()


class Cart:
    def __init__(self, x: int, y: int, direction: int, order: int):
        self.x = x
        self.y = y

        self.previous_x = x
        self.previous_y = y

        self.direction = direction
        self.crashed = False
        self.reached_destination = False

        self.order = order

    def move(self, new_x: int, new_y: int, new_direction: int) -> None:
        """
        Move the object to a new position and update its direction.

        Args:
            new_x (int): The new x-coordinate of the object.
            new_y (int): The new y-coordinate of the object.
            new_direction (str): The new direction of the object.

        Returns:
            None
        """
        self.previous_x, self.previous_y = self.x, self.y
        self.x = new_x
        self.y = new_y
        self.direction = new_direction

    def get_next_position(self):
        """
        Calculates the next position based on the current position and direction.

        Returns:
            Tuple[int, int]: The next position coordinates (x, y).
        """
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

    def update_direction(self, tile: Tile) -> None:
        """
        Update the direction of the cart based on the tile it is on.

        Args:
            tile (Tile): The tile object representing the current location of the cart.

        Returns:
            None
        """
        for i, o in tile.flow:
            if i == self.direction:
                self.direction = o
                break

    def __repr__(self):
        return "Cart(x={}, y={}, previous_x={}, previous_y={}, direction={}, crashed={}, reached_destination={})".format(
            self.x, self.y, self.previous_x, self.previous_y, DIRECTION_TO_STR[self.direction], self.crashed, self.reached_destination)

    @staticmethod
    def check_collision(x1, y1, x2, y2):
        return x1 == x2 and y1 == y2


class Grid:
    def __init__(self, grid, max_placement: int):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.max_placement = max_placement
        self.placed_tiles = 0

    def get_tile(self, x, y) -> Tile:
        """
        Retrieves the tile at the specified coordinates.

        Args:
            x (int): The x-coordinate of the tile.
            y (int): The y-coordinate of the tile.

        Returns:
            Tile: The tile at the specified coordinates.
        """
        return tiles[self.grid[y][x]]

    def set_tile(self, x, y, tile_index: int):
        """
        Sets the tile at the specified coordinates in the grid.

        Args:
            x (int): The x-coordinate of the tile.
            y (int): The y-coordinate of the tile.
            tile_index (int): The index of the tile to set.

        Returns:
            None
        """
        self.grid[y][x] = tile_index

    def get_image(self, carts: list[Cart] = None):
        """
        Generates an image representation of the railbound puzzle board.

        Args:
            carts (list[Cart], optional): A list of Cart objects representing the carts on the board. Defaults to None.

        Returns:
            PIL.Image.Image: The generated image.

        """
        img = PIL.Image.new(
            'RGB', (self.width * 100, self.height * 100), color='white')
        imageDraw = PIL.ImageDraw.Draw(img)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                img.paste(tile.img, (x * 100, y * 100))
                imageDraw.text((x * 100 + 10, y * 100 + 10),
                               str(tile.index), fill='red')
                # draw x-y coordinates
                imageDraw.text((x * 100 + 10, y * 100 + 80),
                               f'{x}, {y}', fill='blue')

        # draw line
        for y in range(self.height):
            imageDraw.line((0, y * 100, self.width * 100, y * 100),
                           fill='black', width=1)
        for x in range(self.width):
            imageDraw.line((x * 100, 0, x * 100, self.height * 100),
                           fill='black', width=1)

        if carts is not None:
            for cart in carts:
                direction = cart.direction
                imageDraw.ellipse((cart.x * 100 + 30, cart.y * 100 + 30, cart.x * 100 + 70, cart.y * 100 + 70),
                                  fill='red', outline='red')

                # draw direction line
                if direction == DIRECTION['top']:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 50, cart.y * 100 + 30),
                                   fill='black', width=2)
                elif direction == DIRECTION['bottom']:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 50, cart.y * 100 + 70),
                                   fill='black', width=2)
                elif direction == DIRECTION['left']:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 30, cart.y * 100 + 50),
                                   fill='black', width=2)
                elif direction == DIRECTION['right']:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 70, cart.y * 100 + 50),
                                   fill='black', width=2)

                # draw order number on cart
                imageDraw.text((cart.x * 100 + 40, cart.y * 100 + 40),
                               str(cart.order), fill='white')
        return img

    def preview_image(self, carts: list[Cart] = None, wait_time=0):
        img = self.get_image(carts)
        cv2.imshow('image', np.array(img))
        cv2.waitKey(wait_time)

    def get_possible_grid(self, pos_to_place_tile):
        """
        Generates all possible grids by placing tiles on the board.

        Args:
            pos_to_place_tile (list): A list of positions to place tiles on the board.

        Yields:
            Grid: A new grid configuration with a tile placed on the board.

        Returns:
            None: If there are no positions to place tiles.

        """
        if not pos_to_place_tile:
            return
        x, y = pos_to_place_tile[0]
        for tile in tiles:
            # check top edge
            if y > 0:
                top_tile = self.get_tile(x, y-1)
                if top_tile.edges[2] != tile.edges[0] and top_tile.name != 'Empty':
                    continue
            else:
                if tile.edges[0] != 0:
                    continue
            # check bottom edge
            if y < self.height - 1:
                bottom_tile = self.get_tile(x, y+1)
                if bottom_tile.edges[0] != tile.edges[2] and bottom_tile.name != 'Empty':
                    continue
            else:
                if tile.edges[2] != 0:
                    continue
            # check left edge
            if x > 0:
                left_tile = self.get_tile(x-1, y)
                if left_tile.edges[1] != tile.edges[3] and left_tile.name != 'Empty':
                    continue
            else:
                if tile.edges[3] != 0:
                    continue
            # check right edge
            if x < self.width - 1:
                right_tile = self.get_tile(x+1, y)
                if right_tile.edges[3] != tile.edges[1] and right_tile.name != 'Empty':
                    continue
            else:
                if tile.edges[1] != 0:
                    continue

            new_grid = copy.deepcopy(self.grid)
            new_grid[y][x] = tile.index
            new_grid = Grid(new_grid, self.max_placement)
            new_grid.placed_tiles = self.placed_tiles + 1
            if new_grid.placed_tiles > self.max_placement:
                return

            if len(pos_to_place_tile) > 1:
                yield from new_grid.get_possible_grid(pos_to_place_tile[1:])
            else:
                yield new_grid

    def check_valid_grid(self):
        # check if the grid is valid: all tiles are connected
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile.name != 'T_turn' and tile.name != 'Curve':
                    continue
                if y > 0:
                    top_tile = self.get_tile(x, y-1)
                    if top_tile.edges[2] != tile.edges[0]:
                        return False
                if y < self.height - 1:
                    bottom_tile = self.get_tile(x, y+1)
                    if bottom_tile.edges[0] != tile.edges[2]:
                        return False
                if x > 0:
                    left_tile = self.get_tile(x-1, y)
                    if left_tile.edges[1] != tile.edges[3]:
                        return False
                if x < self.width - 1:
                    right_tile = self.get_tile(x+1, y)
                    if right_tile.edges[3] != tile.edges[1]:
                        return False
        return True

    def __repr__(self):
        return "Grid({})".format(self.grid)

    def __str__(self):
        return self.__repr__()


def find_solution(i_grid: Grid, i_carts: list[Cart], destination: tuple[int, int]):
    queue = deque()
    queue.append((i_grid, i_carts, []))
    count = 0
    total = 1

    while queue:
        with timer.measure_time("Iteration"):
            count += 1
            print(f"Iteration: {count}, Total: {total}, Queue: {
                len(queue)}", end='\r')
            grid, carts, history = queue.pop()
            new_carts = copy.deepcopy(carts)
            pos_to_place_tile = []
            should_skip = False

            max_steps = 10  # max steps to simulate the carts movement to avoid infinite loop
            with timer.measure_time("Simulation"):
                while len(pos_to_place_tile) == 0 and max_steps > 0:
                    max_steps -= 1
                    for cart in new_carts:
                        if cart.reached_destination:
                            continue
                        next_x, next_y = cart.get_next_position()

                        if next_x < 0 or next_x >= grid.width or next_y < 0 or next_y >= grid.height:
                            cart.crashed = True
                            continue
                        next_tile = grid.get_tile(next_x, next_y)

                        if next_tile.name == 'Rock':
                            cart.crashed = True
                            continue

                        if (next_x, next_y) == destination:
                            cart.reached_destination = True
                            for other_cart in new_carts:
                                if other_cart.reached_destination:
                                    continue
                                if other_cart.order < cart.order:
                                    cart.crashed = True
                                    break
                        cart.move(next_x, next_y, cart.direction)

                        if next_tile.name == 'Empty':
                            pos_to_place_tile.append((next_x, next_y))
                        else:
                            cart.update_direction(next_tile)

                    # check collision
                    for i, cart in enumerate(new_carts):
                        for j, other_cart in enumerate(new_carts):
                            if i == j:
                                continue
                            if cart.reached_destination or other_cart.reached_destination:
                                continue
                            if Cart.check_collision(cart.x, cart.y, other_cart.x, other_cart.y):
                                cart.crashed = True
                                other_cart.crashed = True
                            if Cart.check_collision(cart.x, cart.y, other_cart.previous_x, other_cart.previous_y)\
                                    and Cart.check_collision(cart.previous_x, cart.previous_y, other_cart.x, other_cart.y):
                                cart.crashed = True
                                other_cart.crashed = True

                    if any(cart.crashed for cart in new_carts):
                        should_skip = True
                        break

                    if all(cart.reached_destination for cart in new_carts):
                        should_skip = True
                        if grid.check_valid_grid():
                            # pprint.pprint(grid.grid)
                            # print()
                            # with open('solution.pkl', 'wb') as f:
                            #     pickle.dump(history, f)
                            # grid.preview_image(i_carts)
                            return
                        break

            if should_skip:
                continue
            with timer.measure_time("Grid generation"):
                for new_grid in grid.get_possible_grid(pos_to_place_tile):
                    new_carts_copy = copy.deepcopy(new_carts)
                    for cart in new_carts_copy:
                        # check is cart is on any pos_to_place_tile
                        if (cart.x, cart.y) in pos_to_place_tile:
                            tile = new_grid.get_tile(cart.x, cart.y)
                            cart.update_direction(tile)
                    total += 1
                    # queue.append(
                    #     (new_grid, new_carts_copy, history + [new_grid.grid]))
                    queue.append((new_grid, new_carts_copy, []))
    print("No solution found")
    print("Total iterations:", count)
    print("Total grids checked:", total)


def load_grid(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate the loaded data
    if not all(key in data for key in ['grid', 'destination', 'carts']):
        raise KeyError("The loaded JSON is missing required keys.")

    # Convert destination back to tuple if it exists
    if data["destination"]:
        data["destination"] = tuple(data["destination"])

    # Convert carts to Cart objects
    data["carts"] = [Cart(cart["x"], cart["y"], cart["direction"], cart["order"])
                     for cart in data["carts"]]

    return data


if __name__ == "__main__":
    MAX_PLACEMENT = 100
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path")
    args = parser.parse_args()
    data = load_grid(args.input)
    GRID = Grid(data["grid"], MAX_PLACEMENT)
    CARTS = data["carts"]
    DESTINATION = data["destination"]
    GRID.preview_image(CARTS)
    cv2.destroyAllWindows()
    start = time.time()
    find_solution(GRID, CARTS, DESTINATION)
    print()
    print("Time taken:", time.time() - start)
    print()
    timer.print_averages()
