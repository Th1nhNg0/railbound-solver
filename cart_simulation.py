import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tile import create_tiles, DIRECTION


class Cart:
    def __init__(self, x, y, direction, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.direction = direction
        self.crashed = False
        self.color = color
        self.img = Image.open('images/Cart.png').convert('RGBA')
        self.colorize_cart()

    def move(self, new_x, new_y, new_direction):
        self.x = new_x
        self.y = new_y
        self.direction = new_direction

    def crash(self):
        self.crashed = True

    def colorize_cart(self):
        data = np.array(self.img)
        red, green, blue, alpha = data.T
        white_areas = (red == 255) & (blue == 255) & (green == 255)
        data[..., :-1][white_areas.T] = self.color
        self.img = Image.fromarray(data)


def get_next_position(cart, current_tile, grid_width, grid_height):
    for entry, exit in current_tile.flow:
        if entry == cart.direction:
            if exit == DIRECTION['top']:
                return (cart.x, cart.y - 1, DIRECTION['bottom'])
            elif exit == DIRECTION['right']:
                return (cart.x + 1, cart.y, DIRECTION['left'])
            elif exit == DIRECTION['bottom']:
                return (cart.x, cart.y + 1, DIRECTION['top'])
            elif exit == DIRECTION['left']:
                return (cart.x - 1, cart.y, DIRECTION['right'])
    return None  # If no valid flow is found


def is_valid_position(x, y, grid_width, grid_height):
    return 0 <= x < grid_width and 0 <= y < grid_height


def draw_grid(grid, tiles, carts):
    n = len(grid)
    img = Image.new('RGB', (n * 100, n * 100), color='white')
    draw = ImageDraw.Draw(img)
    for x in range(n):
        for y in range(n):
            tile_index = grid[x][y]
            tile = tiles[tile_index]
            img.paste(
                tiles[tile_index].image_with_edge_indicators, (y * 100, x * 100))
            draw.text((y * 100 + 50, x * 100 + 50),
                      str(tile_index), fill='red')

    for cart in carts:
        cart_img = cart.img.rotate(cart.direction * -90, expand=True)
        if cart.direction % 2 == 0:
            cart_img = cart_img.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            cart_img = cart_img.transpose(Image.FLIP_LEFT_RIGHT)
        if cart.crashed:
            cart_img = cart_img.convert('HSV')
            cart_img = cart_img.point(lambda i: i * 0.5)
            cart_img = cart_img.convert('RGBA')
        img.paste(cart_img, (cart.x * 100 + 37, cart.y * 100 + 45), cart_img)

    for i in range(n):
        draw.line((0, i * 100, n * 100, i * 100), fill='black')
        draw.line((i * 100, 0, i * 100, n * 100), fill='black')

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def simulate_cart_movement(grid, tiles, carts, max_iterations=100):
    grid_height = len(grid)
    grid_width = len(grid[0])
    frames = []
    iteration = 0

    start_time = time.time()

    while iteration < max_iterations and any(not cart.crashed for cart in carts):
        img = draw_grid(grid, tiles, carts)
        frames.append(img)

        for cart in carts:
            if not cart.crashed:
                current_tile = tiles[grid[cart.y][cart.x]]
                next_position = get_next_position(
                    cart, current_tile, grid_width, grid_height)
                if next_position is None or not is_valid_position(*next_position[:2], grid_width, grid_height):
                    cart.crash()
                else:
                    cart.move(*next_position)

        iteration += 1

    # Add final frame
    img = draw_grid(grid, tiles, carts)
    frames.append(img)

    end_time = time.time()
    simulation_time = end_time - start_time
    print(f"Simulation completed in {simulation_time:.4f} seconds")

    return frames


def main():
    grid = [
        [1, 8, 7, 9, 3, 5, 9, 11, 13, 6],
        [3, 1, 11, 9, 10, 11, 9, 3, 4, 10],
        [1, 12, 7, 4, 7, 9, 11, 0, 1, 3],
        [4, 2, 9, 14, 11, 4, 8, 6, 12, 6],
        [0, 5, 9, 11, 5, 0, 0, 0, 1, 14],
        [14, 7, 13, 7, 9, 10, 2, 1, 8, 7],
        [7, 5, 9, 8, 7, 5, 5, 13, 2, 13],
        [9, 8, 12, 6, 3, 9, 11, 13, 8, 12],
        [9, 10, 6, 10, 2, 13, 11, 13, 14, 6],
        [8, 7, 1, 3, 4, 8, 11, 5, 5, 0]
    ]

    tiles = create_tiles()

    # Create multiple carts with different starting positions and colors
    carts = [
        Cart(2, 0, DIRECTION['top'], color=(255, 0, 0)),  # Red cart
        Cart(0, 2, DIRECTION['right'], color=(0, 255, 0)),  # Green cart
        Cart(9, 9, DIRECTION['left'], color=(0, 0, 255))  # Blue cart
    ]

    frames = simulate_cart_movement(grid, tiles, carts, max_iterations=200)

    # Display the simulation
    cv2.namedWindow('Cart Simulation', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Cart Simulation', 1000, 1000)

    for frame in frames:
        cv2.imshow('Cart Simulation', frame)
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
