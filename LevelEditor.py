import json
from dataclasses import dataclass

@dataclass
class TileData:
    type : int
    rot : int

@dataclass
class LevelData:
    path: list[int]
    grid: list[list[TileData]]

def json_serializer(obj):
    if isinstance(obj, LevelData):
        return {"path": obj.path, "grid": obj.grid}

    if isinstance(obj, TileData):
        return {"type": obj.type, "rot": obj.rot}

    raise TypeError(f"Type {type(obj)} not serializable")

class LevelJson:

    json_name = "config/levels.json"
    json_data : dict[str, LevelData] = {}

    def __init__(self):
        self.load_json()

    def load_json(self):
        if self.json_data:
            self.json_data.clear()
        with open(self.json_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for key, level in data.items():
                new_level_data = LevelData([],[])
                for i in level["path"]:
                    new_level_data.path.append(i)
                for row in level["grid"]:
                    grid_row = [TileData(cell["type"], cell["rot"]) for cell in row]
                    new_level_data.grid.append(grid_row)
                self.json_data[key] = new_level_data

    def save_json(self):
        with open(self.json_name, 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=4, default=json_serializer)

    def new_level(self, level_name):
        if level_name not in self.json_data:
            new_row = 8
            new_col = 9
            created_level = LevelData([10, 10, 10], [[TileData(6, 0) for _ in range(new_col)] for _ in range(new_row)])
            self.json_data[level_name] = created_level

    def delete_level(self, level_name):
        if level_name in self.json_data:
            self.json_data.pop(level_name)

    def get_level_data(self, level_name):
        if level_name in self.json_data:
            return self.json_data[level_name]

        return None


