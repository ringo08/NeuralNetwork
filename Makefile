PYTHON = python3.10
PIP = pip3
PROGRAM = ./app.py
ENV_DIR = .venv

install: $(ENV_DIR)
	$(PYTHON) -m venv $(ENV_DIR) --clear --upgrade-deps

start: $(ENV_DIR)
	$(PIP) install pytk

test: 
	$(PYTHON) -m tkinter