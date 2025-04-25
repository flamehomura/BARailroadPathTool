import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import json

from PIL.ImageOps import expand

from LevelData import GridLevel
from PathFind import GridMap


class HexGridPanel:
    master = None
    canvas = None
    control_panel = None
    width = 1200
    height = 1000
    bg = "black"

    combobox_level = None
    draw_button = None

    img_path_1 = None
    img_path_1_label = None
    path_1_spin = None
    path_1_spin_value = None
    img_path_2 = None
    img_path_2_label = None
    path_2_spin = None
    path_2_spin_value = None
    img_path_3 = None
    img_path_3_label = None
    path_3_spin = None
    path_3_spin_value = None

    bonus_checkbox = None
    bonus_check_value = None

    result_label = None

    hexes_json_file_name = "config/hexes.json"
    level_json_file_name = "config/levels.json"

    hex_imgs : dict[int, Image] = {}
    level_keys = []
    level_grids = None

    init_xspace = 100
    init_yspace = 100

    hex_img_refs = []
    path_img_refs = []

    grid_width = 100
    grid_height = 100

    def __init__(self, master):
        self.master = master
        self.master.title("Railway Grid")

        self.canvas = tk.Canvas(master, width = self.width, height = self.height, bg = self.bg)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.load_hex_img()
        self.load_level_data()

        self.control_panel = tk.Frame(master)
        self.control_panel.grid(row=0, column=1, sticky="ns")

        self.combobox_level = ttk.Combobox(self.control_panel, values=self.level_keys, state="readonly")
        self.combobox_level.bind("<<ComboboxSelected>>", self.draw_grids)
        self.combobox_level.grid(row=0, column=0, pady=10)
        self.combobox_level.current(0)

        img = self.hex_imgs[1].resize((100, 100), Image.LANCZOS)
        self.img_path_1 = ImageTk.PhotoImage(img)
        self.img_path_1_label = tk.Label(self.control_panel, image=self.img_path_1)
        self.img_path_1_label.grid(row=1, column=0, pady=10)
        self.path_1_spin_value = tk.IntVar(value=0)
        self.path_1_spin = tk.Spinbox(self.control_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_1_spin_value)
        self.path_1_spin.grid(row=2, column=0, pady=5)

        img = self.hex_imgs[2].resize((100, 100), Image.LANCZOS)
        self.img_path_2 = ImageTk.PhotoImage(img)
        self.img_path_2_label = tk.Label(self.control_panel, image=self.img_path_2)
        self.img_path_2_label.grid(row=3, column=0, pady=10)
        self.path_2_spin_value = tk.IntVar(value=0)
        self.path_2_spin = tk.Spinbox(self.control_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_2_spin_value)
        self.path_2_spin.grid(row=4, column=0, pady=5)

        img = self.hex_imgs[3].resize((100, 100), Image.LANCZOS)
        self.img_path_3 = ImageTk.PhotoImage(img)
        self.img_path_3_label = tk.Label(self.control_panel, image=self.img_path_3)
        self.img_path_3_label.grid(row=5, column=0, pady=10)
        self.path_3_spin_value = tk.IntVar(value=0)
        self.path_3_spin = tk.Spinbox(self.control_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_3_spin_value)
        self.path_3_spin.grid(row=6, column=0, pady=5)

        self.bonus_check_value = tk.BooleanVar(value=False)
        self.bonus_checkbox = tk.Checkbutton(self.control_panel, text="Get All Bonus!", variable=self.bonus_check_value)
        self.bonus_checkbox.grid(row=7, column=0, pady=20)

        self.draw_button = tk.Button(self.control_panel, text="Build Path", command=self.build_path)
        self.draw_button.grid(row=8, column=0, pady=20)

        self.draw_button = tk.Button(self.control_panel, text="Reset Level", command=self.reset_hex)
        self.draw_button.grid(row=9, column=0, pady=20)

        self.result_label = tk.Label(self.control_panel, text="", font=("Arial", 20, "bold"), fg="black")
        self.result_label.grid(row=10, column=0, pady=10)

        self.draw_grids(None)


    def load_hex_img(self):
        with open(self.hexes_json_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            for row in data:
                hex_type = row["type"]
                hex_img_name = row["img"]
                hex_img = None

                if os.path.exists(hex_img_name):
                    hex_img = Image.open(hex_img_name)
                else:
                    print(f"❌ No {hex_img_name} exist！")
                self.hex_imgs[hex_type] = hex_img

    def load_level_data(self):
        with open(self.level_json_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            for key, grid in data.items():
                self.level_keys.append(key)

    def draw_hex(self, col, row, type, rot):
        img = self.hex_imgs[type]
        if img:
            x = self.init_xspace + col * self.grid_width + self.grid_width / 2
            y = self.init_yspace + row * self.grid_height * 0.875 + self.grid_height / 2
            if row % 2 == 1:
                x += self.grid_width / 2
            if rot > 0:
                img = img.rotate(rot * -60, expand=True)
            photo_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(x, y, image=photo_img, anchor=tk.CENTER)
            return photo_img
        return None

    def draw_grids(self, event):
        self.canvas.delete("all")
        level_name = self.combobox_level.get()
        self.level_grids = GridLevel(level_name)
        self.path_1_spin_value.set(self.level_grids.paths[0])
        self.path_2_spin_value.set(self.level_grids.paths[1])
        self.path_3_spin_value.set(self.level_grids.paths[2])

        self.hex_img_refs.clear()
        for i, row in enumerate(self.level_grids.grids):
            for j, data in enumerate(row):
                photo = self.draw_hex(j, i, data.type, data.rot)
                if photo:
                    self.hex_img_refs.append(photo)

    def reset_hex(self):
        self.draw_grids(None)

    def build_path(self):
        grid_map = GridMap(self.level_grids)
        path_limits = [self.path_1_spin_value.get(), self.path_2_spin_value.get(), self.path_3_spin_value.get()]
        get_bonus = self.bonus_check_value.get()
        shortest_path = grid_map.shortest_path(path_limits, get_bonus)
        if shortest_path is not None:
            self.result_label.config(text="Success", fg="green")
            print(shortest_path)
            self.path_img_refs.clear()
            for i, path in enumerate(shortest_path[2]):
                if (path.x, path.y) in grid_map.fixed_grid_map:
                    continue
                if i == len(shortest_path[2]) - 1:
                    break
                else:
                    next_path = shortest_path[2][i + 1]
                path_type = GridMap.get_path_type(path, next_path)
                if path_type > 0:
                    rot = path.side_idx
                    target_side = (next_path[2] + 3) % 6
                    if abs(target_side - path.side_idx) <= path_type:
                        rot = path.side_idx if target_side > path.side_idx else target_side
                    else:
                        rot = target_side if target_side > path.side_idx else path.side_idx
                    photo = self.draw_hex(path.x, path.y, path_type, rot)
                    if photo:
                        self.path_img_refs.append(photo)
                        print(f"{path} type {path_type}")

            self.path_1_spin_value.set(shortest_path[1][1])
            self.path_2_spin_value.set(shortest_path[1][2])
            self.path_3_spin_value.set(shortest_path[1][3])

        else:
            self.result_label.config(text="Failed", fg="red")
