from dataclasses import dataclass
import json

@dataclass
class GridData:
    type : int
    rot : int

class GridLevel:

    json_file_name = "config/levels.json"
    paths : list[int] = []
    grids : list[list[GridData]] = []

    def __init__(self, level_name):
        with open(self.json_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)

            self.paths.clear()
            self.grids.clear()

            for key, level in data.items():
                if key == level_name:
                    path = level["path"]
                    for i in path:
                        self.paths.append(i)
                    grid = level["grid"]
                    for row in grid:
                        grid_row = [GridData(cell["type"], cell["rot"]) for cell in row]
                        self.grids.append(grid_row)