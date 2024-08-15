# This file contains the Grid class which represents the railbound puzzle board.
import cv2
from PIL import Image, ImageDraw
from utils import DIRECTION, DIRECTION_DELTA
import numpy as np
from tile import TILES, Tile, find_possible_tiles
import copy
import itertools
from cart import Cart


class Grid:
    def __init__(self, grid, destination, freeze_tiles=None, tile_placed_count=0):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.destination = tuple(destination)
        self.tile_placed_count = tile_placed_count
        if freeze_tiles is None:
            self._create_freeze_tiles()
        else:
            self.freeze_tiles = freeze_tiles

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def __str__(self):
        return "\n".join(" ".join(str(cell) for cell in row) for row in self.grid)

    def __repr__(self):
        return str(self)

    def __copy__(self):
        return Grid(
            grid=copy.copy(self.grid),
            destination=copy.copy(self.destination),
            freeze_tiles=copy.copy(self.freeze_tiles),
            tile_placed_count=self.tile_placed_count,
        )

    def __deepcopy__(self, memo):
        return Grid(
            grid=copy.deepcopy(self.grid),
            destination=copy.deepcopy(self.destination),
            freeze_tiles=copy.deepcopy(self.freeze_tiles),
            tile_placed_count=self.tile_placed_count,
        )

    def _create_freeze_tiles(self):
        self.freeze_tiles = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != 0:
                    self.freeze_tiles.add((x, y))

    def get_image(self, carts=None):
        """
        Generates an image representation of the railbound puzzle board.

        Args:
            carts(list[Cart], optional): A list of Cart objects representing the carts on the board. Defaults to None.

        Returns:
            PIL.Image.Image: The generated image.

        """
        img = Image.new("RGB", (self.width * 90, self.height * 90), color="white")
        imageDraw = ImageDraw.Draw(img)
        for y in range(self.height):
            for x in range(self.width):
                tile_index = self.grid[y][x]
                tile = TILES[tile_index]
                img.paste(tile.img, (x * 90, y * 90))
                # draw x-y coordinates
                imageDraw.text((x * 90 + 5, y * 90 + 75), f"{x}, {y}", fill="white")

        # draw grid lines
        for y in range(self.height + 1):
            imageDraw.line((0, y * 90, self.width * 90, y * 90), fill="black", width=1)
        for x in range(self.width + 1):
            imageDraw.line((x * 90, 0, x * 90, self.height * 90), fill="black", width=1)

        if carts is not None:
            for cart in carts:
                direction = cart.direction
                imageDraw.ellipse(
                    (
                        cart.x * 90 + 25,
                        cart.y * 90 + 25,
                        cart.x * 90 + 65,
                        cart.y * 90 + 65,
                    ),
                    fill="red",
                    outline="red",
                )

                # draw direction line
                center_x, center_y = cart.x * 90 + 45, cart.y * 90 + 45
                if direction == DIRECTION.TOP:
                    imageDraw.line(
                        (center_x, center_y, center_x, center_y - 20),
                        fill="black",
                        width=2,
                    )
                elif direction == DIRECTION.BOTTOM:
                    imageDraw.line(
                        (center_x, center_y, center_x, center_y + 20),
                        fill="black",
                        width=2,
                    )
                elif direction == DIRECTION.LEFT:
                    imageDraw.line(
                        (center_x, center_y, center_x - 20, center_y),
                        fill="black",
                        width=2,
                    )
                elif direction == DIRECTION.RIGHT:
                    imageDraw.line(
                        (center_x, center_y, center_x + 20, center_y),
                        fill="black",
                        width=2,
                    )

                # draw order number on cart
                imageDraw.text(
                    (cart.x * 90 + 35, cart.y * 90 + 35),
                    str(cart.order),
                    fill="white",
                )
        return img

    def get_image_with_highlighted_tiles(self, pos_to_highlight: list[tuple[int, int]]):
        """
        Generates an image representation of the railbound puzzle board with highlighted tiles.

        Args:
            pos_to_highlight (List[Tuple[int, int]]): A list of positions to highlight.

        Returns:
            PIL.Image.Image: The generated image.
        """
        img = self.get_image()
        for x, y in pos_to_highlight:
            self._highlight_tile(img, x, y)
        return img

    def _highlight_tile(self, img, x, y, color="red"):
        imageDraw = ImageDraw.Draw(img)
        imageDraw.rectangle(
            (x * 90, y * 90, x * 90 + 90, y * 90 + 90),
            outline=color,
            width=2,
        )

    def get_possible_grid(
        self, pos_to_place_tile: list[tuple[int, int]]
    ) -> list["Grid"]:
        """
        Generates all possible grids by placing tiles on the board.

        Args:
            pos_to_place_tile (List[Tuple[int, int]]): A list of positions to place tiles.

        Returns:
            List[Grid]: A list of new grid configurations with tiles placed on the board.
        """
        # Generate all possible combinations of tile placements
        tile_combinations = []
        for pos in pos_to_place_tile:
            possible_tiles = find_possible_tiles(self.grid, pos[1], pos[0])
            tile_combinations.append(possible_tiles)
        tile_combinations = itertools.product(*tile_combinations)
        possible_grids = []
        for combination in tile_combinations:
            new_grid = copy.deepcopy(self)
            for (x, y), tile_idx in zip(pos_to_place_tile, combination):
                new_grid[y][x] = tile_idx
            if new_grid.is_tiles_valid(pos_to_place_tile):
                new_grid.tile_placed_count += len(pos_to_place_tile)
                possible_grids.append(new_grid)

        return possible_grids

    def is_tiles_valid(self, tiles: list[tuple[int, int]]):
        """
        Check if the grid configuration is valid.

        Returns:
            bool: True if the grid is valid, False otherwise.
        """
        for x, y in tiles:
            tile = TILES[self.grid[y][x]]
            for direction in DIRECTION:
                nx = x + DIRECTION_DELTA[direction][0]
                ny = y + DIRECTION_DELTA[direction][1]
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    if tile.edges[direction] != 0 and (x, y) not in self.freeze_tiles:
                        return False
                    continue
                next_tile = TILES[self.grid[ny][nx]]
                if next_tile.name == "Empty":
                    continue
                if not Tile.check_connection(tile, next_tile, direction):
                    return False
        return True

    def simulate(self, carts: list[Cart], max_iter=100):
        """
        Simulate the movement of carts on the board.

        Args:
            carts (List[Cart]): A list of Cart objects representing the carts on the board.
        """
        empty_pos_reached = set()
        while len(empty_pos_reached) == 0 and max_iter > 0:
            max_iter -= 1
            # update cart position and check for empty position reached
            for cart in carts:
                if cart.reached_destination:
                    continue
                cart_x, cart_y = cart.position
                current_tile: Tile = TILES[self.grid[cart_y][cart_x]]
                output_direction = current_tile.get_output_direction(cart.direction)
                next_x = cart_x + DIRECTION_DELTA[output_direction][0]
                next_y = cart_y + DIRECTION_DELTA[output_direction][1]

                cart.set_position((next_x, next_y))
                cart.set_direction(output_direction)
                if (0 <= next_x < self.width) and (0 <= next_y < self.height):
                    next_tile: Tile = TILES[self.grid[next_y][next_x]]
                    if next_tile.name == "Empty":
                        empty_pos_reached.add((next_x, next_y))
                if (next_x, next_y) == self.destination:
                    cart.reached_destination = True
            # check for collision
            for cart in carts:
                if cart.reached_destination:
                    continue
                # is cart run out of the board
                if not (0 <= cart.x < self.width and 0 <= cart.y < self.height):
                    return ("collision", "cart run out of the board")
                if TILES[self.grid[cart.y][cart.x]].name == "Rock":
                    return ("collision", "cart hit rock")
                for other_cart in carts:
                    if cart == other_cart:
                        continue
                    if cart.position == other_cart.position:
                        return ("collision", "cart collision")
                    if (
                        cart.position == other_cart.previous_position
                        and cart.previous_position == other_cart.position
                    ):
                        return ("collision", "cart collision")
            # check if cart reached destination in order, ex: cart with order 1 should reach destination before cart with order 2
            for cart in carts:
                for other_cart in carts:
                    if cart == other_cart:
                        continue
                    if cart.order > other_cart.order:
                        if (
                            cart.reached_destination
                            and not other_cart.reached_destination
                        ):
                            return (
                                "collision",
                                "cart with lower order reached destination first",
                            )
            # check if all carts reached destination
            if all(cart.reached_destination for cart in carts):
                return ("success", "all carts reached destination")
        if max_iter == 0:
            return ("max_iter_reached", "max iteration reached")
        return ("empty_pos_reached", list(empty_pos_reached))


