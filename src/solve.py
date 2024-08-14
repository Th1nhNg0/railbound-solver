from grid import Grid
from cart import Cart
from utils import DIRECTION, TimingManager
import cv2
import numpy as np
from collections import deque
import copy
import argparse
from pprint import pprint
import json


def preview_image(img, wait_time=0):
    cv2.imshow("Grid", np.array(img))
    cv2.waitKey(wait_time)


def load_data(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate the loaded data
    if not all(key in data for key in ["grid", "destination", "carts"]):
        raise KeyError("The loaded JSON is missing required keys.")

    return data


def main(
    input_file,
):

    data = load_data(input_file)
    pprint(data)

    g = Grid(data["grid"], destination=data["destination"])
    carts = [
        Cart((cart["x"], cart["y"]), DIRECTION(cart["direction"]), cart["order"])
        for cart in data["carts"]
    ]
    preview_image(g.get_image(carts), 0)

    ################################################################################################
    timer = TimingManager()
    iteration = 0
    queue = deque([(g, carts)])

    best_solution = None
    best_solution_min_tile = 1000000

    while len(queue):
        with timer.measure_time("Iteration"):
            iteration += 1
            # print(f"Iteration: {iteration}, Queue size: {len(queue)}", end="\r")
            g, carts = queue.popleft()
            if g.tile_placed_count >= best_solution_min_tile:
                continue
            g = copy.deepcopy(g)
            carts = copy.deepcopy(carts)
            # img = g.get_image(carts)
            # preview_image(img, 50)
            with timer.measure_time("Simulation"):
                result = g.simulate(carts, max_iter=10)

            if result[0] == "empty_pos_reached":
                with timer.measure_time("Get possible grid"):
                    possible_grids = g.get_possible_grid(result[1])
                for grid in possible_grids:
                    queue.append((grid, carts))
            if result[0] == "success":
                print("Success")
                print("Tiled placed: ", g.tile_placed_count)
                if g.tile_placed_count < best_solution_min_tile:
                    best_solution = g
                    best_solution_min_tile = g.tile_placed_count
                    print("Best solution updated")
                # img = g.get_image(carts)
                # preview_image(img, 0)
    timer.print()
    img = best_solution.get_image()
    preview_image(img, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path")
    parser.add_argument(
        "-p", "--show-preview", action="store_true", help="show preview of the grid"
    )

    args = parser.parse_args()
    main(args.input)
