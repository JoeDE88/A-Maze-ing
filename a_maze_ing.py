from mazegen import MazeGenerator
from mazegen.maze_visuals import MLXVar

if __name__ == "__main__":
    try:
        m = MazeGenerator()
        m.gen_maze()
        m.solve()

        xvar = MLXVar(m)
        xvar.renderize()

        m.gen_output()

    except Exception as e:
        print(f"error: {e}")
