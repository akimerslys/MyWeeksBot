.PHONY: help
help:
	@echo "  bot-run		Starts the bot (for docker-compose)"
	@echo "  scheduler-run	Starts the scheduler (for docker-compose)"
	@echo "  generate	Generate a new migration"
	@echo "  migrate	Apply migrations"
	@echo "  start Start with docker-compose"
	@echo "  stop  Stop docker-compose"
	@echo "  lint		Reformat code"
	@echo "  requirements  Export poetry.lock to requirements.txt"


.PHONY: bot-run
bot-run:
	migrate
	poetry run python -m bot.main

.PHONY: scheduler-run
scheduler-run:
	poetry run arq scheduler.main.WorkerSettings
.PHONY:
# Poetry and environments utils
REQUIREMENTS_FILE := requirements.txt

.PHONY: requirements
requirements:
	# Export poetry.lock to requirements.txt if needed
	poetry check
	poetry export -o ${REQUIREMENTS_FILE} --without-hashes


# Alembic utils
.PHONY: generate
generate:
	source .env
	poetry run alembic revision --m="$(NAME)" --autogenerate

.PHONY: migrate
migrate:
	source .env
	poetry run alembic upgrade head
	
# Docker utils
.PHONY: rebuild
rebuild:
	docker-compose down --remove-orphans
	docker-compose up --force-recreate --build

.PHONY: start
start:
	docker-compose up --force-recreate ${MODE}

.PHONY: stop
stop:
	docker-compose down --remove-orphans ${MODE}

.PHONY: clear
clear:
	sudo sync && echo 3 > /proc/sys/vm/drop_caches
	echo sudo free -h
