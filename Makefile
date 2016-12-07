build:
	docker build -f docker/Dockerfile -t eblank:dev .

run:
	docker-compose -f docker/docker-compose.yml up --remove-orphans

test:
	docker run -iP -v $(shell pwd):/app:ro eblank:dev su -c 'python -m unittest' bob

coverage:
	docker run -iP -v $(shell pwd)/eblank:/app/eblank:ro -v $(shell pwd)/tests:/app/tests:ro eblank:dev bash -c "chmod 777 /app ; su -c 'coverage run --branch --source=eblank/ -m unittest && coverage report' bob"

flake:
	docker run -iP -v $(shell pwd):/app:ro eblank:dev flake8 --max-line-length=120 . *.py

pylint:
	docker run -iP -v $(shell pwd):/app eblank:dev script/pylint.sh

console:
	docker run -itP -v $(shell pwd):/app eblank:dev bash

attach:
	docker exec -it eblank bash
