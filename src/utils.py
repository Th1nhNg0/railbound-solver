import json
import time
from collections import defaultdict
from contextlib import contextmanager
from statistics import mean


class TimingManager:
    def __init__(self, enabled=True):
        self.execution_times = defaultdict(list)
        self.current_operations = []
        self.enabled = enabled

    @contextmanager
    def measure_time(self, operation_name):
        if not self.enabled:
            yield
            return

        full_operation_name = "/".join(self.current_operations +
                                       [operation_name])
        self.current_operations.append(operation_name)
        start_time = time.perf_counter()
        try:
            yield
        finally:
            if self.enabled:
                end_time = time.perf_counter()
                self.execution_times[full_operation_name].append(
                    end_time - start_time)
                self.current_operations.pop()

    def print_averages(self):
        if not self.enabled:
            print("Timing is disabled.")
            return
        for operation, times in sorted(self.execution_times.items()):
            avg_time = mean(times)
            total_time = sum(times)
            indent = "  " * (operation.count("/"))
            print(
                f"{indent}{operation.split('/')[-1]}: {avg_time:.6f} seconds (total: {total_time:.6f} seconds)")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def reset(self):
        self.execution_times = defaultdict(list)


def load_grid(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["grid"], data["destination"] if data["destination"] else None


class DIRECTION:
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


DIRECTION_TO_STR = {
    0: 'top',
    1: 'right',
    2: 'bottom',
    3: 'left'
}

DIRECTION_DELTA = {
    0: (0, -1),
    1: (1, 0),
    2: (0, 1),
    3: (-1, 0)
}


OPPOSITE_DIRECTION = {
    DIRECTION.TOP: DIRECTION.BOTTOM,
    DIRECTION.RIGHT: DIRECTION.LEFT,
    DIRECTION.BOTTOM: DIRECTION.TOP,
    DIRECTION.LEFT: DIRECTION.RIGHT
}
