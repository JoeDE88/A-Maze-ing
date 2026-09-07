VENV=.venv

$(VENV):
	python3 -m venv $(VENV);
	source $(VENV)/bin/activate