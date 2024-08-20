import copy
from collections import deque
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np

from draw import Draw
from grid import Grid
from tile import TILES_CONNECT, Direction, Position, Tile
from utils import load_data, TimingManager

timer = TimingManager(enabled=False)
drawer = Draw()


@dataclass
class Train:
    position: Position
    direction: Direction
    order: int
    previous_position: Optional[Position] = None

    def __hash__(self):
        return hash((self.position, self.direction, self.order))

    def __eq__(self, other):
        return (
            self.position == other.position
            and self.direction == other.direction
            and self.order == other.order
        )


@dataclass
class State:
    grid: Grid
    trains: list[Train]
    destination: Position
    order_counter: int = 0
    placed_tiles: int = 0
    immutable_positions: list[Position] = None

    def __post_init__(self):
        if self.immutable_positions is None:
            self.immutable_positions = [
                Position(x, y)
                for x in range(self.grid.width)
                for y in range(self.grid.height)
                if self.grid.get(x, y) != Tile.EMPTY
            ]

    def __hash__(self):
        return hash((self.grid, tuple(self.trains)))

    def __eq__(self, other):
        return self.grid == other.grid and self.trains == other.trains

    def __copy__(self):
        return State(
            copy.copy(self.grid),
            copy.copy(self.trains),
            self.destination,
            self.order_counter,
            self.placed_tiles,
            self.immutable_positions,
        )

    def __deepcopy__(self, memo):
        return State(
            copy.deepcopy(self.grid, memo),
            copy.deepcopy(self.trains, memo),
            self.destination,
            self.order_counter,
            self.placed_tiles,
            self.immutable_positions,
        )

    def simulate(self):
        empty_pos_reached = []
        max_iter = 100
        while len(empty_pos_reached) == 0 and max_iter > 0:
            max_iter -= 1
            # update train position and check for empty position reached
            for train in self.trains:
                if train.position == self.destination:
                    continue

                output_direction = Tile(
                    self.grid.get(*train.position)
                ).get_output_direction(train.direction)
                next_position = train.position + output_direction.delta
                train.previous_position = train.position
                train.position = next_position
                train.direction = output_direction

                if (0 <= next_position.x < self.grid.width) and (
                    0 <= next_position.y < self.grid.height
                ):
                    next_tile = self.grid.get(next_position.x, next_position.y)
                    if next_tile == Tile.EMPTY:
                        empty_pos_reached.append((next_position, output_direction))

                    # TODO: SIMULATE INTERACTION OF THE TILE IF NEEDED

                if next_position == self.destination:
                    if train.order == self.order_counter + 1:
                        self.order_counter += 1
                    else:
                        return (
                            "wrong_order",
                            "train reached destination in wrong order",
                        )
            # check for collision
            for train in self.trains:
                if train.position == self.destination:
                    continue
                # is train run out of the board
                if not (
                    0 <= train.position.x < self.grid.width
                    and 0 <= train.position.y < self.grid.height
                ):
                    return ("collision", "train run out of the board")
                if self.grid.get(*train.position) == Tile.FENCE:
                    return ("collision", "train hit FENCE")

                for other_cart in self.trains:
                    if train == other_cart:
                        continue
                    if train.position == other_cart.position:
                        return ("collision", "train collision")
                    if (
                        train.position == other_cart.previous_position
                        and train.previous_position == other_cart.position
                    ):
                        return ("collision", "train collision")
            # check if all trains reached destination
            if all(train.position == self.destination for train in self.trains):
                return ("success", "all trains reached destination")
        if max_iter == 0:
            return ("max_iter_reached", "max iteration reached")
        return ("empty_pos_reached", list(empty_pos_reached))

    def place_possible_tiles(self, empty_positions: list[tuple[Position, Direction]]):
        new_states: list[State] = []
        self._recursive_tile_placement(
            empty_positions, 0, copy.deepcopy(self), new_states
        )
        # filtering out invalid placements
        result = []
        with timer.measure_time("Filtering state_1"):
            for state in new_states:
                for pos, input_direction in empty_positions:
                    tile = Tile(state.grid.get(pos.x, pos.y))
                    if not state.is_valid_placement(pos, tile):
                        output_direction = tile.get_output_direction(input_direction)
                        adjacent_pos = pos + output_direction.delta
                        # try to change the adjacent tile to make the placement valid
                        if (
                            0 <= adjacent_pos.x < state.grid.width
                            and 0 <= adjacent_pos.y < state.grid.height
                            and adjacent_pos not in self.immutable_positions
                        ):
                            adjacent_tile = Tile(
                                state.grid.get(adjacent_pos.x, adjacent_pos.y)
                            )
                            if (
                                adjacent_tile != Tile.EMPTY
                                and adjacent_tile != Tile.FENCE
                                and not adjacent_tile.is_t_turn
                                and not TILES_CONNECT[tile][adjacent_tile][
                                    output_direction
                                ]
                            ):
                                if adjacent_tile.is_curve:
                                    to_change = adjacent_tile.to_t_turn(
                                        output_direction.opposite
                                    )
                                    if to_change != -1:
                                        state.grid.set(
                                            adjacent_pos.x, adjacent_pos.y, to_change
                                        )
                                if adjacent_tile.is_straight:
                                    flow = state.grid.get_flow(
                                        adjacent_pos.x, adjacent_pos.y
                                    )

                                    if len(flow) == 1:
                                        key = next(iter(flow))
                                        to_change = adjacent_tile.to_t_turn(
                                            output_direction.opposite, key
                                        )
                                        if to_change != -1:
                                            state.grid.set(
                                                adjacent_pos.x,
                                                adjacent_pos.y,
                                                to_change,
                                            )

                        # try to change the current tile to make the placement valid
                        for direction in Direction:
                            if (
                                direction == input_direction.opposite
                                or direction == output_direction
                            ):
                                continue
                            adjacent_pos = pos + direction.delta
                            if (
                                0 <= adjacent_pos.x < state.grid.width
                                and 0 <= adjacent_pos.y < state.grid.height
                            ):
                                adjacent_tile = Tile(
                                    state.grid.get(adjacent_pos.x, adjacent_pos.y)
                                )
                                if (
                                    adjacent_tile == Tile.EMPTY
                                    or adjacent_tile == Tile.FENCE
                                ):
                                    continue
                                adj_connection = (
                                    adjacent_tile.get_connection_direction()
                                )
                                if adj_connection[direction.opposite]:
                                    direction_flow = None
                                    if tile.is_straight:
                                        direction_flow = input_direction
                                    to_change = tile.to_t_turn(
                                        direction, direction_flow
                                    )
                                    if to_change != -1:
                                        state.grid.set(pos.x, pos.y, to_change)
        with timer.measure_time("Filtering state_2"):
            result = [
                state
                for state in new_states
                if all(
                    state.is_valid_placement(pos, Tile(state.grid.get(pos.x, pos.y)))
                    for pos, _ in empty_positions
                )
            ]
        return result

    def _recursive_tile_placement(
        self,
        empty_positions: list[tuple[Position, Direction]],
        index: int,
        current_state: "State",
        new_states: list["State"],
    ):
        if index == len(empty_positions):
            new_states.append(current_state)
            return

        pos, direction = empty_positions[index]
        for tile in Tile:
            if not (tile.is_curve or tile.is_straight):
                continue
            adjacent_pos = pos - direction.delta
            if (
                0 <= adjacent_pos.x < self.grid.width
                and 0 <= adjacent_pos.y < self.grid.height
            ):
                adjacent_tile = Tile(self.grid.get(adjacent_pos.x, adjacent_pos.y))
                if (
                    adjacent_tile != Tile.EMPTY
                    and not TILES_CONNECT[tile][adjacent_tile][direction.opposite]
                ):
                    continue

            new_state = copy.deepcopy(current_state)
            new_state.grid.set(pos.x, pos.y, tile)
            if tile.is_straight:
                new_state.grid.add_flow(pos.x, pos.y, direction)
            new_state.placed_tiles += 1
            self._recursive_tile_placement(
                empty_positions, index + 1, new_state, new_states
            )

    def is_valid_placement(self, pos: Position, new_tile: Tile) -> bool:
        for direction in Direction:
            adjacent_pos = pos + direction.delta
            if (
                0 <= adjacent_pos.x < self.grid.width
                and 0 <= adjacent_pos.y < self.grid.height
            ):
                adjacent_tile = Tile(self.grid.get(adjacent_pos.x, adjacent_pos.y))
                if (
                    adjacent_tile != Tile.EMPTY
                    and not TILES_CONNECT[new_tile][adjacent_tile][direction]
                ):
                    return False
        return True


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
    # img = drawer.draw(state.grid)
    # cv2.imshow("image", cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
    # cv2.waitKey(1000)

    timer.reset()
    iteration = 0
    best_solution = None
    best_min_placed_tiles = data["max_tracks"] + 1 if "max_tracks" in data else 10000
    while queue:
        iteration += 1
        with timer.measure_time("Iteration"):
            if method == "dfs":
                state = queue.pop()
            if method == "bfs":
                state = queue.popleft()

            if state.placed_tiles > best_min_placed_tiles:
                continue
            with timer.measure_time("Simulation"):
                result = state.simulate()

            if result[0] == "empty_pos_reached":
                with timer.measure_time("Place Possible Tiles"):
                    empty_positions = result[1]
                    possible_states = state.place_possible_tiles(empty_positions)
                    queue.extend(possible_states)

            if result[0] == "success":
                if state.placed_tiles <= best_min_placed_tiles:
                    best_solution = state
                    best_min_placed_tiles = state.placed_tiles

    timer.print()
    return {
        "best_solution": best_solution,
        "iteration": iteration,
    }


if __name__ == "__main__":
    data = load_data("./src/levels/1-11A.json")
    solution = solve(data, "dfs")
    if solution["best_solution"] is not None:
        print(f'Found solution in {solution["iteration"]} iterations')
        img = drawer.draw(solution["best_solution"].grid)
        cv2.imshow("image", cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
        cv2.waitKey(0)
