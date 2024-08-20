from grid import Grid
from tile import Tile, Position
from PIL import Image, ImageDraw
from utils import load_data
from state import State


class Draw:
    def __init__(self) -> None:
        self.tile_images = {}
        self.image_width = 90
        self.image_height = 90
        self.load_image()

    def load_image(self):
        for tile in Tile:
            self.tile_images[tile.value] = Image.open(f"./src/images/{tile.name}.png")
            if tile.is_curve or tile.is_straight:
                self.tile_images[f"{tile.value}_2"] = Image.open(
                    f"./src/images/{tile.name}_2.png"
                )

    def draw(self, state: State, debug: bool = False) -> None:
        grid = state.grid
        image = Image.new(
            "RGBA",
            (grid.width * self.image_width, grid.height * self.image_height),
            "#dbd692",
        )
        imageDrawer = ImageDraw.Draw(image)
        for y in range(grid.height):
            for x in range(grid.width):
                tile = Tile(grid.get(x, y))
                if Position(x, y) in state.immutable_positions and (
                    tile.is_curve or tile.is_straight
                ):
                    img = self.tile_images[f"{tile.value}_2"]
                else:
                    img = self.tile_images[tile.value]
                image.paste(img, (x * self.image_width, y * self.image_height), img)
                # draw x, y coordinates string on bottom left of the cell
                if debug:
                    imageDrawer.text(
                        (x * self.image_width, y * self.image_height + 70),
                        f"{x}, {y}",
                        fill="black",
                    )
        return image


if __name__ == "__main__":
    data = load_data("./src/levels/1-11.json")
    grid = Grid(data["grid"])
    draw = Draw()
    draw.draw(grid).show()
