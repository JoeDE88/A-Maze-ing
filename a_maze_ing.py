from random import randint
from maze_gen import MazeGenerator
from maze_visuals import MLXVar

if __name__ == "__main__":
    # try:
        m = MazeGenerator()
        m.gen_maze()
        # print(m.grid)
        print(f"\n\nPerfect: {str(m.perfect).upper()}")
        print("   ", end="")
        for i in range(m.width):
            if i < 10:
                print(f"  {i}", end="")
            else:
                print(f" {i}", end="")
        print()
        print("    ", end="")
        print("___" * m.width, end="")
        print() 
        fg = randint(90, 97)
        for x in range(m.height):
            y = 0
            endcolor = "\033[00m"
            print(f"{x:02d} |", end="")
            for y in range(m.width):
                if m.grid[x][y].untouchable:
                    startcolor = f"\033[{fg};{fg + 10}m"
                elif m.grid[x][y].pos == m.entry:
                    startcolor = f"\033[0;{102}m"
                elif m.grid[x][y].pos == m.exit:
                    startcolor = f"\033[{43};{43+10}m"
                else:
                    startcolor = ""
                if m.grid[x][y].walls == 0:
                    print(f"{startcolor}   {endcolor}", end="")
                if m.grid[x][y].walls == 8:
                    print(f"{startcolor}|  {endcolor}", end="")
                if m.grid[x][y].walls == 12:
                    print(f"{startcolor}|__{endcolor}", end="")
                if m.grid[x][y].walls == 9:
                    print(f"{startcolor}|  {endcolor}", end="")
                if m.grid[x][y].walls == 1:
                    print(f"{startcolor}   {endcolor}", end="")
                if m.grid[x][y].walls == 14:
                    print(f"{startcolor}|_|{endcolor}", end="")
                if m.grid[x][y].walls == 13:
                    print(f"{startcolor}|__{endcolor}", end="")
                if m.grid[x][y].walls in [2, 3]:
                    print(f"{startcolor}  |{endcolor}", end="")
                if m.grid[x][y].walls in [4, 5]:
                    print(f"{startcolor}___{endcolor}", end="")
                if m.grid[x][y].walls in [6, 7]:
                    print(f"{startcolor}__|{endcolor}", end="")     
                if m.grid[x][y].walls in [10, 11]:
                    print(f"{startcolor}| |{endcolor}", end="")
                if m.grid[x][y].walls == 15:
                    print(f"{startcolor}|_|{endcolor}", end="")
                y += 1
                if y == m.width:
                    print(f"|{x}")

        xvar = MLXVar(m)
        xvar.renderize()
        # for x in range(m.height):
        #     y = 0
        #     for y in range(m.width):
        #         print(f"{m.grid[x][y].walls:04b}")
        # m.gen_output()
        # m.solve()
    # except Exception as e:
    #     print(f"error: {e}")
