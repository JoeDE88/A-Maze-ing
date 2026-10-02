from mlx import Mlx
from typing import Any
import random
from .maze_generator import MazeGenerator, Cell, Directions
from .drawing_utils import rgba_to_int32, put_pixel, draw_square, draw_wall


class ImgData:
    def __init__(self) -> None:
        self.img = None
        self.w = 0
        self.h = 0
        self.pos_x = 0
        self.pos_y = 0
        self.data = None
        self.sl = 0
        self.bpp = 0
        self.iformat = 0


class MLXVar:
    # Default cell size
    cell_size: int = 25

    # Color palette for cell walls
    palette: list[tuple[int, int, int]] = [
        (random.randint(30, 255),
         random.randint(30, 255),
         random.randint(30, 255)),
        (random.randint(30, 255),
         random.randint(30, 255),
         random.randint(30, 255)),
        (random.randint(30, 255),
         random.randint(30, 255),
         random.randint(30, 255)),
        (random.randint(30, 255),
         random.randint(30, 255),
         random.randint(30, 255)),
    ]

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze: MazeGenerator = maze
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: int = self.mlx.mlx_init()
        self.pos_x: int = 20
        self.imgs_w: int = self.maze.w * self.cell_size
        self.img_conf: ImgData = self.create_img(self.imgs_w,
                                                 80,
                                                 self.pos_x,
                                                 20)
        self.img_maze: ImgData = self.create_img(self.imgs_w,
                                                 self.maze.h * self.cell_size,
                                                 self.pos_x,
                                                 (self.img_conf.h +
                                                  self.img_conf.pos_y))
        self.img_menu: ImgData = self.create_img(self.imgs_w,
                                                 100,
                                                 self.pos_x,
                                                 (self.img_conf.h +
                                                  self.img_maze.h +
                                                  40))
        self.screen_w: int = self.img_maze.w + 40
        if self.screen_w < 415:
            self.screen_w = 415
            self.img_maze.pos_x = (self.screen_w - self.img_maze.w) // 2
        self.screen_h: int = (self.img_maze.h +
                              self.img_conf.h +
                              self.img_menu.h +
                              40)
        self.win_1: Any = self.mlx.mlx_new_window(self.mlx_ptr,
                                                  self.screen_w,
                                                  self.screen_h,
                                                  "A_Maze_Ing")
        self.show_solution: bool = False
        self.wall_color_idx: int = 0
        self.solution_cells: set[tuple[int, int]] = self.find_solution_cells()

    def draw_cell(self, img: ImgData, cell: Cell, x: int, y: int) -> None:
        path_col = (0, 0, 0)
        solution_col = (90, 190, 255)
        base = self.palette[self.wall_color_idx]
        jitter = random.randint(-50, 50)
        walls_col = tuple(max(0, min(255, c + jitter)) for c in base)
        ft_col = (237, 52, 145)
        entry_col = (6, 183, 56)
        exit_col = (23, 12, 240)
        if cell.untouchable:
            draw_square(img, self.cell_size, x, y, ft_col)
        elif cell.pos == self.maze.entry:
            draw_square(img, self.cell_size, x + 5, y + 5, entry_col)
        elif cell.pos == self.maze.exit:
            draw_square(img, self.cell_size, x, y, exit_col)
        elif self.show_solution and cell.pos in self.solution_cells:
            draw_square(img, self.cell_size, x, y, solution_col)
        else:
            draw_square(img, self.cell_size, x, y, path_col)
        draw_wall(img, self.cell_size, x, y, cell.walls, walls_col)

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
        del param
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def find_solution_cells(self) -> set[tuple[int, int]]:
        cells: set[tuple[int, int]] = {self.maze.entry}
        x, y = self.maze.entry
        for direction in self.maze.solution:
            dx, dy = Directions[direction].value
            x, y = x + dx, y + dy
            cells.add((x, y))
        return cells

    def toggle_solution(self) -> None:
        self.show_solution = not self.show_solution
        self.redraw()

    def rotate_wall_color(self) -> None:
        self.wall_color_idx = (self.wall_color_idx + 1) % len(self.palette)
        print(f"[A-Maze-ing] Walls color #{self.wall_color_idx + 1}.")
        self.redraw()

    def regenerate_maze(self) -> None:
        print("[A-Maze-ing] Regenerating maze...")
        try:
            new_maze = MazeGenerator()
            new_maze.gen_maze()
            new_maze.solve()
        except Exception as e:
            print(f"[A-Maze-ing] error while regenerating: {e}")
            return
        self.maze = new_maze
        self.solution_cells = self.find_solution_cells()
        self.redraw()

    def fill_img(self, img: ImgData, color: int) -> None:
        for y in range(img.h):
            for x in range(img.w):
                put_pixel(img, x, y, color)

    def draw_menu_text(self) -> None:
        text_color = rgba_to_int32(255, 255, 255)
        base_y = self.img_menu.pos_y
        lines = [
            "1: Regenerate maze",
            "2: Show/Hide solution",
            "3: Change color",
            "4 or q: Quit",
        ]
        for i, line in enumerate(lines):
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_1, 20, base_y + i * 20,
                text_color, line)

    def draw_config_text(self) -> None:
        config_color = rgba_to_int32(255, 255, 255)
        first_col_x = self.img_conf.pos_x
        first_col_y = self.img_conf.pos_y
        second_col_x = self.img_conf.pos_x + 100
        second_col_y = self.img_conf.pos_y
        third_col_x = self.img_conf.pos_x + 200
        third_col_y = self.img_conf.pos_y
        fourth_col_x = self.img_conf.pos_x + 300
        fourth_col_y = self.img_conf.pos_y
        first_col = [
            "WIDTH:",
            "ENTRY:",
            "PERFECT:"
        ]
        second_col = [
            f"{self.maze.w}",
            f"{self.maze.entry}",
            f"{self.maze.perfect}"
        ]
        third_col = [
            "HEIGHT:",
            "EXIT:",
            "SEED:"
        ]
        fourth_col = [
            f"{self.maze.h}",
            f"{self.maze.exit}",
        ]
        if self.maze.seed:
            fourth_col.append(f"'{self.maze.seed}'")
        else:
            fourth_col.append("None")

        for i, line in enumerate(first_col):
            self.mlx.mlx_string_put(self.mlx_ptr,
                                    self.win_1,
                                    first_col_x,
                                    first_col_y + i * 20,
                                    config_color,
                                    line)

        for i, line in enumerate(second_col):
            self.mlx.mlx_string_put(self.mlx_ptr,
                                    self.win_1,
                                    second_col_x,
                                    second_col_y + i * 20,
                                    config_color,
                                    line)

        for i, line in enumerate(third_col):
            self.mlx.mlx_string_put(self.mlx_ptr,
                                    self.win_1,
                                    third_col_x,
                                    third_col_y + i * 20,
                                    config_color,
                                    line)

        for i, line in enumerate(fourth_col):
            self.mlx.mlx_string_put(self.mlx_ptr,
                                    self.win_1,
                                    fourth_col_x,
                                    fourth_col_y + i * 20,
                                    config_color,
                                    line)

    def redraw(self) -> None:
        for x in range(self.maze.h):
            for y in range(self.maze.w):
                cell: Cell = self.maze.get_cell(x, y)
                self.draw_cell(
                    self.img_maze,
                    cell,
                    y * self.cell_size,
                    x * self.cell_size)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_maze.img,
            self.img_maze.pos_x,
            self.img_maze.pos_y
        )

    def create_img(self, w: int, h: int, pos_x: int, pos_y: int) -> ImgData:
        img = ImgData()
        img.w = w
        img.h = h
        img.pos_x = pos_x
        img.pos_y = pos_y
        img.img = self.mlx.mlx_new_image(
                        self.mlx_ptr,
                        img.w,
                        img.h)

        (img.data,
         img.bpp,
         img.sl,
         img.iformat
         ) = self.mlx.mlx_get_data_addr(img.img)

        return img

    def on_expose(self, param: None) -> None:
        del param
        self.renderize()

    def clean_resources(self) -> None:
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_conf.img)
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_maze.img)
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_menu.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_1)
        self.mlx.mlx_release(self.mlx_ptr)

    def declare_hooks(self) -> None:
        self.mlx.mlx_expose_hook(self.win_1, self.on_expose, None)
        self.mlx.mlx_key_hook(self.win_1, self.press_key, None)
        self.mlx.mlx_hook(self.win_1, 33, 0, self.close_mini, None)

    def run(self) -> None:
        self.declare_hooks()
        for x in range(self.maze.h):
            for y in range(self.maze.w):
                cell: Cell = self.maze.get_cell(x, y)
                self.draw_cell(
                    self.img_maze,
                    cell,
                    y * self.cell_size,
                    x * self.cell_size)
        self.fill_img(self.img_conf, 0xFF000000)
        self.fill_img(self.img_menu, 0xFF000000)
        self.renderize()
        self.mlx.mlx_loop(self.mlx_ptr)
        self.clean_resources()

    def renderize(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_1)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_conf.img,
            self.img_conf.pos_x,
            self.img_conf.pos_y)

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_maze.img,
            self.img_maze.pos_x,
            self.img_maze.pos_y)

        # menu
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_1,
            self.img_menu.img,
            self.img_menu.pos_x,
            self.img_menu.pos_y)

        self.draw_menu_text()
        self.draw_config_text()
