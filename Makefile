# Makefile to simplify some common development tasks.
# Run 'make help' for a list of commands.

PYTHON=`which python`

# cli prefix for commands to run in container
RUN_DOCK = \
docker-compose up --build && docker-compose run --rm sql2gee sh -l -c

.PHONY: shell, help, install, clean, test, release 
default: help

help:
	@echo "Available commands:"
	@sed -n '/^[a-zA-Z0-9_.]*:/s/:.*//p' <Makefile | sort

install:
	pip install -e .

shell:
	$(RUN_DOCK) "cd ~/sql2gee \
		&& ([ -d "sql2gee" ] || ln -sf module "sql2gee") \
		&& bash"

test:
	py.test -v

clean:
	$(PYTHON) setup.py clean
	find . -name '*.pyc' -delete
	find . -name '*~' -delete

release:
	@rm -rf dist/
	python setup.py sdist upload -r pypi
	python setup.py bdist_wheel upload -r pypi
