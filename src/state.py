from dataclasses import dataclass, field
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
    effects: dict[Position, tuple[str, any]]
    loop_detection: set = field(default_factory=set)
    order_counter: int = 0
    placed_tiles: int = 0

    def simulate(self):
        pos_to_check = []

        new_trains = []
        # move trains
        for train in self.trains:
            current_pos = train.position
            if current_pos == self.destination:
                continue
            current_tile = Tile(self.grid[current_pos.y][current_pos.x])

            if train.position in self.effects:
                # TODO: SIMULATE EFFECT
                pass
            else:
                output_direction = current_tile.get_output_direction(train.direction)
                if output_direction == -1:
                    return ("collision", "train hit invalid track")
                next_position = train.position + output_direction.delta
                new_train = train.move(next_position, output_direction)
            new_trains.append(new_train)
            if (
                0 <= next_position.x < len(self.grid[0])
                and 0 <= next_position.y < len(self.grid)
                and next_position not in self.immutable_positions
            ):
                pos_to_check.append(next_position)
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
                0 <= train.position.x < len(self.grid[0])
                and 0 <= train.position.y < len(self.grid)
            ):
                return ("collision", "train run out of the board")
            if Tile(self.grid[train.position.y][train.position.x]) == Tile.FENCE:
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
            return ("goal_reached", "all trains reached destination")

        # check if there is a loop
        new_pos = hash(tuple(train.position for train in new_trains))
        if new_pos in self.loop_detection:
            return ("loop", "loop detected")
        self.loop_detection.add(new_pos)

        # update trains
        self.trains = new_trains
        print(new_trains)
        return ("simulate_success", pos_to_check)

    def generate_possible_states(self, positions_to_check):
        # TODO: generate possible states
        return []


if __name__ == "__main__":
    state = State(
        grid=np.array([[1, 6, 2], [5, 0, 5], [4, 6, 3]]),
        trains=[Train(Position(2, 1), Direction.TOP, 1)],
        destination=Position(2, 2),
        immutable_positions={Position(1, 1)},
        effects={},
    )
    print(state.simulate())
