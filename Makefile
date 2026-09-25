VENV=venv

$(VENV):
	uv $(VENV) --python 3.14

install:
	uv pip install -r requirements.txt

install_mlx:
	uv pip install mlx-2.2-py3-none-any.whl

run:
	python3 a_maze_ing.py config.txt

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d \( -name .git -o -name .venv \) -prune -o -type d -iname '*cache*' -print -exec rm -rf {} +

lint:
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-import --disallow-untyped-defs --check-untyped-defs
	flake8 .

lint-strict:
	mypy . --strict

.PHONY: all clean re