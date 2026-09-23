*This project has been created as part of the 42 curriculum by jdiaz-ec and gblas-he.*

# A-Maze-ing


## Description

A-Maze-ing is a maze generator written in Python. You give it a config file,
it builds a maze on a rectangular grid, finds the shortest path from the entry
to the exit, dumps everything to a hex output file, and shows the maze in a
MiniLibX (MLX) window.

There are two modes, depending on the `PERFECT` flag in the config:

- **`PERFECT=True`** — a proper perfect maze. One single path from entry to
  exit, zero loops, the classic "lab" maze look.
- **`PERFECT=False`** (the default) — a playable board, Pac-Man style.
  Everything is connected, the four corners and the centre are open, there
  are at least two independent routes between entry and exit (so there are
  loops), and dead-ends are kept to a minimum.

Either way, the maze always has a **"42"** pattern drawn into it, made of cells
that stay completely closed and are never touched. If the grid is too small to
fit the pattern, we print a warning and skip it instead of crashing.

## Instructions

### What you need

- Python 3.14+
- Whatever is listed in `requirements.txt`
- A working MiniLibX (MLX) Python binding (the `mlx` module) for the graphical
  part — unpack it with `make unpack`

### Install

```bash
make install
```

This pulls in the Python dependencies (through `uv`/`pip`).

### Run

```bash
python3 a_maze_ing.py config.txt
```

Or through the Makefile:

```bash
make run
```

- `a_maze_ing.py` is the mandatory entry point.
- `config.txt` (or whatever filename you pass as the only argument) is a
  plain-text config file — format is described below. There's a default
  `config.txt` sitting at the root of the repo.

If you want to debug the main script with `pdb`:

```bash
make debug
```

For linting (`flake8` + `mypy`):

```bash
make lint           # the mandatory flags
make lint-strict    # mypy --strict, optional but recommended
```

To clean up generated/cache files:

```bash
make clean
```

The program should never crash on bad input. Config errors, out-of-bounds
coordinates, an impossible "42" pattern — all of that is caught and printed
as a clean `error: ...` line on the console instead of a traceback.

### Playing with the maze (menu)

Once the MLX window opens, you can use these keys (the window needs focus):

| Key | What it does |
|-----|--------------|
| `1` | Regenerate a brand-new maze and redraw it |
| `2` | Show / hide the shortest path between entry and exit |
| `3` | Rotate the wall colour palette |
| `4` or `q` | Quit and close the window |

The same list of options is printed to the terminal when the window opens,
so you don't have to memorise it.

## Config file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and get
ignored.

| Key | What it means | Example |
|-----|---------------|---------|
| `WIDTH` | Maze width, in cells | `WIDTH=10` |
| `HEIGHT` | Maze height, in cells | `HEIGHT=10` |
| `ENTRY` | Entry coordinates, `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates, `x,y` | `EXIT=9,9` |
| `OUTPUT_FILE` | Name of the file to write the maze to | `OUTPUT_FILE=output_maze.txt` |
| `PERFECT` | `True` for a perfect single-path maze, `False` for a playable/looped board | `PERFECT=False` |
| `SEED` *(optional)* | Seed for the random generator, handy for reproducibility | `SEED=42` |

All six mandatory keys need to be there. If one is missing, or the entry/exit
is out of bounds, or `ENTRY == EXIT`, we treat it as a config error and exit
cleanly.

### Output file format

Row by row, one hex digit per cell. Each digit encodes the closed walls of that
cell (bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West — a set bit means
the wall is closed). After a blank line, three more lines come: entry
coordinates, exit coordinates, and the shortest path from entry to exit as a
string of `N`/`E`/`S`/`W` letters.

## How the maze is generated

We used an improved version of the **Hunt & Kill** algorithm:

1. **Walk** — start from the entry cell, randomly wander into an unvisited
   neighbour, carving a passage (opening both matching walls) as you go. Keep
   going until you get stuck (no unvisited neighbour left).
2. **Hunt** — scan the grid row by row for the first unvisited cell that has
   at least one visited neighbour, carve a passage between them, and start
   walking again from there.
3. Repeat steps 1–2 until every reachable cell has been visited.
4. The improvement is remembering the last hunting position and keep hunting from there, instead of starting the hunt every time from the (0,0) point.

When `PERFECT=False`, we run two extra passes afterwards: `open_corners()`
opens one extra wall on each of the four "dead-end" corners, and
`open_dead_ends()` opens one extra wall on every remaining cell that only has a
single opening. That's what gives the maze the loops and connectivity a
Pac-Man-style board needs, instead of leaving it as a perfect single-path maze.

**Why Hunt & Kill?** A few reasons. It's easy to reason about and to implement
correctly — you don't need an external stack or union-find structure beyond the
grid itself. It naturally produces long, winding corridors with relatively few
dead-ends, especially once you add the corner/dead-end-opening passes. And it
keeps the "carve a passage between two neighbouring cells" step local, which
made it much easier to keep wall coherence between neighbours and to leave the
"42" cells untouched (we just skip `untouchable` cells as neighbours).

The shortest path (used for the output file and the "show solution" option in
the menu) is computed separately with **Dijkstra's algorithm** (`dijkstra()` /
`get_solution()`), treating the open walls of the maze as a graph.

## Reusable module

All the generation logic lives in `maze_gen.py`, inside the `MazeGenerator`
class, and has zero dependency on the display code (`maze_visuals.py`). You can
import it and reuse it in another project without dragging the rest along.

### Basic usage

```python
from mazegen import MazeGenerator

# NOTE: MazeGenerator reads its config through conf_validator.check_config(),
# which in turn reads sys.argv[1] as the path to a config file.
# See "Custom parameters" below for programmatic alternatives.
maze = MazeGenerator()
maze.gen_maze()   # builds the maze
maze.solve()      # computes the shortest path, stored in maze.solution

print(maze.width, maze.height)
print(maze.entry, maze.exit)
print(maze.solution)          # e.g. ['E', 'E', 'S', ...]
```

### Custom parameters (size, seed, entry/exit, ...)

Every parameter (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, `PERFECT`,
and optionally `SEED`) comes from the config file passed as `sys.argv[1]`. If you want to reuse the generator
with different parameters, just write or point to a different config file. 


### Packaging

The reusable module (code plus this short doc) ships as a pip package,
`mazegen-*`, built at the root of the repo (`.whl` / `.tar.gz`), so it can be
installed and imported in a later project without needing the display or CLI
parts of this repo.

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Buckblog: "Maze Generation: Hunt-and-Kill algorithm"](https://weblog.jamisbuck.org/2011/1/24/maze-generation-hunt-and-kill-algorithm)
- [Dijkstra's algorithm — Wikipedia]
- [42 MiniLibX docs](https://harm-smits.github.io/42docs/libs/minilibx) — for the graphical display

### AI usage

We used AI assistance during the project.
Every bit of AI-generated code was read, understood, and adapted by us before
it got committed. We didn't keep anything we couldn't explain.

## Team & project management

* **Team members and roles**:

  * **jdiaz-ec**: worked on the maze generation and the path between the entry and exit.
  * **gblas-he**: worked on the visual part, including the MLX window, colours and user interaction.

* **Planning**: We divided the project into two main parts: maze generation and visualisation. We worked on them separately at first and then integrated both parts and fixed the problems that appeared.

* **What worked well / what we'd improve**: Dividing the work helped us work faster and focus on our parts. We could have planned the integration between both parts better from the beginning.

* **Tools we used**: Python, MiniLibX, Git, uv, mypy, flake8 and pdb.