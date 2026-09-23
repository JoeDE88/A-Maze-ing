from random import randint
from maze_generator import MazeGenerator
from maze_visuals import MLXVar

if __name__ == "__main__":
    # try:
        # CREAR CLASE MazeGenerator PARA GENERAR LABERINTO
        m = MazeGenerator()
        m.gen_maze()

        # PARA RESOLVER ENCONTRAR RUTA MAS CORTA ENTRE entry Y exit
        # (se hace ANTES de abrir la ventana para que el menú de la
        # ventana MLX pueda mostrar/esconder la solución desde el inicio)
        m.solve()

        # PARA INICIAR MAZE EN MINILIBX
        xvar = MLXVar(m)
        xvar.renderize()

        # PARA GENERAR OUTPUT FILE
        m.gen_output()

    # except Exception as e:
        # print(f"error: {e}")
