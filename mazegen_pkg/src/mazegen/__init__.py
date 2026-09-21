"""mazegen: generador de laberintos reutilizable.

Instanciar y usar (ejemplo básico)
-----------------------------------
>>> from mazegen import MazeGenerator
>>> maze = MazeGenerator()   # lee WIDTH/HEIGHT/ENTRY/EXIT/... de sys.argv[1]
>>> maze.gen_maze()
>>> maze.solve()
>>> print(maze.width, maze.height)
>>> print(maze.entry, maze.exit)
>>> print(maze.solution)     # p.ej. ['E', 'E', 'S', ...]

Pasar parámetros personalizados (tamaño, semilla, ...)
-------------------------------------------------------
`MazeGenerator()` obtiene todos sus parámetros (WIDTH, HEIGHT, ENTRY, EXIT,
OUTPUT_FILE, PERFECT, SEED opcional) de un fichero de configuración leído
mediante `check_config()`, que a su vez toma la ruta desde `sys.argv[1]`.
Para generar un laberinto con parámetros distintos, apunta `sys.argv[1]` a
otro fichero de configuración antes de instanciar la clase:

>>> import sys
>>> sys.argv = [sys.argv[0], "mi_config.txt"]
>>> from mazegen import MazeGenerator
>>> maze = MazeGenerator()

Acceder a la estructura generada y a la solución
--------------------------------------------------
- `maze.grid`: array 2D de objetos `Cell` (`grid[x][y]`), cada uno con:
  - `cell.pos`: coordenadas `(x, y)`
  - `cell.walls`: entero de 0 a 15 que codifica las paredes cerradas
    (bit 0=Norte, 1=Este, 2=Sur, 3=Oeste; 1 = pared cerrada)
  - `cell.untouchable`: `True` si la celda pertenece al patrón "42"
- `maze.entry`, `maze.exit`: coordenadas de entrada/salida
- `maze.solution`: tras llamar a `maze.solve()`, lista de letras
  `N`/`E`/`S`/`W` con el camino más corto de entrada a salida
- `maze.gen_output()`: escribe el laberinto en `maze.output` usando el
  formato hexadecimal (no es el mismo formato que `maze.grid`)
"""

from .maze_gen import MazeGenerator, Cell, Directions, Walls
from .conf_validator import check_config, ConfigModel

__all__ = [
    "MazeGenerator",
    "Cell",
    "Directions",
    "Walls",
    "check_config",
    "ConfigModel",
]

__version__ = "1.0.0"
