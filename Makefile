VENV=.venv

$(VENV):
	python3 -m venv $(VENV);

install:
	uv pip install -r requirements.txt

unpack:
	tar -xvf mlx-2.2.tgz
	unzip ubuntu/mlx-2.2-py3-none-any.whl

run:
	uv run a_maze_ing.py config.txt

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf ubuntu fedora src mlx-2.2.dist-info
	find . -type d \( -name .git -o -name .venv \) -prune -o -type d -iname '*cache*' -print -exec rm -rf {} +

lint:
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-import --disallow-untyped-defs --check-untyped-defs
	flake8 .

lint-strict:
	mypy . --strict

.PHONY: all clean re