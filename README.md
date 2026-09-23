*This project has been created as part of the 42 curriculum by jdiaz-ec, gblas-he.*

# A-Maze-ing

## Description

**A-Maze-ing** is a Python maze generator. Given a configuration file, it builds a
maze on a rectangular grid, computes the shortest path between an entry and an
exit cell, writes the result to a hexadecimal output file, and displays the maze
graphically through a MiniLibX (MLX) window.

The maze can be generated in two modes, controlled by the `PERFECT` flag of the
configuration file:

- **`PERFECT=True`**: a perfect maze — just one path between the entry and the
  exit, no loops at all (a classic "lab" maze).
- **`PERFECT=False`** (default): a **playable, Pac-Man-like board** — fully
  connected, with the four corners and the centre open, at least two independent
  routes between entry and exit (loops), and dead-ends kept rare.

Whichever mode is chosen, the maze always contains a visible **"42"** pattern made
of untouchable, fully-closed cells (as long as the grid is large enough to fit
it — otherwise a warning is printed and the pattern is skipped).

## Instructions

### Requirements

- Python 3.14+
- The dependencies listed in `requirements.txt`
- A working MiniLibX (MLX) Python binding (`mlx` module) for the graphical
  display — installed with `make unpack`

### Installation

```bash
make install
```

This installs the project's Python dependencies (via `uv`/`pip`).

### Running

```bash
python3 a_maze_ing.py config.txt
```

or, using the provided Makefile:

```bash
make run
```

- `a_maze_ing.py` is the mandatory entry point.
- `config.txt` (or any other filename you pass as the single argument) is a
  plain-text configuration file, see the format below. A default `config.txt`
  is provided at the root of the repository.

Debugging (drops into `pdb` on the main script):

```bash
make debug
```

Linting (`flake8` + `mypy`):

```bash
make lint          # mandatory flags
make lint-strict    # mypy --strict (recommended, optional)
```

Cleaning generated/cache files:

```bash
make clean
```

The program never crashes on bad input: configuration errors, out-of-bounds
coordinates, an impossible "42" pattern, etc. are all caught and reported with a
clear `error: ...` message on the console instead of a traceback.

### Interacting with the maze (menu)

Once the MLX window opens, the following keyboard shortcuts are available (the
window must have focus):

| Key | Action |
|-----|--------|
| `1` | Regenerate a brand-new maze and redraw it |
| `2` | Show / hide the shortest path between entry and exit |
| `3` | Rotate the wall colour palette |
| `4` or `q` | Quit and close the window |

The same summary is printed to the terminal as soon as the window opens.

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line. Lines starting
with `#` are comments and are ignored.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width, in cells | `WIDTH=10` |
| `HEIGHT` | Maze height, in cells | `HEIGHT=10` |
| `ENTRY` | Entry coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` | `EXIT=9,9` |
| `OUTPUT_FILE` | Name of the generated output file | `OUTPUT_FILE=output_maze.txt` |
| `PERFECT` | `True` for a perfect (single-path) maze, `False` for a playable/looped board | `PERFECT=False` |
| `SEED` *(optional)* | Seed for the random generator, for reproducibility | `SEED=42` |

All six mandatory keys must be present; a missing key, an out-of-bounds entry or
exit, or `ENTRY == EXIT` is reported as a configuration error and the program
stops cleanly.

### Output file format

The output file contains, row by row, one hexadecimal digit per cell encoding
its closed walls (bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West — a
set bit means the wall is closed). After a blank line, three more lines follow:
the entry coordinates, the exit coordinates, and the shortest path from entry to
exit as a sequence of `N`/`E`/`S`/`W` letters.

## Maze generation algorithm

The maze is generated with an improved version of **Hunt & Kill** algorithm:

1. **Walk**: starting from the entry cell, randomly walk to an unvisited
   neighbour, carving a passage (opening the two matching walls) as it goes,
   until it gets stuck (no unvisited neighbour left).
2. **Hunt**: scan the grid row by row for the first unvisited cell that has at
   least one already-visited neighbour, carve a passage between them, and
   resume walking from there.
3. Repeat steps 1–2 until every reachable cell has been visited.

When `PERFECT=False`, two extra passes are applied afterwards:
`open_corners()` opens one extra wall on each of the four "dead-end" corners,
and `open_dead_ends()` opens one extra wall on every remaining cell that only
has a single opening, so that the maze gets the loops and connectivity required
by a Pac-Man-style board instead of staying a perfect (single-path) maze.

**Why Hunt & Kill?** It is simple to reason about and to implement correctly
, it naturally produces long, winding corridors with comparatively few dead-ends
once combined with the corner/dead-end-opening passes, and it keeps the "carve
a passage between two neighbouring cells" operation local, which made it easy
to guarantee wall coherence between neighbouring cells and to keep the "42"
pattern cells untouched (`untouchable` cells are simply skipped as neighbours).
It was improved by remembering the last position of the hunting part.


## Maze solver algorithm
The shortest path between entry point and exit point is computed separately with **Dijkstra's algorithm** walking the open walls of the maze as a graph.

Djikstra’s Algorithm give always an optimal solution based on a **Bread-First-Search** and queues.
The working of Dijkstra’s algorithm follows a greedy approach. It always picks the node with the smallest known distance and expands from there.

## Reusable module

The maze generation logic lives entirely in `maze_gen.py`, inside the
`MazeGenerator` class. It can be imported and reused in another project.

### Basic usage

```python
from mazegen import MazeGenerator

# NOTE: MazeGenerator reads its configuration through conf_validator.check_config(),
# which itself reads sys.argv[1] as the path to a config file
# (see "Custom parameters" below for programmatic alternatives).
maze = MazeGenerator()
maze.gen_maze()   # builds the maze
maze.solve()       # computes the shortest path, stored in maze.solution

print(maze.width, maze.height)
print(maze.entry, maze.exit)
print(maze.solution)          # e.g. ['E', 'E', 'S', ...]
```

### Custom parameters (size, seed, entry/exit, ...)

All parameters (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, `PERFECT`,
optionally `SEED`) come from the configuration file passed as `sys.argv[1]`.
To reuse the generator with different parameters, write/point to a different configuration file.


### Packaging

The reusable module (code + this short documentation) is distributed as a pip
package, `mazegen-*`, built at the root of the repository (`.whl`/`.tar.gz`),
so it can be installed and imported in a later project independently of the
display and CLI parts of this repository.

## Resources

- [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Buckblog: "Maze Generation: Hunt-and-Kill algorithm"](https://weblog.jamisbuck.org/2011/1/24/maze-generation-hunt-and-kill-algorithm) — reference for the Hunt & Kill algorithm implemented.
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — used for the shortest-path solver
- [42 MiniLibX documentation](https://harm-smits.github.io/42docs/libs/minilibx) — used for the graphical display

### AI usage

AI assistance was used during this project as follows:

- Drafting the interactive MLX menu (`maze_visuals.py`): the keyboard-driven
  options to regenerate the maze, show/hide the shortest path, and rotate the
  wall colours, plus the corresponding `redraw()` logic.


All AI-generated code was read, understood, and adapted by the team before
being committed; nothing was used without being able to explain how it works.

## Team & project management

- **Team members and roles**: jdiaz-ec, gblas-he
- **Planning**: initial plan, and how it evolved through the project.
- **What worked well / what could be improved**.
- **Specific tools used**: e.g. `uv` for dependency management, `mypy`/`flake8`
  for static checking, git branches/PR workflow, etc.