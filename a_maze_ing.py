from mazegen import MazeGenerator
from mazegen.maze_visuals import MLXVar
from mazegen import CustomException

if __name__ == "__main__":
    try:
        m = MazeGenerator()
        m.gen_maze()
        m.solve()

        xvar = MLXVar(m)
        xvar.renderize()

        m.gen_output()

    except PermissionError as p:
        if p.errno == 13:
            print(p)

    except CustomException as c:
        print(f"{c}")

    except Exception as e:
        print(f"{e}")
