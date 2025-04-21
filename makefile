.EXPORT_ALL_VARIABLES:
PY_CACHE_DIR = $(shell find . -type d -name __pycache__)

define cleanPyCache
	@echo "Cleaning Python cache directories..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
endef

.PHONY: build
## Build package
build:
	@echo "building package..."
	@poetry version $(shell git describe --tags --abbrev=0)
	poetry build

.PHONY: format
## Run pre-commit hook to do the formatting
format:
	@poetry run pre-commit install
	@poetry run pre-commit run --all

.PHONY: publish
## Tag new version, build package and upload it to pypi
publish:
	@poetry version $(shell git describe --tags --abbrev=0); \
	rm -rf build; \
	poetry publish --build

.PHONY: clean
## Remove build, dist, and *.egg-info directories after build or installation
clean:
	@-rm -rf build
	@-rm -rf dist
	@-rm -rf *.egg-info
	$(call cleanPyCache)

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
