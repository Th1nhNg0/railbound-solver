from dataclasses import dataclass
from typing import Union, List
import numpy as np
from tile import Direction
from collections import defaultdict
import timeit
import copy


@dataclass
class Grid:
    data: Union[List[List[int]], np.ndarray]
    flows: dict = None

    def __post_init__(self):
        if isinstance(self.data, list):
            if not self.data or not all(self.data):
                raise ValueError("Input list must be a non-empty 2D array")
            self.height = len(self.data)
            self.width = len(self.data[0])
            if any(len(row) != self.width for row in self.data):
                raise ValueError("All rows must have the same length")
            self.data = np.array(self.data, dtype=int)
        elif isinstance(self.data, np.ndarray):
            if self.data.ndim != 2:
                raise ValueError("Input NumPy array must be 2D")
            self.height, self.width = self.data.shape
            self.data = self.data.astype(int)
        else:
            raise TypeError("Input must be either a 2D list or a NumPy array")
        if self.flows is None:
            self.flows = defaultdict(lambda: defaultdict(bool))

    def get(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return int(self.data[y, x])
        raise IndexError("Coordinates out of bounds")

    def set(self, x: int, y: int, value: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y, x] = value
        else:
            raise IndexError("Coordinates out of bounds")

    def get_flow(self, x: int, y: int) -> dict:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.flows[(x, y)]
        raise IndexError("Coordinates out of bounds")

    def add_flow(self, x: int, y: int, direction: Direction) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.flows[(x, y)][direction] = True
        else:
            raise IndexError("Coordinates out of bounds")

    def __str__(self) -> str:
        return "\n".join(
            " ".join(f"{self.get(x, y):2d}" for x in range(self.width))
            for y in range(self.height)
        )

    def __hash__(self) -> int:
        return hash(self.data.tobytes())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Grid):
            return NotImplemented
        return np.array_equal(self.data, other.data)

    def __deepcopy__(self, memo):
        return Grid(
            np.copy(self.data),
            self.flows,
        )


if __name__ == "__main__":
    # Example usage
    print("Creating grid from 2D list:")
    grid_from_list = Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(grid_from_list)
    print(f"Hash: {hash(grid_from_list)}")

    print("\nCreating grid from NumPy array:")
    np_array = np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]])
    grid_from_np = Grid(np_array)
    print(grid_from_np)
    print(f"Hash: {hash(grid_from_np)}")
