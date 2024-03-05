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
	poetry run python -m scheduler.main
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

.PHONY: rebuild
rebuild:
	docker-compose down --remove-orphans
	docker-compose up --force-recreate --build

# Docker utils
.PHONY: start
start:
	docker-compose up --force-recreate ${MODE}

.PHONY: stop
project-stop:
	docker-compose down --remove-orphans ${MODE}