.PHONY: help install install-dev clean test coverage lint format type-check build upload upload-test venv

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
	@echo "  make upload-test   - Upload to TestPyPI"
	@echo "  make upload        - Upload to PyPI"

venv/bin/python:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Upgrading pip..."
	venv/bin/pip install --upgrade pip

.install-stamp: venv/bin/python requirements.txt
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .
	@touch .install-stamp

.install-dev-stamp: .install-stamp requirements-dev.txt
	venv/bin/pip install -r requirements-dev.txt
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
	rm -rf venv/
	rm -rf .install-stamp .install-dev-stamp
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: .install-dev-stamp
	venv/bin/python -m pytest tests/ -v

coverage: .install-dev-stamp
	venv/bin/python -m pytest tests/ --cov=energy_tracker_api --cov-report=html --cov-report=term

lint: .install-dev-stamp
	venv/bin/python -m black --check energy_tracker_api/ tests/
	venv/bin/python -m isort --check-only energy_tracker_api/ tests/

format: .install-dev-stamp
	venv/bin/python -m black energy_tracker_api/ tests/
	venv/bin/python -m isort energy_tracker_api/ tests/

type-check: .install-dev-stamp
	venv/bin/python -m mypy energy_tracker_api/

build: .install-dev-stamp
	venv/bin/python -m build

upload-test: .install-dev-stamp build
	venv/bin/python -m twine upload --repository testpypi dist/*

upload: .install-dev-stamp build
	venv/bin/python -m twine upload dist/*

all: clean format lint type-check test
