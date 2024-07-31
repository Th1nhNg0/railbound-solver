import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tile import create_tiles, DIRECTION
from utils import load_grid
from cart import Cart


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
    grid_height = len(grid)
    grid_width = len(grid[0])
    img = Image.new('RGB', (grid_width * 100, grid_height * 100), 'white')
    draw = ImageDraw.Draw(img)
    for x in range(grid_height):
        for y in range(grid_width):
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

        # Draw destination
        dest_x, dest_y = cart.destination
        draw.rectangle([dest_x * 100 + 25, dest_y * 100 + 25,
                        dest_x * 100 + 75, dest_y * 100 + 75],
                       outline=cart.color, width=3)

    # draw line
    for i in range(grid_height):
        draw.line((0, i * 100, grid_width * 100, i * 100), fill='black')
    for i in range(grid_width):
        draw.line((i * 100, 0, i * 100, grid_height * 100), fill='black')

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def check_collision(carts):
    active_carts = [
        cart for cart in carts if not cart.crashed and not cart.reached_destination]

    # Check for head-on collisions
    for i in range(len(active_carts)):
        for j in range(i + 1, len(active_carts)):
            cart1, cart2 = active_carts[i], active_carts[j]
            if (cart1.x == cart2.previous_x and cart1.y == cart2.previous_y and
                    cart2.x == cart1.previous_x and cart2.y == cart1.previous_y):
                return True

    # Check for same position collisions
    positions = [(cart.x, cart.y) for cart in active_carts]
    if len(positions) != len(set(positions)):
        return True

    return False


def simulate_cart_movement(grid, tiles, carts, max_iterations=100):
    grid_height = len(grid)
    grid_width = len(grid[0])
    frames = []
    iteration = 0

    start_time = time.time()

    while iteration < max_iterations:
        img = draw_grid(grid, tiles, carts)
        frames.append(img)

        # Move carts
        for cart in carts:
            if not cart.crashed and not cart.reached_destination:
                current_tile = tiles[grid[cart.y][cart.x]]
                next_position = get_next_position(
                    cart, current_tile, grid_width, grid_height)
                if next_position is None or not is_valid_position(*next_position[:2], grid_width, grid_height):
                    cart.crash()
                else:
                    cart.move(*next_position)

        # Check for collisions after all carts have moved
        if check_collision(carts):
            for cart in carts:
                if not cart.reached_destination:
                    cart.crash()
            break

        if all(cart.reached_destination or cart.crashed for cart in carts):
            break

        iteration += 1

    # Add final frame
    img = draw_grid(grid, tiles, carts)
    frames.append(img)

    end_time = time.time()
    simulation_time = end_time - start_time
    print(f"Simulation completed in {simulation_time:.4f} seconds")

    return frames


def main():
    grid, destination = load_grid('level/1-3.json')
    tiles = create_tiles()

    # Create multiple carts with different starting positions, colors, and destinations
    carts = [
        Cart(0, 4, DIRECTION['bottom'],
             destination=destination, color=(255, 0, 0)),
        Cart(0, 3, DIRECTION['bottom'],
             destination=destination, color=(255, 0, 0)),
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
