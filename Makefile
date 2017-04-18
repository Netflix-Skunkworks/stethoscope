USER := $(shell whoami)

check-root:
ifeq ($(USER), root)
	@echo "WARNING: Installing as root should be avoided at all costs. Use a virtualenv."
endif

install-python-requirements: setup.py check-root
	@echo "--> Installing Python development dependencies."
	pip install setuptools
	pip install -r requirements.txt

install-node-requirements:
	@echo "--> Installing Node development dependencies."
	cd stethoscope/ui && npm install

install-requirements: install-python-requirements install-node-requirements

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

develop: install-requirements install-editable-package react-build

install-develop-ui: install-node-requirements develop-ui

build-ui: install-node-requirements react-build

docker-build-ui:
	@echo "--> Building UI code in a Docker container."
	docker-compose up node-builder

develop-ui:
	cd stethoscope/ui && npm start

docker-build: Dockerfile Dockerfile-nginx docker-compose.yml docker-compose.base.yml
	docker-compose build

react-build:
	cd stethoscope/ui && npm run build

dev-token-docker:
	@echo "--> Generating authentication token for local development using Docker."
	echo REACT_APP_TOKEN=$(shell docker-compose run -e STETHOSCOPE_API_INSTANCE_PATH="/code/instance/" login stethoscope-token) > stethoscope/ui/.env

dev-token:
	@echo "--> Generating authentication token for local development."
	echo REACT_APP_TOKEN=$(shell stethoscope-token) > stethoscope/ui/.env

lint: lint-python lint-js

lint-python:
	@echo "--> Linting Python files."
	pep8 instance config stethoscope tests  # settings in setup.cfg

lint-js:
	@echo "--> Linting JavaScript files."
	cd stethoscope/ui && npm run lint

test: cleanpy
	@echo "--> Running Python tests (see test.log for output)."
	py.test | tee test.log  # settings in pytest.ini

test-js-watch:
	@echo "--> Running JavaScript tests."
	cd stethoscope/ui && npm run test

test-js: cleanjsbuild
	@echo "--> Running JavaScript tests."
	cd stethoscope/ui && CI=true npm run test

tox: cleanpy
	@echo "--> Running tox."
	./tox.sh

coverage: cleanpy
	@echo "--> Running Python tests with coverage (see test.log and htmlcov/ for output)."
	py.test --cov-report html --cov=stethoscope | tee test.log  # settings in pytest.ini

cleanpy:
	@echo "--> Removing Python bytecode files."
	find . -name '__pycache__' -delete  # Python 3
	find . -name '*.py[co]' -delete  # Python 2

cleanjs: cleanjsbuild distcleanjs cleanstatic

cleanjsbuild:
	@echo "--> Removing JavaScript build output."
	rm -r stethoscope/ui/build ; true

cleanstatic:
	@echo "--> Removing generated static content."
	rm -r stethoscope/static ; rm stethoscope/login/templates/layout.html ; true

clean: cleanpy cleanjs cleanstatic

distcleanpy: cleanpy
	@echo "--> Removing egg-info directory."
	rm -rf Stethoscope.egg-info

distcleanjs:
	@echo "--> Removing node modules."
	rm -rf stethoscope/ui/node_modules ; true

distclean: distcleanpy distcleanjs

.PHONY: \
	build-ui \
	check-root \
	clean \
	cleanpy \
	cleanjsbuild \
	cleanstatic \
	coverage \
	dev-token \
	dev-token-docker \
	develop \
	develop-ui \
	distclean \
	distcleanjs \
	distcleanpy \
	docker-build \
	docker-build-ui \
	install-develop-ui \
	install-requirements \
	install-editable-package \
	install-node-requirements \
	install-python-requirements \
	lint \
	lint-python \
	lint-js \
	react-build \
	test \
	test-js \
	test-js-watch \
	tox
