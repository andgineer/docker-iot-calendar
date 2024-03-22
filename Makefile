#!make

.HELP: build  ## Build the image
build:
	docker build -t 'andgineer/iot-calendar' -f docker/Dockerfile .

.HELP: pull  ## Pull the image
pull:
	docker pull 'andgineer/iot-calendar'

.HELP: run  ## Run the container
run:
	docker run --rm -it -v '$(PWD)/../amazon-dash-private:/amazon-dash-private:ro' -p '4444:4444' 'andgineer/iot-calendar'

.HELP: reqs  ## Upgrade requirements including pre-commit
reqs:
	pre-commit autoupdate
	bash ./scripts/compile_requirements.sh
	uv pip install -r requirements.dev.txt

.PHONY: docs # mark as phony so it always runs even we have a docs folder
.HELP: docs  ## Docs preview English
docs:
	./scripts/docstrings.sh
	open -a "Google Chrome" http://127.0.0.1:8000/docker-iot-calendar/
	scripts/docs-render-config.sh en
	mkdocs serve -f docs/_mkdocs.yml

.HELP: docs-ru  ## Docs preview Russian
docs-ru:
	./scripts/docstrings.sh
	open -a "Google Chrome" http://127.0.0.1:8000/docker-iot-calendar/
	scripts/docs-render-config.sh ru
	mkdocs serve -f docs/_mkdocs.yml

.HELP: help  ## Display this message
help:
	@grep -E \
		'^.HELP: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".HELP: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
