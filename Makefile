
run:
	docker run -p 4444:4444 -v $$PWD/amazon-dash-private:/amazon-dash-private:ro --rm andgineer/iot-calendar

reqs:
	pre-commit autoupdate
	bash ./scripts/compile_requirements.sh
	pip install -r requirements.txt
	pip install -r requirements.dev.txt
