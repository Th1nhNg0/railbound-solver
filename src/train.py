"""
This module contains the Train class which represents a train object.
The Train class has the following attributes:
- position: The current position of the train.
- direction: The direction in which the train is moving.
- order: The order of the train.
- previous_position: The previous position of the train (optional).
The Train class has the following methods:
- __hash__(): Returns the hash value of the train object.
- __eq__(other): Checks if the train object is equal to another train object.
- move(position, direction): Moves the train to a new position in the specified direction.
Example usage:
train = Train(Position(0, 0), Direction.NORTH, 1)
new_train = train.move(Position(1, 0), Direction.EAST)

"""

from dataclasses import dataclass
from typing import Optional
from tile import Position, Direction


@dataclass
class Train:
    """
    Represents a train object.

    Attributes:
        position (Position): The current position of the train.
        direction (Direction): The direction in which the train is moving.
        order (int): The order of the train.
        previous_position (Optional[Position]): The previous position of the train.

        Methods:
        __hash__(): Returns the hash value of the train object.
        __eq__(other): Checks if the train object is equal to another train object.
        move(position, direction): Moves the train to a new position in the specified direction.

    """

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

    def move(self, postion: Position, direction: Direction):
        """
        Moves the train to a new position in the specified direction.

        Args:
            postion (Position): The new position for the train.
            direction (Direction): The direction in which the train should move.

        Returns:
            Train: A new Train object with the updated position and direction.
        """
        return Train(postion, direction, self.order, self.position)
