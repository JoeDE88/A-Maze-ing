import numpy as np
from conf_validator import check_config, ConfigModel
from enum import Enum
from typing import cast, TYPE_CHECKING, Any
import random

if TYPE_CHECKING:
    from maze_visuals import ImgData
import heapq

import time


class Directions(Enum):
    N = (-1, 0)
    E = (0, +1)
    S = (+1, 0)
    W = (0, -1)


# PAREDES EXISTENTES POR CADA CELDA, EN BINARIO:
class Walls(Enum):
    N = 0b1110
    E = 0b1101
    S = 0b1011
    W = 0b0111


# CELDAS
class Cell():
    def __init__(self, x: int, y: int,
                 visited: bool = False, untouchable: bool = False) -> None:
        self.pos: tuple[int, int] = (x, y)
        self.visited: bool = bool(visited)
        self.untouchable: bool = bool(untouchable)
        self.walls: int = 0b1111
        self.visual: ImgData | None = None

    # FUNCIÓN PARA ABRIR PARED DESDE CELDA ACTUAL
    def open_wall(self, direction: str) -> None:
        wall = Walls[direction].value
        self.walls &= wall

    # FUNCIÓN PARA ABRIR PARED DESDE CELDA VECINA
    def open_opposite(self, direction: str) -> None:
        if direction == 'N' or direction == 'S':
            opp_direction = Walls[direction].value ^ 0b0101
        else:
            opp_direction = Walls[direction].value ^ 0b1010
        self.walls &= opp_direction


