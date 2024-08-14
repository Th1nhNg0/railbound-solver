from utils import DIRECTION
import copy


class Cart:
    def __init__(
        self,
        position: tuple[int, int],
        direction: DIRECTION,
        order: int,
        reached_destination: bool = False,
    ):
        self.position = position
        self.previous_position = None
        self.direction = direction
        self.turn = 0
        self.order = order
        self.reached_destination = reached_destination

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    def __copy__(self):
        return Cart(
            position=copy.copy(self.position),
            direction=self.direction,
            order=self.order,
            reached_destination=self.reached_destination,
        )

    def __deepcopy__(self, memo):
        return Cart(
            position=copy.deepcopy(self.position),
            direction=self.direction,
            order=self.order,
            reached_destination=self.reached_destination,
        )

    def set_position(self, new_position: tuple[int, int]):
        self.previous_position = self.position
        self.position = new_position

    def set_direction(self, new_direction: DIRECTION):
        self.direction = new_direction
