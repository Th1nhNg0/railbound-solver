from dataclasses import dataclass
import numpy as np
from tile import Position, Direction, Tile
from train import Train
from typing import Optional


@dataclass
class State:
    grid: np.ndarray
    trains: list[Train]
    destination: Position
    immutable_positions: Optional[set[Position]]
    order_counter: int = 0
    placed_tiles: int = 0
    effects: Optional[dict[Position, tuple[str, any]]] = None

    def simulate(self):
        pos_to_check = []
        loop_detection = {}

        while True:
            new_trains = []
            for train in self.trains:
                current_pos = train.position
                if current_pos == self.destination:
                    continue
                current_tile = Tile(self.grid[current_pos.y][current_pos.x])

                if train.position in self.effects:
                    # do something
                    pass
                else:
                    output_direction = current_tile.get_output_direction(
                        train.direction
                    )
                    if output_direction == -1:
                        return ("wrong_direction", "invalid track direction")
                    next_position = train.position + output_direction.delta
                    new_train = train.move(next_position, output_direction)
                new_trains.append(new_train)

                # check if next_position is in the grid
                if (
                    next_position.x < 0
                    or next_position.x >= len(self.grid[0])
                    or next_position.y < 0
                    or next_position.y >= len(self.grid)
                ):
                    return ("simulate_finish", "train out of bounds")

        return ("simulate_success", [(0, 0)])

    def generate_possible_states(self, positions_to_check):
        return []
