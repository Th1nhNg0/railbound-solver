import numpy as np
from utils import load_data
from pprint import pprint
from collections import deque
from state import State
from tile import Position, Direction
from train import Train


def solve(data, method: str = "bfs"):
    init_state = State(
        grid=np.array(data["grid"]),
        trains=[
            Train(
                position=Position(train["x"], train["y"]),
                direction=Direction(train["direction"]),
                order=train["order"],
            )
            for train in data["trains"]
        ],
        destination=Position(*data["destination"]),
        immutable_positions=data["immutable_positions"],
        effects=data["effects"],
    )
    queue = deque([init_state])

    iteration = 0
    best_solution = (None, data["max_tracks"] + 1)  # (state, score)

    while queue:
        iteration += 1
        if method == "dfs":
            state = queue.pop()
        if method == "bfs":
            state = queue.popleft()

        if state.placed_tiles > best_solution[1]:
            continue

        result = state.simulate()

        if result[0] == "simulate_success":
            positions_to_check = result[1]
            possible_states = state.generate_possible_states(positions_to_check)
            queue.extend(possible_states)
            # pprint(possible_states)
        if result[0] == "goal_reached":
            if state.placed_tiles <= best_solution[1]:
                best_solution = (state, state.placed_tiles)

    return best_solution


def run_profile(data):
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        solve(data)

    result = pstats.Stats(pr)
    result.sort_stats(pstats.SortKey.TIME)
    result.print_stats()
    result.dump_stats("solver_stats")


if __name__ == "__main__":
    data = load_data("1-1")
    # run_profile(data)
    result = solve(data, method="bfs")
    pprint(result)
