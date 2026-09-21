# mazegen

Módulo reutilizable de generación de laberintos, extraído del proyecto
*A-Maze-ing* (42). Contiene la clase `MazeGenerator` y no depende del
código de visualización del proyecto original.

## Instalación

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Uso básico

```python
from mazegen import MazeGenerator

maze = MazeGenerator()   # lee WIDTH/HEIGHT/ENTRY/EXIT/... de sys.argv[1]
maze.gen_maze()
maze.solve()

print(maze.width, maze.height)
print(maze.entry, maze.exit)
print(maze.solution)     # p.ej. ['E', 'E', 'S', ...]
```

## Parámetros personalizados (tamaño, semilla, ...)

`MazeGenerator()` toma todos sus parámetros (`WIDTH`, `HEIGHT`, `ENTRY`,
`EXIT`, `OUTPUT_FILE`, `PERFECT`, `SEED` opcional) de un fichero de
configuración leído a través de `check_config()`, que a su vez usa
`sys.argv[1]` como ruta. Para generar con parámetros distintos, apunta
`sys.argv[1]` a otro fichero antes de instanciar:

```python
import sys
sys.argv = [sys.argv[0], "mi_config.txt"]

from mazegen import MazeGenerator
maze = MazeGenerator()
```

> Nota: esta es una limitación conocida del diseño actual — no hay todavía
> un constructor con argumentos nombrados (`MazeGenerator(width=10, ...)`).
> Queda como posible mejora futura.

## Acceder a la estructura generada y a la solución

- `maze.grid`: array 2D de objetos `Cell` (`grid[x][y]`), cada uno con:
  - `cell.pos`: coordenadas `(x, y)`
  - `cell.walls`: entero de 0 a 15 que codifica las paredes cerradas
    (bit 0 = Norte, 1 = Este, 2 = Sur, 3 = Oeste; bit a 1 = pared cerrada)
  - `cell.untouchable`: `True` si la celda pertenece al patrón "42"
- `maze.entry`, `maze.exit`: coordenadas de entrada y salida
- `maze.solution`: tras llamar a `maze.solve()`, lista de letras
  `N`/`E`/`S`/`W` con el camino más corto de entrada a salida
- `maze.gen_output()`: escribe el laberinto en `maze.output` usando el
  formato hexadecimal descrito en el proyecto principal (no es el mismo
  formato que `maze.grid`)

## Licencia

MIT — ver `LICENSE.md`. Permite el uso, copia, modificación y
distribución de este módulo por cualquier proyecto que lo reutilice.
