import tkinter as tk
import math

from PIL import Image, ImageTk

def is_rotatable_hex(hex_type):
    if hex_type == 0 or hex_type == 6 or hex_type == 7:
        return False
    return True

class HexTileImage:

    image = None
    tk_image = None
    grid_x = 0
    grid_y = 0
    grid_type = 0
    grid_rot = 0
    hex_width = 0
    hex_height = 0
    center_x = 0
    center_y = 0
    canvas_id = 0
    img_data = None
    clickable = False

    canvas_xspace = 100
    canvas_yspace = 100

    def __init__(self, canvas, image, x, y, type_, rot, width, height, clickable):
        self.image = image.convert('RGBA')
        self.grid_x = x
        self.grid_y = y
        self.grid_type = type_
        self.grid_rot = rot
        self.hex_width = width
        self.hex_height = height
        self.clickable = clickable

        self.draw_image(canvas)

    def draw_image(self, canvas):
        x = self.canvas_xspace + self.grid_x * self.hex_width
        y = self.canvas_yspace + self.grid_y * self.hex_height * 0.875
        if self.grid_y % 2 == 1:
            x += self.hex_width / 2
        image = self.image
        if self.grid_rot > 0 and is_rotatable_hex(self.grid_type):
            image = self.image.rotate(self.grid_rot * -60, expand=True)

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas_id = canvas.create_image(x, y, image=self.tk_image, anchor=tk.CENTER)
        self.center_x = x
        self.center_y = y
        self.img_data = image

    def replace_image(self, canvas, type_, image):
        self.image = image.convert('RGBA')
        self.grid_type = type_
        image = self.image
        if self.grid_rot > 0 and is_rotatable_hex(self.grid_type):
            image = self.image.rotate(self.grid_rot * -60, expand=True)
        else:
            self.grid_rot = 0
        self.tk_image = ImageTk.PhotoImage(image)
        canvas.itemconfig(self.canvas_id, image=self.tk_image)
        self.img_data = image

    def rot_image(self, canvas):
        if is_rotatable_hex(self.grid_type):
            self.grid_rot = (self.grid_rot + 1) % 6
            image = self.image.rotate(self.grid_rot * -60, expand=True)
            self.tk_image = ImageTk.PhotoImage(image)
            canvas.itemconfig(self.canvas_id, image=self.tk_image)
            self.img_data = image

    def check_clicked(self, event):
        if not self.clickable:
            return False

        rel_x = event.x - self.center_x
        rel_y = event.y - self.center_y
        rot_radians = math.radians(self.grid_rot * -60)
        cos_theta = math.cos(rot_radians)
        sin_theta = math.sin(rot_radians)
        unrotated_x = rel_x * cos_theta + rel_y * sin_theta
        unrotated_y = -rel_x * sin_theta + rel_y * cos_theta
        rel_x = unrotated_x + self.image.width / 2
        rel_y = unrotated_y + self.image.height / 2

        if 0 <= rel_x < self.image.width and 0 <= rel_y < self.image.height:
            pixel = self.image.getpixel((int(rel_x), int(rel_y)))
            alpha = pixel[3]
            if alpha > 0:
                return True
        return False

    def get_grid_coord(self):
        return self.grid_x, self.grid_y