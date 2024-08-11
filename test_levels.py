import os
import json
from solve import main as solve_puzzle


def test_all_levels(levels_folder):
    results = {}

    for filename in os.listdir(levels_folder):
        # skip 1-11A, 1-11B, 1-13A
        if filename in ["1-11A.json", "1-11B.json", "1-13A.json"]:
            continue
        if filename.endswith('.json'):
            level_path = os.path.join(levels_folder, filename)
            print(f"\033[1;32;40mTesting level: {filename}\033[0m")
            try:
                solution_found = solve_puzzle(level_path, show_preview=False)
                if solution_found:
                    results[filename] = "Solved"
                    # blue color
                    print(f"\033[1;34;40mResult: Solved\033[0m")
                else:
                    results[filename] = "Unsolved"
                    print(f"\033[1;31;40mResult: Unsolved\033[0m")
            except Exception as e:
                results[filename] = f"Error: {str(e)}"
                print(f"\033[1;31;40mResult: Error: {str(e)}\033[0m")

            print()  # Empty line for readability

    return results


def print_summary(results):
    print("Summary of Results:")
    print("-------------------")
    for level, result in results.items():
        print(f"{level}: {result}")

    solved_count = list(results.values()).count("Solved")
    total_count = len(results)
    print(f"\nTotal levels solved: {solved_count}/{total_count}")
    print(f"Success rate: {solved_count/total_count:.2%}")


if __name__ == "__main__":
    levels_folder = "levels"  # Update this if your folder is named differently
    results = test_all_levels(levels_folder)
    print_summary(results)
