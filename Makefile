build:
	docker build -t 'andgineer/iot-calendar' -f docker/Dockerfile .

pull:
	docker pull 'andgineer/iot-calendar'

run:
	docker run --rm -it -v '$(PWD)/../amazon-dash-private:/amazon-dash-private:ro' -p '4444:4444' 'andgineer/iot-calendar'

reqs:
	pre-commit autoupdate
	bash ./scripts/compile_requirements.sh
	pip install -r requirements.dev.txt
