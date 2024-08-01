

clean:
	rm -f dist/*

build: clean
	python -m build

test_pypi: build
	python -m twine upload --repository testpypi dist/*

pypi: build
	python -m twine upload dist/*




