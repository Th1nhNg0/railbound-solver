import cv2
import numpy as np
from PIL import Image
from cart_simulation import simulate_cart_movement, create_tiles, DIRECTION, Cart
import os


def create_gif(frames, output_filename, duration=500):
    pil_frames = [Image.fromarray(cv2.cvtColor(
        frame, cv2.COLOR_BGR2RGB)) for frame in frames]
    pil_frames[0].save(
        output_filename,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration,
        loop=0
    )


def main():
    tiles = create_tiles()

    grid = [
        [1, 8, 7, 9, 3, 5, 9, 11, 13, 6],
        [3, 1, 11, 9, 10, 11, 9, 3, 4, 10],
        [1, 12, 7, 4, 7, 9, 11, 0, 1, 3],
        [4, 2, 9, 14, 11, 4, 8, 6, 12, 6],
        [0, 5, 9, 11, 5, 0, 0, 0, 1, 14],
        [14, 7, 13, 7, 9, 10, 2, 1, 8, 7],
        [7, 5, 9, 8, 7, 5, 5, 13, 2, 13],
        [9, 8, 12, 6, 3, 9, 11, 13, 8, 12],
        [9, 10, 6, 10, 2, 13, 11, 13, 14, 6],
        [8, 7, 1, 3, 4, 8, 11, 5, 5, 0]
    ]
    grid = [[6, 6, 6, 6, 6],
            ]
    # Create multiple carts with different starting positions and colors
    carts = [
        Cart(0, 0, DIRECTION['left'], color=(255, 0, 0), destination=(4, 0)),
    ]

    frames = simulate_cart_movement(grid, tiles, carts, max_iterations=20)
    create_gif(frames, 'multi_cart_simulation.gif')


if __name__ == "__main__":
    main()
