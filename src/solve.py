import argparse
import json
from collections import deque

import cv2
import numpy as np
import PIL

from tile import Tile, create_tiles, curve_to_t_turn, straight_to_t_turn
from utils import DIRECTION, DIRECTION_TO_STR, TimingManager, DIRECTION_DELTA, OPPOSITE_DIRECTION

timer = TimingManager(enabled=False)
tiles = create_tiles()


def load_grid(file_path):
    """
    Load a JSON file containing the grid, destination, and carts data.

    Args:
        file_path(str): The path to the JSON file.

    Returns:
        dict: A dictionary containing the loaded data.
    """
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


class Cart:
    """
    A class to represent a cart on the railbound puzzle board.
    """
    __slots__ = ('x', 'y', 'previous_x', 'previous_y',
                 'direction', 'reached_destination', 'order')

    def __init__(self, x: int, y: int, direction: int, order: int, reached_destination=False):
        self.x = x
        self.y = y

        self.previous_x = x
        self.previous_y = y

        self.direction = direction
        self.reached_destination = reached_destination

        self.order = order

    def move(self, new_x: int, new_y: int, new_direction: int) -> None:
        """
        Move the object to a new position and update its direction.

        Args:
            new_x(int): The new x-coordinate of the object.
            new_y(int): The new y-coordinate of the object.
            new_direction(str): The new direction of the object.

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
            Tuple[int, int]: The next position coordinates(x, y).
        """
        next_x, next_y = self.x, self.y
        if self.direction == DIRECTION.TOP:
            next_y -= 1
        elif self.direction == DIRECTION.BOTTOM:
            next_y += 1
        elif self.direction == DIRECTION.LEFT:
            next_x -= 1
        elif self.direction == DIRECTION.RIGHT:
            next_x += 1
        return next_x, next_y

    def update_direction(self, tile: Tile) -> None:
        """
        Update the direction of the cart based on the tile it is on.

        Args:
            tile(Tile): The tile object representing the current location of the cart.

        Returns:
            None
        """
        for i, o in tile.flow:
            if i == self.direction:
                self.direction = o
                break

    def __repr__(self):
        return (
            f"Cart(x={self.x}, y={self.y}, "
            f"previous_x={self.previous_x}, previous_y={self.previous_y}, "
            f"direction={DIRECTION_TO_STR[self.direction]}, "
            f"reached_destination={self.reached_destination})"
        )

    @staticmethod
    def check_collision(x1, y1, x2, y2):
        """
        Check if two points collide.
        Parameters:
        - x1 (int): The x-coordinate of the first point.
        - y1 (int): The y-coordinate of the first point.
        - x2 (int): The x-coordinate of the second point.
        - y2 (int): The y-coordinate of the second point.
        Returns:
        - bool: True if the points collide, False otherwise.
        """

        return x1 == x2 and y1 == y2

    def copy(self):
        """
        Creates a copy of the current Cart object.
        Returns:
            Cart: A new Cart object with the same attributes as the original.
        """

        return Cart(x=self.x, y=self.y, direction=self.direction, order=self.order, reached_destination=self.reached_destination)


