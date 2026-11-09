PYTHON ?= python3

.PHONY: install data validate test run
install:
	$(PYTHON) -m pip install -r requirements-dev.txt

data:
	$(PYTHON) -m bench generate-data

validate:
	$(PYTHON) -m bench validate-data

test:
	$(PYTHON) -m pytest -q

run:
	$(PYTHON) -m bench run --backend ollama --model qwen2.5:7b --split dev
