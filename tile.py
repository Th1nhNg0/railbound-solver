"""
This module contains the Tile class that represents a tile in the game.

The Tile class has the following attributes:
    - name (str): The name of the tile.
    - img (PIL.Image): The image of the tile.
    - edges (tuple of 4 ints): The edges of the tile (top, right, bottom, left).

The Tile class has the following methods:
    - rotate(n: int) -> Tile: Rotates the tile by n * 90 degrees.
    - flip() -> Tile: Flips the tile horizontally.
    - __str__() -> str: Returns a string representation of the tile.
    - __repr__() -> str: Returns a string representation of the tile.
"""

from PIL import Image, ImageDraw
import cv2
import numpy as np
import itertools


# define direction: 0: top, 1: right, 2: bottom, 3: left

DIRECTION = {
    'top': 0,
    'right': 1,
    'bottom': 2,
    'left': 3
}


class Tile:
    """
    A class to represent a tile in the game.
    """

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

    def rotate(self, n) -> 'Tile':
        """
        Create a new Tile instance with the rotated image and edges.

        Args:
            n (int): The number of rotations.

        Returns:
            Tile: A new Tile instance with the rotated image and edges.
        """
        rotated_img = self.img.rotate(n * 90)
        rotated_edges = self.edges[n:] + self.edges[:n]
        flow = []
        for i, o in self.flow:
            i = (i + n) % 4
            o = (o + n) % 4
            flow.append((i, o))
        return Tile(self.name, rotated_img, rotated_edges, flow)

    def flip(self) -> 'Tile':
        """
        Create a new Tile instance with the flipped image and edges.

        Args:
            None

        Returns:
            Tile: A new Tile instance with the flipped image and edges.
        """
        flipped_img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
        flipped_edges = self.edges[2:] + self.edges[:2]
        flow = []
        for i, o in self.flow:
            i = (i + 2) % 4
            o = (o + 2) % 4
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
        draw.text((img.width // 2, 0), str(self.edges[0]), fill='black')
        draw.text((img.width - 10, img.height // 2),
                  str(self.edges[1]), fill='black')
        draw.text((img.width // 2, img.height-10),
                  str(self.edges[2]), fill='black')
        draw.text((0, img.height // 2
                   ), str(self.edges[3]), fill='black')
        return img

    def __str__(self) -> str:
        return f'{self.name}-{self.index}'

    def __repr__(self) -> str:
        return f'{self.name}(index={self.index},edges={self.edges})'


def create_tiles() -> list[Tile]:
    """
    Create a list of tiles with different shapes and orientations.

    Args:
        None

    Returns:
        list: A list of tiles with different shapes and orientations
    """

    tiles = []
    empty_tile = Tile('Empty', Image.open(
        'images/Empty.png'), (0, 0, 0, 0), [])
    curve_tile = Tile('Curve', Image.open('images/Curve.png'),
                      (0, 1, 1, 0), [(DIRECTION['right'], DIRECTION['bottom']),
                                     (DIRECTION['bottom'], DIRECTION['right'])])
    straight_tile = Tile('Straight', Image.open(
        'images/Straight.png'), (1, 0, 1, 0), [(DIRECTION['top'], DIRECTION['bottom']),
                                               (DIRECTION['bottom'], DIRECTION['top'])])
    t_turn_tile = Tile('T_turn', Image.open('images/T turn.png'), (1, 0, 1, 1),
                       [(DIRECTION['top'], DIRECTION['bottom']),
                        (DIRECTION['left'], DIRECTION['bottom']),
                        (DIRECTION['bottom'], DIRECTION['left'])])

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

    # override the index of each tile for easy reference
    index = 0
    for tile in tiles:
        tile.index = index
        index += 1

    return tiles


if __name__ == '__main__':
    # preview the tiles
    tiles = create_tiles()
    for tile in tiles:
        print(tile)
        # show the image in a window, scale the image 4 times
        cv2.imshow('Tile', np.array(tile.image_with_edge_indicators))
        cv2.waitKey(0)
    cv2.destroyAllWindows()
