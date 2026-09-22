from mlx import Mlx
from typing import Any, cast
import random
from maze_gen import MazeGenerator, Cell, Directions


class ImgData:
    def __init__(self) -> None:
        self.img = None
        self.width = 0
        self.height = 0
        self.data = None
        self.sl = 0
        self.bpp = 0
        self.iformat = 0


class MLXVar:
    cell_size: int = 20

    # PALETA DE COLORES DISPONIBLES PARA LAS PAREDES
    wall_palette: list[tuple[int, int, int]] = [
        (180, 180, 180),
        (255, 120, 80),
        (120, 200, 255),
        (120, 255, 150),
        (255, 215, 90),
        (200, 120, 255),
    ]

    def __init__(self, maze: MazeGenerator) -> None:
        self.mlx: Mlx | None = None
        self.mlx_ptr: int = 0
        self.maze: MazeGenerator = maze
        self.screen_w: int = maze.width * self.cell_size + 40
        self.screen_h: int = maze.height * self.cell_size + 90
        self.win_1: Any | None = None
        self.win_2 = None
        self.img_1: ImgData | None = None
        self.show_solution: bool = False
        self.wall_color_idx: int = 0
        self.solution_cells: set[tuple[int, int]] = self.compute_solution_cells()

    def put_pixel_to_img(self, img: ImgData,
                         x: int, y: int, color: int) -> None:
        if not (0 <= x < img.width and 0 <= y < img.height):
            return
        bytes_per_pixel = img.bpp // 8
        offset = y * img.sl + x * bytes_per_pixel
        data = cast(memoryview, img.data)
        data[offset:offset + bytes_per_pixel] = color.to_bytes(4, 'little')

    def put_pixel(self, r: int, g: int, b: int, a: int = 255) -> int:
        return (a << 24) | (r << 16) | (g << 8) | b

    def draw_wall(self, img: ImgData, x: int, y: int,
                  walls: int, rgb: tuple[int, ...]) -> None:
        thickness = 2
        color = self.put_pixel(*rgb)
        if (walls & 1):
            for t in range(thickness):
                for dx in range(self.cell_size):
                    self.put_pixel_to_img(img, x + dx, y + t, color)
        if (walls & 2):
            for t in range(thickness):
                for dy in range(self.cell_size):
                    self.put_pixel_to_img(img, x + self.cell_size - 1 - t,
                                          y + dy, color)
        if (walls & 4):
            for t in range(thickness):
                for dx in range(self.cell_size):
                    self.put_pixel_to_img(img, x + dx,
                                          y + self.cell_size - 1 - t, color)
        if (walls & 8):
            for t in range(thickness):
                for dy in range(self.cell_size):
                    self.put_pixel_to_img(img, x + t, y + dy, color)

    def put_square(self, img: ImgData,
                   x: int, y: int, rgb: tuple[int, ...]) -> None:
        color = self.put_pixel(*rgb)
        for dx in range(self.cell_size):
            for dy in range(self.cell_size):
                self.put_pixel_to_img(img, x + dx, y + dy, color)

    def draw_cell(self, img: ImgData, cell: Cell, x: int, y: int) -> None:
        path_col = (0, 0, 0)
        solution_col = (90, 190, 255)
        base = self.wall_palette[self.wall_color_idx]
        jitter = random.randint(-25, 25)
        walls_col = tuple(max(0, min(255, c + jitter)) for c in base)
        ft_col = (200, 125, 23)
        entry_col = (6, 183, 56)
        exit_col = (23, 12, 240)
        if cell.untouchable:
            self.put_square(img, x, y, ft_col)
        elif cell.pos == self.maze.entry:
            self.put_square(img, x + 5, y + 5, entry_col)
        elif cell.pos == self.maze.exit:
            self.put_square(img, x, y, exit_col)
        elif self.show_solution and cell.pos in self.solution_cells:
            self.put_square(img, x, y, solution_col)
        else:
            self.put_square(img, x, y, path_col)
        self.draw_wall(img, x, y, cell.walls, walls_col)

    # TECLAS DEL MENÚ INTERACTIVO:
    def press_key(self, keynum: int, param: Any) -> None:
        if keynum in (113, 52):
            self.close_mini(param)
        elif keynum == 49:
            self.regenerate_maze()
        elif keynum == 50:
            self.toggle_solution()
        elif keynum == 51:
            self.rotate_wall_color()

    def close_mini(self, param: None) -> None:
        assert isinstance(self.mlx, Mlx)
        del param
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    # Ventana redimensionar, minimizar/restaurar, taparla con otra ventana
    def on_expose(self, param: None) -> None:
        assert isinstance(self.mlx, Mlx)
        assert isinstance(self.img_1, ImgData)
        del param
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_1, self.img_1.img, 20, 20)
        self.draw_menu_text()

    # FUNCIÓN CALCULAR LAS CELDAS DEL CAMINO SOLUCIÓN
    def compute_solution_cells(self) -> set[tuple[int, int]]:
        cells: set[tuple[int, int]] = {self.maze.entry}
        x, y = self.maze.entry
        for direction in self.maze.solution:
            dx, dy = Directions[direction].value
            x, y = x + dx, y + dy
            cells.add((x, y))
        return cells

    # OPCIÓN 2 DEL MENÚ: MOSTRAR / ESCONDER LA SOLUCIÓN
    def toggle_solution(self) -> None:
        self.show_solution = not self.show_solution
        state = "visible" if self.show_solution else "escondido"
        print(f"[A-Maze-ing] Camino solución: {state}.")
        self.redraw()

    # OPCIÓN 3 DEL MENÚ: ROTAR EL COLOR DE LAS PAREDES
    def rotate_wall_color(self) -> None:
        self.wall_color_idx = (self.wall_color_idx + 1) % len(self.wall_palette)
        print(f"[A-Maze-ing] Color de paredes #{self.wall_color_idx + 1}.")
        self.redraw()

    # OPCIÓN 1 DEL MENÚ: REGENERAR UN LABERINTO NUEVO
    def regenerate_maze(self) -> None:
        print("[A-Maze-ing] Regenerando laberinto...")
        try:
            new_maze = MazeGenerator()
            new_maze.gen_maze()
            new_maze.solve()
        except Exception as e:
            print(f"[A-Maze-ing] error al regenerar: {e}")
            return
        self.maze = new_maze
        self.solution_cells = self.compute_solution_cells()
        self.redraw()

    # DIBUJA EL  MENÚ  SOBRE LA VENTANA
    def draw_menu_text(self) -> None:
        assert isinstance(self.mlx, Mlx)
        text_color = self.put_pixel(255, 255, 255)
        base_y = 20 + self.maze.height * self.cell_size + 25
        lines = [
            "1: regen   2: path   3: color   4/q: salir",
        ]
        for i, line in enumerate(lines):
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_1, 20, base_y + i * 18,
                text_color, line)

    # VUELVE A DIBUJAR TODAS LAS CELDAS DEL LABERINTO
    def redraw(self) -> None:
        assert isinstance(self.mlx, Mlx)
        assert isinstance(self.img_1, ImgData)
        for x in range(self.maze.height):
            for y in range(self.maze.width):
                cell: Cell = self.maze.get_cell(x, y)
                self.draw_cell(
                    self.img_1,
                    cell,
                    y * self.cell_size,
                    x * self.cell_size)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_1.img,
            20,
            20)
        self.draw_menu_text()

    def renderize(self) -> None:
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()

        self.win_1 = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.screen_w,
            self.screen_h,
            "A_Maze_Ing"
        )

        self.img_1 = ImgData()
        self.img_1.width = self.maze.width * self.cell_size
        self.img_1.height = self.maze.height * self.cell_size
        self.img_1.img = self.mlx.mlx_new_image(
                       self.mlx_ptr,
                       self.img_1.width,
                       self.img_1.height)

        (self.img_1.data,
         self.img_1.bpp,
         self.img_1.sl,
         self.img_1.iformat
         ) = self.mlx.mlx_get_data_addr(
            self.img_1.img)

        for x in range(self.maze.height):
            for y in range(self.maze.width):
                cell: Cell = self.maze.get_cell(x, y)
                self.draw_cell(
                    self.img_1,
                    cell,
                    y * self.cell_size,
                    x * self.cell_size)

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_1.img,
            20,
            20)
        self.draw_menu_text()
        self.mlx.mlx_key_hook(self.win_1, self.press_key, None)
        self.mlx.mlx_hook(self.win_1, 33, 0, self.close_mini, None)
        self.mlx.mlx_expose_hook(self.win_1, self.on_expose, None)

        print("\n=== A-Maze-ing ===")
        print("1. Regenerar un nuevo laberinto")
        print("2. Mostrar / esconder el camino solución")
        print("3. Rotar el color de las paredes")
        print("4. Salir (también con 'q')")
        print("(la ventana debe tener el foco para recibir las teclas)\n")

        self.mlx.mlx_loop(self.mlx_ptr)

        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_1.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_1)
        self.mlx.mlx_release(self.mlx_ptr)
