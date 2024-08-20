from utils import load_data
from typing import Dict, Any
import time
from solver import solve
import os
from tabulate import tabulate
import timeit
import re


def benchmark_level(file_path: str) -> Dict[str, Dict[str, float]]:
    data = load_data(file_path)
    results = {}
    print(f"Benchmarking {file_path}")
    for method in ["dfs", "bfs"]:
        # Use timeit for more accurate timing
        time_taken = timeit.timeit(lambda: solve(data, method), number=1)
        solution = solve(data, method)

        results[method] = {
            "time": time_taken,
            "iterations": solution["iteration"]
            if solution["best_state"] is not None
            else float("inf"),
        }
    print(f"Finished benchmarking {file_path}")
    return results


def benchmark_all_levels(folder_path: str) -> Dict[str, Dict[str, Dict[str, float]]]:
    all_results = {}
    levels = os.listdir(folder_path)
    # sort by number in it num-num
    levels = sorted(levels, key=lambda x: list(map(int, re.findall(r"\d+", x))))
    for filename in levels[:10]:
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            all_results[filename] = benchmark_level(file_path)

    return all_results


def print_results_table(results: Dict[str, Dict[str, Dict[str, float]]]):
    table_data = []
    headers = ["Level", "DFS Time", "DFS Iterations", "BFS Time", "BFS Iterations"]

    for level, data in results.items():
        row = [
            level,
            f"{data['dfs']['time']:.4f}",
            f"{data['dfs']['iterations']}",
            f"{data['bfs']['time']:.4f}",
            f"{data['bfs']['iterations']}",
        ]
        table_data.append(row)

    print(tabulate(table_data, headers=headers, tablefmt="rounded_outline"))


if __name__ == "__main__":
    levels_folder = "./src/levels"
    results = benchmark_all_levels(levels_folder)
    # save results to a file
    with open("benchmark_results.txt", "w") as f:
        f.write(str(results))
    print_results_table(results)
