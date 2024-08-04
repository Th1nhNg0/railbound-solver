import copy
import cv2
import numpy as np
import PIL
from tile import create_tiles, Tile
from utils import DIRECTION, DIRECTION_TO_STR, flip_direction

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

    def __repr__(self):
        return "Grid(\n{}\n)".format(self.grid)

    def __str__(self):
        return self.__repr__()

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


def find_solution(i_grid: Grid, i_carts: list[Cart], destination: tuple[int, int]):

    stack: list[tuple[Grid, list[Cart]]] = []
    stack.append((i_grid, i_carts))

    while stack:
        grid, carts = stack.pop()
        carts = copy.deepcopy(carts)
        grid.preview_image(carts, 1)
        pos_to_place_tile = []
        should_skip = False

        max_steps = 10
        while len(pos_to_place_tile) == 0 and max_steps > 0:
            max_steps -= 1
            for cart in (carts):
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
                    continue

                cart.move(next_x, next_y, cart.direction)

                if next_tile.name == 'Empty':
                    pos_to_place_tile.append((next_x, next_y))
                else:
                    cart.update_direction(next_tile)

            if any(cart.crashed for cart in carts):
                should_skip = True
                break

            if all(cart.reached_destination for cart in carts):
                should_skip = True
                print("Solution found")
                print("Grid:")
                print(grid)
                grid.preview_image(i_carts)
                break

        if should_skip:
            continue

        for new_grid in grid.get_possible_grid(pos_to_place_tile):
            new_carts = copy.deepcopy(carts)
            for cart in new_carts:
                tile = new_grid.get_tile(cart.x, cart.y)
                cart.update_direction(tile)
            stack.insert(0, (new_grid, new_carts))


if __name__ == "__main__":
    MAX_PLACEMENT = 6
    GRID_DATA = np.array([[5, 0, 0],
                          [0, 0, 0],
                          [0, 0, 5],
                          [0, 0, 0],
                          [5, 0, 0]])
    CARTS = [
        Cart(x=0, y=4, direction=DIRECTION['top'], order=1),
        Cart(x=2, y=2, direction=DIRECTION['top'], order=2),
    ]
    DESTINATION = (0, 0)
    GRID = Grid(GRID_DATA, MAX_PLACEMENT)
    GRID.preview_image(CARTS)
    find_solution(GRID, CARTS, DESTINATION)
