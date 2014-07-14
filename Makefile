default: test

test: lint
	python setup.py test

lint:
	flake8 errbit_reporter/ test/ *.py

clean:
	rm -f errbit_reporter/*.pyc test/*.pyc
	rm -rf errbit_reporter/__pycache__ test/__pycache__ \
	       *.egg-info *.egg build/
