"""
This module contains the Tile class that represents a tile in the game.
"""

from PIL import Image, ImageDraw
import itertools
from utils import DIRECTION, OPPOSITE_DIRECTION
import os


class Tile:
    """
    A class to represent a tile in the game.
    """

    __slots__ = ("name", "img", "edges", "index", "flow")
    index_counter = itertools.count()

    def __init__(self, name, img, edges, flow):
        """
        Initialize a new instance of the class.

        Args:
            name (str): The name of the tile.
            img (PIL.Image): The input image.
            edges (tuple of 4 ints): (top, right, bottom, left) edges of the tile.  When 2 edge on different tiles have the same value, they can be connected.
            flow (list of tuple of 2 ints): (i, o) i represents the direction of the object when it enters the tile, o represents the direction the object will exit the tile.

        Returns:
            None
        """
        self.name = name
        self.img = img
        self.edges = edges
        self.index = next(Tile.index_counter)
        self.flow = flow

    def rotate(self, n) -> "Tile":
        """
        Create a new Tile instance with the rotated image and edges.

        Args:
            n (int): The number of rotations.

        Returns:
            Tile: A new Tile instance with the rotated image and edges.
        """
        rotated_img = self.img.rotate(n * -90)
        rotated_edges = self.edges[-n:] + self.edges[:-n]
        flow = []
        for i, o in self.flow:
            i = DIRECTION((i + n) % 4)
            o = DIRECTION((o + n) % 4)
            flow.append((i, o))
        return Tile(self.name, rotated_img, rotated_edges, flow)

    def flip(self, axes="vertical") -> "Tile":
        """
        Create a new Tile instance with the flipped image and edges.

        Args:
            axes (str): The axes to flip the image. vertical or horizontal.

        Returns:
            Tile: A new Tile instance with the flipped image and edges.
        """
        if axes == "vertical":
            flipped_img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
            flipped_edges = (self.edges[2], self.edges[1], self.edges[0], self.edges[3])
            flow = []
            for i, o in self.flow:
                if i % 2 == 0:
                    i = DIRECTION((i + 2) % 4)
                if o % 2 == 0:
                    o = DIRECTION((o + 2) % 4)
                flow.append((i, o))
        elif axes == "horizontal":
            flipped_img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_edges = (self.edges[0], self.edges[3], self.edges[2], self.edges[1])
            flow = []
            for i, o in self.flow:
                if i % 2 == 1:
                    i = DIRECTION((i + 2) % 4)
                if o % 2 == 1:
                    o = DIRECTION((o + 2) % 4)
                flow.append((i, o))
        return Tile(self.name, flipped_img, flipped_edges, flow)

    @property
    def image_with_edge_indicators(self) -> Image:
        """
        Create a new image with the edge indicators. The edge indicators are
        drawn as text on the edges of the tile.

        Args:
            None

        Returns:
            Image: A new image with the edge indicators.
        """
        img = self.img.copy()
        draw = ImageDraw.Draw(img)
        # draw at center of each edge from top to left in clockwise order
        # the text should be inside the tile
        draw.text((img.width // 2, 0), str(self.edges[0]), fill="black")
        draw.text((img.width - 10, img.height // 2), str(self.edges[1]), fill="black")
        draw.text((img.width // 2, img.height - 10), str(self.edges[2]), fill="black")
        draw.text((0, img.height // 2), str(self.edges[3]), fill="black")
        return img

    def get_output_direction(self, input_direction) -> int:
        """
        Get the output direction based on the input direction.

        Args:
            input_direction (int): The input direction.

        Returns:
            int: The output direction.
        """
        for i, o in self.flow:
            if i == input_direction:
                return o
        return -1

    @staticmethod
    def check_connection(tile1, tile2, direction):
        """
        Check if two tiles can be connected.
        The tile1 is the original, tile2 is the target tile.
        Direction is the direction of tile2 relative to tile1.

        Args:
            tile1 (Tile): The original tile
            tile2 (Tile): The target tile
            direction (int): The direction of tile2 relative to tile1 (use DIRECTION constants)

        Returns:
            bool: True if the tiles can be connected, False otherwise

        Example:
        tile1 = Tile('Curve', Image.open('images/Curve.png'), (0, 1, 1, 0),
                     [(DIRECTION.TOP, DIRECTION.RIGHT), (DIRECTION.LEFT, DIRECTION.BOTTOM)])
        tile2 = Tile('Curve', Image.open('images/Curve.png'), (0, 1, 1, 0),
                     [(DIRECTION.TOP, DIRECTION.RIGHT), (DIRECTION.LEFT, DIRECTION.BOTTOM)])
        Tile.check_connection(tile1, tile2, DIRECTION.RIGHT)
        Means: check if the right edge of tile1 can be connected to the left edge of tile2.
        """
        # Get the edge indices for the connecting sides
        tile1_edge_index = direction
        tile2_edge_index = OPPOSITE_DIRECTION[direction]

        # Check if the edges match
        return tile1.edges[tile1_edge_index] == tile2.edges[tile2_edge_index]

    def __repr__(self) -> str:
        flow = ", ".join([f"({i.name}, {o.name})" for i, o in self.flow])
        return f"{self.name}(index={self.index},edges={self.edges}),flow={flow})"


def create_tiles() -> list[Tile]:
    """
    Create a list of tiles with different shapes and orientations.

    Args:
        None

    Returns:
        list: A list of tiles with different shapes and orientations
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tiles = []
    empty_tile = Tile(
        "Empty",
        Image.open(os.path.join(current_dir, "./images/Empty.png")),
        (0, 0, 0, 0),
        [],
    )

    curve_tile = Tile(
        "Curve",
        Image.open(os.path.join(current_dir, "./images/Curve.png")),
        (0, 1, 1, 0),
        [(DIRECTION.TOP, DIRECTION.RIGHT), (DIRECTION.LEFT, DIRECTION.BOTTOM)],
    )
    straight_tile = Tile(
        "Straight",
        Image.open(os.path.join(current_dir, "./images/Straight.png")),
        (1, 0, 1, 0),
        [(DIRECTION.TOP, DIRECTION.TOP), (DIRECTION.BOTTOM, DIRECTION.BOTTOM)],
    )
    t_turn_tile = Tile(
        "T_turn",
        Image.open(os.path.join(current_dir, "images/T turn.png")),
        (1, 0, 1, 1),
        [
            (DIRECTION.BOTTOM, DIRECTION.BOTTOM),
            (DIRECTION.RIGHT, DIRECTION.BOTTOM),
            (DIRECTION.TOP, DIRECTION.LEFT),
        ],
    )
    rock_tile = Tile(
        "Rock",
        Image.open(os.path.join(current_dir, "./images/Rock.png")),
        (0, 0, 0, 0),
        [],
    )

    tiles.append(empty_tile)
    tiles.append(curve_tile)
    tiles.append(curve_tile.rotate(1))
    tiles.append(curve_tile.rotate(2))
    tiles.append(curve_tile.rotate(3))
    tiles.append(straight_tile)
    tiles.append(straight_tile.rotate(1))
    tiles.append(t_turn_tile)
    tiles.append(t_turn_tile.rotate(1))
    tiles.append(t_turn_tile.rotate(2))
    tiles.append(t_turn_tile.rotate(3))
    tiles.append(t_turn_tile.flip())
    tiles.append(t_turn_tile.flip().rotate(1))
    tiles.append(t_turn_tile.flip().rotate(2))
    tiles.append(t_turn_tile.flip().rotate(3))

    tiles.append(rock_tile)

    # tiles.append(dead_end)
    # tiles.append(dead_end.rotate(1))
    # tiles.append(dead_end.rotate(2))
    # tiles.append(dead_end.rotate(3))
    # override the index of each tile for easy reference
    index = 0
    for tile in tiles:
        tile.index = index
        index += 1

    return tiles


def find_possible_tiles(grid, row, col):
    """
    Find all possible tiles that can be placed at a specific position in the grid.

    Args:
        grid (List[List[int]]): The grid of tile indices
        row (int): The row index of the position to check
        col (int): The column index of the position to check
        all_tiles (List[Tile]): List of all available tiles

    Returns:
        List[int]: List of indices of compatible tiles
    """
    height = len(grid)
    width = len(grid[0]) if grid else 0
    # make sure row and col are within the grid
    if row < 0 or row >= height or col < 0 or col >= width:
        return []
    # Get adjacent tile indices
    top = grid[row - 1][col] if row > 0 else None
    right = grid[row][col + 1] if col < width - 1 else None
    bottom = grid[row + 1][col] if row < height - 1 else None
    left = grid[row][col - 1] if col > 0 else None

    # Get edges of adjacent tiles
    top_edge = TILES[top].edges[2] if top is not None else 0
    right_edge = TILES[right].edges[3] if right is not None else 0
    bottom_edge = TILES[bottom].edges[0] if bottom is not None else 0
    left_edge = TILES[left].edges[1] if left is not None else 0

    top_edge = None if top == 0 else top_edge
    right_edge = None if right == 0 else right_edge
    bottom_edge = None if bottom == 0 else bottom_edge
    left_edge = None if left == 0 else left_edge

    compatible_tiles = []

    for tile in TILES:
        if (
            (top_edge is None or tile.edges[0] == top_edge)
            and (right_edge is None or tile.edges[1] == right_edge)
            and (bottom_edge is None or tile.edges[2] == bottom_edge)
            and (left_edge is None or tile.edges[3] == left_edge)
        ):
            compatible_tiles.append(tile.index)

    return compatible_tiles


TILES = create_tiles()


if __name__ == "__main__":
    grid =     [
        [0, 0, 5, 0, 0],
        [0, 1, 8, 2, 0],
        [0, 0, 15, 0, 0],
        [0, 4, 6, 3, 0],
        [5, 0, 0, 0, 5],
    ]
    # Example usage
    row = 0  # Choose the row you want to check
    col = 2  # Choose the column you want to check

    possible_tiles = find_possible_tiles(grid, row, col)

    print(f"Possible tiles for position ({row}, {col}): {possible_tiles}")
    for tile_index in possible_tiles:
        # print all possible grid with the possible tiles
        grid[row][col] = tile_index
        print(grid, ",")
