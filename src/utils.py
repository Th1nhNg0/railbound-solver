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

        full_operation_name = "/".join(self.current_operations + [operation_name])
        self.current_operations.append(operation_name)
        start_time = time.perf_counter()
        try:
            yield
        finally:
            if self.enabled:
                end_time = time.perf_counter()
                self.execution_times[full_operation_name].append(end_time - start_time)
                self.current_operations.pop()

    def print(self):
        if not self.enabled:
            return

        print("\n" + "=" * 80)
        print("{:^80}".format("Average Execution Times"))
        print("=" * 80)
        print(
            "{:<50} {:>15} {:>15}".format("Operation", "Avg Time (s)", "Total Time (s)")
        )
        print("-" * 80)

        for operation, times in sorted(self.execution_times.items()):
            avg_time = mean(times)
            total_time = sum(times)
            indent = "  " * (operation.count("/"))
            operation_name = operation.split("/")[-1]
            print(
                "{:<50} {:>15.6f} {:>15.6f}".format(
                    f"{indent}{operation_name}", avg_time, total_time
                )
            )

        print("=" * 80 + "\n")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def reset(self):
        self.execution_times = defaultdict(list)
