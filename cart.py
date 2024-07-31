
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class Cart:
    """
    Represents a cart in a railbound game.

    Attributes:
        x (int): The x-coordinate of the cart's position.
        y (int): The y-coordinate of the cart's position.
        direction (str): The direction the cart is facing.
        destination (tuple): The coordinates of the cart's destination.
        color (tuple): The RGB color value of the cart.
        crashed (bool): Indicates whether the cart has crashed.
        reached_destination (bool): Indicates whether the cart has reached its destination.
        img (PIL.Image.Image): The image representation of the cart.
        previous_x (int): The previous x-coordinate of the cart's position.
        previous_y (int): The previous y-coordinate of the cart's position.
    """

    def __init__(self, x, y, direction, destination, color=(255, 0, 0)):
        self.x = x
        self.y = y

        self.direction = direction
        self.destination = destination
        self.crashed = False
        self.reached_destination = False
        self.img = Image.open('images/Cart.png').convert('RGBA')
        self.colorize_cart(color)

        self.previous_x = x
        self.previous_y = y

    def move(self, new_x, new_y, new_direction):
        """
        Moves the cart to the specified position and updates its direction.

        Args:
            new_x (int): The new x-coordinate of the cart's position.
            new_y (int): The new y-coordinate of the cart's position.
            new_direction (str): The new direction the cart is facing.

        Returns:
            None
        """
        self.previous_x, self.previous_y = self.x, self.y
        self.x = new_x
        self.y = new_y
        self.direction = new_direction
        if (self.x, self.y) == self.destination:
            self.reached_destination = True

    def crash(self):
        """
        Marks the cart as crashed.

        Returns:
            None
        """
        self.crashed = True

    def colorize_cart(self, color):
        data = np.array(self.img)
        red, green, blue, alpha = data.T
        white_areas = (red > 200) & (blue > 200) & (green > 200)
        data[..., :-1][white_areas.T] = color
        self.img = Image.fromarray(data)
