.PHONY: help build up down shell migrate createsuperuser logs clean test lint

help:
	@echo "Available commands:"
	@echo "  build      Build Docker containers"
	@echo "  up         Start development environment"
	@echo "  down       Stop containers"
	@echo "  shell      Django shell"
	@echo "  migrate    Run migrations"
	@echo "  createsuperuser Create admin user"
	@echo "  logs       Show logs"
	@echo "  clean      Clean containers and volumes"
	@echo "  test       Run tests"
	@echo "  lint       Run linting"

build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

shell:
	docker-compose exec web python manage.py shell

migrations:
	docker-compose exec web python manage.py makemigrations

migrate:
	docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec web python manage.py test

lint:
	docker-compose exec web flake8 . --max-line-length=88 --exclude=migrations
