import argparse
import json
from pprint import pprint
from tile import TILES


def load_data(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate the loaded data
    if not all(key in data for key in ["grid", "destination", "carts"]):
        raise KeyError("The loaded JSON is missing required keys.")

    return data


def main(input_file, show_preview):
    data = load_data(input_file)
    pprint(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file path")
    parser.add_argument(
        "-p", "--show-preview", action="store_true", help="show preview of the grid"
    )

    args = parser.parse_args()
    main(args.input, args.show_preview)
