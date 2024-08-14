from grid import Grid
from cart import Cart
from utils import DIRECTION
import cv2
import numpy as np


def preview_image(img):
    cv2.imshow("Grid", np.array(img))
    cv2.waitKey(1000)


if __name__ == "__main__":
    test_data = [
        [5, 0, 0, 5],
        [5, 0, 0, 5],
        [0, 3, 4, 0],
        [0, 2, 1, 0],
        [5, 0, 0, 5],
        [5, 0, 0, 5],
    ]
    g = Grid(test_data, destination=(3, 0))
    carts = [
        Cart((3, 5), 0, order=1),
        Cart((0, 0), 2, order=1),
        Cart((0, 5), 0, order=1),
    ]
    img = g.get_image(carts)
    preview_image(img)
    result = g.simulate(carts)
    if result[0] == "empty_pos_reached":
        possible_grids = g.get_possible_grid(result[1])
        print(f"Possible grids: {len(possible_grids)}")
        for grid in possible_grids:
            img = grid.get_image(carts)
            preview_image(img)
