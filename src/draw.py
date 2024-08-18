from grid import Grid
from tile import Tile
from PIL import Image


class Draw:
    def __init__(self) -> None:
        self.tile_images = {}
        self.image_width = 90
        self.image_height = 90
        self.load_image()

    def load_image(self):
        for tile in Tile:
            self.tile_images[tile] = Image.open(f"./src/images/{tile.name}.png")

    def draw(self, grid: Grid) -> None:
        image = Image.new(
            "RGB",
            (grid.width * self.image_width, grid.height * self.image_height),
            "white",
        )
        for y in range(grid.height):
            for x in range(grid.width):
                tile = Tile(grid.get(x, y))
                image.paste(
                    self.tile_images[tile],
                    (x * self.image_width, y * self.image_height),
                )
        return image


if __name__ == "__main__":
    grid = Grid([[0, 5, 0], [0, 0, 0], [5, 15, 5], [0, 0, 0]])
    draw = Draw()
    draw.draw(grid)
