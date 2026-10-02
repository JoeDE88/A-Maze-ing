from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from mazegen.maze_visuals import ImgData


def rgba_to_int32(r: int, g: int, b: int, a: int = 255) -> int:
    return (a << 24) | (r << 16) | (g << 8) | b


def put_pixel(img: ImgData, x: int, y: int, color: int) -> None:
    if not (0 <= x < img.w and 0 <= y < img.h):
        return
    bpp = img.bpp // 8
    offset = y * img.sl + x * bpp
    data = cast(memoryview, img.data)
    data[offset:offset + bpp] = color.to_bytes(4, 'little')


def draw_square(
    img: ImgData,
    cell_size: int,
    x: int,
    y: int,
    rgb: tuple[int, ...]
) -> None:
    color = rgba_to_int32(*rgb)
    for dx in range(cell_size):
        for dy in range(cell_size):
            put_pixel(img, x + dx, y + dy, color)


def draw_wall(
    img: ImgData,
    cell_size: int,
    x: int,
    y: int,
    walls: int,
    rgb: tuple[int, ...]
) -> None:
    thickness = 1
    color = rgba_to_int32(*rgb)
    if (walls & 1):
        for t in range(thickness):
            for dx in range(cell_size):
                put_pixel(img, x + dx, y + t, color)
    if (walls & 2):
        for t in range(thickness):
            for dy in range(cell_size):
                put_pixel(img, x + cell_size - 1 - t, y + dy, color)
    if (walls & 4):
        for t in range(thickness):
            for dx in range(cell_size):
                put_pixel(img, x + dx, y + cell_size - 1 - t, color)
    if (walls & 8):
        for t in range(thickness):
            for dy in range(cell_size):
                put_pixel(img, x + t, y + dy, color)
