import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import os
import json

from PIL.ImageOps import expand
from select import select

from LevelData import GridLevel
from PathFind import GridMap
from LevelEditor import LevelJson
from HexImage import HexTileImage


class HexGridPanel:
    master = None

    canvas = None
    width = 1200
    height = 900
    bg = "black"

    control_notebook = None
    path_finding_table = None
    level_editor_table = None
    path_finding_panel = None
    level_editor_panel = None

    combobox_level_pf = None
    combobox_level_le = None

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

    shortest_checkbox = None
    shortest_check_value = None
    bonus_checkbox = None
    bonus_check_value = None

    draw_button = None
    result_label = None

    new_button = None
    delete_button = None
    save_button = None

    radio_button_frame = None
    radio_button_hex = None
    radio_button_hex_img = None
    radio_button_hex_path_3 = None
    radio_button_hex_path_3_img = None
    radio_button_hex_path_2 = None
    radio_button_hex_path_2_img = None
    radio_button_hex_path_1 = None
    radio_button_hex_path_1_img = None
    radio_button_hex_start = None
    radio_button_hex_start_img = None
    radio_button_hex_goal = None
    radio_button_hex_goal_img = None
    radio_button_hex_dis = None
    radio_button_hex_dis_img = None
    radio_button_hex_poi = None
    radio_button_hex_poi_img = None
    hex_type_select_value = None

    editor_spin_frame = None
    editor_img_path_1 = None
    editor_img_path_1_label = None
    editor_path_1_spin = None
    editor_path_1_spin_value = None
    editor_img_path_2 = None
    editor_img_path_2_label = None
    editor_path_2_spin = None
    editor_path_2_spin_value = None
    editor_img_path_3 = None
    editor_img_path_3_label = None
    editor_path_3_spin = None
    editor_path_3_spin_value = None

    hexes_json_file_name = "config/hexes.json"
    level_json_file_name = "config/levels.json"

    hex_imgs : dict[int, Image] = {}
    editor_hex_ids : dict[int, (int, int)] = {}
    level_keys = []
    level_grids = None
    level_grids_editor = None
    level_editor = None
    level_editor_keys = []

    init_xspace = 100
    init_yspace = 100

    hex_img_refs = []
    path_img_refs = []
    editor_hex_img_refs = []

    grid_width = 100
    grid_height = 100

    def __init__(self, master):
        self.master = master
        self.master.geometry('1400x960')
        self.master.title("Railway Grid")

        self.load_hex_img()
        self.load_level_data()
        self.load_level_editor_data()

        self.control_notebook = ttk.Notebook(master)
        self.control_notebook.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.control_notebook.pack(fill='both', expand=True)

        self.path_finding_table = tk.Frame(self.control_notebook)
        self.level_editor_table = tk.Frame(self.control_notebook)
        self.control_notebook.add(self.path_finding_table, text = "Path Finding")
        self.control_notebook.add(self.level_editor_table, text = "Level Editor")

        self.canvas_pf = tk.Canvas(self.path_finding_table, width = self.width, height = self.height, bg = self.bg)
        self.canvas_pf.grid(row=0, column=0, sticky="nsew")
        self.path_finding_panel = tk.Frame(self.path_finding_table)
        self.path_finding_panel.grid(row=0, column=1, sticky="ns")

        self.canvas_le = tk.Canvas(self.level_editor_table, width = self.width, height = self.height, bg = self.bg)
        self.canvas_le.grid(row=0, column=0, sticky="nsew")
        self.canvas_le.bind("<Button-1>", self.on_canvas_left_click)
        self.canvas_le.bind("<Button-3>", self.on_canvas_right_click)
        self.level_editor_panel = tk.Frame(self.level_editor_table)
        self.level_editor_panel.grid(row=0, column=1, sticky="ns")

        # path finding table
        self.combobox_level_pf = ttk.Combobox(self.path_finding_panel, values=self.level_keys, state="readonly")
        self.combobox_level_pf.bind("<<ComboboxSelected>>", self.draw_grids)
        self.combobox_level_pf.grid(row=0, column=0, pady=10)
        self.combobox_level_pf.current(0)

        img = self.hex_imgs[3].resize((100, 100), Image.LANCZOS)
        self.img_path_3 = ImageTk.PhotoImage(img)
        self.img_path_3_label = tk.Label(self.path_finding_panel, image=self.img_path_3)
        self.img_path_3_label.grid(row=1, column=0, pady=10)
        self.path_3_spin_value = tk.IntVar(value=0)
        self.path_3_spin = tk.Spinbox(self.path_finding_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_3_spin_value)
        self.path_3_spin.grid(row=2, column=0, pady=5)

        img = self.hex_imgs[2].resize((100, 100), Image.LANCZOS)
        self.img_path_2 = ImageTk.PhotoImage(img)
        self.img_path_2_label = tk.Label(self.path_finding_panel, image=self.img_path_2)
        self.img_path_2_label.grid(row=3, column=0, pady=10)
        self.path_2_spin_value = tk.IntVar(value=0)
        self.path_2_spin = tk.Spinbox(self.path_finding_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_2_spin_value)
        self.path_2_spin.grid(row=4, column=0, pady=5)

        img = self.hex_imgs[1].resize((100, 100), Image.LANCZOS)
        self.img_path_1 = ImageTk.PhotoImage(img)
        self.img_path_1_label = tk.Label(self.path_finding_panel, image=self.img_path_1)
        self.img_path_1_label.grid(row=5, column=0, pady=10)
        self.path_1_spin_value = tk.IntVar(value=0)
        self.path_1_spin = tk.Spinbox(self.path_finding_panel, from_=0, to=100, increment=1, width=7, textvariable=self.path_1_spin_value)
        self.path_1_spin.grid(row=6, column=0, pady=5)

        self.shortest_check_value = tk.BooleanVar(value=True)
        self.shortest_checkbox = tk.Checkbutton(self.path_finding_panel, text="Shortest Path", variable=self.shortest_check_value)
        self.shortest_checkbox.grid(row=7, column=0, pady=20)

        self.bonus_check_value = tk.BooleanVar(value=False)
        self.bonus_checkbox = tk.Checkbutton(self.path_finding_panel, text="Get All Bonus!", variable=self.bonus_check_value)
        self.bonus_checkbox.grid(row=8, column=0, pady=20)

        self.draw_button = tk.Button(self.path_finding_panel, text="Build Path", command=self.build_path)
        self.draw_button.grid(row=9, column=0, pady=20)

        self.draw_button = tk.Button(self.path_finding_panel, text="Reset Level", command=self.reset_hex)
        self.draw_button.grid(row=10, column=0, pady=20)

        self.result_label = tk.Label(self.path_finding_panel, text="", font=("Arial", 20, "bold"), fg="black")
        self.result_label.grid(row=11, column=0, pady=10)


        # level editor table
        self.combobox_level_le = ttk.Combobox(self.level_editor_panel, values=self.level_editor_keys, state="readonly")
        self.combobox_level_le.bind("<<ComboboxSelected>>", self.draw_grids_editor)
        self.combobox_level_le.grid(row=0, column=0, pady=10)
        self.combobox_level_le.current(0)

        self.new_button = tk.Button(self.level_editor_panel, text="New Level", command=self.new_level)
        self.new_button.grid(row=1, column=0, pady=10)

        self.delete_button = tk.Button(self.level_editor_panel, text="Delete Level", command=self.delete_level)
        self.delete_button.grid(row=2, column=0, pady=10)

        self.save_button = tk.Button(self.level_editor_panel, text="Save Levels", command=self.save_level)
        self.save_button.grid(row=3, column=0, pady=10)

        des_label = tk.Label(self.level_editor_panel,
                             text="Click:\n Left to place;\n Right to rotate;\n",
                             anchor="w",
                             justify="left")
        des_label.grid(row=4, column=0, pady=5)

        self.radio_button_frame = tk.Frame(self.level_editor_panel)
        self.radio_button_frame.grid(row=5, column=0, pady=2)

        self.hex_type_select_value = tk.IntVar(value=0)
        radio_button_img_size = (64, 64)

        img = self.hex_imgs[0].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_img = ImageTk.PhotoImage(img)
        self.radio_button_hex = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_img, variable=self.hex_type_select_value, value=0)
        self.radio_button_hex.grid(row=0, column=0, pady=4)

        img = self.hex_imgs[6].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_dis_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_dis = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_dis_img, variable=self.hex_type_select_value, value=6)
        self.radio_button_hex_dis.grid(row=0, column=1, pady=4)

        img = self.hex_imgs[-3].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_path_3_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_path_3 = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_path_3_img, variable=self.hex_type_select_value, value=-3)
        self.radio_button_hex_path_3.grid(row=1, column=0, pady=4)

        img = self.hex_imgs[-2].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_path_2_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_path_2 = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_path_2_img, variable=self.hex_type_select_value, value=-2)
        self.radio_button_hex_path_2.grid(row=1, column=1, pady=4)

        img = self.hex_imgs[-1].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_path_1_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_path_1 = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_path_1_img, variable=self.hex_type_select_value, value=-1)
        self.radio_button_hex_path_1.grid(row=2, column=0, pady=4)

        img = self.hex_imgs[7].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_poi_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_poi = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_poi_img, variable=self.hex_type_select_value, value=7)
        self.radio_button_hex_poi.grid(row=2, column=1, pady=4)

        img = self.hex_imgs[4].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_start_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_start = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_start_img, variable=self.hex_type_select_value, value=4)
        self.radio_button_hex_start.grid(row=3, column=0, pady=4)

        img = self.hex_imgs[5].resize(radio_button_img_size, Image.LANCZOS)
        self.radio_button_hex_goal_img = ImageTk.PhotoImage(img)
        self.radio_button_hex_goal = tk.Radiobutton(self.radio_button_frame, image=self.radio_button_hex_goal_img, variable=self.hex_type_select_value, value=5)
        self.radio_button_hex_goal.grid(row=3, column=1, pady=4)


        self.editor_spin_frame = tk.Frame(self.level_editor_panel)
        self.editor_spin_frame.grid(row=6, column=0, pady=10)

        spin_img_size = (64, 64)
        img = self.hex_imgs[3].resize(spin_img_size, Image.LANCZOS)
        self.editor_img_path_3 = ImageTk.PhotoImage(img)
        self.editor_img_path_3_label = tk.Label(self.editor_spin_frame, image=self.editor_img_path_3)
        self.editor_img_path_3_label.grid(row=0, column=0, pady=4)
        self.editor_path_3_spin_value = tk.IntVar(value=0)
        self.editor_path_3_spin = tk.Spinbox(self.editor_spin_frame, from_=0, to=100, increment=1, width=7, textvariable=self.editor_path_3_spin_value)
        self.editor_path_3_spin.grid(row=1, column=0, pady=2)

        img = self.hex_imgs[2].resize(spin_img_size, Image.LANCZOS)
        self.editor_img_path_2 = ImageTk.PhotoImage(img)
        self.editor_img_path_2_label = tk.Label(self.editor_spin_frame, image=self.editor_img_path_2)
        self.editor_img_path_2_label.grid(row=2, column=0, pady=4)
        self.editor_path_2_spin_value = tk.IntVar(value=0)
        self.editor_path_2_spin = tk.Spinbox(self.editor_spin_frame, from_=0, to=100, increment=1, width=7, textvariable=self.editor_path_2_spin_value)
        self.editor_path_2_spin.grid(row=3, column=0, pady=2)

        img = self.hex_imgs[1].resize(spin_img_size, Image.LANCZOS)
        self.editor_img_path_1 = ImageTk.PhotoImage(img)
        self.editor_img_path_1_label = tk.Label(self.editor_spin_frame, image=self.editor_img_path_1)
        self.editor_img_path_1_label.grid(row=4, column=0, pady=4)
        self.editor_path_1_spin_value = tk.IntVar(value=0)
        self.editor_path_1_spin = tk.Spinbox(self.editor_spin_frame, from_=0, to=100, increment=1, width=7, textvariable=self.editor_path_1_spin_value)
        self.editor_path_1_spin.grid(row=5, column=0, pady=2)

        self.draw_grids(None)
        self.draw_grids_editor(None)


    def load_hex_img(self):
        self.hex_imgs.clear()
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
        self.level_keys.clear()
        with open(self.level_json_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            for key, grid in data.items():
                self.level_keys.append(key)

    def load_level_editor_data(self):
        if self.level_editor is None:
            self.level_editor = LevelJson()

        self.level_editor_keys.clear()
        for key, grid in self.level_editor.json_data.items():
            self.level_editor_keys.append(key)

    def tab_changed(self, event):
        if self.control_notebook:
            selected_tab = self.control_notebook.select()
            selected_index = self.control_notebook.index(selected_tab)
            if selected_index == 0:
                self.load_level_data()
                self.update_combobox_pf(None)
                self.draw_grids(None)

            if selected_index == 1:
                self.load_level_editor_data()
                self.update_combobox_le(None)
                self.draw_grids_editor(None)

    def draw_hex(self, col, row, type_, rot):
        img = self.hex_imgs[type_]
        if img:
            hex_img = HexTileImage(self.canvas_pf, img, col, row, type_, rot, self.grid_width, self.grid_width, False)
            self.hex_img_refs.append(hex_img)

    def draw_path_hex(self, col, row, type_, rot):
        img = self.hex_imgs[type_]
        if img:
            hex_img = HexTileImage(self.canvas_pf, img, col, row, type_, rot, self.grid_width, self.grid_width, False)
            self.path_img_refs.append(hex_img)

    def draw_hex_editor(self, col, row, type_, rot):
        img = self.hex_imgs[type_]
        if img:
            hex_img = HexTileImage(self.canvas_le, img, col, row, type_, rot, self.grid_width, self.grid_width, True)
            self.editor_hex_img_refs.append(hex_img)

    def draw_grids(self, event):
        self.canvas_pf.delete("all")
        self.hex_img_refs.clear()

        level_name = self.combobox_level_pf.get()
        self.level_grids = GridLevel(level_name)
        self.path_1_spin_value.set(self.level_grids.paths[0])
        self.path_2_spin_value.set(self.level_grids.paths[1])
        self.path_3_spin_value.set(self.level_grids.paths[2])

        for i, row in enumerate(self.level_grids.grids):
            for j, data in enumerate(row):
                self.draw_hex(j, i, data.type, data.rot)

    def draw_grids_editor(self, event):
        self.canvas_le.delete("all")
        self.editor_hex_img_refs.clear()
        self.editor_hex_ids.clear()

        level_name = self.combobox_level_le.get()
        if self.level_editor:
            self.level_grids_editor = self.level_editor.get_level_data(level_name)
            self.editor_path_1_spin_value.set(self.level_grids_editor.path[0])
            self.editor_path_2_spin_value.set(self.level_grids_editor.path[1])
            self.editor_path_3_spin_value.set(self.level_grids_editor.path[2])

            for i, row in enumerate(self.level_grids_editor.grid):
                for j, data in enumerate(row):
                    self.draw_hex_editor(j, i, data.type, data.rot)

    def reset_hex(self):
        self.draw_grids(None)

    def build_path(self):
        grid_map = GridMap(self.level_grids)
        path_limits = [self.path_1_spin_value.get(), self.path_2_spin_value.get(), self.path_3_spin_value.get()]
        get_bonus = self.bonus_check_value.get()
        shortest = self.shortest_check_value.get()
        calced_path = grid_map.calc_path(path_limits, get_bonus, shortest)
        if calced_path is not None:
            self.result_label.config(text="Success", fg="green")
            # print(calced_path)
            self.path_img_refs.clear()
            for i, path in enumerate(calced_path[2]):
                if (path.x, path.y) in grid_map.fixed_grid_map:
                    continue
                if i == len(calced_path[2]) - 1:
                    break
                else:
                    next_path = calced_path[2][i + 1]
                path_type = GridMap.get_path_type(path, next_path)
                if path_type > 0:
                    rot = path.side_idx
                    target_side = (next_path[2] + 3) % 6
                    if abs(target_side - path.side_idx) <= path_type:
                        rot = path.side_idx if target_side > path.side_idx else target_side
                    else:
                        rot = target_side if target_side > path.side_idx else path.side_idx
                    self.draw_path_hex(path.x, path.y, path_type, rot)

            self.path_1_spin_value.set(calced_path[1][1])
            self.path_2_spin_value.set(calced_path[1][2])
            self.path_3_spin_value.set(calced_path[1][3])

        else:
            self.result_label.config(text="Failed", fg="red")

    def new_level(self):
        new_input = simpledialog.askstring("Input", "Input new level name:")
        if new_input:
            if self.level_editor:
                self.level_editor.new_level(new_input)
                self.load_level_editor_data()

                self.update_combobox_le(new_input)

    def delete_level(self):
        level_name = self.combobox_level_le.get()
        result = messagebox.askyesno("Confirm", f"Decide to delete {level_name}?")
        if result:
            if self.level_editor:
                self.level_editor.delete_level(level_name)
                self.load_level_editor_data()

                self.update_combobox_le(None)

    def save_level(self):
        result = messagebox.askyesno("Confirm", f"Decide to save levels?")
        if result:
            if self.level_editor:
                self.level_grids_editor.path[0] = self.editor_path_1_spin_value.get()
                self.level_grids_editor.path[1] = self.editor_path_2_spin_value.get()
                self.level_grids_editor.path[2] = self.editor_path_3_spin_value.get()
                self.level_editor.save_json()
                self.load_level_editor_data()


    def on_canvas_left_click(self, event):
        for img in reversed(self.editor_hex_img_refs):
            if img.check_clicked(event):
                hex_coord = img.get_grid_coord()
                selected_hex_type = self.hex_type_select_value.get()
                hex_img = self.hex_imgs[selected_hex_type]
                if hex_img:
                    img.replace_image(self.canvas_le, selected_hex_type, hex_img)
                    self.level_grids_editor.grid[hex_coord[1]][hex_coord[0]].type = selected_hex_type
                    self.level_grids_editor.grid[hex_coord[1]][hex_coord[0]].rot = img.grid_rot
                return

    def on_canvas_right_click(self, event):
        for img in reversed(self.editor_hex_img_refs):
            if img.check_clicked(event):
                hex_coord = img.get_grid_coord()
                img.rot_image(self.canvas_le)
                self.level_grids_editor.grid[hex_coord[1]][hex_coord[0]].rot = img.grid_rot
                return

    def update_combobox_pf(self, new_sel):
        if self.combobox_level_pf:
            self.combobox_level_pf['values'] = self.level_keys
            if new_sel:
                if new_sel in self.combobox_level_pf['values']:
                    index = self.combobox_level_pf['values'].index(new_sel)
                    self.combobox_level_pf.current(index)
                    self.draw_grids(None)
            else:
                if self.combobox_level_pf.get() not in self.combobox_level_pf['values']:
                    self.combobox_level_pf.current(0)
                    self.draw_grids(None)

    def update_combobox_le(self, new_sel):
        if self.combobox_level_le:
            self.combobox_level_le['values'] = self.level_editor_keys
            if new_sel:
                if new_sel in self.combobox_level_le['values']:
                    index = self.combobox_level_le['values'].index(new_sel)
                    self.combobox_level_le.current(index)
                    self.draw_grids_editor(None)
            else:
                if self.combobox_level_le.get() not in self.combobox_level_le['values']:
                    self.combobox_level_le.current(0)
                    self.draw_grids_editor(None)