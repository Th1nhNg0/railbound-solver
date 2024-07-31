from tile import create_tiles
import random
import copy
from utils import load_grid
import cv2
import numpy as np
from PIL import Image, ImageDraw


class Cell:
    def __init__(self, possible_tiles):
        self.possible_tiles = possible_tiles
        self.collapsed_tile = None

    def is_collapsed(self):
        return self.collapsed_tile is not None

    def collapse(self):
        if not self.is_collapsed():
            if not self.possible_tiles:
                raise ValueError("No valid tiles left to choose from.")
            self.collapsed_tile = random.choice(self.possible_tiles)
            self.possible_tiles = [self.collapsed_tile]


def convert_grid(grid, tiles):
    new_grid = []
    for row in grid:
        new_row = []
        for cell in row:
            if cell == 0:
                new_row.append(Cell(copy.deepcopy(tiles[1:])))
            else:
                cell = Cell([tile for tile in tiles if tile.index == cell])
                cell.collapse()
                new_row.append(cell)
        new_grid.append(new_row)
    # update_neighbors for all collapsed cells
    for x in range(len(new_grid)):
        for y in range(len(new_grid[0])):
            if new_grid[x][y].is_collapsed():
                update_neighbors(new_grid, x, y)
    return new_grid


def get_neighbors(grid, x, y):
    grid_height = len(grid)
    grid_width = len(grid[0])
    neighbors = []
    if x > 0:
        neighbors.append((x - 1, y))
    if x < grid_height - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < grid_width - 1:
        neighbors.append((x, y + 1))
    return neighbors


def update_neighbors(grid, x, y):
    tile = grid[x][y].collapsed_tile
    neighbors = get_neighbors(grid, x, y)
    for nx, ny in neighbors:
        neighbor = grid[nx][ny]
        if not neighbor.is_collapsed():
            valid_tiles = []
            for neighbor_tile in neighbor.possible_tiles:
                if match(tile, neighbor_tile, (nx - x, ny - y)):
                    valid_tiles.append(neighbor_tile)
            neighbor.possible_tiles = valid_tiles
            if not valid_tiles:
                raise ValueError("No valid tiles left after update.")


def match(tile, neighbor_tile, direction):
    if direction == (-1, 0):  # neighbor is above
        return tile.edges[0] == neighbor_tile.edges[2]
    elif direction == (1, 0):  # neighbor is below
        return tile.edges[2] == neighbor_tile.edges[0]
    elif direction == (0, -1):  # neighbor is to the left
        return tile.edges[3] == neighbor_tile.edges[1]
    elif direction == (0, 1):  # neighbor is to the right
        return tile.edges[1] == neighbor_tile.edges[3]


def wave_function_collapse(grid):
    grid_height = len(grid)
    grid_width = len(grid[0])
    while True:
        try:
            while any(not cell.is_collapsed() for row in grid for cell in row
                      if len(cell.possible_tiles) > 0
                      ):
                non_collapsed_cells = [
                    (x, y)
                    for x in range(grid_height)
                    for y in range(grid_width)
                    if not grid[x][y].is_collapsed()
                    and len(grid[x][y].possible_tiles) > 0
                ]
                # choose the smallest entropy cell
                non_collapsed_cells.sort(
                    key=lambda cell: len(grid[cell[0]][cell[1]].possible_tiles))
                # filter out cells with the same entropy
                non_collapsed_cells = [
                    cell for cell in non_collapsed_cells
                    if len(grid[cell[0]][cell[1]].possible_tiles) == len(grid[non_collapsed_cells[0][0]][non_collapsed_cells[0][1]].possible_tiles)
                ]
                # choose a random cell from the filtered cells
                random.shuffle(non_collapsed_cells)
                for x, y in non_collapsed_cells:
                    grid[x][y].collapse()
                    update_neighbors(grid, x, y)
                    break
                plot_grid(grid, 0)
            return grid
        except ValueError:
            pass


def plot_grid(grid, delay=100):
    tiles = create_tiles()
    grid_height = len(grid)
    grid_width = len(grid[0])
    img = Image.new('RGB', (grid_width * 100, grid_height * 100), 'white')
    draw = ImageDraw.Draw(img)
    for x in range(grid_height):
        for y in range(grid_width):
            cell = grid[x][y]
            if cell.is_collapsed():
                tile_index = cell.collapsed_tile.index
                tile = tiles[tile_index]
                img.paste(
                    tiles[tile_index].img, (y * 100, x * 100))
            else:
                draw.text((y * 100 + 50, x * 100 + 50),
                          str(len(cell.possible_tiles)), fill='red')
    for i in range(grid_height):
        draw.line((0, i * 100, grid_width * 100, i * 100), fill='black')
    for i in range(grid_width):
        draw.line((i * 100, 0, i * 100, grid_height * 100), fill='black')

    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow('image', img)
    cv2.waitKey(delay)

    tiles = create_tiles()


if __name__ == "__main__":
    tiles = create_tiles()
    grid, _ = load_grid('level/1-10.json')
    # add a padding of 0s around the grid
    # print grid
    for row in grid:
        print(row)
    grid = [[15] + row + [15] for row in grid]
    grid = [[15] * len(grid[0])] + grid + [[15] * len(grid[0])]
    for row in grid:
        print(row)
    grid = convert_grid(grid, tiles)
    collapsed_grid = wave_function_collapse(grid)

    for row in collapsed_grid:
        for cell in row:
            if cell.is_collapsed():
                print(cell.collapsed_tile.index, end=" ")
            else:
                print("X", end=" ")
        print()

    plot_grid(collapsed_grid, 0)
    cv2.destroyAllWindows()
