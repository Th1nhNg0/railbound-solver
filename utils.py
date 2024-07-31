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

DIRECTION_TO_STR = {
    0: 'top',
    1: 'right',
    2: 'bottom',
    3: 'left'
}


def flip_direction(direction):
    if direction == DIRECTION['top']:
        return DIRECTION['bottom']
    elif direction == DIRECTION['bottom']:
        return DIRECTION['top']
    elif direction == DIRECTION['left']:
        return DIRECTION['right']
    elif direction == DIRECTION['right']:
        return DIRECTION['left']
