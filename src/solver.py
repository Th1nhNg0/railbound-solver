import json
from grid import Grid
from dataclasses import dataclass
from tile import Direction, Tile, Position
from collections import deque
import copy
from typing import Optional


def load_data(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


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
        )

    def __deepcopy__(self, memo):
        return State(
            copy.deepcopy(self.grid, memo),
            copy.deepcopy(self.trains, memo),
            self.destination,
            self.order_counter,
        )

    def simulate(self):
        empty_pos_reached = set()
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
                        empty_pos_reached.add(next_position)

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


def solve(data: dict):
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
    while queue:
        state = queue.popleft()
        result = state.simulate()


if __name__ == "__main__":
    data = load_data("./src/levels/1-1.json")
    solve(data)
