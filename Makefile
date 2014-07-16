default: test

test: lint
	python setup.py test

lint:
	flake8 errbit_reporter/ test/ *.py

clean:
	rm -f errbit_reporter/*.pyc test/*.pyc
	rm -rf errbit_reporter/__pycache__ test/__pycache__ \
	       *.egg-info *.egg build/ docs/_build/

doc:
	rm -rf docs/_build
	python setup.py build_sphinx

upload-doc: doc
	python setup.py upload_sphinx
