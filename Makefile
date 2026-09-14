VENV=.venv

$(VENV):
	python3 -m venv $(VENV);

install: requirements.txt
	pip install -r requirements.txt

unpack: mlx-2.2.tgz
	tar -xvf mlx-2.2.tgz
	unzip ubuntu/mlx-2.2-py3-none-any.whl

clean:
	rm -rf ubuntu fedora src mlx-2.2.dist-info

.PHONY: all clean re