class Grid:
    __slots__ = ('grid', 'height', 'width', 'max_placement',
                 'placed_tile_count', 'destination', 'can_change_tiled')

    def __init__(self, grid, max_placement: int, placed_tile_count=0, destination=(0, 0),
                 can_change_tiled=None):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.max_placement = max_placement
        self.placed_tile_count = placed_tile_count
        self.destination = destination
        self.can_change_tiled = can_change_tiled

        if can_change_tiled is None:
            self.calc_can_change_tiled()

    def calc_can_change_tiled(self):
        can_change_tiled = {}
        for y in range(self.height):
            for x in range(self.width):
                can_change_tiled[(x, y)] = self.get_tile(x, y).name == 'Empty'
        self.can_change_tiled = can_change_tiled

    def get_tile(self, x, y) -> Tile:
        """
        Retrieves the tile at the specified coordinates.

        Args:
            x(int): The x-coordinate of the tile.
            y(int): The y-coordinate of the tile.

        Returns:
            Tile: The tile at the specified coordinates.
        """
        return tiles[self.grid[y][x]]

    def set_tile(self, x, y, tile_index: int):
        """
        Sets the tile at the specified coordinates in the grid.

        Args:
            x(int): The x-coordinate of the tile.
            y(int): The y-coordinate of the tile.
            tile_index(int): The index of the tile to set.

        Returns:
            None
        """
        self.grid[y][x] = tile_index

    def get_image(self, carts: list[Cart] = None):
        """
        Generates an image representation of the railbound puzzle board.

        Args:
            carts(list[Cart], optional): A list of Cart objects representing the carts on the board. Defaults to None.

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
                if direction == DIRECTION.TOP:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 50, cart.y * 100 + 30),
                                   fill='black', width=2)
                elif direction == DIRECTION.BOTTOM:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 50, cart.y * 100 + 70),
                                   fill='black', width=2)
                elif direction == DIRECTION.LEFT:
                    imageDraw.line((cart.x * 100 + 50, cart.y * 100 + 50, cart.x * 100 + 30, cart.y * 100 + 50),
                                   fill='black', width=2)
                elif direction == DIRECTION.RIGHT:
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

    def __repr__(self):
        return '\n'.join([' '.join([str(tile) for tile in row]) for row in self.grid])

    def __str__(self):
        return self.__repr__()

    def copy(self):
        grid = [row.copy() for row in self.grid]
        return Grid(grid, self.max_placement, self.placed_tile_count, self.destination, self.can_change_tiled)

    def get_possible_grid(self, pos_to_place_tile):
        """
        Generates all possible grids by placing tiles on the board.

        Args:
            pos_to_place_tile(list): A list of positions to place tiles on the board.

        Yields:
            Grid: A new grid configuration with a tile placed on the board.

        Returns:
            None: If there are no positions to place tiles.

        """
        self.preview_image(wait_time=1)
        if not pos_to_place_tile or self.placed_tile_count >= self.max_placement:
            return
        x, y, d = pos_to_place_tile[0]
        for tile in tiles:
            if tile.name not in ['Straight', 'Curve']:
                continue

            output_direction = tile.get_output_direction(d)
            if output_direction == -1:
                continue

            px, py = x - DIRECTION_DELTA[d][0], y - DIRECTION_DELTA[d][1]
            if 0 <= px < self.width and 0 <= py < self.height:
                p_tile = self.get_tile(px, py)
                if not Tile.check_connection(tile, p_tile, OPPOSITE_DIRECTION[d]) and p_tile.name != 'Empty':
                    continue

            nx, ny = x + DIRECTION_DELTA[output_direction][0], y + \
                DIRECTION_DELTA[output_direction][1]

            t_turn_to_place = None
            if 0 <= nx < self.width and 0 <= ny < self.height:
                n_tile = self.get_tile(nx, ny)
                if not Tile.check_connection(tile, n_tile, output_direction) and n_tile.name != 'Empty':
                    if self.can_change_tiled[(nx, ny)]:
                        if n_tile.name == 'Curve':
                            t_turn_to_place = curve_to_t_turn(
                                n_tile, OPPOSITE_DIRECTION[output_direction], tiles)
                        if n_tile.name == 'Straight':
                            direction = [x[0] for x in n_tile.flow]
                            t_turn_to_place = (straight_to_t_turn(
                                n_tile, OPPOSITE_DIRECTION[output_direction], direction[0], tiles),
                                straight_to_t_turn(
                                n_tile, OPPOSITE_DIRECTION[output_direction], direction[1], tiles))
                    else:
                        continue

            new_grid = [row.copy() for row in self.grid]
            new_grid = Grid(new_grid, self.max_placement,
                            self.placed_tile_count+1, self.destination, self.can_change_tiled)

            new_grid.set_tile(x, y, tile.index)
            # check if current tile can be transformed to T-Turn
            connect_count = 0
            direction_to_change = None
            for _d in range(4):
                _nx = x + DIRECTION_DELTA[_d][0]
                _ny = y + DIRECTION_DELTA[_d][1]
                if 0 <= _nx < self.width and 0 <= _ny < self.height:
                    _n_tile = self.get_tile(_nx, _ny)
                    _d_to_check = OPPOSITE_DIRECTION[_d]
                    if _n_tile.edges[_d_to_check] == 1:
                        connect_count += 1
                        if tile.edges[_d] == 0:
                            direction_to_change = _d
            # no valid tiled to connect 4 tiled around
            if connect_count == 4:
                continue
            if direction_to_change is not None:
                if tile.name == 'Curve':
                    t_turn_self = curve_to_t_turn(
                        tile, direction_to_change, tiles)
                    new_grid.set_tile(x, y, t_turn_self.index)
            # TODO: CONTINUE FROM HERE
            if t_turn_to_place:
                if isinstance(t_turn_to_place, tuple):
                    temp_grid = new_grid.copy()
                    temp_grid.set_tile(nx, ny, t_turn_to_place[0].index)
                    if len(pos_to_place_tile) > 1:
                        yield from temp_grid.get_possible_grid(pos_to_place_tile[1:])
                    else:
                        yield temp_grid
                    temp_grid = new_grid.copy()
                    temp_grid.set_tile(nx, ny, t_turn_to_place[1].index)
                    if len(pos_to_place_tile) > 1:
                        yield from temp_grid.get_possible_grid(pos_to_place_tile[1:])
                    else:
                        yield temp_grid
                else:
                    temp_grid = new_grid.copy()
                    temp_grid.set_tile(nx, ny, t_turn_to_place.index)
                    if len(pos_to_place_tile) > 1:
                        yield from temp_grid.get_possible_grid(pos_to_place_tile[1:])
                    else:
                        yield temp_grid
            else:
                if len(pos_to_place_tile) > 1:
                    yield from new_grid.get_possible_grid(pos_to_place_tile[1:])
                else:
                    yield new_grid


def process(grid, carts):
    new_carts = [cart.copy() for cart in carts]
    new_grid = grid.copy()
    # new_grid.preview_image(new_carts, 300)
    pos_to_place_tile = []

    # simulate the movement of the carts
    max_steps = 30  # to prevent infinite loop
    with timer.measure_time('simulation'):
        while len(pos_to_place_tile) == 0 and max_steps > 0:
            if all(cart.reached_destination for cart in new_carts):
                return ('solution', new_grid)

            max_steps -= 1
            for cart in new_carts:
                if cart.reached_destination:
                    continue
                next_x, next_y = cart.get_next_position()
                if next_x < 0 or next_x >= new_grid.width or next_y < 0 or next_y >= new_grid.height:
                    return ('dead_end', 'cart out of grid')
                next_tile = new_grid.get_tile(next_x, next_y)

                # check if the cart crashed into a rock
                if next_tile.name == "Rock":
                    return ('dead_end', 'cart crashed into rock')

                # check if the cart reached the destination
                if (next_x, next_y) == new_grid.destination:
                    cart.reached_destination = True
                    # check if other carts are still moving or
                    # have reached their destination in the right order
                    for other_cart in new_carts:
                        if not other_cart.reached_destination and other_cart.order < cart.order:
                            return ('dead_end', 'cart reached destination out of order')

                cart.move(next_x, next_y, cart.direction)

                if next_tile.name == "Empty":
                    pos_to_place_tile.append((next_x, next_y, cart.direction))
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
                        return ('dead_end', 'collision')
                    if (Cart.check_collision(cart.x, cart.y,
                                             other_cart.previous_x, other_cart.previous_y)
                        and Cart.check_collision(cart.previous_x, cart.previous_y,
                                                 other_cart.x, other_cart.y)):
                        return ('dead_end', 'collision')
                continue

    # explore more possibilities, return list of possible
    with timer.measure_time('get_possible_grid'):
        results = []
        pos_to_place_tile_pos = [(x, y) for x, y, _ in pos_to_place_tile]
        for new_grid in grid.get_possible_grid(pos_to_place_tile):
            new_carts_copy = [cart.copy() for cart in new_carts]
            for cart in new_carts_copy:
                if (cart.x, cart.y) in pos_to_place_tile_pos:
                    tile = new_grid.get_tile(cart.x, cart.y)
                    cart.update_direction(tile)
            results.append((new_grid, new_carts_copy))
    return ('possibilities', results)


def find_solution(i_grid: Grid, i_carts: list[Cart]):
    # (min_steps, best_solution)
    best_solution = (1e8, None)

    queue = deque([])
    queue.append((i_grid, i_carts))
    iteration = 0
    total = 0
    while queue:
        if iteration % 5000 == 0:
            print(
                f"Iteration: {iteration}, Total: {total}, Queue: {len(queue)}")

        iteration += 1
        grid, carts = queue.popleft()  # popLeft for BFS, pop for DFS
        if grid.placed_tile_count > best_solution[0]:
            continue
        with timer.measure_time('process'):
            state, result = process(grid, carts)
        if state == 'solution':
            # save the best solution
            if grid.placed_tile_count < best_solution[0]:
                grid.preview_image(carts, 200)
                best_solution = (grid.placed_tile_count, grid)
                print(
                    f"Found solution: {best_solution[0]}, Iteration: {iteration}, Total: {total}, Queue: {len(queue)}")
        if state == 'possibilities':
            queue.extend(result)
            total += len(result)

    return best_solution


def main(input_file, show_preview=True):
    MAX_PLACEMENT = 1000
    data = load_grid(input_file)
    DESTINATION = data["destination"]
    GRID = Grid(data["grid"], MAX_PLACEMENT, destination=DESTINATION)
    CARTS = data["carts"]
    if show_preview:
        GRID.preview_image(CARTS, 1000)

    timer.reset()
    best_solution = find_solution(GRID, CARTS)
    timer.print_averages()

    if best_solution[1]:
        print(f"Best solution with {best_solution[0]} tile placed")
        print(best_solution[1])
        best_solution[1].preview_image(CARTS, 0)
    else:
        print("No solution found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path")
    parser.add_argument("-p", "--show-preview", action="store_true",
                        help="show preview of the grid")

    args = parser.parse_args()
    main(args.input, args.show_preview)
