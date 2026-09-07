import random
import numpy as np
from conf_validator import check_config, ConfigModel
from enum import Enum
from typing import cast

import time


class Directions(Enum):
    N = (-1, 0)
    E = (0, +1)
    S = (+1, 0)
    W = (0, -1)


class Walls(Enum):
    N = 0b1110
    E = 0b1101
    S = 0b1011
    W = 0b0111


class MazeGenerator():

    def __init__(self) -> None:
        config: ConfigModel = check_config()
        self.width = config["WIDTH"]
        self.height = config["HEIGHT"]
        self.center = (self.height // 2, self.width // 2)
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.perfect = config["PERFECT"]
        self.grid = np.ndarray((self.height, self.width), dtype=object)
        self.one_walls = [0b0111, 0b1011, 0b1101, 0b1110]
        self.populate_grid()
        self.output = config["OUTPUT_FILE"]
        try:
            self.check_fortytwo()
        except Exception as e:
            print(e)

    def check_fortytwo(self) -> None:
        if self.width < 9 or self.height < 7:
            raise Exception("Maze size is too small to print '42'")
        start_point: tuple[int, int] = (self.center[0] - 2, self.center[1] - 3)
        fortytwo = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]
        x = start_point[0]
        for i in fortytwo:
            y = start_point[1]
            for j in i:
                if j == 1:
                    self.get_cell(x, y).untouchable = True
                y += 1
            x += 1

    def populate_grid(self) -> None:
        for x in range(self.height):
            for y in range(self.width):
                self.grid[x][y] = Cell(x, y)

    def get_cell(self, x: int | None, y: int | None) -> Cell:
        return cast(Cell, self.grid[x][y])

    def get_corners(self) -> list[Cell]:
        corners = []
        if self.get_cell(0, 0).walls in self.one_walls:
            corners.append(self.get_cell(0, 0))
        if self.get_cell(0, self.width - 1).walls in self.one_walls:
            corners.append(self.get_cell(0, self.width - 1))
        if self.get_cell(self.height - 1, 0).walls in self.one_walls:
            corners.append(self.get_cell(self.height - 1, 0))
        if self.get_cell(self.height - 1,
                         self.width - 1).walls in self.one_walls:
            corners.append(self.get_cell(self.height - 1, self.width - 1))
        return corners

    def gen_maze(self) -> None:
        pos: tuple[int, int] | tuple[None, None] = self.entry
        x2, y2 = pos
        while True:
            x, y = x2, y2
            if x is None:
                break
            while x is not None:
                x, y = self.walk(x, y)
            while x2 is not None:
                x2, y2 = self.hunt(x2, y2)
                break
        if not self.perfect:
            self.open_corners()
            self.open_dead_ends()

    def open_corners(self) -> None:
        corners = self.get_corners()
        for i in range(len(corners)):
            cell = corners[i]
            x, y = cell.pos[0], cell.pos[1]
            directions = list(Directions)
            nx, ny = 0, 0
            while directions:
                new_dir = random.choice(directions)
                directions.remove(new_dir)
                if x is not None and y is not None:
                    nx, ny = x + new_dir.value[0], y + new_dir.value[1]
                if all([nx >= 0, ny >= 0, ny < self.width, nx < self.height]):
                    ncell = self.get_cell(nx, ny)
                    cell.open_wall(new_dir.name)
                    ncell.open_opposite(new_dir.name)

    def open_dead_ends(self) -> None:
        for x in range(self.height):
            for y in range(self.width):
                cell: Cell = self.get_cell(x, y)
                if cell.walls in self.one_walls:
                    path = Walls(cell.walls).name
                    directions = [direction for direction in Directions
                                  if direction.name != path]
                    while directions:
                        new_dir = random.choice(directions)
                        directions.remove(new_dir)
                        nx, ny = x + new_dir.value[0], y + new_dir.value[1]
                        if all([nx >= 0, ny >= 0,
                                ny < self.width, nx < self.height]):
                            if not self.get_cell(nx, ny).untouchable:
                                ncell = self.get_cell(nx, ny)
                                cell.open_wall(new_dir.name)
                                ncell.open_opposite(new_dir.name)
                                break

    def walk(self, x: int | None, y: int | None) \
            -> tuple[int, int] | tuple[None, None]:
        directions = list(Directions)
        nx, ny = 0, 0
        cell = self.get_cell(x, y)
        cell.visited = True
        while directions:
            new_dir = random.choice(directions)
            directions.remove(new_dir)
            if x is not None and y is not None:
                nx, ny = x + new_dir.value[0], y + new_dir.value[1]
            if all([nx >= 0, ny >= 0, ny < self.width, nx < self.height]):
                n_cell: Cell = self.get_cell(nx, ny)
                if not n_cell.visited and not n_cell.untouchable:
                    self.get_cell(nx, ny).visited = True
                    cell.open_wall(new_dir.name)
                    n_cell.open_opposite(new_dir.name)
                    return (nx, ny)
        return (None, None)

    def find_neighbors(self, x: int, y: int) -> list[Directions]:
        existing_neighbors = []
        if x > 0 and self.get_cell(x - 1, y).visited and \
           not self.get_cell(x - 1, y).untouchable:
            existing_neighbors.append(Directions.N)
        if y > 0 and self.get_cell(x, y - 1).visited and \
           not self.get_cell(x, y - 1).untouchable:
            existing_neighbors.append(Directions.W)
        if y + 1 < self.width and self.get_cell(x, y + 1).visited and \
           not self.get_cell(x, y + 1).untouchable:
            existing_neighbors.append(Directions.E)
        if x + 1 < self.height and self.get_cell(x + 1, y).visited and \
           not self.get_cell(x + 1, y).untouchable:
            existing_neighbors.append(Directions.S)
        return existing_neighbors

    def hunt(self, x: int | None, y: int | None) \
            -> tuple[int, int] | tuple[None, None]:
        for x in range(self.height):
            for y in range(self.width):
                cell: Cell = self.get_cell(x, y)
                if not cell.visited and not cell.untouchable:
                    cell.visited = True
                    existing_neighbors = self.find_neighbors(x, y)
                    if existing_neighbors:
                        new_dir = random.choice(existing_neighbors)
                        nx, ny = x + new_dir.value[0], y + new_dir.value[1]
                        ncell: Cell = self.get_cell(nx, ny)
                        ncell.visited = True
                        cell.open_wall(new_dir.name)
                        ncell.open_opposite(new_dir.name)
                    return (x, y)
        return (None, None)

    def solve(self) -> None:
        start = list(self.entry)
        end = self.exit
        # print(tuple(map(sum, zip(start, Directions['S'].value))))

    def gen_output(self) -> None:
        with open(self.output, "w") as file:
            x = 0
            for x in range(self.height):
                y = 0
                for y in range(self.width):
                    file.write(f"{self.grid[x][y].walls:x}")
                    y += 1
                    if y == self.width:
                        file.write("\n")
                x += 1
            file.write("\n")
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")
            file.close()


class Cell():
    def __init__(self, x: int | None, y: int | None,
                 visited: bool = False, untouchable: bool = False) -> None:
        self.pos = (x, y)
        self.visited = bool(visited)
        self.untouchable = bool(untouchable)
        self.walls = 0b1111

    def __repr__(self) -> str:
        return f"{self.pos}"

    def open_wall(self, direction: str) -> None:
        wall = Walls[direction].value
        self.walls &= wall

    def open_opposite(self, direction: str) -> None:
        if direction == 'N' or direction == 'S':
            opp_direction = Walls[direction].value ^ 0b0101
        else:
            opp_direction = Walls[direction].value ^ 0b1010
        self.walls &= opp_direction
