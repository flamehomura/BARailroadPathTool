import heapq
from LevelData import GridLevel
from LevelData import GridData
from collections import namedtuple
from itertools import count

class GridMap:

    level_grids : GridLevel = None
    valid_grid_map : dict[tuple[int, int], GridData] = {}
    fixed_grid_map : dict[tuple[int, int], GridData] = {}
    poi_grid_map : dict[tuple[int, int], GridData] = {}

    fixed_grid_list : list[tuple[int, int, int]] = []

    start_coord = None
    goal_coord = None

    hex_dirs_odd = [
        (-1, 0), (0, -1), (1, -1),
        (1, 0), (1, +1), (0, +1)
    ]
    hex_dirs_even = [
        (-1, 0), (-1, -1), (0, -1),
        (1, 0), (0, +1), (-1, +1)
    ]

    SidePos = namedtuple("SidePos", ["x", "y", "side_idx"])

    def __init__(self, levelgrids):
        self.level_grids = levelgrids

        #self.grid_coords = {(x, y) for y in range(len(self.level_grids.grids)) for x in range(len(self.level_grids.grids[y]))}
        self.grid_coords = set()
        self.valid_grid_map.clear()
        self.fixed_grid_map.clear()
        self.poi_grid_map.clear()

        for i, row in enumerate(self.level_grids.grids):
            for j, data in enumerate(row):
                if data.type == 0:
                    self.valid_grid_map[(j, i)] = data
                elif data.type == 4:
                    self.start_coord = (j, i, data.rot)
                elif data.type == 5:
                    self.goal_coord = (j, i, data.rot)
                elif data.type == 7:
                    self.poi_grid_map[(j, i)] = data
                    self.valid_grid_map[(j, i)] = data
                elif data.type < 0:
                    self.fixed_grid_map[(j, i)] = data

    def get_next_pos(self, from_pos):
        x, y, i = from_pos
        dir_pos = (0, 0)
        if y % 2 == 0:
            dir_pos = self.hex_dirs_even[i]
        elif y % 2 == 1:
            dir_pos = self.hex_dirs_odd[i]

        target_x, target_y = x + dir_pos[0], y + dir_pos[1]
        target_d = (i + 3) % 6

        if (target_x, target_y) in self.fixed_grid_map:
            grid_data = self.fixed_grid_map[(target_x, target_y)]
            if target_d != grid_data.rot and target_d != (grid_data.rot + abs(grid_data.type)) % 6:
                return None
            else:
                return GridMap.SidePos(target_x, target_y, target_d)
        elif ((target_x, target_y) in self.valid_grid_map) or (target_x, target_y, target_d) == self.goal_coord:
            return GridMap.SidePos(target_x, target_y, target_d)

        return None

    @staticmethod
    def get_path_type(from_pos, to_pos):
        from_x, from_y, from_i = from_pos
        to_x, to_y, to_i = to_pos
        type = abs(((to_i - 3) % 6) - from_i)
        if type > 3:
            type = abs(6 - type)
        elif type < -3:
            type = abs(type + 6)

        return type

    def get_valid_goal(self, from_pos):
        x, y, i = from_pos
        goals = []
        goal_pos = None
        target_i = 0
        if (x, y) in self.fixed_grid_map:
            grid_data = self.fixed_grid_map[(x, y)]
            target_i = (grid_data.rot + abs(grid_data.type)) % 6
            if grid_data.rot == i:
                goal_pos = self.get_next_pos(GridMap.SidePos(x, y, target_i))
            elif target_i == i:
                goal_pos = self.get_next_pos(GridMap.SidePos(x, y, grid_data.rot))
            if goal_pos is not None:
                goals.append((goal_pos, abs(grid_data.type)))
        else:
            for path_type in range(-3, 3):
                if path_type == 0:
                    continue
                target_i = (i + path_type) % 6
                goal_pos = self.get_next_pos(GridMap.SidePos(x, y, target_i))
                if goal_pos is not None:
                    goals.append((goal_pos, abs(path_type)))

        return goals

    def calc_path(self, path_limits, get_bonus, use_shortest):
        start_pos = self.get_next_pos(self.start_coord)
        if start_pos is None:
            return None
        counter = count()
        path_costs = {1 : 0, 2 : 0, 3 : 0}
        cost = 0
        paths = [start_pos]
        fixed_grids = set(self.fixed_grid_map.keys())
        if get_bonus:
            fixed_grids |= set(self.poi_grid_map.keys())

        return self.get_path_from_to(start_pos, self.goal_coord, use_shortest, cost, counter, path_costs, fixed_grids, paths, path_limits)

    def get_path_from_to(self, from_pos, to_pos, shortest, cost, counter, path_costs, fixed_grids, paths, path_limits):
        if from_pos is None:
            return None

        path_set = set()
        path_set.add((from_pos.x, from_pos.y))

        heap = [(cost, next(counter), from_pos, path_costs, frozenset(), paths, path_set)]
        visited_state = set()
        best_path = None
        best_used = 0
        if shortest:
            best_used = path_limits[0] + path_limits[1] + path_limits[2] + 1

        while heap:
            cost, _, current, path_cost, grids, path, path_coord = heapq.heappop(heap)
            current_state = (current, path_cost[1], path_cost[2], path_cost[3], grids)
            if current_state in visited_state:
                continue
            visited_state.add(current_state)

            if current == to_pos and grids == fixed_grids:
                used_total = path_cost[1] + path_cost[2] + path_cost[3]
                if shortest and used_total < best_used:
                    best_used = used_total
                    best_path = (cost, path_cost.copy(), path)

                elif not shortest and used_total > best_used:
                    best_used = used_total
                    best_path = (cost, path_cost.copy(), path)
                continue

            # print(f"Current: {current} path_costs: {path_cost} path: {path}")
            for next_pos, path_type in self.get_valid_goal(current):
                if (next_pos.x, next_pos.y) in path_coord:
                    continue
                if (current.x, current.y) not in self.fixed_grid_map:
                    if path_cost[path_type] >= path_limits[path_type - 1]:
                        continue
                    new_path_cost = path_cost.copy()
                    new_path_cost[path_type] += 1
                    new_cost = cost
                    if shortest:
                        new_cost += int((new_path_cost[path_type] / path_limits[path_type - 1]) ** 2 * 500)
                    else:
                        new_cost -= int((new_path_cost[path_type] / path_limits[path_type - 1]) ** 2 * 500)

                    if (next_pos.x, next_pos.y) in self.poi_grid_map:
                        new_cost -= 1000
                    if (next_pos.x, next_pos.y) in self.fixed_grid_map:
                        new_cost -= 1000
                    new_path_coord = path_coord.copy()
                    new_path_coord.add((next_pos.x, next_pos.y))

                    new_grids = grids
                    if (current.x, current.y) in fixed_grids:
                        new_grids |= {(current.x, current.y)}

                    # print(f"Next: {next_pos}")
                    heapq.heappush(heap, (new_cost, next(counter), next_pos, new_path_cost, new_grids, path + [next_pos], new_path_coord))

                    # print(f"Current: {next_pos} costs: {new_cost} path: {path}")

                else:
                    new_path_cost = path_cost.copy()
                    new_cost = cost
                    new_path_coord = path_coord.copy()
                    new_path_coord.add((next_pos.x, next_pos.y))

                    new_grids = grids | {(current.x, current.y)}

                    # print(f"Next: {next_pos}")
                    heapq.heappush(heap, (new_cost, next(counter), next_pos, new_path_cost, new_grids, path + [next_pos], new_path_coord))

        return best_path
