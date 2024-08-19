from grid import Grid
from tile import Tile, Position
from PIL import Image, ImageDraw
from utils import load_data


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
        imageDrawer = ImageDraw.Draw(image)
        for y in range(grid.height):
            for x in range(grid.width):
                tile = Tile(grid.get(x, y))
                image.paste(
                    self.tile_images[tile],
                    (x * self.image_width, y * self.image_height),
                )
                # draw x, y coordinates string on bottom left of the cell
                imageDrawer.text(
                    (x * self.image_width, y * self.image_height + 70),
                    f"{x}, {y}",
                    fill="white",
                )
        return image

    def draw_with_highlight(self, grid: Grid, postitions: list[Position]) -> None:
        image = self.draw(grid)
        imageDrawer = ImageDraw.Draw(image)
        for position in postitions:
            imageDrawer.rectangle(
                [
                    position.x * self.image_width,
                    position.y * self.image_height,
                    (position.x + 1) * self.image_width,
                    (position.y + 1) * self.image_height,
                ],
                outline="red",
            )
        return image


if __name__ == "__main__":
    data = load_data("./src/levels/1-11.json")
    grid = Grid(data["grid"])
    draw = Draw()
    draw.draw(grid).show()