class MazeGenerator():

    def __init__(self) -> None:
        config: ConfigModel = check_config()
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.center: tuple[int, int] = (self.height // 2, self.width // 2)
        self.entry: tuple[int, int] = config["ENTRY"]
        self.exit: tuple[int, int] = config["EXIT"]
        self.perfect: bool = config["PERFECT"]
        self.grid: np.ndarray[Any, np.dtype[Any]] = np.empty((self.height,
                                                             self.width),
                                                             dtype=object)
        self.one_walls: list[int] = [0b0111, 0b1011, 0b1101, 0b1110]
        self.populate_grid()
        self.solution: list[str] = []
        self.output: str = config["OUTPUT_FILE"]
        try:
            self.check_fortytwo()
        except Exception as e:
            print(e)

    # FUNCIÓN PARA VERIFICAR QUE LE 42 CABE DENTRO DEL MAZE
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

    # FUNCIÓN PARA INSTANCIAR UNA CELDA POR CADA POSICIÓN DEL ARRAY self.grid
    def populate_grid(self) -> None:
        for x in range(self.height):
            for y in range(self.width):
                self.grid[x][y] = Cell(x, y)

    # FUNCIÓN PARA OBTENER LA CELDA SEGÚN POSICIÓN x, y
    def get_cell(self, x: int, y: int) -> Cell:
        return cast(Cell, self.grid[x][y])

    # FUNCIÓN PARA OBTENER LA LISTA DE LAS CELDAS EN LAS 4 ESQUINAS CON 3 PAREDES
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

    # FUNCIÓN PARA ABRIR LAS PAREDES DE LAS CELDAS EN LA LISTA DE CELDAS DE LAS ESQUINAS
    def open_corners(self) -> None:
        corners = self.get_corners()
        for i in range(len(corners)):
            cell = corners[i]
            x, y = cell.pos[0], cell.pos[1]
            directions = list(Directions)
            while directions:
                new_dir = random.choice(directions)
                directions.remove(new_dir)
                nx, ny = x + new_dir.value[0], y + new_dir.value[1]
                if all(
                       [
                        nx >= 0,
                        ny >= 0,
                        ny < self.width,
                        nx < self.height
                        ]
                        ):
                    ncell = self.get_cell(nx, ny)
                    cell.open_wall(new_dir.name)
                    ncell.open_opposite(new_dir.name)

    # FUNCIÓN PARA ABRIR CUALQUIER CELDA QUE TENGA 3 PAREDES
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
                        if all(
                               [nx >= 0,
                                ny >= 0,
                                ny < self.width,
                                nx < self.height
                                ]
                                ):
                            if not self.get_cell(nx, ny).untouchable:
                                ncell = self.get_cell(nx, ny)
                                cell.open_wall(new_dir.name)
                                ncell.open_opposite(new_dir.name)
                                break

    #####################################################################################
    #       AQUÌ EMPIEZAN LAS FUNCIONES PARA GENERAR EL MAZE                            #
    #       ALGORITMO: HUNT & KILL                                                      #
    #####################################################################################

    # FUNCIÓN PRINCIPAL DEL ALGORITMO
    def gen_maze(self) -> None:
        pos: tuple[int, int] = self.entry
        x2, y2 = pos
        while True:
            x, y = x2, y2
            if x == -1:
                break
            while x != -1:
                x, y = self.walk(x, y)
            while x2 != -1:
                x2, y2 = self.hunt(x2, y2)
                break
        if not self.perfect:
            self.open_corners()
            self.open_dead_ends()

    # PRIMERA PARTE DEL ALGORITMO:
    # se empieza desde la entrada, aleatoriamente elige una dirección para moverse de celda
    # y verifica que:
    # esté dentro de los limites
    # que la siguiente celda no haya ya sido visitada,
    # que la siguiente celda no sea parte de las que forman el 42
    # si todo esto pasa, abre las paredes de ambas
    def walk(self, x: int, y: int) \
            -> tuple[int, int]:
        directions = list(Directions)
        cell = self.get_cell(x, y)
        cell.visited = True
        while directions:
            new_dir = random.choice(directions)
            directions.remove(new_dir)
            nx, ny = x + new_dir.value[0], y + new_dir.value[1]
            if all(
                   [
                    nx >= 0,
                    ny >= 0,
                    ny < self.width,
                    nx < self.height
                    ]
                    ):
                n_cell: Cell = self.get_cell(nx, ny)
                if not n_cell.visited and not n_cell.untouchable:
                    self.get_cell(nx, ny).visited = True
                    cell.open_wall(new_dir.name)
                    n_cell.open_opposite(new_dir.name)
                    return (nx, ny)
        return (-1, -1)

    # FUNCIÓN AUXILIAR DE hunt() PARA ENCONTRAR CELDAS VECINAS EXISTENTES Y YA VISITADAS
    def find_neighbors(self, x: int, y: int) -> list[Directions]:
        existing_neighbors: list[Directions] = []
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

    # SEGUNDA PARTE DEL ALGORITMO
    # empezando desde la celda de entrada, encuentra la primera celda que no haya sido visitada
    # cuando la encuentra, verifica que tenga una celda vecina ya visitada, y abre las paredes de ambas
    def hunt(self, x: int, y: int) \
            -> tuple[int, int]:
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
        return (-1, -1)

    #####################################################################################
    #       AQUÌ EMPIEZAN LAS FUNCIONES PARA ENCONTRAR EL CAMINO                        #
    #       ALGORITMO: DIJKSTRA                                                         #
    #####################################################################################
    def possible_directions(self, x: int, y: int) -> list[tuple[int, int]]:
        cell = self.get_cell(x, y)
        directions: list[tuple[int, int]] = []
        if not cell.walls & 1:
            directions.append(Directions['N'].value)
        if not cell.walls & 2:
            directions.append(Directions['E'].value)
        if not cell.walls & 4:
            directions.append(Directions['S'].value)
        if not cell.walls & 8:
            directions.append(Directions['W'].value)
        return directions

    # FUNCIÓN PRINCIPAL
    def dijkstra(self) -> list[str] | None:
        start = list(self.entry)
        end = list(self.exit)
        solution: list[list[int | list[int]]] = []
        visited = [[False for _ in range(self.width)]
                   for _ in range(self.height)]
        visited[start[0]][start[1]] = True
        queue: list[list[int | list[int]]] = []

        node: list[int | list[int]] = [0, start]
        heapq.heappush(solution, node)
        heapq.heappush(queue, node)

        while queue:
            dist, cell = heapq.heappop(queue)
            assert isinstance(dist, int)
            assert isinstance(cell, list)

            if cell[0] == end[0] and cell[1] == end[1]:
                path = self.get_solution(solution)
                return path
            open_dir = self.possible_directions(cell[0], cell[1])
            for i in range(len(open_dir)):
                x = cell[0] + open_dir[i][0]
                y = cell[1] + open_dir[i][1]

                if (((x >= 0) and (x < self.height)
                   and (y >= 0) and (y < self.width))
                   and not visited[x][y]):
                    if not self.get_cell(x, y).untouchable:
                        visited[x][y] = True
                        n_cell: list[int | list[int]] = [dist + 1, [x, y]]
                        heapq.heappush(solution, n_cell)
                        heapq.heappush(queue, n_cell)
        return None

    def check_neighbor(self, cell: Cell, n_cell: Cell) -> bool:
        x, y = cell.pos
        assert isinstance(x, int)
        assert isinstance(y, int)
        directions = self.possible_directions(x, y)
        neighbor = False
        for i in range(len(directions)):
            if n_cell.pos[0] == x + directions[i][0] \
               and n_cell.pos[1] == y + directions[i][1]:
                neighbor = True
        return neighbor

    def get_solution(self, solution: list[list[int | list[int]]]) -> list[str]:
        path: list[str] = []
        distance: int | None = None
        prev_cell: list[int] | None = None
        for i in range(len(solution)-1, -1, -1):
            pos = solution[i][1]
            step = solution[i][0]
            assert isinstance(step, int)
            assert isinstance(pos, list)
            if not distance and not prev_cell:
                if pos == list(self.exit):
                    distance = step - 1
                    prev_cell = pos
            else:
                nx, ny = pos[0], pos[1]
                assert isinstance(prev_cell, list)
                assert isinstance(distance, int)
                x, y = prev_cell[0], prev_cell[1]
                is_neighbor = self.check_neighbor(self.get_cell(x, y),
                                                  self.get_cell(nx, ny))
                if distance == step and is_neighbor:
                    direction = pos[0] - prev_cell[0], pos[1] - prev_cell[1]
                    path.append(Directions(direction).name)
                    distance -= 1
                    prev_cell = pos
        return path

    def solve(self) -> None:
        solution: list[str] | None = self.dijkstra()
        assert isinstance(solution, list)
        for i in range(len(solution)):
            if solution[i] == 'N' or solution[i] == 'S':
                opp_direction = Walls[solution[i]].value ^ 0b0101
            else:
                opp_direction = Walls[solution[i]].value ^ 0b1010
            solution[i] = Walls(opp_direction).name
        self.solution = solution[::-1]

    # FUNCION QUE GENERA EL FILE output_maze.txt CON LA INFO DE:
    # LAS PAREDES
    # ENTRADA, SALIDA
    # CAMINO PARA LA SALIDA
    def gen_output(self) -> None:
        with open(self.output, "w") as file:
            x = 0
            for x in range(self.height):
                y = 0
                for y in range(self.width):
                    file.write(f"{self.get_cell(x, y).walls:x}")
                    y += 1
                    if y == self.width:
                        file.write("\n")
                x += 1
            file.write("\n")
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")
            for direction in self.solution:
                file.write(direction)
            file.close()
