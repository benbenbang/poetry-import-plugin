.EXPORT_ALL_VARIABLES:
PYTHON_INTERPRETER = $(shell which python)
PY_CACHE_DIR = `find . -type d -name __pycache__`

# Args
pypi_apitoken =

ifeq (,$(shell which poetry))
HAS_POETRY=False
else
HAS_POETRY=True
endif

define cleanPyCache
@while read pyCD; \
do \
	if [ -n "$$pyCD" ]; then \
		rm -r $$pyCD; \
	fi \
done <<< $(PY_CACHE_DIR)
endef

.PHONY: build
## Build
build_pkg:
	@echo "Start to build pkg"
ifeq (True,$(HAS_POETRY))
	@poetry version $(shell git describe --tags --abbrev=0); \
	poetry build
else
	@export VERSION=$(shell git describe --tags --abbrev=0); \
	$(PYTHON_INTERPRETER) setup.py build; \
	$(PYTHON_INTERPRETER) setup.py sdist
endif

.PHONY: format
## Run pre-commit hook to do the formating
format:
ifeq (True,$(HAS_POETRY))
	@-poetry run pre-commit install
	@-poetry run pre-commit run --all
else
	@-pre-commit install
	@-pre-commit run --all
endif

.PHONY: publish
## Tag new version and upload to pypi
upload:
	@poetry config pypi-token.pypi $$pypi_apitoken; \
	poetry version $(shell git describe --tags --abbrev=0); \
	poetry publish --build

.PHONY: clean
## Remove build, dist and *.egg-info directories after build or installation
clean:
	@-rm -r build
	@-rm -r dist
	@-rm -r oqim.egg-info
	@-$(call cleanPyCache)

.PHONY: build
## Run build_pkg, format together
build: format build_pkg

.PHONY: install
## Install package in current env
install: install_pkg clean

ci: test build_pkg

.DEFAULT_GOAL := help

help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