if __name__ == "__main__":
    test_data = [
        [0, 0, 5, 0, 0],
        [0, 1, 8, 2, 0],
        [0, 0, 15, 0, 0],
        [0, 4, 6, 3, 0],
        [5, 0, 0, 0, 5],
    ]
    g = Grid(test_data, destination=(0, 0))
    print("Original grid:")
    print(g)

    pos_to_place_tiles = [(1, 2), (0, 3), (0, 2)]
    # find 2 random empty cells to place tiles
    while len(pos_to_place_tiles) < 2:
        x = np.random.randint(0, g.width)
        y = np.random.randint(0, g.height)
        if g[y][x] == 0:
            pos_to_place_tiles.append((x, y))

    img = g.get_image_with_highlighted_tiles(pos_to_place_tiles)
    cv2.imshow("Grid", np.array(img))
    cv2.waitKey(0)

    possible_grids = g.get_possible_grid(pos_to_place_tiles)

    print(f"\nNumber of possible grids: {len(possible_grids)}")
    for i, grid in enumerate(possible_grids):  # Print first 5 grids as an example
        print(f"\nPossible grid {i + 1}:")
        print(grid)
        img = grid.get_image_with_highlighted_tiles(pos_to_place_tiles)
        cv2.imshow("Grid", np.array(img))
        cv2.waitKey(0)
