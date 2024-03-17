.PHONY: help
help:
	@echo "  bot-run		Starts the bot (for docker-compose)"
	@echo "  scheduler-run	Starts the scheduler (for docker-compose)"
	@echo "  generate	Generate a new migration with make generate m=msg  "
	@echo "  migrate	Apply migrations"
	@echo "  rebuild  	Rebuilding images"
	@echo "  start 		Start with docker-compose"
	@echo "  stop  		Stop docker-compose"
	@echo "  dead  		Deleting Images"
	@echo "  clear  	Clears cache"
	@echo "  lint		Reformat code"
	@echo "  requirements  Export poetry.lock to requirements.txt"


.PHONY: bot-run
bot-run:
	poetry run alembic upgrade head
	poetry run python3 -m src.bot

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
	poetry run alembic revision --autogenerate -m "$(m)"

.PHONY: migrate
migrate:
	poetry run alembic upgrade head

#language utils
.PHONY: update-locale
update-locale:
	cd src/bot
	pybabel extract --input-dirs=. -o locales/messages.pot --project=messages.
	pybabel update -i locales/messages.pot -d locales -D messages

# Docker utils
.PHONY: rebuild
rebuild:
	docker-compose down --remove-orphans ${MODE}
	docker-compose up --force-recreate --build

.PHONY: start
startup:
	docker-compose up 

.PHONY: kill
kill:
	docker-compose down --remove-orphans ${MODE}

.PHONY: rebuildbot
rebuildbot:
	docker stop $$(docker ps -qf "ancestor=myweeksbot_bot")
	docker rm $$(docker ps -aqf "ancestor=myweeksbot_bot")
	docker rmi myweeksbot_bot
	docker-compose up --build bot


.PHONY: rebuildscheduler
rebuildscheduler:
	docker stop $$(docker ps -qf "ancestor=myweeksbot_scheduler")
	docker rm $$(docker ps -aqf "ancestor=myweeksbot_scheduler")
	docker rmi myweeksbot_scheduler
	docker-compose up --build scheduler


.PHONY: mem
mem:
	@echo "DOCKER:"
	docker system df
	@echo " "
	@echo "SSD:"
	df -h
	@echo " "
	@echo " RAM:"
	free -h


.PHONY: clear
clear:
	docker system prune -a