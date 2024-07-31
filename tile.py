"""
This module contains the Tile class that represents a tile in the game.
"""

from PIL import Image, ImageDraw
import cv2
import numpy as np
import itertools
from utils import DIRECTION,  DIRECTION_TO_STR


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
        rotated_img = self.img.rotate(n * -90)
        rotated_edges = self.edges[-n:] + self.edges[:-n]
        flow = []
        for i, o in self.flow:
            i = (i + n) % 4
            o = (o + n) % 4
            flow.append((i, o))
        return Tile(self.name, rotated_img, rotated_edges, flow)

    def flip(self, axes='vertical') -> 'Tile':
        """
        Create a new Tile instance with the flipped image and edges.

        Args:
            axes (str): The axes to flip the image. vertical or horizontal.

        Returns:
            Tile: A new Tile instance with the flipped image and edges.
        """
        if axes == 'vertical':
            flipped_img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
            flipped_edges = (
                self.edges[2], self.edges[1], self.edges[0], self.edges[3])
            flow = []
            for i, o in self.flow:
                if i % 2 == 0:
                    i = (i + 2) % 4
                if o % 2 == 0:
                    o = (o + 2) % 4
                flow.append((i, o))
        elif axes == 'horizontal':
            flipped_img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_edges = (
                self.edges[0], self.edges[3], self.edges[2], self.edges[1])
            flow = []
            for i, o in self.flow:
                if i % 2 == 1:
                    i = (i + 2) % 4
                if o % 2 == 1:
                    o = (o + 2) % 4
                flow.append((i, o))
        return Tile(self.name, flipped_img, flipped_edges, flow)

    @ property
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

    def __repr__(self) -> str:
        flow = ', '.join(
            [f'({DIRECTION_TO_STR[i]}, {DIRECTION_TO_STR[o]})' for i, o in self.flow])
        return f'{self.name}(index={self.index},edges={self.edges}),flow={flow})'


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
                      (0, 1, 1, 0), [(DIRECTION['top'], DIRECTION['right']),
                                     (DIRECTION['left'], DIRECTION['bottom'])])
    straight_tile = Tile('Straight', Image.open(
        'images/Straight.png'), (1, 0, 1, 0), [(DIRECTION['top'], DIRECTION['bottom']),
                                               (DIRECTION['bottom'], DIRECTION['top'])])
    t_turn_tile = Tile('T_turn', Image.open('images/T turn.png'), (1, 0, 1, 1),
                       [(DIRECTION['bottom'], DIRECTION['bottom']),
                       (DIRECTION['right'], DIRECTION['bottom']),
                       (DIRECTION['top'], DIRECTION['left'])])
    rock_tile = Tile('Rock', Image.open(
        'images/Rock.png'), (0, 0, 0, 0), [])
    dead_end = Tile('Dead end', Image.open(
        'images/Dead end.png'), (1, 0, 0, 0), [])

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


if __name__ == '__main__':
    # preview the tiles
    tiles = create_tiles()
    for tile in tiles:
        print(tile)
        # show the image in a window, scale the image 4 times
        cv2.imshow('Tile', np.array(tile.image_with_edge_indicators))
        cv2.waitKey(0)
    cv2.destroyAllWindows()
