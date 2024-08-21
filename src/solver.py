import os
import re
import time
from collections import deque

import cv2
import numpy as np

from draw import Draw
from grid import Grid
from tile import Position
from utils import load_data
from state import State, Train

drawer = Draw()


def solve(data: dict, method: str = "bfs"):
    if method not in ["bfs", "dfs"]:
        raise ValueError("Invalid method")
    trains = [
        Train(
            Position(train["x"], train["y"]),
            train["direction"],
            train["order"],
        )
        for train in data["trains"]
    ]
    grid = Grid(data["grid"])
    state = State(grid, trains, Position(*data["destination"]))
    queue = deque([state])
    # img = drawer.draw(state)
    # cv2.imshow("image", cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
    # cv2.waitKey(1000)

    iteration = 0
    best_solution = None
    best_min_placed_tiles = data["max_tracks"] + 1 if "max_tracks" in data else 10000
    while queue:
        iteration += 1
        if method == "dfs":
            state = queue.pop()
        if method == "bfs":
            state = queue.popleft()

        if state.placed_tiles > best_min_placed_tiles:
            continue

        # img = drawer.draw(state)
        # cv2.imshow("image", cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
        # cv2.waitKey(1)
        result = state.simulate()

        if result[0] == "empty_pos_reached":
            empty_positions = result[1]
            possible_states = state.place_possible_tiles(empty_positions)
            queue.extend(possible_states)

        if result[0] == "success":
            if state.placed_tiles <= best_min_placed_tiles:
                best_solution = state
                best_min_placed_tiles = state.placed_tiles

    return {
        "best_solution": best_solution,
        "iteration": iteration,
    }


def solve_all():
    levels = os.listdir("./src/levels/")
    levels = sorted(levels, key=lambda x: list(map(int, re.findall(r"\d+", x))))
    for filename in levels:
        if filename.endswith(".json"):
            file_path = os.path.join("./src/levels/", filename)
            data = load_data(file_path)
            start_time = time.time()
            print(f"Solving {filename}")
            solution = solve(data, "bfs")
            print("--- %s seconds ---" % (time.time() - start_time))
            if solution["best_solution"] is not None:
                print(f'Found solution in {solution["iteration"]} iterations')
                img = drawer.draw(solution["best_solution"])
                # save to ./src/solutions
                cv2.imwrite(
                    f"./src/solutions/{filename.split('.')[0]}.png",
                    cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB),
                )


def solve_one(filepath, showImage=False):
    data = load_data(filepath)
    start_time = time.time()
    print(f"Solving {filepath}")
    solution = solve(data, "dfs")
    print("--- %s seconds ---" % (time.time() - start_time))
    if solution["best_solution"] is not None:
        print(f'Found solution in {solution["iteration"]} iterations')
        print(f"Placed tiles: {solution['best_solution'].placed_tiles}")

        if showImage:
            img = drawer.draw(solution["best_solution"], debug=True)
            cv2.imshow("image", cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
            cv2.waitKey(0)


def run_profile(filepath):
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        solve_one(filepath)

    result = pstats.Stats(pr)
    result.sort_stats(pstats.SortKey.TIME)
    result.print_stats()
    result.dump_stats("solver_stats")


if __name__ == "__main__":
    # run_profile("./src/levels/1-11A.json")
    solve_one("./src/levels/test.json", showImage=True)
    # solve_all()
