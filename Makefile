PYTHON ?= python3.14
SOURCES = energy_tracker_api/ tests/ scripts/ example.py

.PHONY: help install install-dev clean test coverage lint format type-check build check-dist upload upload-test venv all

help:
	@echo "Available commands:"
	@echo "  make venv          - Create virtual environment"
	@echo "  make install       - Install package in production mode"
	@echo "  make install-dev   - Install package with development dependencies"
	@echo "  make clean         - Remove build artifacts and cache files"
	@echo "  make test          - Run tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run code linting (black check + isort check)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make type-check    - Run type checking with mypy"
	@echo "  make build         - Build distribution packages"
	@echo "  make check-dist    - Validate packages and test an isolated wheel installation"
	@echo "  make upload-test   - Upload to TestPyPI"
	@echo "  make upload        - Upload to PyPI"

venv/bin/python:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Upgrading pip..."
	venv/bin/pip install --upgrade pip

venv: venv/bin/python

.install-stamp: venv/bin/python pyproject.toml
	venv/bin/pip install -e .
	@touch .install-stamp

.install-dev-stamp: .install-stamp pyproject.toml
	venv/bin/pip install -e '.[dev]'
	@touch .install-dev-stamp

install: .install-stamp

install-dev: .install-dev-stamp

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	rm -rf .install-stamp .install-dev-stamp
	find energy_tracker_api tests scripts -type d -name __pycache__ -exec rm -rf {} +

test: .install-dev-stamp
	venv/bin/python -m pytest tests/ -v

coverage: .install-dev-stamp
	venv/bin/python -m pytest tests/ --cov=energy_tracker_api --cov-report=html --cov-report=term --cov-report=xml

lint: .install-dev-stamp
	venv/bin/python -m black --check $(SOURCES)
	venv/bin/python -m isort --check-only $(SOURCES)

format: .install-dev-stamp
	venv/bin/python -m isort $(SOURCES)
	venv/bin/python -m black $(SOURCES)

type-check: .install-dev-stamp
	venv/bin/python -m mypy energy_tracker_api/ scripts/ example.py

build: .install-dev-stamp
	rm -rf build/ dist/
	venv/bin/python -m build

check-dist: build
	venv/bin/python -m twine check dist/*
	venv/bin/python scripts/check_distribution.py

upload-test: check-dist
	venv/bin/python -m twine upload --repository testpypi dist/*

upload: check-dist
	venv/bin/python -m twine upload dist/*

all: lint type-check coverage check-dist
