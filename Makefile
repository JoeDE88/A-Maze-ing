VENV=.venv

$(VENV):
	python3 -m venv $(VENV);

install:
	uv pip install -r requirements.txt
	uv pip install mlx-2.2/ubuntu/mlx-2.2-py3-none-any.whl

unpack:
	tar -xzf mlx-2.2/src/mlx_CLXV-2.2.tgz

run:
	uv run a_maze_ing.py config.txt

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf mlx_CLXV
	find . -type d \( -name .git -o -name .venv \) -prune -o -type d -iname '*cache*' -print -exec rm -rf {} +

lint:
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-import --disallow-untyped-defs --check-untyped-defs
	flake8 .

lint-strict:
	mypy . --strict

.PHONY: all clean re