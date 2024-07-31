import json


def load_grid(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data["grid"], data["destination"] if data["destination"] else None


DIRECTION = {
    'top': 0,
    'right': 1,
    'bottom': 2,
    'left': 3
}
