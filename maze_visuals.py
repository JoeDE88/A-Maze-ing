from mlx import Mlx
from typing import TYPE_CHECKING, Any
import random

if TYPE_CHECKING:
    from maze_gen import MazeGenerator

class ImgData:
    def __init__(self) -> None:
        self.img: Any | None = None
        self.width = 0
        self.height = 0
        self.data: Any | None = None
        self.sl = 0
        self.bpp = 0
        self.iformat = 0


class MLXVar:
    def __init__(self, maze) -> None:
        self.mlx: Any | None = None
        self.mlx_ptr: Any | None = None
        self.maze: MazeGenerator = maze
        self.screen_w = maze.width * 20 + 40
        self.screen_h = maze.height * 20 + 90
        self.win_1 = None
        self.win_2 = None


    def put_pixel_to_img(self, img, x, y, color) -> None:
        bytes_per_pixel = img.bpp // 8
        offset = y * img.sl + x * bytes_per_pixel
        img.data[offset:offset + bytes_per_pixel] = color.to_bytes(4, 'little')


    def put_pixel(self, r, g, b, a = 255) -> None:
        return (r << 24) | (g << 16 ) | (b << 8) | a

    def put_square(self, img, rgb=(125,125,125)) -> None:
        color =  self.put_pixel(*rgb)
        for i in range(img.width):
            for j in range(img.height):
                if i * j < len(img.data) - 3:
                    self.put_pixel_to_img(img, i, j, color)
                    # pos = (i * 20 + j) * 4
                    # img.data[pos:pos+4] = (0xFFFF0000).to_bytes(4, 'little')


    def renderize(self) -> None:
        self.mlx = Mlx()

        self.mlx_ptr = self.mlx.mlx_init()
        self.win_1 = self.mlx.mlx_new_window(self.mlx_ptr, self.screen_w, self.screen_h, "A_Maze_Ing")
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                cell = self.maze.get_cell(x, y)
                cell.visual = ImgData()
                cell.visual.width = 20
                cell.visual.height = 20
                cell.visual.img = self.mlx.mlx_new_image(self.mlx_ptr, cell.visual.width, cell.visual.height)
                cell.visual.data, cell.visual.bpp, cell.visual.sl, cell.visual.iformat = self.mlx.mlx_get_data_addr(cell.visual.img)
                # PUT PIXEL FUNC
                self.put_square(cell.visual)
                self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_1, cell.visual.img, x * 20 + cell.visual.width, y * 20 + cell.visual.height)
        self.mlx.mlx_loop(self.mlx_ptr)