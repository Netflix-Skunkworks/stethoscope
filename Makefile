SHELL = /bin/bash -o pipefail

USER := $(shell whoami)

check-root:
ifeq ($(USER), root)
	@echo "WARNING: Installing as root should be avoided at all costs. Use a virtualenv."
endif

### REQUIREMENTS

install-python-requirements: setup.py check-root
	@echo "--> Installing Python development dependencies."
	pip install setuptools
	pip install -r requirements.txt

install-node-requirements:
	@echo "--> Installing Node development dependencies."
	cd stethoscope/ui && npm install

install-requirements: install-python-requirements install-node-requirements

### INSTALL/DEVELOP/BUILD

install-editable-package:
	@echo "--> Installing editable package."
	pip install --no-deps -e .[\
	google,\
	jamf,\
	landesk,\
	duo,\
	bitfit,\
	vpn_labeler,\
	mac_manufacturer,\
	vm_filter,\
	oidc,\
	es_logger,\
	es_notifications,\
	restful_feedback,\
	atlas,\
	batch,\
	batch_es,\
	batch_restful_summary\
	]

react-build:
	cd stethoscope/ui && npm run build

develop: install-requirements install-editable-package react-build

build-ui: install-node-requirements react-build

develop-ui:
	cd stethoscope/ui && npm start

install-develop-ui: install-node-requirements develop-ui

### DOCKER

docker-build-ui:
	@echo "--> Building UI code in a Docker container."
	docker-compose up node-builder

docker-build: Dockerfile Dockerfile-nginx docker-compose.yml docker-compose.base.yml
	docker-compose build

### TOKENS

dev-token-docker:
	@echo "--> Generating authentication token for local development using Docker."
	echo REACT_APP_TOKEN=$(shell docker-compose run -e STETHOSCOPE_API_INSTANCE_PATH="/code/instance/" login stethoscope-token) > stethoscope/ui/.env

dev-token:
	@echo "--> Generating authentication token for local development."
	echo REACT_APP_TOKEN=$(shell stethoscope-token) > stethoscope/ui/.env

### LINT

lint-py:
	@echo "--> Linting Python files."
# settings in setup.cfg
	pep8 instance config stethoscope tests
	isort --check-only --recursive --diff instance config stethoscope tests

lint-js:
	@echo "--> Linting JavaScript files."
	cd stethoscope/ui && npm run lint

lint: lint-py lint-js

### TEST

test-py: clean-py
	@echo "--> Running Python tests (see test.log for output)."
	py.test | tee test.log  # settings in pytest.ini

test-js-watch:
	@echo "--> Running JavaScript tests."
	cd stethoscope/ui && npm run test

test-js:
	@echo "--> Running JavaScript tests."
	cd stethoscope/ui && CI=true npm run test

test: test-py test-js

tox: clean-py
	@echo "--> Running tox."
	./tox.sh

coverage-py: clean-py
	@echo "--> Running Python tests with coverage (see test.log and htmlcov/ for output)."
	py.test --cov-report html --cov=stethoscope | tee test.log  # settings in pytest.ini

### CLEAN

clean-py:
	@echo "--> Removing Python bytecode files."
	find . -name '__pycache__' -delete  # Python 3
	find . -name '*.py[co]' -delete  # Python 2

clean-js:
	@echo "--> Removing JavaScript build output."
	rm -rf stethoscope/ui/build

clean-static:
	@echo "--> Removing generated static content."
	rm -rf stethoscope/static && rm -f stethoscope/login/templates/layout.html

clean: clean-py clean-js clean-static

### DISTCLEAN

distclean-py: clean-py
	@echo "--> Removing egg-info directory."
	rm -rf Stethoscope.egg-info

distclean-js: clean-js
	@echo "--> Removing node modules."
	rm -rf stethoscope/ui/node_modules

distclean: distclean-py distclean-js clean-static

### PHONY

.PHONY: \
	check-root \
	install-python-requirements \
	install-node-requirements \
	install-requirements \
	install-editable-package \
	develop \
	install-develop-ui \
	build-ui \
	docker-build-ui \
	develop-ui \
	docker-build \
	react-build \
	dev-token-docker \
	dev-token \
	lint \
	lint-py \
	lint-js \
	test \
	test-py \
	test-js-watch \
	test-js \
	tox \
	coverage-py \
	clean-py \
	clean-js \
	clean-static \
	clean \
	distclean-py \
	distclean-js \
	distclean
