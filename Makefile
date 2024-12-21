

clean:
	rm -f dist/*

build: clean
	python -m build

test_pypi: build
	python -m twine upload --verbose --repository testpypi dist/*

pypi: build
	python -m twine upload dist/*

test:
	. ../pip-viz-venv/bin/activate; export PYTHONPATH='src'; pytest

upgrade_pypi_tools:
	. ../pip-viz-venv/bin/activate; pip install --upgrade build twine pkginfo
